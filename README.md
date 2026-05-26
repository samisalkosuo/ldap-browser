# LDAP Browser

A web-based, read-only LDAP directory browser designed for troubleshooting, exploration, and inspection of LDAP servers.

## Features

- 🔍 **Read-Only Access** - Browse LDAP directories safely without modification capabilities
- 🔐 **Automatic Security Detection** - Supports LDAPS, StartTLS, and plain LDAP with clear security indicators
- 🌲 **Tree Navigation** - Lazy-loaded hierarchical tree view for efficient browsing of large directories
- 📋 **Attribute Viewer** - Detailed view of all entry attributes with sorting and type detection
- 🔎 **LDAP Search** - Flexible search with customizable filters, scopes, and limits
- 🎯 **Base DN Discovery** - Automatic detection of naming contexts via Root DSE
- 🐳 **Container Ready** - Docker/Podman compatible with non-root user
- ☸️ **Kubernetes/OpenShift** - Production-ready deployment manifests included
- 🔒 **Security Focused** - Accepts self-signed certificates, never logs passwords

## Architecture

- **Backend**: Python FastAPI with python-ldap
- **Frontend**: React with modern UI components
- **Container**: Multi-stage Docker build
- **Deployment**: Kubernetes and OpenShift compatible

## Quick Start

### Using Docker

```bash
# Build the image
docker build -t ldap-browser .

# Run the container
docker run -p 8080:8080 ldap-browser
```

Access the application at http://localhost:8080

### Using Docker Compose (Recommended for Testing)

The easiest way to try the LDAP Browser with a test LDAP server:

```bash
# Build and start all services
docker-compose up -d

# Access the application
# LDAP Browser: http://localhost:8080
# phpLDAPadmin: http://localhost:8081
```

**Test LDAP Server Credentials:**
- Host: `test-ldap`
- Port: `389`
- Bind DN: `cn=admin,dc=example,dc=com`
- Password: `admin`
- Base DN: `dc=example,dc=com`

## Local Development

### Backend

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Run the backend
python main.py
```

Backend will be available at http://localhost:8080

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm start
```

Frontend will be available at http://localhost:3000

## Configuration

The application can be configured using environment variables:

### Application Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_PORT` | `8080` | Port the application listens on |
| `APP_AUTH_ENABLED` | `false` | Enable basic authentication for the web app |
| `APP_AUTH_USERNAME` | `admin` | Username for web app authentication |
| `APP_AUTH_PASSWORD` | `changeme` | Password for web app authentication |
| `LOG_LEVEL` | `info` | Logging level (debug, info, warning, error) |

### LDAP Connection Defaults (Optional)

These environment variables allow you to pre-fill the connection form with default values. When set, users only need to click "Connect" to establish an LDAP connection.

| Variable | Default | Description |
|----------|---------|-------------|
| `LDAP_PROTOCOL` | - | Protocol: `ldap` or `ldaps` |
| `LDAP_HOST` | - | LDAP server hostname or IP address |
| `LDAP_PORT` | - | LDAP server port (e.g., 389, 636, 3268, 3269) |
| `LDAP_BIND_DN` | - | Bind DN for authentication (e.g., `cn=admin,dc=example,dc=com`) |
| `LDAP_USERNAME` | - | Username (alternative to Bind DN, if supported by server) |
| `LDAP_PASSWORD` | - | Password for authentication |
| `LDAP_BASE_DN` | - | Base DN for searches (e.g., `dc=example,dc=com`) |
| `LDAP_TIMEOUT_SECONDS` | - | Connection timeout in seconds |

**Example Docker run with LDAP defaults:**

```bash
docker run -p 8080:8080 \
  -e LDAP_PROTOCOL=ldap \
  -e LDAP_HOST=ldap.example.com \
  -e LDAP_PORT=389 \
  -e LDAP_BIND_DN=cn=admin,dc=example,dc=com \
  -e LDAP_PASSWORD=secret \
  -e LDAP_BASE_DN=dc=example,dc=com \
  ldap-browser
```

**Note**: All LDAP connection defaults are optional. If not set, users will need to manually enter connection details in the form.

## OpenShift Deployment

### Prerequisites

- OpenShift cluster (4.x+)
- oc CLI configured
- Container image built and pushed to registry

### Deploy

```bash
# Login to OpenShift
oc login

# Update image in 03-deployment.yaml if needed
# Example: image: your-registry.com/ldap-browser:latest

# Update ConfigMap (01-configmap.yaml) and Secret (02-secret.yaml) as needed
# ConfigMap contains: LOG_LEVEL and optional LDAP_* connection defaults (including LDAP_PASSWORD)
# Secret contains: APP_PORT, APP_AUTH_ENABLED, APP_AUTH_USERNAME, APP_AUTH_PASSWORD
# Note: LDAP_PASSWORD in ConfigMap is for pre-filling connection form only, not for app authentication

# Apply manifests using install.sh script
cd openshift
./install.sh

# Or apply manually in order:
# oc apply -f 00-namespace.yaml
# oc apply -f 01-configmap.yaml
# oc apply -f 02-secret.yaml
# oc apply -f 03-deployment.yaml
# oc apply -f 04-service.yaml
# oc apply -f 05-route.yaml

# Check status
oc get pods -n ldap-browser
oc get route ldap-browser -n ldap-browser
```

### Access

```bash
# Get the route URL
oc get route ldap-browser -o jsonpath='{.spec.host}'
```

## Building Container Image

```bash
# Docker
docker build -t ldap-browser:latest .

# Podman
podman build -t ldap-browser:latest .

# Tag and push to registry
docker tag ldap-browser:latest your-registry.com/ldap-browser:latest
docker push your-registry.com/ldap-browser:latest
```

## Security Considerations

### What This Application Does

✅ Read-only LDAP operations (bind, search, read)  
✅ Accepts self-signed certificates (with warning)  
✅ Shows security status clearly  
✅ Never logs passwords  
✅ Runs as non-root user in container  
✅ OpenShift security context compatible  

### What This Application Does NOT Do

❌ No LDAP write operations  
❌ No credential storage (in-memory only)  
❌ No user authentication by default  
❌ No audit logging (optional feature)  

### Recommendations

- Use in trusted networks or with VPN
- Enable `APP_AUTH_ENABLED` for production
- Use LDAPS or StartTLS when possible
- Review connection security indicators
- Limit network access with firewall rules
- Use read-only LDAP accounts

## Troubleshooting

### Connection Fails

**Problem**: Cannot connect to LDAP server

**Solutions**:
- Verify host and port are correct
- Check network connectivity: `telnet ldap-host 389`
- Verify bind DN and password
- Check firewall rules
- Review backend logs: `docker logs <container-id>`

### Certificate Errors

**Problem**: TLS/SSL certificate errors

**Solution**: The application accepts self-signed certificates automatically. Check the security badge - it will show "Self-Signed Cert" warning.

### Tree Not Loading

**Problem**: Tree shows "Loading..." indefinitely

**Solutions**:
- Check base DN is correct
- Verify user has read permissions
- Check backend logs for errors
- Try manual search with base DN

### Attributes Not Displaying

**Problem**: Entry selected but attributes don't show

**Solutions**:
- Verify user has read permissions for attributes
- Check for binary attributes that may not decode
- Review browser console for errors

## License

See LICENSE file for details.

## Acknowledgments

- Built with FastAPI and React
- Uses python-ldap for LDAP operations
- Test LDAP server: osixia/openldap
- Icons: react-icons

---

**Note**: This is a read-only tool designed for LDAP exploration and troubleshooting. It does not support LDAP modifications, user creation, or password changes.