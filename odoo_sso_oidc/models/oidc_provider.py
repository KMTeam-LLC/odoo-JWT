# -*- coding: utf-8 -*-
import logging
import secrets
import json
import urllib.request
import urllib.parse
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

# Check for optional dependencies
try:
    import jwt
    HAS_JWT = True
except ImportError:
    HAS_JWT = False
    _logger.warning("PyJWT not available - JWT signature verification will be disabled")

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    _logger.warning("requests library not available - using urllib instead")


class OIDCProvider(models.Model):
    _name = 'oidc.provider'
    _description = 'OIDC Provider Configuration'
    _order = 'sequence, name'

    name = fields.Char(string='Name', required=True, help='Provider name (e.g., Authentik, Okta)')
    sequence = fields.Integer(string='Sequence', default=10)
    active = fields.Boolean(string='Active', default=True)
    
    # OIDC Configuration
    client_id = fields.Char(string='Client ID', required=True, help='OAuth2/OIDC Client ID')
    client_secret = fields.Char(string='Client Secret', required=True, help='OAuth2/OIDC Client Secret')
    authorization_endpoint = fields.Char(
        string='Authorization Endpoint',
        required=True,
        help='Full URL to the authorization endpoint (e.g., https://authentik.example.com/application/o/authorize/)'
    )
    token_endpoint = fields.Char(
        string='Token Endpoint',
        required=True,
        help='Full URL to the token endpoint (e.g., https://authentik.example.com/application/o/token/)'
    )
    userinfo_endpoint = fields.Char(
        string='Userinfo Endpoint',
        required=True,
        help='Full URL to the userinfo endpoint (e.g., https://authentik.example.com/application/o/userinfo/)'
    )
    jwks_uri = fields.Char(
        string='JWKS URI',
        help='Full URL to the JWKS endpoint for JWT verification (optional)'
    )
    
    # Scopes and Claims
    scope = fields.Char(
        string='Scopes',
        default='openid profile email groups',
        required=True,
        help='Space-separated list of scopes to request'
    )
    groups_claim = fields.Char(
        string='Groups Claim',
        default='groups',
        help='Claim name in the ID token or userinfo that contains user groups'
    )
    email_claim = fields.Char(
        string='Email Claim',
        default='email',
        help='Claim name for user email'
    )
    name_claim = fields.Char(
        string='Name Claim',
        default='name',
        help='Claim name for user full name'
    )
    preferred_username_claim = fields.Char(
        string='Username Claim',
        default='preferred_username',
        help='Claim name for username'
    )
    
    # User Management
    auto_create_users = fields.Boolean(
        string='Auto-create Users',
        default=True,
        help='Automatically create Odoo users on first login'
    )
    sync_groups_on_login = fields.Boolean(
        string='Sync Groups on Login',
        default=True,
        help='Synchronize user groups from OIDC provider on every login'
    )
    
    # Group Mappings
    group_mapping_ids = fields.One2many(
        'oidc.group.mapping',
        'provider_id',
        string='Group Mappings',
        help='Map OIDC groups to Odoo groups'
    )
    
    # Callback URL (computed)
    callback_url = fields.Char(
        string='Callback URL',
        compute='_compute_callback_url',
        help='Use this URL as the redirect URI in your OIDC provider configuration'
    )
    
    @api.depends('id')
    def _compute_callback_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for provider in self:
            if provider.id:
                provider.callback_url = f"{base_url}/auth/oidc/callback/{provider.id}"
            else:
                provider.callback_url = f"{base_url}/auth/oidc/callback/[ID]"
    
    @api.constrains('client_id', 'client_secret')
    def _check_credentials(self):
        for provider in self:
            if not provider.client_id or not provider.client_secret:
                raise ValidationError(_('Client ID and Client Secret are required.'))
    
    def _get_authorization_url(self, state, redirect_uri):
        """Generate the authorization URL for OAuth2 flow"""
        self.ensure_one()
        
        params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'scope': self.scope,
            'redirect_uri': redirect_uri,
            'state': state,
        }
        
        url_parts = list(urllib.parse.urlparse(self.authorization_endpoint))
        query = dict(urllib.parse.parse_qsl(url_parts[4]))
        query.update(params)
        url_parts[4] = urllib.parse.urlencode(query)
        
        return urllib.parse.urlunparse(url_parts)
    
    def _exchange_code_for_token(self, code, redirect_uri):
        """Exchange authorization code for access token"""
        self.ensure_one()
        
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': redirect_uri,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
        }
        
        try:
            if HAS_REQUESTS:
                # Use requests library if available
                import requests
                response = requests.post(self.token_endpoint, data=data, timeout=10)
                response.raise_for_status()
                return response.json()
            else:
                # Fallback to urllib (always available in Python)
                data_encoded = urllib.parse.urlencode(data).encode('utf-8')
                req = urllib.request.Request(
                    self.token_endpoint,
                    data=data_encoded,
                    headers={'Content-Type': 'application/x-www-form-urlencoded'}
                )
                with urllib.request.urlopen(req, timeout=10) as response:
                    return json.loads(response.read().decode('utf-8'))
        except Exception as e:
            _logger.error(f"Token exchange failed: {e}")
            raise ValidationError(_('Failed to exchange authorization code for token: %s') % str(e))
    
    def _get_userinfo(self, access_token):
        """Get user information from userinfo endpoint"""
        self.ensure_one()
        
        headers = {
            'Authorization': f'Bearer {access_token}',
        }
        
        try:
            if HAS_REQUESTS:
                # Use requests library if available
                import requests
                response = requests.get(self.userinfo_endpoint, headers=headers, timeout=10)
                response.raise_for_status()
                return response.json()
            else:
                # Fallback to urllib (always available in Python)
                req = urllib.request.Request(
                    self.userinfo_endpoint,
                    headers=headers
                )
                with urllib.request.urlopen(req, timeout=10) as response:
                    return json.loads(response.read().decode('utf-8'))
        except Exception as e:
            _logger.error(f"Userinfo request failed: {e}")
            raise ValidationError(_('Failed to get user information: %s') % str(e))
    
    def _verify_jwt_token(self, token):
        """Verify JWT token (ID token) if JWKS URI is configured"""
        self.ensure_one()
        
        if not self.jwks_uri:
            # Skip JWT verification if JWKS URI is not configured
            _logger.warning("JWKS URI not configured, skipping JWT verification")
            return None
        
        if not HAS_JWT:
            # Skip JWT verification if PyJWT is not available
            _logger.warning("PyJWT not available, skipping JWT verification. Install PyJWT for enhanced security.")
            return None
        
        try:
            import jwt
            
            # Try to use PyJWKClient if available
            try:
                from jwt import PyJWKClient
                jwks_client = PyJWKClient(self.jwks_uri)
                signing_key = jwks_client.get_signing_key_from_jwt(token)
                
                data = jwt.decode(
                    token,
                    signing_key.key,
                    algorithms=["RS256"],
                    audience=self.client_id,
                    options={"verify_exp": True}
                )
                return data
            except ImportError:
                # PyJWKClient not available, try basic JWT decode without verification
                _logger.warning("PyJWKClient not available, decoding JWT without signature verification")
                data = jwt.decode(
                    token,
                    options={"verify_signature": False}
                )
                return data
        except Exception as e:
            _logger.error(f"JWT verification failed: {e}")
            # Don't raise error, just log and continue
            return None
