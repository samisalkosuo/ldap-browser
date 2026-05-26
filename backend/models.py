from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum


class SecurityMode(str, Enum):
    """LDAP connection security modes."""
    LDAPS = "ldaps"
    STARTTLS = "starttls"
    PLAIN = "plain"


class CertificateStatus(str, Enum):
    """Certificate validation status."""
    TRUSTED = "trusted"
    SELF_SIGNED = "self_signed"
    UNTRUSTED = "untrusted"
    NONE = "none"


class ConnectionRequest(BaseModel):
    """Request model for creating an LDAP connection."""
    name: str = Field(..., description="Connection name")
    protocol: str = Field("ldap", description="Protocol: ldap or ldaps")
    host: str = Field(..., description="LDAP server hostname")
    port: int = Field(389, description="LDAP server port")
    bind_dn: str = Field("", description="Bind DN for authentication")
    username: str = Field("", description="Username (alternative to bind DN)")
    password: str = Field("", description="Password for authentication")
    base_dn: Optional[str] = Field(None, description="Base DN for searches")
    timeout_seconds: int = Field(10, description="Connection timeout in seconds")


class ConnectionStatus(BaseModel):
    """Status of an LDAP connection."""
    connection_id: str
    name: str
    host: str
    port: int
    connected: bool
    security_mode: SecurityMode
    certificate_status: CertificateStatus
    base_dn: Optional[str] = None
    error: Optional[str] = None


class RootDSE(BaseModel):
    """Root DSE information."""
    naming_contexts: List[str] = []
    default_naming_context: Optional[str] = None
    root_domain_naming_context: Optional[str] = None
    subschema_subentry: Optional[str] = None
    vendor_name: Optional[str] = None
    vendor_version: Optional[str] = None
    supported_ldap_version: List[str] = []
    supported_sasl_mechanisms: List[str] = []


class AttributeType(str, Enum):
    """Detected attribute types."""
    STRING = "String"
    NUMBER = "Number"
    BOOLEAN = "Boolean"
    DN = "DN"
    DATETIME = "Date/Time"
    BINARY = "Binary"
    JPEG = "JPEG/Photo"
    CERTIFICATE = "Certificate"
    SID = "SID"
    GUID = "GUID"
    UNKNOWN = "Unknown"


class AttributeValue(BaseModel):
    """Single attribute with metadata."""
    name: str
    values: List[str]
    type: AttributeType
    size_bytes: int
    multi_value: bool


class LDAPEntry(BaseModel):
    """LDAP entry with attributes."""
    dn: str
    object_classes: List[str]
    attributes: List[AttributeValue]


class TreeNode(BaseModel):
    """Tree node for LDAP hierarchy."""
    dn: str
    rdn: str
    object_classes: List[str]
    has_children: bool
    icon_type: str = "unknown"


class SearchScope(str, Enum):
    """LDAP search scopes."""
    BASE = "base"
    ONE_LEVEL = "one"
    SUBTREE = "sub"


class SearchRequest(BaseModel):
    """LDAP search request."""
    base_dn: str
    filter: str = "(objectClass=*)"
    scope: SearchScope = SearchScope.SUBTREE
    size_limit: int = 100
    time_limit: int = 10


class SearchResult(BaseModel):
    """LDAP search result."""
    dn: str
    object_classes: List[str]
    attributes: Dict[str, List[str]] = {}

# Made with Bob
