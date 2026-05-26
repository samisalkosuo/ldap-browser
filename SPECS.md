# Web-Based Read-Only LDAP Browser Specification

## Goal

Create a minimal-fuss, containerized, web-based LDAP client for browsing LDAP directory trees.

The application must be deployable to Kubernetes and OpenShift. It is intended for read-only LDAP exploration, troubleshooting, and inspection.

No LDAP write operations are allowed.

---

## Core Requirements

## Application Type

Create a web application with:

- Backend service that connects to LDAP/LDAPS servers
- Frontend UI for browsing LDAP entries
- Container image build support
- Kubernetes/OpenShift deployment manifests

Preferred stack:

- Backend: Python FastAPI or Node.js
- Frontend: React
- Container: Docker/Podman-compatible image
- Deployment: Kubernetes YAML and OpenShift-compatible YAML

The implementation should be simple, maintainable, and easy to run locally.

---

## Main Features

## 1. LDAP Connections

The user must be able to create LDAP connections from the UI.

Connection fields:

- Connection name
- Host
- Port
- Bind DN
- Username
- Password
- Optional base DN
- Optional connection timeout

The client must automatically detect connection security:

- Try LDAPS if port appears to be secure, for example `636`
- Try plain LDAP with StartTLS if available
- Try plain LDAP if TLS is not available
- Detect and report:
  - LDAPS
  - LDAP + StartTLS
  - Plain unencrypted LDAP
  - Self-signed or untrusted certificate

All certificates must be accepted automatically, including self-signed certificates.

The UI must clearly show security status:

- Secure TLS
- Self-signed or untrusted certificate
- Unencrypted connection warning

Passwords must never be logged.

---

## 2. Read-Only LDAP Access

The application must only support read operations.

Allowed operations:

- Bind
- Search
- Read entry attributes
- Browse children
- Retrieve schema information if available

Forbidden operations:

- Add
- Modify
- Delete
- Rename
- Move
- Password change

The backend must not expose write endpoints.

---

## 3. LDAP Tree Browser

The main UI layout must have two panels.

Left panel:

- LDAP tree navigation
- Expand/collapse nodes
- Show DN hierarchy
- Use icons for common object classes if possible:
  - User/person
  - Group
  - Organizational unit
  - Domain/component
  - Container/folder
  - Unknown entry

Right panel:

- Selected entry details
- Distinguished Name shown clearly
- Object classes shown prominently
- Attribute table

Tree behavior:

- Lazy-load child entries when expanding nodes
- Do not load entire LDAP tree at once
- Support large directories
- Show loading indicator while expanding
- Show error message if branch cannot be loaded

---

## 4. Attribute Viewer

For selected LDAP entry, show all attributes in a user-friendly table.

Columns:

- Attribute name
- Value
- Type
- Size

Attribute requirements:

- All attributes must be visible
- Multi-value attributes must show all values
- Binary values must be detected and displayed safely
- Long values must be collapsible or expandable
- Values must be copyable
- DN values may be visually highlighted
- Attribute sorting must be supported

Sorting options:

- Attribute name A-Z
- Attribute name Z-A
- Type
- Size

Type detection:

Examples:

- String
- Number
- Boolean
- DN
- Date/time
- Binary
- JPEG/photo
- Certificate
- SID/GUID if detectable
- Unknown

Size:

- Show size in bytes
- For multi-value attributes, show value count and total size

---

## 5. Search

Include simple LDAP search.

Search fields:

- Base DN
- Filter
- Scope:
  - Base
  - One level
  - Subtree
- Size limit
- Time limit

Default filter:

```text
(objectClass=*)
````

Search results:

* Show DN
* Show object classes
* Allow clicking result to open entry
* No modification actions

---

## 6. Base DN Discovery

If user does not provide base DN, attempt automatic discovery.

Use root DSE where available.

Read:

* defaultNamingContext
* namingContexts
* rootDomainNamingContext
* subschemaSubentry
* vendorName
* vendorVersion

If multiple naming contexts exist, let user choose.

---

## 7. Connection Handling

Connections may be stored in memory only by default.

Do not persist passwords unless explicitly configured.

Provide optional configuration:

* In-memory only mode
* Optional encrypted server-side connection storage
* Optional Kubernetes Secret integration later

For first version, implement in-memory connections only.

When browser session ends or backend restarts, connections may be lost.

---

## 8. Security Requirements

Even though this is an internal tool, implement basic safety.

Required:

* Do not log passwords
* Do not expose passwords through API responses
* Do not allow LDAP write operations
* Accept self-signed certificates but show warning
* Show warning for unencrypted LDAP
* Backend APIs should validate input
* Backend should protect against LDAP filter injection where applicable
* Container should run as non-root
* OpenShift-compatible security context

Optional but recommended:

* Basic authentication for the web app
* Environment variable to enable/disable app authentication
* Session timeout
* Read-only audit log of connection attempts and searches

---

## 9. UI Requirements

The UI should be clean and simple.

Layout:

```text
+------------------------------------------------------+
| Header: LDAP Browser | Connection selector | Status  |
+----------------------+-------------------------------+
| Tree navigation      | Entry details / attributes     |
|                      |                               |
|                      | Attribute table               |
+----------------------+-------------------------------+
```

Header should show:

* Current connection
* Security status
* Base DN
* Disconnect button

Left tree panel:

* Search/filter tree if possible
* Expand/collapse
* Icons
* Loading indicators

Right panel:

* Selected DN
* Object classes
* Attribute table
* Copy DN button
* Copy attribute value button

Use visual warnings:

* Yellow warning for self-signed certificate
* Red/orange warning for unencrypted LDAP
* Green/blue indicator for encrypted TLS

---

## 10. API Design

Example backend endpoints:

```text
POST /api/connections
GET  /api/connections
DELETE /api/connections/{connectionId}

