# Installation Guide

This guide covers installation across different Odoo deployment types.

## Prerequisites

- Odoo 19.0 or later
- An OIDC-compliant identity provider (Authentik, Okta, Azure AD, etc.)
- HTTPS configured (recommended for production)

## Platform-Specific Installation

### Odoo Online

Odoo Online has the simplest installation process as no dependencies need to be manually installed.

#### Steps:

1. **Upload the Module**
   - Download or clone this repository
   - Zip the `odoo_sso_oidc` folder
   - Go to your Odoo Online instance
   - Navigate to **Apps**
   - Click the **Upload** button (you may need to enable developer mode)
   - Upload the zip file

2. **Update Apps List**
   - Go to **Apps**
   - Click **Update Apps List**
   - Search for "OIDC Single Sign-On"

3. **Install the Module**
   - Click **Install** on the "OIDC Single Sign-On" module
   - Wait for installation to complete

4. **Configure**
   - Follow the [Configuration Guide](README.md#configuration)

**Note**: On Odoo Online, JWT signature verification will be disabled (but the module still works securely).

---

### Odoo.sh

Odoo.sh allows you to optionally add Python dependencies for enhanced features.

#### Option A: Basic Installation (No Dependencies)

1. **Add Module to Repository**
   - Add the `odoo_sso_oidc` folder to your repository
   - Commit and push:
     ```bash
     git add odoo_sso_oidc
     git commit -m "Add OIDC SSO module"
     git push
     ```

2. **Update and Install**
   - Odoo.sh will automatically detect the new module
   - Go to your Odoo.sh instance
   - Navigate to **Apps > Update Apps List**
   - Search for "OIDC Single Sign-On"
   - Click **Install**

#### Option B: Installation with Dependencies (Recommended)

1. **Add Dependencies to requirements.txt**
   
   Create or edit `requirements.txt` in your **repository root** (not in the module folder):
   
   ```txt
   # OIDC SSO dependencies for enhanced security
   PyJWT>=2.8.0
   cryptography>=41.0.0
   requests>=2.31.0
   ```

2. **Add Module to Repository**
   ```bash
   git add odoo_sso_oidc
   git add requirements.txt
   git commit -m "Add OIDC SSO module with dependencies"
   git push
   ```

3. **Deploy**
   - Odoo.sh will install the dependencies during deployment
   - Wait for the build to complete
   - Check the build logs to confirm dependencies were installed

4. **Update and Install**
   - Go to your Odoo.sh instance
   - Navigate to **Apps > Update Apps List**
   - Search for "OIDC Single Sign-On"
   - Click **Install**

**Note**: With dependencies installed, JWT signature verification will be enabled for enhanced security.

---

### On-Premise

On-premise installations offer the most flexibility and control.

#### Method 1: System-wide Installation (Recommended)

1. **Install Python Dependencies**
   
   ```bash
   # Ubuntu/Debian
   sudo pip3 install PyJWT>=2.8.0 cryptography>=41.0.0 requests>=2.31.0
   
   # Or using the requirements file
   cd /path/to/odoo_sso_oidc
   sudo pip3 install -r requirements.txt
   ```

2. **Copy Module to Addons Directory**
   
   ```bash
   # Copy to Odoo addons directory
   sudo cp -r odoo_sso_oidc /opt/odoo/addons/
   
   # Or create a symlink
   sudo ln -s /path/to/odoo_sso_oidc /opt/odoo/addons/odoo_sso_oidc
   ```

3. **Set Permissions**
   
   ```bash
   sudo chown -R odoo:odoo /opt/odoo/addons/odoo_sso_oidc
   sudo chmod -R 755 /opt/odoo/addons/odoo_sso_oidc
   ```

4. **Update Addons Path** (if using custom directory)
   
   Edit your Odoo configuration file (e.g., `/etc/odoo/odoo.conf`):
   
   ```ini
   [options]
   addons_path = /opt/odoo/addons,/path/to/custom/addons
   ```

5. **Restart Odoo**
   
   ```bash
   sudo systemctl restart odoo
   ```

6. **Install Module**
   - Log in as administrator
   - Go to **Apps**
   - Click **Update Apps List**
   - Remove any filters
   - Search for "OIDC Single Sign-On"
   - Click **Install**

#### Method 2: Virtual Environment Installation

1. **Activate Odoo Virtual Environment**
   
   ```bash
   source /path/to/odoo-venv/bin/activate
   ```

2. **Install Dependencies**
   
   ```bash
   pip install PyJWT>=2.8.0 cryptography>=41.0.0 requests>=2.31.0
   ```

3. **Follow steps 2-6 from Method 1**

#### Method 3: Docker Installation

If you're using Docker:

1. **Add to Dockerfile**
   
   ```dockerfile
   # Install Python dependencies
   RUN pip3 install PyJWT>=2.8.0 cryptography>=41.0.0 requests>=2.31.0
   
   # Copy module
   COPY ./odoo_sso_oidc /mnt/extra-addons/odoo_sso_oidc
   ```

2. **Or use docker-compose.yml**
   
   ```yaml
   version: '3'
   services:
     odoo:
       image: odoo:19
       volumes:
         - ./odoo_sso_oidc:/mnt/extra-addons/odoo_sso_oidc
       command: >
         bash -c "pip3 install PyJWT cryptography requests && odoo"
   ```

3. **Rebuild and restart**
   
   ```bash
   docker-compose build
   docker-compose up -d
   ```

---

## Verification

After installation, verify the module is working:

1. **Check Module Status**
   - Go to **Apps**
   - Search for "OIDC Single Sign-On"
   - Status should show "Installed"

2. **Access Configuration**
   - Go to **Settings > Users & Companies > OIDC Authentication**
   - You should see "OIDC Providers" option

3. **Check Logs**
   
   Look for any warning messages about missing dependencies:
   
   ```bash
   # On-premise
   sudo tail -f /var/log/odoo/odoo.log
   
   # Docker
   docker-compose logs -f odoo
   ```
   
   Expected messages (if dependencies not installed):
   - `PyJWT not available - JWT signature verification will be disabled`
   - `requests library not available - using urllib instead`
   
   These are warnings, not errors - the module will still work.

4. **Test Basic Functionality**
   - Try creating an OIDC provider configuration
   - Check that the callback URL is generated correctly
   - Verify views and menus are accessible

---

## Upgrading

### Upgrading the Module

1. **Backup your database** (always!)

2. **Update module files**
   ```bash
   # On-premise
   cd /opt/odoo/addons/odoo_sso_oidc
   git pull  # if using git
   # or replace files manually
   ```

3. **Restart Odoo**
   ```bash
   sudo systemctl restart odoo
   ```

4. **Upgrade module in Odoo**
   - Go to **Apps**
   - Search for "OIDC Single Sign-On"
   - Click **Upgrade**

### Upgrading Dependencies

```bash
# On-premise
sudo pip3 install --upgrade PyJWT cryptography requests

# Virtual environment
source /path/to/odoo-venv/bin/activate
pip install --upgrade PyJWT cryptography requests

# Docker - rebuild image
docker-compose build --no-cache
```

---

## Uninstallation

If you need to uninstall the module:

1. **Uninstall from Odoo**
   - Go to **Apps**
   - Search for "OIDC Single Sign-On"
   - Click **Uninstall**
   - Confirm the uninstallation

2. **Remove module files** (optional)
   ```bash
   # On-premise
   sudo rm -rf /opt/odoo/addons/odoo_sso_oidc
   ```

3. **Remove dependencies** (optional, only if not used by other modules)
   ```bash
   sudo pip3 uninstall PyJWT cryptography requests
   ```

**Note**: User accounts created via OIDC will remain in Odoo after uninstallation.

---

## Troubleshooting Installation

### Module Not Appearing in Apps List

1. Check addons path in configuration
2. Verify file permissions
3. Update apps list (Settings > Apps > Update Apps List)
4. Enable developer mode and remove "Apps" filter

### Import Errors

```
ModuleNotFoundError: No module named 'jwt'
```

**Solution**: This is just a warning. The module will work without PyJWT using fallback methods. To resolve, install PyJWT:
```bash
pip3 install PyJWT
```

### Permission Denied Errors

```bash
# Fix permissions
sudo chown -R odoo:odoo /opt/odoo/addons/odoo_sso_oidc
sudo chmod -R 755 /opt/odoo/addons/odoo_sso_oidc
```

### Module Fails to Install

1. Check Odoo logs for specific error
2. Verify all XML files are valid
3. Ensure all dependencies are met
4. Try installing in safe mode:
   ```bash
   odoo -c /etc/odoo/odoo.conf -d your_database -i odoo_sso_oidc --stop-after-init
   ```

### Dependencies Not Working on Odoo.sh

1. Verify `requirements.txt` is in repository root, not module folder
2. Check build logs for dependency installation errors
3. Ensure correct version specifications
4. Wait for full build completion before testing

---

## Support

For installation issues:

1. Check the logs first
2. Review this guide thoroughly
3. Check [COMPATIBILITY.md](COMPATIBILITY.md) for platform-specific notes
4. Open an issue on GitHub with:
   - Platform (Odoo Online/Odoo.sh/On-Premise)
   - Odoo version
   - Error messages from logs
   - Steps to reproduce

---

## Next Steps

After successful installation:

1. Follow the [Configuration Guide](README.md#configuration)
2. Review [Provider Setup Examples](PROVIDER_SETUP.md)
3. Configure your OIDC provider
4. Test with a test user
5. Set up group mappings
6. Deploy to production
