# agents/config.py

import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

class LLMConfig(BaseModel):
    """Configurações para os Modelos de Linguagem."""
    primary_provider: str = "anthropic"
    primary_model: str = "claude-3-sonnet-20240229"

    fallback_provider: str = "openai"
    secondary_model: str = "gpt-4-turbo"

    tertiary_model: str = "gemini-2.5-flash"

    temperature: float = 0.1
    max_tokens: int = 2048
    timeout: int = 120

class APIKeys(BaseModel):
    """Credenciais de API."""
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY")
    openai_api_key: str = os.getenv("OPENAI_API_KEY")
    google_api_key: Optional[str] = Field(None, alias="GOOGLE_API_KEY")

class ServiceUrls(BaseModel):
    """URLs para serviços externos."""
    rag_service_url: str = os.getenv("RAG_SERVICE_URL", "http://localhost:8001/query")
    mcp_service_url: str = os.getenv("MCP_SERVICE_URL", "http://localhost:8002/execute")
    # Exemplo: URL de um serviço externo para validar CNPJ na Receita Federal
    cnpj_validation_service_url: str = "https://www.receitaws.com.br/v1/cnpj/{cnpj}"

class AgentConfig(BaseModel):
    """Configurações gerais dos agentes."""
    max_retries: int = 3
    retry_delay: int = 2 # segundos

class AppConfig(BaseModel):
    """Agrupa todas as configurações da aplicação."""
    llm: LLMConfig = LLMConfig()
    api_keys: APIKeys = APIKeys()
    service_urls: ServiceUrls = ServiceUrls()
    agent: AgentConfig = AgentConfig()

class LoggerConfig(BaseModel):
    """
    Configurações do logger.
    """
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format: str = "%Y-%m-%d %H:%M:%S"

class AppSettings(BaseSettings):
    """
    Configurações principais da aplicação, carregadas do .env.
    """
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_nested_delimiter='__', 
        env_file_encoding='utf-8', 
        extra='ignore'
    )
    api_keys: APIKeys = Field(default_factory=APIKeys)
    llm: LLMConfig = Field(default_factory=LLMConfig)
    logging: LoggerConfig = Field(default_factory=LoggerConfig)

# Instância global de configuração para ser importada em outros módulos
settings = AppConfig()

# Validação para garantir que as chaves de API foram carregadas
if not settings.api_keys.anthropic_api_key or not settings.api_keys.openai_api_key:
    print("AVISO: Chaves de API (ANTHROPIC_API_KEY, OPENAI_API_KEY) não encontradas no .env")
    # Em um ambiente de produção, seria melhor lançar um erro:
    # raise ValueError("API keys must be set in the environment.")