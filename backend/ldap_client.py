import ldap
import ssl
import socket
import logging
from typing import Optional, List, Dict, Any, Tuple
from models import (
    SecurityMode, CertificateStatus, RootDSE,
    AttributeType, AttributeValue, LDAPEntry, TreeNode, SearchScope
)

logger = logging.getLogger(__name__)


class LDAPClient:
    """LDAP client with read-only operations."""
    
    def __init__(self, host: str, port: int, protocol: str = "ldap", timeout: int = 10):
        self.host = host
        self.port = port
        self.protocol = protocol.lower()
        self.timeout = timeout
        self.connection: Optional[ldap.ldapobject.LDAPObject] = None
        self.security_mode: SecurityMode = SecurityMode.PLAIN
        self.certificate_status: CertificateStatus = CertificateStatus.NONE
        self.base_dn: Optional[str] = None
        self.certificate_chain_pem: Optional[str] = None
        
    def connect_and_bind(self, bind_dn: str, password: str) -> Tuple[bool, Optional[str]]:
        """
        Connect to LDAP server using specified protocol.
        Returns (success, error_message).
        """
        try:
            # Use LDAPS if protocol is ldaps
            if self.protocol == "ldaps":
                success, error = self._try_ldaps(bind_dn, password)
                if success:
                    return True, None
                return False, error or "LDAPS connection failed"
            
            # Otherwise use plain LDAP
            success, error = self._try_plain_ldap(bind_dn, password)
            if success:
                return True, None
            
            return False, error or "LDAP connection failed"
            
        except Exception as e:
            logger.error(f"Connection error: {str(e)}")
            return False, str(e)
    
    def _try_ldaps(self, bind_dn: str, password: str) -> Tuple[bool, Optional[str]]:
        """Try LDAPS connection."""
        try:
            ldap_url = f"ldaps://{self.host}:{self.port}"
            logger.info(f"Attempting LDAPS connection to {ldap_url}")
            
            # Capture certificate chain before LDAP connection
            self._capture_certificate_chain()
            
            # Create TLS context that accepts all certificates
            ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
            
            conn = ldap.initialize(ldap_url)
            conn.set_option(ldap.OPT_NETWORK_TIMEOUT, self.timeout)
            conn.set_option(ldap.OPT_TIMEOUT, self.timeout)
            conn.set_option(ldap.OPT_PROTOCOL_VERSION, ldap.VERSION3)
            
            # Attempt bind
            conn.simple_bind_s(bind_dn, password)
            
            self.connection = conn
            self.security_mode = SecurityMode.LDAPS
            # Assume self-signed since we disabled cert verification
            self.certificate_status = CertificateStatus.SELF_SIGNED
            
            logger.info(f"LDAPS connection successful")
            return True, None
            
        except ldap.INVALID_CREDENTIALS:
            return False, "Invalid credentials"
        except ldap.SERVER_DOWN:
            return False, "Server not available on LDAPS"
        except Exception as e:
            logger.debug(f"LDAPS failed: {str(e)}")
            return False, str(e)
    
    def _try_starttls(self, bind_dn: str, password: str) -> Tuple[bool, Optional[str]]:
        """Try LDAP with StartTLS."""
        try:
            ldap_url = f"ldap://{self.host}:{self.port}"
            logger.info(f"Attempting LDAP+StartTLS connection to {ldap_url}")
            
            # Capture certificate chain before LDAP connection
            self._capture_certificate_chain()
            
            # Create connection
            ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
            
            conn = ldap.initialize(ldap_url)
            conn.set_option(ldap.OPT_NETWORK_TIMEOUT, self.timeout)
            conn.set_option(ldap.OPT_TIMEOUT, self.timeout)
            conn.set_option(ldap.OPT_PROTOCOL_VERSION, ldap.VERSION3)
            
            # Start TLS
            conn.start_tls_s()
            
            # Attempt bind
            conn.simple_bind_s(bind_dn, password)
            
            self.connection = conn
            self.security_mode = SecurityMode.STARTTLS
            self.certificate_status = CertificateStatus.SELF_SIGNED
            
            logger.info(f"LDAP+StartTLS connection successful")
            return True, None
            
        except ldap.INVALID_CREDENTIALS:
            return False, "Invalid credentials"
        except ldap.SERVER_DOWN:
            return False, "Server not available"
        except ldap.CONNECT_ERROR:
            return False, "StartTLS not supported"
        except Exception as e:
            logger.debug(f"StartTLS failed: {str(e)}")
            return False, str(e)
    
    def _try_plain_ldap(self, bind_dn: str, password: str) -> Tuple[bool, Optional[str]]:
        """Try plain LDAP connection (unencrypted)."""
        try:
            ldap_url = f"ldap://{self.host}:{self.port}"
            logger.warning(f"Attempting PLAIN LDAP connection to {ldap_url} (UNENCRYPTED)")
            
            conn = ldap.initialize(ldap_url)
            conn.set_option(ldap.OPT_NETWORK_TIMEOUT, self.timeout)
            conn.set_option(ldap.OPT_TIMEOUT, self.timeout)
            conn.set_option(ldap.OPT_PROTOCOL_VERSION, ldap.VERSION3)
            
            # Attempt bind
            conn.simple_bind_s(bind_dn, password)
            
            self.connection = conn
            self.security_mode = SecurityMode.PLAIN
            self.certificate_status = CertificateStatus.NONE
            
            logger.warning(f"Plain LDAP connection successful (UNENCRYPTED)")
            return True, None
            
        except ldap.INVALID_CREDENTIALS:
            return False, "Invalid credentials"
        except ldap.SERVER_DOWN:
            return False, "Server not available"
        except Exception as e:
            logger.error(f"Plain LDAP failed: {str(e)}")
            return False, str(e)
    
    def get_root_dse(self) -> Optional[RootDSE]:
        """Retrieve Root DSE information."""
        if not self.connection:
            return None
        
        try:
            result = self.connection.search_s(
                "", 
                ldap.SCOPE_BASE, 
                "(objectClass=*)",
                [
                    "namingContexts",
                    "defaultNamingContext",
                    "rootDomainNamingContext",
                    "subschemaSubentry",
                    "vendorName",
                    "vendorVersion",
                    "supportedLDAPVersion",
                    "supportedSASLMechanisms"
                ]
            )
            
            if not result:
                return None
            
            _, attrs = result[0]
            
            root_dse = RootDSE(
                naming_contexts=self._decode_attr(attrs.get("namingContexts", [])),
                default_naming_context=self._decode_single_attr(attrs.get("defaultNamingContext")),
                root_domain_naming_context=self._decode_single_attr(attrs.get("rootDomainNamingContext")),
                subschema_subentry=self._decode_single_attr(attrs.get("subschemaSubentry")),
                vendor_name=self._decode_single_attr(attrs.get("vendorName")),
                vendor_version=self._decode_single_attr(attrs.get("vendorVersion")),
                supported_ldap_version=self._decode_attr(attrs.get("supportedLDAPVersion", [])),
                supported_sasl_mechanisms=self._decode_attr(attrs.get("supportedSASLMechanisms", []))
            )
            
            # Set base DN if not already set
            if not self.base_dn:
                if root_dse.default_naming_context:
                    self.base_dn = root_dse.default_naming_context
                elif root_dse.naming_contexts:
                    self.base_dn = root_dse.naming_contexts[0]
            
            return root_dse
            
        except Exception as e:
            logger.error(f"Failed to retrieve Root DSE: {str(e)}")
            return None
    
    def get_children(self, dn: str) -> List[TreeNode]:
        """Get immediate children of a DN."""
        if not self.connection:
            return []
        
        try:
            result = self.connection.search_s(
                dn,
                ldap.SCOPE_ONELEVEL,
                "(objectClass=*)",
                ["objectClass"]
            )
            
            children = []
            for child_dn, attrs in result:
                if child_dn:
                    object_classes = self._decode_attr(attrs.get("objectClass", []))
                    rdn = child_dn.split(",")[0] if "," in child_dn else child_dn
                    
                    # Check if has children
                    has_children = self._has_children(child_dn)
                    
                    children.append(TreeNode(
                        dn=child_dn,
                        rdn=rdn,
                        object_classes=object_classes,
                        has_children=has_children,
                        icon_type=self._determine_icon_type(object_classes)
                    ))
            
            return children
            
        except ldap.NO_SUCH_OBJECT:
            logger.error(f"DN not found: {dn}")
            return []
        except Exception as e:
            logger.error(f"Failed to get children of {dn}: {str(e)}")
            return []
    
    def _has_children(self, dn: str) -> bool:
        """Check if DN has children."""
        try:
            result = self.connection.search_s(
                dn,
                ldap.SCOPE_ONELEVEL,
                "(objectClass=*)",
                ["dn"]
            )
            return len(result) > 0
        except:
            return False
    
    def get_entry(self, dn: str) -> Optional[LDAPEntry]:
        """Get full entry with all attributes."""
        if not self.connection:
            return None
        
        try:
            result = self.connection.search_s(
                dn,
                ldap.SCOPE_BASE,
                "(objectClass=*)",
                ["*"]
            )
            
            if not result:
                return None
            
            _, attrs = result[0]
            
            object_classes = self._decode_attr(attrs.get("objectClass", []))
            
            attributes = []
            for attr_name, attr_values in attrs.items():
                if attr_name.lower() == "objectclass":
                    continue
                
                attr_info = self._process_attribute(attr_name, attr_values)
                attributes.append(attr_info)
            
            return LDAPEntry(
                dn=dn,
                object_classes=object_classes,
                attributes=attributes
            )
            
        except ldap.NO_SUCH_OBJECT:
            logger.error(f"Entry not found: {dn}")
            return None
        except Exception as e:
            logger.error(f"Failed to get entry {dn}: {str(e)}")
            return None
    
    def search(self, base_dn: str, filter_str: str, scope: SearchScope, 
               size_limit: int = 100, time_limit: int = 10) -> List[Dict[str, Any]]:
        """Perform LDAP search."""
        if not self.connection:
            return []
        
        try:
            scope_map = {
                SearchScope.BASE: ldap.SCOPE_BASE,
                SearchScope.ONE_LEVEL: ldap.SCOPE_ONELEVEL,
                SearchScope.SUBTREE: ldap.SCOPE_SUBTREE
            }
            
            ldap_scope = scope_map.get(scope, ldap.SCOPE_SUBTREE)
            
            # Set limits
            self.connection.set_option(ldap.OPT_SIZELIMIT, size_limit)
            self.connection.set_option(ldap.OPT_TIMELIMIT, time_limit)
            
            result = self.connection.search_s(
                base_dn,
                ldap_scope,
                filter_str,
                ["*"]
            )
            
            results = []
            for dn, attrs in result:
                if dn:
                    object_classes = self._decode_attr(attrs.get("objectClass", []))
                    
                    # Convert attributes to dict
                    attr_dict = {}
                    for attr_name, attr_values in attrs.items():
                        attr_dict[attr_name] = self._decode_attr(attr_values)
                    
                    results.append({
                        "dn": dn,
                        "objectClasses": object_classes,
                        "attributes": attr_dict
                    })
            
            return results
            
        except ldap.SIZELIMIT_EXCEEDED:
            logger.warning(f"Search size limit exceeded")
            return []
        except ldap.TIMELIMIT_EXCEEDED:
            logger.warning(f"Search time limit exceeded")
            return []
        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            return []
    
    def _process_attribute(self, name: str, values: List[bytes]) -> AttributeValue:
        """Process attribute and detect type."""
        decoded_values = []
        total_size = 0
        attr_type = AttributeType.UNKNOWN
        
        for value in values:
            total_size += len(value)
            
            # Try to decode as string
            try:
                decoded = value.decode('utf-8')
                decoded_values.append(decoded)
                
                # Detect type
                if attr_type == AttributeType.UNKNOWN:
                    attr_type = self._detect_type(name, decoded, value)
                    
            except UnicodeDecodeError:
                # Binary data
                attr_type = self._detect_binary_type(name, value)
                decoded_values.append(f"<binary data: {len(value)} bytes>")
        
        return AttributeValue(
            name=name,
            values=decoded_values,
            type=attr_type,
            size_bytes=total_size,
            multi_value=len(values) > 1
        )
    
    def _detect_type(self, name: str, value: str, raw_value: bytes) -> AttributeType:
        """Detect attribute type from name and value."""
        name_lower = name.lower()
        
        # DN detection
        if any(x in name_lower for x in ["dn", "member", "memberof", "manager"]):
            if "," in value and "=" in value:
                return AttributeType.DN
        
        # Number detection
        try:
            int(value)
            return AttributeType.NUMBER
        except:
            pass
        
        # Boolean detection
        if value.upper() in ["TRUE", "FALSE"]:
            return AttributeType.BOOLEAN
        
        # Date/time detection (basic)
        if any(x in name_lower for x in ["time", "date", "when"]):
            return AttributeType.DATETIME
        
        # GUID/SID detection
        if "guid" in name_lower or "uuid" in name_lower:
            return AttributeType.GUID
        if "sid" in name_lower:
            return AttributeType.SID
        
        return AttributeType.STRING
    
    def _detect_binary_type(self, name: str, value: bytes) -> AttributeType:
        """Detect binary attribute type."""
        name_lower = name.lower()
        
        # JPEG detection
        if name_lower in ["jpegphoto", "thumbnailphoto"]:
            return AttributeType.JPEG
        
        # Certificate detection
        if "certificate" in name_lower:
            return AttributeType.CERTIFICATE
        
        # GUID
        if "guid" in name_lower:
            return AttributeType.GUID
        
        # SID
        if "sid" in name_lower:
            return AttributeType.SID
        
        return AttributeType.BINARY
    
    def _determine_icon_type(self, object_classes: List[str]) -> str:
        """Determine icon type from object classes."""
        classes_lower = [oc.lower() for oc in object_classes]
        
        if any(x in classes_lower for x in ["person", "user", "inetorgperson"]):
            return "user"
        if any(x in classes_lower for x in ["group", "groupofnames", "groupofuniquenames"]):
            return "group"
        if "organizationalunit" in classes_lower:
            return "ou"
        if any(x in classes_lower for x in ["domain", "dcobject"]):
            return "domain"
        if "container" in classes_lower:
            return "container"
        
        return "unknown"
    
    def _decode_attr(self, values: List[bytes]) -> List[str]:
        """Decode attribute values to strings."""
        decoded = []
        for value in values:
            try:
                decoded.append(value.decode('utf-8'))
            except:
                decoded.append(f"<binary: {len(value)} bytes>")
        return decoded
    
    def _decode_single_attr(self, values: Optional[List[bytes]]) -> Optional[str]:
        """Decode single attribute value."""
        if not values:
            return None
        decoded = self._decode_attr(values)
        return decoded[0] if decoded else None
    
    def _capture_certificate_chain(self):
        """Capture SSL certificate chain from the server."""
        try:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            with socket.create_connection((self.host, self.port), timeout=self.timeout) as sock:
                with context.wrap_socket(sock, server_hostname=self.host) as ssock:
                    # Get the certificate in DER format
                    der_cert = ssock.getpeercert(binary_form=True)
                    
                    if der_cert:
                        # Convert DER to PEM
                        import base64
                        pem_cert = "-----BEGIN CERTIFICATE-----\n"
                        pem_cert += base64.b64encode(der_cert).decode('ascii')
                        # Split into 64-character lines
                        pem_lines = [pem_cert[i:i+64] for i in range(len(pem_cert), len(pem_cert) + len(base64.b64encode(der_cert).decode('ascii')), 64)]
                        pem_cert = "-----BEGIN CERTIFICATE-----\n"
                        pem_cert += "\n".join([base64.b64encode(der_cert).decode('ascii')[i:i+64]
                                              for i in range(0, len(base64.b64encode(der_cert).decode('ascii')), 64)])
                        pem_cert += "\n-----END CERTIFICATE-----\n"
                        
                        self.certificate_chain_pem = pem_cert
                        logger.info("Certificate chain captured successfully")
        except Exception as e:
            logger.warning(f"Failed to capture certificate chain: {str(e)}")
            self.certificate_chain_pem = None
    
    def get_certificate_chain_pem(self) -> Optional[str]:
        """Get the certificate chain in PEM format."""
        return self.certificate_chain_pem
    
    def disconnect(self):
        """Close LDAP connection."""
        if self.connection:
            try:
                self.connection.unbind_s()
            except:
                pass
            self.connection = None

# Made with Bob
