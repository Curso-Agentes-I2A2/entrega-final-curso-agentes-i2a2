"""
Configurações centralizadas da aplicação usando Pydantic Settings.
Carrega variáveis de ambiente do arquivo .env
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """
    Configurações da aplicação carregadas de variáveis de ambiente.
    
    Exemplo de arquivo .env:
        DATABASE_URL=postgresql://user:pass@localhost:5432/nf_audit
        SECRET_KEY=seu-secret-key-super-seguro
        RAG_SERVICE_URL=http://localhost:8001
    """
    
    # Configurações da aplicação
    APP_NAME: str = "Sistema de Auditoria de Notas Fiscais"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Configurações do servidor
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Configurações de CORS - permite frontend Streamlit
    CORS_ORIGINS: list[str] = [
        "http://localhost:8501",  # Streamlit default
        "http://localhost:3000",
        "http://127.0.0.1:8501",
    ]
    
    # Configurações do banco de dados PostgreSQL
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/nf_audit"
    DB_ECHO: bool = False  # Log SQL queries se True
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    
    # Configurações de autenticação JWT
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 horas
    
    # Configurações de serviços externos
    RAG_SERVICE_URL: Optional[str] = None  # URL do serviço RAG (opcional)
    RAG_SERVICE_TIMEOUT: int = 30  # Timeout em segundos
    
    AGENT_SERVICE_URL: Optional[str] = None  # URL do serviço de Agents (opcional)
    AGENT_SERVICE_TIMEOUT: int = 60
    
    # Configurações de upload
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: set[str] = {".xml", ".pdf"}
    UPLOAD_DIR: str = "./uploads"
    
    # Configurações de auditoria
    MIN_CONFIDENCE_SCORE: float = 0.7  # Score mínimo de confiança
    
    # Configurações de log
    LOG_LEVEL: str = "INFO"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


# Instância global de configurações
settings = Settings()