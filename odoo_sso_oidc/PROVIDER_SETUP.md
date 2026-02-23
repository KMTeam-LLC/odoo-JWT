# Provider Setup Examples

This document provides step-by-step setup instructions for popular OIDC providers.

## Table of Contents

1. [Authentik](#authentik)
2. [Okta](#okta)
3. [Azure AD / Microsoft Entra ID](#azure-ad--microsoft-entra-id)
4. [Keycloak](#keycloak)
5. [Google Workspace](#google-workspace)

---

## Authentik

### 1. Create OAuth2/OpenID Provider

1. Go to **Admin interface > Applications > Providers**
2. Click **Create** and select **OAuth2/OpenID Provider**
3. Configure:
   - **Name**: `Odoo SSO`
   - **Authorization flow**: `Authorization Code`
   - **Client type**: `Confidential`
   - **Redirect URIs/Origins**: Add your Odoo callback URL
     ```
     https://your-odoo-instance.com/auth/oidc/callback/1
     ```
     (Replace `1` with your provider ID from Odoo)
   - **Signing Key**: Select an available certificate
4. Click **Finish**
5. Note the **Client ID** and **Client Secret**

### 2. Configure Scopes

1. Edit the provider
2. Go to **Advanced protocol settings**
3. Ensure these scopes are included:
   - `openid`
   - `profile`
   - `email`
   - `groups` (may need to add custom scope)

### 3. Create Application

1. Go to **Applications > Applications**
2. Click **Create**
3. Configure:
   - **Name**: `Odoo`
   - **Slug**: `odoo`
   - **Provider**: Select the provider you just created
4. Click **Create**

### 4. Odoo Configuration

```
Name: Authentik
Client ID: [from step 1]
Client Secret: [from step 1]
Authorization Endpoint: https://authentik.example.com/application/o/authorize/
Token Endpoint: https://authentik.example.com/application/o/token/
Userinfo Endpoint: https://authentik.example.com/application/o/userinfo/
JWKS URI: https://authentik.example.com/application/o/odoo/jwks/
Scopes: openid profile email groups
Groups Claim: groups
```

---

## Okta

### 1. Create Application

1. Log in to **Okta Admin Console**
2. Go to **Applications > Applications**
3. Click **Create App Integration**
4. Select:
   - **Sign-in method**: `OIDC - OpenID Connect`
   - **Application type**: `Web Application`
5. Click **Next**

### 2. Configure Application

1. **App integration name**: `Odoo SSO`
2. **Grant type**: Check `Authorization Code`
3. **Sign-in redirect URIs**: Add your callback URL
   ```
   https://your-odoo-instance.com/auth/oidc/callback/1
   ```
4. **Sign-out redirect URIs**: (optional)
5. **Controlled access**: Choose who can access
6. Click **Save**
7. Note the **Client ID** and **Client Secret**

### 3. Configure Token Claims

1. Go to **Security > API > Authorization Servers**
2. Select your authorization server (default is `default`)
3. Go to **Claims** tab
4. Add custom claim for groups if needed:
   - **Name**: `groups`
   - **Include in token type**: `ID Token`, `Always`
   - **Value type**: `Groups`
   - **Filter**: `Matches regex .*` (or specific filter)
   - **Include in**: `Any scope`

### 4. Assign Users/Groups

1. Go back to your application
2. Go to **Assignments** tab
3. Assign users or groups who should have access

### 5. Odoo Configuration

Find your endpoints at **Security > API > Authorization Servers > [your server] > Metadata URI**

```
Name: Okta
Client ID: [from step 2]
Client Secret: [from step 2]
Authorization Endpoint: https://your-domain.okta.com/oauth2/default/v1/authorize
Token Endpoint: https://your-domain.okta.com/oauth2/default/v1/token
Userinfo Endpoint: https://your-domain.okta.com/oauth2/default/v1/userinfo
JWKS URI: https://your-domain.okta.com/oauth2/default/v1/keys
Scopes: openid profile email groups
Groups Claim: groups
```

---

## Azure AD / Microsoft Entra ID

### 1. Register Application

1. Go to **Azure Portal > Microsoft Entra ID > App registrations**
2. Click **New registration**
3. Configure:
   - **Name**: `Odoo SSO`
   - **Supported account types**: Choose appropriate option
   - **Redirect URI**: 
     - Platform: `Web`
     - URI: `https://your-odoo-instance.com/auth/oidc/callback/1`
4. Click **Register**
5. Note the **Application (client) ID** and **Directory (tenant) ID**

### 2. Create Client Secret

1. Go to **Certificates & secrets**
2. Click **New client secret**
3. Add description and choose expiration
4. Click **Add**
5. **Copy the secret value immediately** (it won't be shown again)

### 3. Configure API Permissions

1. Go to **API permissions**
2. Click **Add a permission**
3. Select **Microsoft Graph**
4. Select **Delegated permissions**
5. Add:
   - `openid`
   - `profile`
   - `email`
   - `User.Read`
   - `GroupMember.Read.All` (for group sync)
6. Click **Add permissions**
7. Click **Grant admin consent** (if you have permissions)

### 4. Configure Token Claims

1. Go to **Token configuration**
2. Click **Add optional claim**
3. Select **ID** token
4. Add claims:
   - `email`
   - `family_name`
   - `given_name`
   - `upn`
5. Click **Add**
6. For groups:
   - Click **Add groups claim**
   - Select **Security groups**
   - Check **ID**
   - Click **Add**

### 5. Odoo Configuration

```
Name: Azure AD
Client ID: [Application (client) ID]
Client Secret: [from step 2]
Authorization Endpoint: https://login.microsoftonline.com/[tenant-id]/oauth2/v2.0/authorize
Token Endpoint: https://login.microsoftonline.com/[tenant-id]/oauth2/v2.0/token
Userinfo Endpoint: https://graph.microsoft.com/oidc/userinfo
JWKS URI: https://login.microsoftonline.com/[tenant-id]/discovery/v2.0/keys
Scopes: openid profile email User.Read GroupMember.Read.All
Groups Claim: groups
```

**Note**: Replace `[tenant-id]` with your Directory (tenant) ID

---

## Keycloak

### 1. Create Client

1. Go to **Keycloak Admin Console**
2. Select your **Realm**
3. Go to **Clients**
4. Click **Create**
5. Configure:
   - **Client ID**: `odoo`
   - **Client Protocol**: `openid-connect`
6. Click **Save**

### 2. Configure Client Settings

1. **Access Type**: `confidential`
2. **Standard Flow Enabled**: `ON`
3. **Valid Redirect URIs**: Add
   ```
   https://your-odoo-instance.com/auth/oidc/callback/1
   ```
4. Click **Save**
5. Go to **Credentials** tab
6. Note the **Secret**

### 3. Configure Client Scopes

1. Go to **Client Scopes**
2. Make sure `groups` scope exists or create it
3. Go back to your client
4. Go to **Client Scopes** tab
5. Add `groups` to **Default Client Scopes**

### 4. Configure Mappers (Optional)

1. In your client, go to **Mappers** tab
2. Create mapper for groups if not exists:
   - **Name**: `groups`
   - **Mapper Type**: `Group Membership`
   - **Token Claim Name**: `groups`
   - **Add to ID token**: `ON`
   - **Add to access token**: `ON`
   - **Add to userinfo**: `ON`

### 5. Odoo Configuration

```
Name: Keycloak
Client ID: odoo
Client Secret: [from step 2]
Authorization Endpoint: https://keycloak.example.com/realms/[realm]/protocol/openid-connect/auth
Token Endpoint: https://keycloak.example.com/realms/[realm]/protocol/openid-connect/token
Userinfo Endpoint: https://keycloak.example.com/realms/[realm]/protocol/openid-connect/userinfo
JWKS URI: https://keycloak.example.com/realms/[realm]/protocol/openid-connect/certs
Scopes: openid profile email groups
Groups Claim: groups
```

**Note**: Replace `[realm]` with your realm name

---

## Google Workspace

### 1. Create OAuth2 Client

1. Go to **Google Cloud Console > APIs & Services > Credentials**
2. Create a project if you haven't already
3. Click **Create Credentials > OAuth client ID**
4. Configure consent screen if prompted
5. Choose **Application type**: `Web application`
6. Configure:
   - **Name**: `Odoo SSO`
   - **Authorized redirect URIs**: Add
     ```
     https://your-odoo-instance.com/auth/oidc/callback/1
     ```
7. Click **Create**
8. Note the **Client ID** and **Client Secret**

### 2. Configure OAuth Consent Screen

1. Go to **OAuth consent screen**
2. Add scopes:
   - `openid`
   - `profile`
   - `email`
3. Add test users if in testing mode

### 3. Odoo Configuration

```
Name: Google
Client ID: [from step 1]
Client Secret: [from step 1]
Authorization Endpoint: https://accounts.google.com/o/oauth2/v2/auth
Token Endpoint: https://oauth2.googleapis.com/token
Userinfo Endpoint: https://openidconnect.googleapis.com/v1/userinfo
JWKS URI: https://www.googleapis.com/oauth2/v3/certs
Scopes: openid profile email
Groups Claim: (leave empty - Google doesn't provide groups by default)
```

**Note**: Google Workspace doesn't provide group information via OIDC by default. You would need to use the Google Directory API separately or use a different claim mapping strategy.

---

## General Tips

1. **Always use HTTPS** in production
2. **Test with a test account** first
3. **Check provider documentation** for any specific requirements
4. **Enable debug logging** in Odoo initially to troubleshoot
5. **Verify callback URLs** match exactly (including trailing slashes)
6. **Check firewall rules** to ensure Odoo can reach the OIDC provider
7. **Review provider logs** if authentication fails

## Troubleshooting

### Common Issues

1. **Redirect URI Mismatch**
   - Ensure the callback URL in Odoo matches exactly what's configured in the provider
   - Check for http vs https
   - Check for trailing slashes

2. **Missing Groups Claim**
   - Verify the groups claim is included in the token
   - Check if you need to add a custom scope or mapper
   - Some providers require explicit configuration to include groups

3. **Authentication Loop**
   - Clear browser cookies and cache
   - Check Odoo logs for detailed error messages
   - Verify client secret is correct

4. **User Not Created**
   - Ensure "Auto-create Users" is enabled
   - Check that email claim is being returned
   - Review Odoo logs for error messages

For more help, check the main README.md or open an issue on GitHub.
