import uuid
import logging
from typing import Dict, Optional
from ldap_client import LDAPClient
from models import ConnectionRequest, ConnectionStatus, SecurityMode, CertificateStatus

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages multiple LDAP connections in memory."""
    
    def __init__(self):
        self.connections: Dict[str, Dict] = {}
    
    def create_connection(self, request: ConnectionRequest) -> tuple[str, Optional[str]]:
        """
        Create a new LDAP connection.
        Returns (connection_id, error_message).
        """
        connection_id = str(uuid.uuid4())
        
        try:
            # Create LDAP client
            client = LDAPClient(
                host=request.host,
                port=request.port,
                protocol=request.protocol,
                timeout=request.timeout_seconds
            )
            
            # Determine bind DN
            bind_dn = request.bind_dn if request.bind_dn else request.username
            
            if not bind_dn:
                return "", "Either bind_dn or username must be provided"
            
            # Connect and bind
            logger.info(f"Connecting to {request.host}:{request.port} as {bind_dn}")
            success, error = client.connect_and_bind(bind_dn, request.password)
            
            if not success:
                return "", error or "Connection failed"
            
            # Get Root DSE if base DN not provided
            if not request.base_dn:
                root_dse = client.get_root_dse()
                if root_dse and client.base_dn:
                    logger.info(f"Auto-discovered base DN: {client.base_dn}")
            else:
                client.base_dn = request.base_dn
            
            # Store connection
            self.connections[connection_id] = {
                "client": client,
                "name": request.name,
                "host": request.host,
                "port": request.port,
                "bind_dn": bind_dn,
                "base_dn": client.base_dn
            }
            
            logger.info(f"Connection {connection_id} created successfully")
            return connection_id, None
            
        except Exception as e:
            logger.error(f"Failed to create connection: {str(e)}")
            return "", str(e)
    
    def get_connection(self, connection_id: str) -> Optional[LDAPClient]:
        """Get LDAP client by connection ID."""
        conn_data = self.connections.get(connection_id)
        if conn_data:
            return conn_data["client"]
        return None
    
    def get_connection_status(self, connection_id: str) -> Optional[ConnectionStatus]:
        """Get connection status."""
        conn_data = self.connections.get(connection_id)
        if not conn_data:
            return None
        
        client: LDAPClient = conn_data["client"]
        
        return ConnectionStatus(
            connection_id=connection_id,
            name=conn_data["name"],
            host=conn_data["host"],
            port=conn_data["port"],
            connected=client.connection is not None,
            security_mode=client.security_mode,
            certificate_status=client.certificate_status,
            base_dn=conn_data.get("base_dn"),
            error=None
        )
    
    def list_connections(self) -> list[ConnectionStatus]:
        """List all connections."""
        statuses = []
        for conn_id in self.connections.keys():
            status = self.get_connection_status(conn_id)
            if status:
                statuses.append(status)
        return statuses
    
    def delete_connection(self, connection_id: str) -> bool:
        """Delete a connection."""
        conn_data = self.connections.get(connection_id)
        if not conn_data:
            return False
        
        # Disconnect
        client: LDAPClient = conn_data["client"]
        client.disconnect()
        
        # Remove from dict
        del self.connections[connection_id]
        
        logger.info(f"Connection {connection_id} deleted")
        return True
    
    def get_base_dn(self, connection_id: str) -> Optional[str]:
        """Get base DN for a connection."""
        conn_data = self.connections.get(connection_id)
        if conn_data:
            return conn_data.get("base_dn")
        return None


# Global connection manager instance
connection_manager = ConnectionManager()

# Made with Bob
