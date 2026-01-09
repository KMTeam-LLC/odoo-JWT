# -*- coding: utf-8 -*-
import logging
import secrets
import werkzeug
from odoo import http, _
from odoo.http import request
from odoo.exceptions import AccessDenied, ValidationError
from odoo.addons.web.controllers.home import Home

_logger = logging.getLogger(__name__)


class OIDCController(http.Controller):
    
    @http.route('/auth/oidc/login/<int:provider_id>', type='http', auth='public', website=True, csrf=False)
    def oidc_login(self, provider_id, **kwargs):
        """Initiate OIDC authentication flow"""
        try:
            provider = request.env['oidc.provider'].sudo().browse(provider_id)
            if not provider.exists() or not provider.active:
                return werkzeug.exceptions.NotFound(_('OIDC provider not found'))
            
            # Generate state for CSRF protection
            state = secrets.token_urlsafe(32)
            
            # Store state in session
            request.session['oidc_state'] = state
            request.session['oidc_provider_id'] = provider_id
            
            # Get redirect URI (callback URL)
            base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
            redirect_uri = f"{base_url}/auth/oidc/callback/{provider_id}"
            
            # Generate authorization URL
            auth_url = provider._get_authorization_url(state, redirect_uri)
            
            _logger.info(f"Redirecting to OIDC provider {provider.name} for authentication")
            return werkzeug.utils.redirect(auth_url)
            
        except Exception as e:
            _logger.error(f"OIDC login error: {e}", exc_info=True)
            return werkzeug.exceptions.InternalServerError(_('Authentication error: %s') % str(e))
    
    @http.route('/auth/oidc/callback/<int:provider_id>', type='http', auth='public', website=True, csrf=False)
    def oidc_callback(self, provider_id, **kwargs):
        """Handle OIDC callback after authentication"""
        try:
            # Get authorization code and state from callback
            code = kwargs.get('code')
            state = kwargs.get('state')
            error = kwargs.get('error')
            error_description = kwargs.get('error_description')
            
            if error:
                _logger.error(f"OIDC error: {error} - {error_description}")
                return self._render_error(_('Authentication failed: %s') % error_description or error)
            
            if not code or not state:
                return self._render_error(_('Missing authorization code or state'))
            
            # Verify state (CSRF protection)
            session_state = request.session.get('oidc_state')
            session_provider_id = request.session.get('oidc_provider_id')
            
            if not session_state or state != session_state:
                _logger.error("State mismatch - potential CSRF attack")
                return self._render_error(_('State verification failed'))
            
            if session_provider_id != provider_id:
                _logger.error("Provider ID mismatch")
                return self._render_error(_('Provider verification failed'))
            
            # Clear session state
            request.session.pop('oidc_state', None)
            request.session.pop('oidc_provider_id', None)
            
            # Get provider
            provider = request.env['oidc.provider'].sudo().browse(provider_id)
            if not provider.exists() or not provider.active:
                return self._render_error(_('OIDC provider not found'))
            
            # Exchange code for token
            base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
            redirect_uri = f"{base_url}/auth/oidc/callback/{provider_id}"
            
            token_data = provider._exchange_code_for_token(code, redirect_uri)
            access_token = token_data.get('access_token')
            id_token = token_data.get('id_token')
            
            if not access_token:
                return self._render_error(_('No access token received'))
            
            # Verify ID token if present
            id_token_data = None
            if id_token and provider.jwks_uri:
                try:
                    id_token_data = provider._verify_jwt_token(id_token)
                except Exception as e:
                    _logger.warning(f"ID token verification failed: {e}")
                    # Continue anyway, we'll use userinfo endpoint
            
            # Get user info
            userinfo = provider._get_userinfo(access_token)
            
            # Authenticate or create user
            login = request.env['res.users']._auth_oidc_signin(
                provider_id,
                userinfo,
                id_token_data
            )
            
            # Log the user in
            request.session.authenticate(request.db, login, access_token)
            
            _logger.info(f"User {login} successfully authenticated via OIDC")
            
            # Redirect to home page
            return werkzeug.utils.redirect('/web')
            
        except AccessDenied as e:
            _logger.error(f"Access denied: {e}")
            return self._render_error(_('Access denied: %s') % str(e))
        except ValidationError as e:
            _logger.error(f"Validation error: {e}")
            return self._render_error(_('Authentication error: %s') % str(e))
        except Exception as e:
            _logger.error(f"OIDC callback error: {e}", exc_info=True)
            return self._render_error(_('Authentication error occurred'))
    
    def _render_error(self, message):
        """Render error page"""
        return request.render('odoo_sso_oidc.oidc_error', {
            'error_message': message,
        })


class HomeExtended(Home):
    """Extend Home controller to add OIDC login to the web login page"""
    
    @http.route()
    def web_login(self, redirect=None, **kw):
        """Override web_login to inject OIDC providers"""
        response = super(HomeExtended, self).web_login(redirect=redirect, **kw)
        
        if request.params.get('login_success'):
            # Already logged in, return response as-is
            return response
        
        # Get active OIDC providers
        providers = request.env['oidc.provider'].sudo().search([('active', '=', True)])
        
        if hasattr(response, 'qcontext'):
            response.qcontext['oidc_providers'] = providers
        
        return response
