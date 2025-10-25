# agents/config.py

import os
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Optional

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

class LLMConfig(BaseModel):
    """Configurações para os Modelos de Linguagem."""
    primary_provider: str = "anthropic"
    primary_model: str = "claude-3-sonnet-20240229"
    fallback_provider: str = "openai"
    fallback_model: str = "gpt-4-turbo"
    temperature: float = 0.1
    max_tokens: int = 2048
    timeout: int = 120 # Timeout em segundos para chamadas ao LLM

class APIKeys(BaseModel):
    """Credenciais de API."""
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY")
    openai_api_key: str = os.getenv("OPENAI_API_KEY")

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

# Instância global de configuração para ser importada em outros módulos
settings = AppConfig()

# Validação para garantir que as chaves de API foram carregadas
if not settings.api_keys.anthropic_api_key or not settings.api_keys.openai_api_key:
    print("AVISO: Chaves de API (ANTHROPIC_API_KEY, OPENAI_API_KEY) não encontradas no .env")
    # Em um ambiente de produção, seria melhor lançar um erro:
    # raise ValueError("API keys must be set in the environment.")