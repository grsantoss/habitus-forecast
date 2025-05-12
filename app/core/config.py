"""
Módulo de configuração para o Habitus Forecast.

Este módulo contém as configurações globais da aplicação,
incluindo variáveis de ambiente e constantes.
"""

import os
import secrets
from typing import Any, Dict, List, Optional, Union
from pydantic import AnyHttpUrl, BaseSettings, validator, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()


class Settings(BaseSettings):
    """
    Configurações da aplicação.
    
    Attributes:
        API_V1_STR: Prefixo para as rotas da API v1.
        SECRET_KEY: Chave secreta utilizada para criptografia de tokens JWT.
        ACCESS_TOKEN_EXPIRE_MINUTES: Tempo de expiração dos tokens de acesso.
        PROJECT_NAME: Nome do projeto.
        MONGODB_URL: URL de conexão com o MongoDB.
        MONGODB_DB: Nome do banco de dados MongoDB.
        BACKEND_CORS_ORIGINS: Lista de origens permitidas para CORS.
        MAX_CONNECTIONS_COUNT: Número máximo de conexões com o MongoDB.
        MIN_CONNECTIONS_COUNT: Número mínimo de conexões com o MongoDB.
    """
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    PROJECT_NAME: str = "Habitus Forecast"
    
    # MongoDB settings
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    MONGODB_DB: str = os.getenv("MONGODB_DB", "habitus_forecast")
    MAX_CONNECTIONS_COUNT: int = int(os.getenv("MAX_CONNECTIONS_COUNT", "10"))
    MIN_CONNECTIONS_COUNT: int = int(os.getenv("MIN_CONNECTIONS_COUNT", "1"))
    
    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        """
        Processa origens CORS.
        
        Args:
            v: String com origens separadas por vírgula ou lista de origens.
            
        Returns:
            Lista de origens.
        """
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Config de arquivos
    UPLOAD_FOLDER: str = os.getenv("UPLOAD_FOLDER", "./uploads")
    MAX_UPLOAD_SIZE: int = int(os.getenv("MAX_UPLOAD_SIZE", "10485760"))  # 10MB
    ALLOWED_EXTENSIONS: List[str] = ["xlsx", "xls"]
    
    # Config de logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    # Configuração para uso de modelos de aprendizado de máquina
    ML_MODELS_PATH: str = os.getenv("ML_MODELS_PATH", "./ml_models")
    
    # Configurações adicionais
    DEFAULT_TIMEZONE: str = os.getenv("DEFAULT_TIMEZONE", "America/Sao_Paulo")
    
    model_config = SettingsConfigDict(case_sensitive=True)


settings = Settings() 