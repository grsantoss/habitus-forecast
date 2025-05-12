from typing import List
from pydantic import field_validator, AnyHttpUrl
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # API settings
    PROJECT_NAME: str = "Habitus Forecast API"
    PROJECT_DESCRIPTION: str = "API for Habitus Forecast financial SaaS application"
    PROJECT_VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    
    # CORS Settings
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "https://localhost:3000"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str] | str:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # MongoDB Settings
    MONGODB_URL: str
    MONGODB_DB_NAME: str = "habitus_forecast"
    
    # JWT Settings
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # File upload settings
    UPLOAD_DIR: str = "uploads"
    ALLOWED_EXTENSIONS: List[str] = ["xlsx", "xls", "csv"]
    MAX_CONTENT_LENGTH: int = 16 * 1024 * 1024  # 16MB
    
    # Email settings
    SMTP_ENABLED: bool = False
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_NAME: str = "Habitus Forecast"
    SMTP_FROM_EMAIL: str = ""
    SMTP_TLS: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings() 