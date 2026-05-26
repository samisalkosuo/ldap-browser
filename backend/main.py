from fastapi import FastAPI, HTTPException, Query, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import logging
import os
import secrets
from typing import Optional

from config import settings
from models import (
    ConnectionRequest, ConnectionStatus, RootDSE,
    LDAPEntry, TreeNode, SearchRequest, SearchResult
)
from connection_manager import connection_manager

# Configure logging
logging.basicConfig(
    level=settings.log_level.upper(),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize HTTP Basic Auth
security = HTTPBasic(auto_error=False)

def verify_credentials(credentials: Optional[HTTPBasicCredentials] = Depends(security)):
    """Verify HTTP Basic Authentication credentials."""
    if not settings.app_auth_enabled:
        return True
    
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    correct_username = secrets.compare_digest(
        credentials.username.encode("utf8"),
        settings.app_auth_username.encode("utf8")
    )
    correct_password = secrets.compare_digest(
        credentials.password.encode("utf8"),
        settings.app_auth_password.encode("utf8")
    )
    
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return True

# Create FastAPI app
app = FastAPI(
    title="LDAP Browser API",
    description="Read-only LDAP browser backend",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files if they exist (for production)
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    # Mount the static subdirectory for CSS/JS files
    static_assets = os.path.join(static_dir, "static")
    if os.path.exists(static_assets):
        app.mount("/static", StaticFiles(directory=static_assets), name="static")
        logger.info(f"Serving static assets from {static_assets}")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

@app.get("/api/connection-defaults")
async def get_connection_defaults():
    """Get default LDAP connection values from environment variables."""
    defaults = {}
    
    if settings.ldap_protocol:
        defaults["protocol"] = settings.ldap_protocol
    if settings.ldap_host:
        defaults["host"] = settings.ldap_host
    if settings.ldap_port:
        defaults["port"] = settings.ldap_port
    if settings.ldap_bind_dn:
        defaults["bind_dn"] = settings.ldap_bind_dn
    if settings.ldap_username:
        defaults["username"] = settings.ldap_username
    if settings.ldap_password:
        defaults["password"] = settings.ldap_password
    if settings.ldap_base_dn:
        defaults["base_dn"] = settings.ldap_base_dn
    if settings.ldap_timeout_seconds:
        defaults["timeout_seconds"] = settings.ldap_timeout_seconds
    
    return defaults



@app.post("/api/connections", response_model=ConnectionStatus)
async def create_connection(request: ConnectionRequest, authenticated: bool = Depends(verify_credentials)):
    """Create a new LDAP connection."""
    logger.info(f"Creating connection to {request.host}:{request.port}")
    
    connection_id, error = connection_manager.create_connection(request)
    
    if error:
        logger.error(f"Connection failed: {error}")
        raise HTTPException(status_code=400, detail=error)
    
    status = connection_manager.get_connection_status(connection_id)
    if not status:
        raise HTTPException(status_code=500, detail="Failed to retrieve connection status")
    
    return status


@app.get("/api/connections", response_model=list[ConnectionStatus])
async def list_connections(authenticated: bool = Depends(verify_credentials)):
    """List all active connections."""
    return connection_manager.list_connections()


@app.get("/api/connections/{connection_id}/status", response_model=ConnectionStatus)
async def get_connection_status(connection_id: str, authenticated: bool = Depends(verify_credentials)):
    """Get connection status."""
    status = connection_manager.get_connection_status(connection_id)
    if not status:
        raise HTTPException(status_code=404, detail="Connection not found")
    return status


@app.delete("/api/connections/{connection_id}")
async def delete_connection(connection_id: str, authenticated: bool = Depends(verify_credentials)):
    """Delete a connection."""
    success = connection_manager.delete_connection(connection_id)
    if not success:
        raise HTTPException(status_code=404, detail="Connection not found")
    return {"message": "Connection deleted"}


@app.get("/api/connections/{connection_id}/root-dse", response_model=RootDSE)
async def get_root_dse(connection_id: str, authenticated: bool = Depends(verify_credentials)):
    """Get Root DSE information."""
    client = connection_manager.get_connection(connection_id)
    if not client:
        raise HTTPException(status_code=404, detail="Connection not found")
    
    root_dse = client.get_root_dse()
    if not root_dse:
        raise HTTPException(status_code=500, detail="Failed to retrieve Root DSE")
    
    return root_dse


@app.get("/api/connections/{connection_id}/children", response_model=list[TreeNode])
async def get_children(connection_id: str, dn: Optional[str] = Query(None), authenticated: bool = Depends(verify_credentials)):
    """Get children of a DN."""
    client = connection_manager.get_connection(connection_id)
    if not client:
        raise HTTPException(status_code=404, detail="Connection not found")
    
    # If no DN provided, use base DN
    if not dn:
        dn = connection_manager.get_base_dn(connection_id)
        if not dn:
            raise HTTPException(status_code=400, detail="No DN provided and no base DN available")
    
    try:
        children = client.get_children(dn)
        return children
    except Exception as e:
        logger.error(f"Failed to get children: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/connections/{connection_id}/entry", response_model=LDAPEntry)
async def get_entry(connection_id: str, dn: str = Query(...), authenticated: bool = Depends(verify_credentials)):
    """Get full LDAP entry with all attributes."""
    client = connection_manager.get_connection(connection_id)
    if not client:
        raise HTTPException(status_code=404, detail="Connection not found")
    
    try:
        entry = client.get_entry(dn)
        if not entry:
            raise HTTPException(status_code=404, detail="Entry not found")
        return entry
    except Exception as e:
        logger.error(f"Failed to get entry: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/connections/{connection_id}/search")
async def search_ldap(connection_id: str, request: SearchRequest, authenticated: bool = Depends(verify_credentials)):
    """Perform LDAP search."""
    client = connection_manager.get_connection(connection_id)
    if not client:
        raise HTTPException(status_code=404, detail="Connection not found")
    
    try:
        results = client.search(
            base_dn=request.base_dn,
            filter_str=request.filter,
            scope=request.scope,
            size_limit=request.size_limit,
            time_limit=request.time_limit
        )
        return results
    except Exception as e:
        logger.error(f"Search failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/connections/{connection_id}/certificate")
async def get_certificate_chain(connection_id: str, authenticated: bool = Depends(verify_credentials)):
    """Get certificate chain in PEM format."""
    client = connection_manager.get_connection(connection_id)
    if not client:
        raise HTTPException(status_code=404, detail="Connection not found")
    
    cert_pem = client.get_certificate_chain_pem()
    if not cert_pem:
        raise HTTPException(status_code=404, detail="No certificate available")
    
    return JSONResponse(
        content={"certificate_pem": cert_pem},
        media_type="application/json"
    )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


# Serve React app for all other routes (must be last)
@app.get("/{full_path:path}")
async def serve_react_app(full_path: str):
    """Serve React app for client-side routing."""
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    index_file = os.path.join(static_dir, "index.html")
    
    # If static files exist, serve index.html for client-side routing
    if os.path.exists(index_file):
        return FileResponse(index_file)
    
    # Otherwise return 404
    raise HTTPException(status_code=404, detail="Not found")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.app_port,
        log_level=settings.log_level.lower()
    )

# Made with Bob
