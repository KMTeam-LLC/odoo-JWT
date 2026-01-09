# Testing Guide

This guide covers how to test the OIDC SSO module across different scenarios.

## Prerequisites for Testing

1. **Running Odoo Instance**: Any deployment type (Online, Odoo.sh, On-Premise)
2. **OIDC Provider**: Access to configure an OIDC provider (Authentik, Okta, etc.)
3. **Test User Accounts**: At least 2-3 test users in your OIDC provider
4. **Group Configurations**: Test groups in your OIDC provider

## Test Scenarios

### 1. Module Installation

#### Test Steps:
1. Go to **Apps** in Odoo
2. Update Apps List
3. Search for "OIDC Single Sign-On"
4. Click **Install**
5. Wait for installation to complete

#### Expected Results:
- ✅ Module installs without errors
- ✅ New menu appears: Settings > Users & Companies > OIDC Authentication
- ✅ OIDC Providers menu is accessible
- ✅ No error messages in logs

#### Check Logs:
```bash
# On-premise
tail -f /var/log/odoo/odoo.log | grep oidc

# Look for:
# - "PyJWT not available" (warning, acceptable)
# - "requests library not available" (warning, acceptable)
# - No errors during module installation
```

---

### 2. Provider Configuration

#### Test Steps:
1. Go to **Settings > Users & Companies > OIDC Authentication > OIDC Providers**
2. Click **Create**
3. Fill in all required fields:
   - Name: "Test Provider"
   - Client ID: [from your OIDC provider]
   - Client Secret: [from your OIDC provider]
   - Authorization Endpoint
   - Token Endpoint
   - Userinfo Endpoint
4. Save the record

#### Expected Results:
- ✅ Provider saves successfully
- ✅ Callback URL is generated and displayed
- ✅ All tabs are accessible (Configuration, Group Mappings, Help)
- ✅ Form validation works (try saving without required fields)

#### Test Edge Cases:
- [ ] Try saving without Client ID - should show error
- [ ] Try saving without Client Secret - should show error
- [ ] Verify callback URL format is correct
- [ ] Check that inactive providers don't show on login page

---

### 3. First-Time User Login (Auto-Creation)

#### Prerequisites:
- Provider configured with "Auto-create Users" enabled
- Test user exists in OIDC provider but NOT in Odoo

#### Test Steps:
1. Log out of Odoo
2. Go to login page
3. Verify "Sign in with [Provider Name]" button appears
4. Click the SSO button
5. Authenticate with OIDC provider using test user
6. Complete any MFA if required

#### Expected Results:
- ✅ Redirected to OIDC provider login page
- ✅ Successfully authenticate with OIDC provider
- ✅ Redirected back to Odoo
- ✅ Logged in to Odoo automatically
- ✅ New user account created in Odoo
- ✅ User details populated (name, email)
- ✅ No password set for user (password authentication disabled)

#### Verify in Odoo:
1. Go to **Settings > Users & Companies > Users**
2. Find the newly created user
3. Check:
   - ✅ Name matches OIDC provider
   - ✅ Email matches OIDC provider
   - ✅ Login set correctly
   - ✅ OIDC Provider field set
   - ✅ OIDC Subject field populated

#### Check Logs:
```bash
# Should see:
# - "OIDC login attempt - sub: [redacted]"
# - "Creating new user [email] from OIDC provider [name]"
# - "Created new user: [login] (id: [id])"
# - "User [login] successfully authenticated via OIDC"
```

---

### 4. Existing User Login

#### Prerequisites:
- User already exists in Odoo (from previous test or manually created)

#### Test Steps:
1. Log out of Odoo
2. Go to login page
3. Click SSO button
4. Authenticate with same user

#### Expected Results:
- ✅ User logged in successfully
- ✅ No duplicate user created
- ✅ Existing user recognized by OIDC sub or email

#### Check Logs:
```bash
# Should see:
# - "OIDC login attempt - sub: [redacted]"
# - "Linking existing user [email] to OIDC provider [name]" (if first OIDC login)
# - "User [login] successfully authenticated via OIDC"
# - No "Creating new user" message
```

---

### 5. Group Synchronization

#### Prerequisites:
- Provider configured with "Sync Groups on Login" enabled
- Group mappings configured
- Test user has specific groups in OIDC provider

#### Setup:
1. In OIDC provider, create test groups:
   - `odoo-admin`
   - `odoo-user`
