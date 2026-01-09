# -*- coding: utf-8 -*-
{
    'name': 'OIDC Single Sign-On',
    'version': '19.0.1.0.0',
    'category': 'Authentication',
    'summary': 'OIDC SSO integration with group synchronization for Authentik, Okta, and other providers',
    'description': """
OIDC Single Sign-On Integration
================================

This module provides OpenID Connect (OIDC) integration for Odoo, supporting:

* Single Sign-On (SSO) with any OIDC-compliant provider (Authentik, Okta, etc.)
* Automatic user creation on first login
* Group synchronization from OIDC provider to Odoo groups on every login
* JWT token validation (when PyJWT is available)
* Secure authentication flow
* Compatible with Odoo Online, Odoo.sh, and On-Premise installations

Configuration
-------------
1. Configure your OIDC provider settings in Settings > Users & Companies > OIDC Providers
2. Set up your OIDC provider (Authentik, Okta, etc.) with the callback URL
3. Map OIDC groups to Odoo groups
4. Users will see an SSO login option on the login page

Note: JWT verification requires PyJWT and cryptography libraries. If not available,
the module will work but skip JWT signature verification.
    """,
    'author': 'KMTeam LLC',
    'website': 'https://github.com/KMTeam-LLC/odoo-JWT',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'web',
    ],
    'external_dependencies': {
        'python': [],
    },
    'data': [
        'security/ir.model.access.csv',
        'views/oidc_provider_views.xml',
        'views/res_config_settings_views.xml',
        'views/webclient_templates.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'odoo_sso_oidc/static/src/js/login.js',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
