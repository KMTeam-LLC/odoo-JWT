# Odoo 19 OIDC Single Sign-On Module

A comprehensive OpenID Connect (OIDC) authentication module for Odoo 19 that enables Single Sign-On (SSO) with any OIDC-compliant identity provider such as Authentik, Okta, Azure AD, Google Workspace, Keycloak, and more.

## 🌐 Platform Compatibility

**✅ Works on ALL Odoo deployments:**
- **Odoo Online**: Fully compatible (no additional setup required)
- **Odoo.sh**: Fully compatible (optional dependencies for enhanced features)
- **On-Premise**: Fully compatible (all features available)

See [COMPATIBILITY.md](COMPATIBILITY.md) for detailed platform-specific information.

## Features

- ✅ **Universal OIDC Support**: Works with any OIDC-compliant provider (Authentik, Okta, Azure AD, Google, Keycloak, Auth0, etc.)
- ✅ **Automatic User Creation**: Creates Odoo user accounts automatically on first login
- ✅ **Group Synchronization**: Automatically syncs user groups from OIDC provider to Odoo groups on every login
- ✅ **JWT Token Validation**: Secure token verification with JWKS support
- ✅ **Multiple Providers**: Support for multiple OIDC providers simultaneously
- ✅ **Flexible Mapping**: Map OIDC groups to Odoo groups with customizable mappings
- ✅ **Security**: CSRF protection with state parameter, secure token handling

## Installation

### Python Dependencies (Optional)

This module works **without any external dependencies** using Python's built-in libraries. However, for enhanced security features (JWT signature verification), you can optionally install:

```bash
pip3 install PyJWT cryptography requests
```

Or use the included requirements file:

```bash
pip3 install -r requirements.txt
```

**Note**: 
- **Odoo Online**: No additional installation needed - works out of the box
- **Odoo.sh**: Add dependencies to your repository's `requirements.txt` (optional)
- **On-Premise**: Install dependencies with pip (recommended)

### Install the Module

1. Copy the `odoo_sso_oidc` folder to your Odoo addons directory
2. Update the apps list in Odoo
3. Install the "OIDC Single Sign-On" module

## Configuration

### Step 1: Configure Your OIDC Provider

#### For Authentik:

1. Go to **Applications > Providers** in Authentik
2. Create a new **OAuth2/OpenID Provider**
3. Configure:
   - Client Type: `Confidential`
   - Redirect URIs: Add the callback URL from Odoo (see Step 2)
   - Scopes: Enable `openid`, `profile`, `email`, `groups`
4. Create an Application and bind it to the provider
5. Note the **Client ID** and **Client Secret**

#### For Okta:

1. Go to **Applications > Applications** in Okta Admin Console
2. Click **Create App Integration**
3. Choose **OIDC - OpenID Connect** and **Web Application**
4. Configure:
   - Sign-in redirect URIs: Add the callback URL from Odoo
   - Assignments: Choose who can access
   - Grant type: Authorization Code
5. Note the **Client ID** and **Client Secret**
6. Go to **Security > API > Authorization Servers** to find your endpoints

#### For Azure AD (Microsoft Entra ID):

1. Go to **Azure Active Directory > App registrations**
2. Click **New registration**
3. Configure:
   - Name: Your app name
   - Redirect URI: Web, add callback URL from Odoo
4. Note the **Application (client) ID**
5. Go to **Certificates & secrets** and create a new client secret
6. Go to **Token configuration** and add optional claims (groups, email, etc.)
7. Endpoints can be found in **Overview > Endpoints**

### Step 2: Configure Odoo

1. In Odoo, go to **Settings > Users & Companies > OIDC Authentication > OIDC Providers**
2. Click **Create**
3. Fill in the provider details:

   **Basic Information:**
   - Name: e.g., "Authentik", "Okta", "Azure AD"
   - Active: Check this box

   **OAuth2/OIDC Credentials:**
   - Client ID: Your client ID from the provider
   - Client Secret: Your client secret from the provider

   **Endpoints:** (Examples for Authentik)
   - Authorization Endpoint: `https://authentik.example.com/application/o/authorize/`
   - Token Endpoint: `https://authentik.example.com/application/o/token/`
   - Userinfo Endpoint: `https://authentik.example.com/application/o/userinfo/`
   - JWKS URI (optional): `https://authentik.example.com/application/o/[app-slug]/jwks/`

   **Scopes and Claims:**
   - Scopes: `openid profile email groups` (default)
   - Groups Claim: `groups` (or customize based on your provider)
   - Email Claim: `email`
   - Name Claim: `name`
   - Username Claim: `preferred_username`

   **User Management:**
   - Auto-create Users: ✓ (Enable automatic user creation)
   - Sync Groups on Login: ✓ (Enable group synchronization)

4. **Copy the Callback URL** shown in the form and add it to your OIDC provider configuration

### Step 3: Set Up Group Mappings

