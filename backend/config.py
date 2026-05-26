from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    app_port: int = 8080
    app_auth_enabled: bool = False
    app_auth_username: str = "admin"
    app_auth_password: str = "change-me"
    ldap_connection_timeout_seconds: int = 10
    log_level: str = "info"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

# Made with Bob