2. Assign test user to `odoo-user` group
3. In Odoo, configure group mappings:
   - OIDC: `odoo-admin` → Odoo: "Administration / Settings"
   - OIDC: `odoo-user` → Odoo: "User types / Internal User"

#### Test Steps - Initial Sync:
1. Log in with test user via SSO
2. Go to **Settings > Users & Companies > Users**
3. Open the test user
4. Check the **Groups** tab

#### Expected Results:
- ✅ User is member of "User types / Internal User" group
- ✅ User is NOT member of "Administration / Settings" group
- ✅ Other groups unchanged

#### Check Logs:
```bash
# Should see:
# - "Syncing groups for user [login]: ['odoo-user']"
# - "Adding user [login] to group [group name]"
# - "Group sync completed for user [login]"
```

#### Test Steps - Add Group in OIDC:
1. In OIDC provider, add user to `odoo-admin` group
2. Log out of Odoo
3. Log in again via SSO
4. Check user groups

#### Expected Results:
- ✅ User now has both groups
- ✅ "Administration / Settings" group added
- ✅ "User types / Internal User" still present

#### Test Steps - Remove Group in OIDC:
1. In OIDC provider, remove user from `odoo-admin` group
2. Log out of Odoo
3. Log in again via SSO
4. Check user groups

#### Expected Results:
- ✅ "Administration / Settings" group removed
- ✅ "User types / Internal User" still present

---

### 6. Multiple Providers

#### Prerequisites:
- Two different OIDC providers configured (e.g., Authentik and Okta)
- Test users in each provider

#### Test Steps:
1. Log out of Odoo
2. Verify both SSO buttons appear on login page
3. Test login with each provider
4. Verify different users created for each provider

#### Expected Results:
- ✅ Both provider buttons visible
- ✅ Can log in with either provider
- ✅ Users kept separate (different OIDC subjects)

---

### 7. Error Handling

#### Test 7.1: Invalid Configuration

**Steps:**
1. Create provider with invalid endpoint URLs
2. Try to log in

**Expected:**
- ✅ Clear error message displayed
- ✅ User not logged in
- ✅ Can return to login page
- ✅ Error logged

#### Test 7.2: Missing Required Claim

**Steps:**
1. Configure OIDC provider without email scope
2. Try to log in

**Expected:**
- ✅ Error: "OIDC provider did not return an email"
- ✅ User not created
- ✅ Can retry

#### Test 7.3: Network Timeout

**Steps:**
1. Configure provider with unreachable endpoint
2. Try to log in

**Expected:**
- ✅ Timeout error displayed
- ✅ User not logged in
- ✅ Appropriate error message

#### Test 7.4: State Mismatch (CSRF Protection)

**Steps:**
1. Start login flow
2. Manually modify state parameter in callback URL
3. Complete authentication

**Expected:**
- ✅ Error: "State verification failed"
- ✅ User not logged in
- ✅ Security issue logged

#### Test 7.5: Auto-Creation Disabled

**Steps:**
1. Disable "Auto-create Users" on provider
2. Try to log in with new user (not in Odoo)

**Expected:**
- ✅ Error: "User auto-creation is disabled"
- ✅ No user created
- ✅ Clear instructions provided

---

### 8. Security Testing

#### Test 8.1: Password Authentication Disabled

**Steps:**
1. Create user via OIDC
2. Try to log in with username/password

**Expected:**
- ✅ Password login fails
- ✅ User must use SSO

#### Test 8.2: CSRF Protection

**Steps:**
1. Capture callback URL during login
2. Try to replay it

**Expected:**
- ✅ Replay attack fails
- ✅ State validation prevents reuse

#### Test 8.3: JWT Verification (if PyJWT available)

**Steps:**
1. Install PyJWT
2. Configure JWKS URI
3. Log in

**Expected:**
- ✅ JWT signature verified
- ✅ No warnings in logs about skipping verification

---

### 9. Platform-Specific Testing

#### Test 9.1: Odoo Online

**Verify:**
- ✅ Works without installing any dependencies
- ✅ Login successful
- ✅ User creation works
- ✅ Group sync works
- ⚠️ Logs show "PyJWT not available" (expected)

#### Test 9.2: Odoo.sh (without dependencies)

**Verify:**
- ✅ Same as Odoo Online
- ✅ Module installs from repository
- ✅ All features work except JWT verification

#### Test 9.3: Odoo.sh (with dependencies)

