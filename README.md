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

### Using Docker

```bash
# Build the image
docker build -t ldap-browser .

# Run the container
docker run -p 8080:8080 ldap-browser
```

Access the application at http://localhost:8080

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

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_PORT` | `8080` | Port the application listens on |
| `APP_AUTH_ENABLED` | `false` | Enable basic authentication for the web app |
| `APP_AUTH_USERNAME` | `admin` | Username for web app authentication |
| `APP_AUTH_PASSWORD` | `change-me` | Password for web app authentication |
| `LDAP_CONNECTION_TIMEOUT_SECONDS` | `10` | Timeout for LDAP connections |
| `LOG_LEVEL` | `info` | Logging level (debug, info, warning, error) |

## Kubernetes Deployment

### Prerequisites

- Kubernetes cluster (1.19+)
- kubectl configured
- Container image built and pushed to registry

### Deploy

```bash
# Update image in deployment.yaml to your registry
# Example: image: your-registry.com/ldap-browser:latest

# Apply manifests
kubectl apply -f deploy/kubernetes/deployment.yaml
kubectl apply -f deploy/kubernetes/service.yaml
kubectl apply -f deploy/kubernetes/ingress.yaml

# Check status
kubectl get pods -l app=ldap-browser
kubectl get svc ldap-browser
```

### Access

```bash
# Port forward for testing
kubectl port-forward svc/ldap-browser 8080:8080

# Or configure ingress with your domain
# Edit deploy/kubernetes/ingress.yaml and set your hostname
```

## OpenShift Deployment

### Prerequisites

- OpenShift cluster (4.x+)
- oc CLI configured
- Container image built and pushed to registry

### Deploy

```bash
# Login to OpenShift
oc login

# Create new project
oc new-project ldap-browser

# Update image in deployment.yaml
# Example: image: your-registry.com/ldap-browser:latest

# Apply manifests
oc apply -f deploy/openshift/deployment.yaml
oc apply -f deploy/openshift/service.yaml
oc apply -f deploy/openshift/route.yaml

# Check status
oc get pods
oc get route ldap-browser
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

## Usage Guide

### Creating a Connection

1. Click "New Connection" in the header
2. Fill in the connection details:
   - **Connection Name**: Friendly name for this connection
   - **Host**: LDAP server hostname or IP
   - **Port**: 389 (LDAP), 636 (LDAPS), 3268 (AD GC), 3269 (AD GC SSL)
   - **Bind DN**: Full distinguished name (e.g., `cn=admin,dc=example,dc=com`)
   - **Password**: Bind password
   - **Base DN**: Optional, will be auto-discovered if not provided
3. Click "Connect"

The application will automatically:
- Try LDAPS if port suggests secure connection
- Fall back to StartTLS if available
- Use plain LDAP as last resort
- Display security status with visual indicators

### Browsing the Tree

- Click the arrow icon to expand/collapse nodes
- Click the entry name or icon to view details
- Tree loads children on-demand for performance

### Viewing Attributes

- Select an entry from the tree
- All attributes are displayed in a sortable table
- Sort by: Name (A-Z/Z-A), Type, or Size
- Click "Copy" to copy attribute values to clipboard
- Multi-value attributes show all values

### Searching

1. Click "Search" in the header
2. Configure search parameters:
   - **Base DN**: Starting point for search
   - **Filter**: LDAP filter (e.g., `(objectClass=person)`)
   - **Scope**: Base, One Level, or Subtree
   - **Size Limit**: Maximum results to return
   - **Time Limit**: Search timeout in seconds
3. Click "Search"
4. Click any result to view its details

### Common LDAP Filters

```ldap
# All entries
(objectClass=*)

# All users
(objectClass=person)

# All groups
(objectClass=group)

# Specific user
(cn=John Smith)

# Users with email
(mail=*)

# Complex filter
(&(objectClass=person)(mail=*@example.com))
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

## Development

### Project Structure

```
ldap-browser/
├── backend/              # Python FastAPI backend
│   ├── main.py          # FastAPI application
│   ├── models.py        # Pydantic models
│   ├── ldap_client.py   # LDAP client implementation
│   ├── connection_manager.py  # Connection management
│   ├── config.py        # Configuration
│   └── requirements.txt # Python dependencies
├── frontend/            # React frontend
│   ├── public/         # Static files
│   ├── src/
│   │   ├── components/ # React components
│   │   ├── services/   # API client
│   │   ├── App.js      # Main application
│   │   └── App.css     # Styles
│   └── package.json    # Node dependencies
├── deploy/             # Deployment manifests
│   ├── kubernetes/     # Kubernetes YAML
│   └── openshift/      # OpenShift YAML
├── Dockerfile          # Container build
├── docker-compose.yml  # Local development
└── README.md          # This file
```

### Running Tests

```bash
# Backend tests (if implemented)
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

See LICENSE file for details.

## Support

For issues, questions, or contributions, please use the GitHub issue tracker.

## Acknowledgments

- Built with FastAPI and React
- Uses python-ldap for LDAP operations
- Test LDAP server: osixia/openldap
- Icons: react-icons

---

**Note**: This is a read-only tool designed for LDAP exploration and troubleshooting. It does not support LDAP modifications, user creation, or password changes.