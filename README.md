# Odoo 19 OIDC Single Sign-On

A production-ready Odoo 19 addon that provides OpenID Connect (OIDC) Single Sign-On integration with automatic user creation and group synchronization.

## 🌟 Key Features

- **Universal OIDC Support**: Works with Authentik, Okta, Azure AD, Google Workspace, Keycloak, Auth0, and any OIDC provider
- **Automatic User Provisioning**: Creates user accounts on first login
- **Group Synchronization**: Syncs user groups from SSO provider to Odoo on every login
- **Multi-Platform**: Compatible with Odoo Online, Odoo.sh, and On-Premise installations
- **Zero Dependencies**: Works out-of-the-box using Python standard library

## 🚀 Quick Start

### Odoo Online
1. Install the `odoo_sso_oidc` module
2. Configure your OIDC provider in Settings
3. Start using SSO - no additional setup needed!

### Odoo.sh
1. (Optional) Add to your `requirements.txt` for enhanced security:
   ```
   PyJWT>=2.8.0
   cryptography>=41.0.0
   ```
2. Install the module
3. Configure and use

### On-Premise
1. (Recommended) Install optional dependencies:
   ```bash
   pip3 install -r odoo_sso_oidc/requirements.txt
   ```
2. Install the module
3. Configure and use

## 📚 Documentation

See the complete documentation in [`odoo_sso_oidc/README.md`](odoo_sso_oidc/README.md)

## 🔒 Security

- CSRF protection via state parameter
- Secure token handling
- Optional JWT signature verification
- HTTPS recommended

## 📄 License

LGPL-3