GET /api/connections/{connectionId}/status
GET /api/connections/{connectionId}/root-dse
GET /api/connections/{connectionId}/children?dn=...
GET /api/connections/{connectionId}/entry?dn=...
POST /api/connections/{connectionId}/search
```

No write endpoints must exist.

---

## 11. Example Connection Request

```json
{
  "name": "Local LDAP",
  "host": "ldap.example.local",
  "port": 389,
  "bindDn": "cn=admin,dc=example,dc=local",
  "username": "",
  "password": "secret",
  "baseDn": "dc=example,dc=local",
  "timeoutSeconds": 10
}
```

Support either:

* Full bind DN + password
* Username + password if LDAP server supports it

---

## 12. Example Attribute Response

```json
{
  "dn": "cn=John Smith,ou=Users,dc=example,dc=local",
  "objectClasses": ["top", "person", "organizationalPerson", "inetOrgPerson"],
  "attributes": [
    {
      "name": "cn",
      "values": ["John Smith"],
      "type": "String",
      "sizeBytes": 10,
      "multiValue": false
    },
    {
      "name": "memberOf",
      "values": [
        "cn=Developers,ou=Groups,dc=example,dc=local",
        "cn=VPN Users,ou=Groups,dc=example,dc=local"
      ],
      "type": "DN",
      "sizeBytes": 94,
      "multiValue": true
    }
  ]
}
```

---

## 13. Kubernetes/OpenShift Deployment

Provide:

* `Dockerfile`
* `.dockerignore`
* Kubernetes deployment YAML
* Kubernetes service YAML
* Optional route YAML for OpenShift
* Optional ingress YAML for Kubernetes

Container requirements:

* Run as non-root
* Listen on configurable port, default `8080`
* Health endpoint:

```text
GET /health
```

Environment variables:

```text
APP_PORT=8080
APP_AUTH_ENABLED=false
APP_AUTH_USERNAME=admin
APP_AUTH_PASSWORD=change-me
LDAP_CONNECTION_TIMEOUT_SECONDS=10
LOG_LEVEL=info
```

OpenShift compatibility:

* Do not require root user
* Do not write to read-only filesystem except `/tmp`
* Avoid fixed UID assumptions

---

## 14. Local Development

Provide commands for local use.

Example:

```bash
docker build -t ldap-browser .
docker run --rm -p 8080:8080 ldap-browser
```

Also provide docker-compose with optional test LDAP server.

Recommended test LDAP container:

* OpenLDAP test server
* Preloaded sample users and groups

---

## 15. Error Handling

Show friendly errors for:

* Cannot connect
* Invalid bind DN or password
* TLS failure
* LDAP server unavailable
* Base DN not found
* Search size limit exceeded
* Search timeout
* Permission denied
* Attribute cannot be decoded

Errors must be visible in the UI and also returned as structured API responses.

---

## 16. Logging

Log:

* Connection attempts without password
* LDAP host and port
* Security mode detected
* Search base/scope/filter
* Errors

Never log:

* Passwords
* Full credentials
* Sensitive attribute values by default

---

## 17. Non-Goals

Do not implement:

* LDAP editing
* User creation
* Password reset
* Group membership modification
* Schema editing
* Persistent credential vault in first version
* Multi-user role model in first version

---

## 18. Deliverables

The AI development partner must create:

```text
ldap-browser/
  backend/
  frontend/
  deploy/
    kubernetes/
    openshift/
  docker-compose.yml
  Dockerfile
  README.md
```

README must include:

* Overview
* Features
* Security notes
* Local run instructions
* Container build instructions
* Kubernetes deployment instructions
* OpenShift deployment instructions
* Example LDAP test setup

---

## 19. Acceptance Criteria

The application is complete when:

* User can open web UI
* User can create LDAP connection
* Application detects LDAPS, StartTLS, or plain LDAP
* Self-signed certificates are accepted
* Security status is shown in UI
* User can browse LDAP tree
* Child nodes are lazy-loaded
* User can select an LDAP entry
* All attributes are shown
* Attribute name, value, type, and size are visible
* Attributes can be sorted
* Multi-value attributes are displayed clearly
* Binary attributes do not break the UI
* Search works
* No write operations are possible
* App runs in container
* App deploys to Kubernetes/OpenShift
* Container runs as non-root