**Setup:**
Add to repository `requirements.txt`:
```
PyJWT>=2.8.0
cryptography>=41.0.0
requests>=2.31.0
```

**Verify:**
- ✅ Dependencies install during build
- ✅ JWT verification enabled
- ✅ No warnings about missing dependencies

#### Test 9.4: On-Premise

**Setup:**
```bash
pip3 install PyJWT cryptography requests
systemctl restart odoo
```

**Verify:**
- ✅ All dependencies available
- ✅ Full JWT verification
- ✅ Enhanced security features

---

### 10. Performance Testing

#### Test Load Impact:

**Steps:**
1. Measure baseline login time (password auth)
2. Measure SSO login time
3. Test with multiple concurrent users

**Benchmarks:**
- SSO login should complete in < 3 seconds (network dependent)
- Group sync should add < 500ms per user
- No performance degradation with multiple providers

---

### 11. Upgrade Testing

#### Test 11.1: Module Upgrade

**Steps:**
1. Note current version
2. Update module code
3. Upgrade module in Odoo
4. Test all features

**Verify:**
- ✅ Existing configurations preserved
- ✅ Existing users still work
- ✅ Group mappings intact
- ✅ New features available

#### Test 11.2: Odoo Upgrade

**Steps:**
1. Upgrade Odoo to new version
2. Test module compatibility

**Verify:**
- ✅ Module still loads
- ✅ Authentication still works
- ✅ No deprecation warnings

---

## Test Checklist Summary

### Critical Tests (Must Pass):
- [ ] Module installs without errors
- [ ] Provider configuration saves successfully
- [ ] First-time user login creates account
- [ ] Existing user login works
- [ ] Group synchronization adds groups correctly
- [ ] Group synchronization removes groups correctly
- [ ] Error handling works (invalid config, missing claims)
- [ ] Security features work (CSRF protection, password disabled)

### Important Tests (Should Pass):
- [ ] Multiple providers work
- [ ] All OIDC providers supported (test 2-3)
- [ ] Platform compatibility (test on target platform)
- [ ] Performance acceptable
- [ ] Logging appropriate (no sensitive data)

### Optional Tests (Nice to Have):
- [ ] JWT verification (if dependencies available)
- [ ] Complex group mappings
- [ ] Edge cases and error scenarios
- [ ] Upgrade compatibility

---

## Reporting Issues

When reporting issues, include:

1. **Platform**: Odoo Online / Odoo.sh / On-Premise
2. **Odoo Version**: e.g., 19.0
3. **OIDC Provider**: e.g., Authentik 2023.10
4. **Dependencies**: PyJWT installed? requests installed?
5. **Configuration**: Provider settings (redact secrets)
6. **Steps to Reproduce**: Detailed steps
7. **Expected vs Actual**: What should happen vs what happens
8. **Logs**: Relevant log entries (redact sensitive data)
9. **Screenshots**: If applicable

---

## Debugging Tips

### Enable Debug Logging

Add to Odoo config:
```ini
[options]
log_level = debug
```

### Check Logs:

```bash
# On-premise
tail -f /var/log/odoo/odoo.log | grep -E "oidc|OIDC"

# Docker
docker-compose logs -f odoo | grep -E "oidc|OIDC"

# Look for:
# - Authentication attempts
# - User creation messages
# - Group sync operations
# - Errors and warnings
```

### Test Provider Configuration:

Use curl to test endpoints:
```bash
# Test token endpoint
curl -X POST https://provider.example.com/token \
  -d "grant_type=client_credentials" \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "client_secret=YOUR_CLIENT_SECRET"

# Test userinfo endpoint (requires valid token)
curl https://provider.example.com/userinfo \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Common Issues:

1. **Redirect URI mismatch**: Ensure exact match in provider config
2. **Missing scopes**: Check provider returns required claims
3. **Group claim name**: Verify correct claim name in configuration
4. **Network issues**: Check firewall, DNS resolution
5. **Session issues**: Clear browser cookies and cache

---

## Success Criteria

All critical tests pass, and the module:
- ✅ Installs on all target platforms
- ✅ Authenticates users successfully
- ✅ Creates users automatically
- ✅ Syncs groups correctly
- ✅ Handles errors gracefully
- ✅ Maintains security
- ✅ Performs adequately
- ✅ Logs appropriately

---

## Next Steps After Testing

1. Document any platform-specific findings
2. Update provider setup guides based on testing
3. Create FAQ from common issues
4. Plan for production deployment
5. Train users on SSO login process
