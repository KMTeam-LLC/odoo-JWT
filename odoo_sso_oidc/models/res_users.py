# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api, _
from odoo.exceptions import AccessDenied, ValidationError

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = 'res.users'

    oidc_provider_id = fields.Many2one(
        'oidc.provider',
        string='OIDC Provider',
        help='OIDC provider used for authentication'
    )
    oidc_sub = fields.Char(
        string='OIDC Subject',
        help='Unique identifier from OIDC provider (sub claim)',
        index=True
    )
    
    _sql_constraints = [
        (
            'unique_oidc_sub_per_provider',
            'unique(oidc_provider_id, oidc_sub)',
            'A user with this OIDC subject already exists for this provider!'
        ),
    ]
    
    @api.model
    def _auth_oidc_signin(self, provider_id, userinfo, id_token_data=None):
        """
        Authenticate or create a user from OIDC userinfo
        Returns the user's login
        """
        provider = self.env['oidc.provider'].browse(provider_id)
        if not provider.exists():
            raise ValidationError(_('Invalid OIDC provider'))
        
        # Extract user information from userinfo and/or ID token
        sub = userinfo.get('sub')
        if not sub:
            raise ValidationError(_('OIDC provider did not return a subject (sub) claim'))
        
        email = userinfo.get(provider.email_claim) or userinfo.get('email')
        if not email:
            raise ValidationError(_('OIDC provider did not return an email'))
        
        name = userinfo.get(provider.name_claim) or userinfo.get('name') or email
        preferred_username = userinfo.get(provider.preferred_username_claim) or userinfo.get('preferred_username')
        
        # Get groups from userinfo or ID token
        groups = []
        if provider.groups_claim:
            groups = userinfo.get(provider.groups_claim, [])
            if id_token_data and not groups:
                groups = id_token_data.get(provider.groups_claim, [])
        
        if not isinstance(groups, list):
            groups = [groups] if groups else []
        
        _logger.info(f"OIDC login attempt - sub: {sub[:8]}... (redacted)")
        _logger.debug(f"OIDC login details - email: {email}, groups: {groups}")
        
        # Search for existing user by OIDC sub
        user = self.sudo().search([
            ('oidc_provider_id', '=', provider.id),
            ('oidc_sub', '=', sub)
        ], limit=1)
        
        if not user:
            # Search by email as fallback
            user = self.sudo().search([('login', '=', email)], limit=1)
            
            if user:
                # Link existing user to OIDC provider
                _logger.info(f"Linking existing user {email} to OIDC provider {provider.name}")
                user.write({
                    'oidc_provider_id': provider.id,
                    'oidc_sub': sub,
                })
            elif provider.auto_create_users:
                # Create new user
                _logger.info(f"Creating new user {email} from OIDC provider {provider.name}")
                
                # Generate login from email or preferred_username
                login = email
                if preferred_username:
                    # Check if preferred_username is available
                    existing = self.sudo().search([('login', '=', preferred_username)], limit=1)
                    if not existing:
                        login = preferred_username
                
                user = self.sudo().create({
                    'name': name,
                    'login': login,
                    'email': email,
                    'oidc_provider_id': provider.id,
                    'oidc_sub': sub,
                    'active': True,
                    # Disable password authentication - user must use SSO
                    'password': False,
                })
                _logger.info(f"Created new user: {user.login} (id: {user.id})")
            else:
                raise AccessDenied(_('User auto-creation is disabled. Please contact your administrator.'))
        
        # Sync groups if enabled
        if provider.sync_groups_on_login and user:
            self._sync_oidc_groups(user, provider, groups)
        
        return user.login
    
    @api.model
    def _sync_oidc_groups(self, user, provider, oidc_groups):
        """Synchronize user's Odoo groups based on OIDC groups"""
        if not oidc_groups:
            _logger.info(f"No OIDC groups provided for user {user.login}")
            return
        
        _logger.info(f"Syncing groups for user {user.login}: {oidc_groups}")
        
        # Get all mappings for this provider
        mappings = self.env['oidc.group.mapping'].sudo().search([
            ('provider_id', '=', provider.id),
            ('active', '=', True),
        ])
        
        if not mappings:
            _logger.warning(f"No group mappings configured for provider {provider.name}")
            return
        
        # Build mapping dictionary
        group_map = {m.oidc_group_name: m.odoo_group_id for m in mappings}
        
        # Determine which Odoo groups the user should have
        groups_to_add = []
        groups_to_remove = []
        
        for oidc_group in oidc_groups:
            if oidc_group in group_map:
                odoo_group = group_map[oidc_group]
                if odoo_group not in user.groups_id:
                    groups_to_add.append(odoo_group.id)
                    _logger.info(f"Adding user {user.login} to group {odoo_group.name}")
        
        # Remove user from mapped groups they're no longer a member of
        mapped_odoo_groups = [g.odoo_group_id for g in mappings]
        for odoo_group in user.groups_id:
            if odoo_group in mapped_odoo_groups:
                # This is a mapped group - check if user should still have it
                corresponding_oidc_groups = [
                    m.oidc_group_name for m in mappings if m.odoo_group_id == odoo_group
                ]
                if not any(og in oidc_groups for og in corresponding_oidc_groups):
                    groups_to_remove.append(odoo_group.id)
                    _logger.info(f"Removing user {user.login} from group {odoo_group.name}")
        
        # Apply group changes
        if groups_to_add:
            user.sudo().write({'groups_id': [(4, gid) for gid in groups_to_add]})
        
        if groups_to_remove:
            user.sudo().write({'groups_id': [(3, gid) for gid in groups_to_remove]})
        
        _logger.info(f"Group sync completed for user {user.login}")
