# Platform Compatibility Guide

This module is designed to work seamlessly across all Odoo deployment types:

## ✅ Odoo Online

**Status**: Fully Compatible

The module works out of the box on Odoo Online without requiring any additional dependencies. It uses Python's built-in `urllib` library for HTTP requests, which is always available.

### Features:
- ✅ OIDC authentication
- ✅ Automatic user creation
- ✅ Group synchronization
- ⚠️ JWT verification: Limited (signature verification not available without PyJWT)

### Notes:
- JWT tokens are decoded but signature verification is skipped if PyJWT is not available
- The module logs warnings when optional dependencies are missing
- Security still maintained through state parameter (CSRF protection) and HTTPS

## ✅ Odoo.sh

**Status**: Fully Compatible

On Odoo.sh, you can optionally add dependencies to enhance security features.

### Installation with Optional Dependencies:

Create or edit `requirements.txt` in your repository root:

```txt
PyJWT>=2.8.0
cryptography>=41.0.0
requests>=2.31.0
```

### Features:
- ✅ OIDC authentication
- ✅ Automatic user creation
- ✅ Group synchronization
- ✅ JWT verification (when dependencies installed)

### Without Optional Dependencies:
Same as Odoo Online - fully functional with limited JWT verification

## ✅ On-Premise

**Status**: Fully Compatible

For on-premise installations, you have full control over dependencies.

### Recommended Installation:

```bash
# Install optional dependencies for full feature support
pip3 install PyJWT>=2.8.0 cryptography>=41.0.0 requests>=2.31.0
```

Or use the included requirements file:

```bash
pip3 install -r odoo_sso_oidc/requirements.txt
```

### Features:
- ✅ OIDC authentication
- ✅ Automatic user creation
- ✅ Group synchronization
- ✅ Full JWT verification with signature validation
- ✅ Enhanced HTTP handling with requests library

## Feature Comparison

| Feature | Odoo Online | Odoo.sh (no deps) | Odoo.sh (with deps) | On-Premise (with deps) |
|---------|-------------|-------------------|---------------------|------------------------|
| OIDC SSO Login | ✅ | ✅ | ✅ | ✅ |
| User Auto-creation | ✅ | ✅ | ✅ | ✅ |
| Group Sync | ✅ | ✅ | ✅ | ✅ |
| JWT Decoding | ✅ | ✅ | ✅ | ✅ |
| JWT Signature Verification | ❌ | ❌ | ✅ | ✅ |
| HTTP Requests | urllib | urllib | requests | requests |

## Security Considerations

### All Platforms:
- CSRF protection via state parameter
- HTTPS enforcement recommended
- Secure token storage in session
- Access token used for API calls

### With PyJWT (Odoo.sh with deps, On-Premise):
- Additional JWT signature verification
- Audience validation
- Expiration time validation
- Cryptographic signature checking

### Without PyJWT (Odoo Online, Odoo.sh without deps):
- Tokens are still validated by the OIDC provider
- Userinfo endpoint provides verified user data
- State parameter prevents CSRF attacks
- Still secure for most use cases

## Troubleshooting by Platform

### Odoo Online

**Issue**: Module appears to work but shows warnings in logs
- **Solution**: This is expected. The module is working correctly using fallback methods.

**Issue**: Need JWT signature verification
- **Solution**: Not available on Odoo Online. Consider Odoo.sh or On-Premise for this feature.

### Odoo.sh

**Issue**: Want to enable JWT verification
- **Solution**: Add dependencies to requirements.txt in repository root and push changes

**Issue**: Dependencies not installing
- **Solution**: Check requirements.txt syntax and ensure it's in the repository root

### On-Premise

**Issue**: Import errors for JWT or requests
- **Solution**: Install dependencies with pip: `pip3 install PyJWT cryptography requests`

**Issue**: Module installed but dependencies not detected
- **Solution**: Restart Odoo server after installing dependencies

## Testing Compatibility

To check which features are available on your installation:

1. Install the module
2. Check Odoo logs for messages like:
   - `PyJWT not available - JWT signature verification will be disabled`
   - `requests library not available - using urllib instead`
3. These warnings are informational - the module will still work

## Recommendations by Deployment Type

### Odoo Online
- ✅ Use as-is, works perfectly for most scenarios
- ✅ Ensure OIDC provider is properly configured
- ✅ Use HTTPS for Odoo instance
- ⚠️ Accept that JWT signature verification is not available

### Odoo.sh
- ✅ Add optional dependencies to requirements.txt for enhanced security
- ✅ Test after each deployment
- ✅ Use HTTPS (automatically provided)

### On-Premise
- ✅ Install all optional dependencies
- ✅ Enable debug logging initially to monitor authentication
- ✅ Use HTTPS with valid SSL certificates
- ✅ Regular security updates for dependencies

## Support Matrix

| Odoo Version | Odoo Online | Odoo.sh | On-Premise |
|--------------|-------------|---------|------------|
| 19.0 | ✅ | ✅ | ✅ |

## Additional Notes

- The module automatically detects available libraries and adapts
- No code changes needed for different platforms
- Graceful degradation ensures functionality even without optional dependencies
- All platforms support the core functionality: SSO login, user creation, and group sync