1. In the OIDC Provider form, go to the **Group Mappings** tab
2. Click **Add a line**
3. Map OIDC groups to Odoo groups:
   - OIDC Group Name: The exact group name from your OIDC provider (case-sensitive)
   - Odoo Group: Select the corresponding Odoo group
   - Active: Check this box

Example mappings:
- OIDC Group: `odoo-admins` → Odoo Group: `Administration / Settings`
- OIDC Group: `odoo-users` → Odoo Group: `User types / Internal User`
- OIDC Group: `sales-team` → Odoo Group: `Sales / User: Own Documents Only`

### Step 4: Test the Configuration

1. **Log out** from Odoo
2. Go to the **login page**
3. You should see a button like **"Sign in with Authentik"** (or your provider name)
4. Click the button
5. Authenticate with your OIDC provider
6. You should be redirected back to Odoo and logged in automatically

## How It Works

### Authentication Flow

1. User clicks the SSO login button on Odoo login page
2. User is redirected to the OIDC provider for authentication
3. After successful authentication, provider redirects back to Odoo with an authorization code
4. Odoo exchanges the code for an access token
5. Odoo retrieves user information from the provider
6. Odoo creates a new user account (if it doesn't exist) or links to existing account
7. Odoo synchronizes user groups based on group mappings
8. User is logged into Odoo

### Group Synchronization

On every login:
1. Odoo retrieves the user's groups from the OIDC provider
2. For each group mapping:
   - If user is a member of the OIDC group, they are added to the corresponding Odoo group
   - If user is not a member of the OIDC group, they are removed from the corresponding Odoo group
3. Groups are synchronized to match the current state in the OIDC provider

### User Creation

When a user logs in for the first time:
1. Odoo checks if a user with the OIDC subject (`sub` claim) already exists
2. If not, checks if a user with the same email exists
3. If an email match is found, links that user to the OIDC provider
4. If no match is found and auto-creation is enabled, creates a new user with:
   - Name from OIDC provider
   - Email from OIDC provider
   - Login from email or preferred_username
   - Random password (user will use SSO to log in)

## Provider-Specific Notes

### Authentik

- Default groups claim: `groups`
- Ensure "Include User Claims" is enabled in the provider scope mappings
- Groups should be configured in Authentik and assigned to users

### Okta

- Default groups claim: `groups`
- May need to add a custom claim for groups in the authorization server
- Groups filter can be used to limit which groups are included

### Azure AD / Microsoft Entra ID

- Groups claim might be `groups` or `roles` depending on configuration
- May need to configure "Group Claims" in Token Configuration
- For large directories, consider using group filtering

### Google Workspace

- Google doesn't provide groups claim by default
- You may need to use Google Directory API separately or use roles instead

## Troubleshooting

### "State verification failed" error

- This is a security feature. Make sure cookies are enabled in your browser
- Clear your browser cache and cookies
- Check that your Odoo instance URL is correctly configured

### "No access token received" error

- Verify your client ID and secret are correct
- Check that the callback URL in your OIDC provider matches exactly
- Review OIDC provider logs for detailed error messages

### User not created automatically

- Verify "Auto-create Users" is enabled in the provider configuration
- Check Odoo logs for detailed error messages
- Ensure the OIDC provider is returning required claims (email, name, sub)

### Groups not syncing

- Verify "Sync Groups on Login" is enabled
- Check that group mappings are configured correctly
- Ensure the OIDC provider is including groups in the response
- Check the "Groups Claim" field matches your provider's claim name
- Review Odoo logs for group synchronization messages

### Enable Debug Logging

To see detailed logs:

1. Edit your Odoo configuration file
2. Set log level to debug:
   ```
   log_level = debug
   ```
3. Look for log messages from `odoo_sso_oidc` in the Odoo logs

## Security Considerations

- Always use HTTPS in production
- Keep your client secrets secure
- Regularly rotate client secrets
- Use strong OIDC provider security settings
- Review and audit group mappings regularly
- Consider using JWT verification with JWKS URI for additional security

## Technical Details

### Models

- `oidc.provider`: Stores OIDC provider configuration
- `oidc.group.mapping`: Maps OIDC groups to Odoo groups
- `res.users`: Extended with OIDC-specific fields

### Controllers

- `/auth/oidc/login/<provider_id>`: Initiates OIDC authentication flow
- `/auth/oidc/callback/<provider_id>`: Handles OIDC callback after authentication

### Dependencies

- `PyJWT` (optional): JWT token decoding and verification
- `cryptography` (optional): Cryptographic operations for JWT
- `requests` (optional): HTTP requests to OIDC endpoints

**Without optional dependencies**: The module uses Python's built-in `urllib` and skips JWT signature verification. Still secure and functional for most use cases.

## License

LGPL-3

## Support

For issues, feature requests, or contributions, please visit:
https://github.com/KMTeam-LLC/odoo-JWT

## Credits

Developed by KMTeam LLC
