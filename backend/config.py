from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    app_port: int = 8080
    app_auth_enabled: bool = False
    app_auth_username: str = "admin"
    app_auth_password: str = "changeme"
    log_level: str = "info"
    
    # LDAP connection defaults from environment
    ldap_protocol: Optional[str] = None
    ldap_host: Optional[str] = None
    ldap_port: Optional[int] = None
    ldap_bind_dn: Optional[str] = None
    ldap_username: Optional[str] = None
    ldap_password: Optional[str] = None
    ldap_base_dn: Optional[str] = None
    ldap_timeout_seconds: Optional[int] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

# Made with Bob
