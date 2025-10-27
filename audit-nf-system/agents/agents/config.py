"""
Configurações da aplicação
Gerencia todas as variáveis de ambiente e configurações dos agentes
"""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """
    Configurações centralizadas da aplicação
    Todas as variáveis vêm do arquivo .env ou variáveis de ambiente
    """
    
    # ========================================================================
    # CONFIGURAÇÕES GERAIS
    # ========================================================================
    
    ENVIRONMENT: str = Field(default="development", description="Ambiente de execução")
    DEBUG: bool = Field(default=True, description="Modo debug")
    HOST: str = Field(default="0.0.0.0", description="Host do servidor")
    PORT: int = Field(default=8002, description="Porta do servidor")
    
    # CORS
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        description="Origens permitidas para CORS"
    )
    
    # ========================================================================
    # API KEYS - MODELOS DE LINGUAGEM
    # ========================================================================
    
    ANTHROPIC_API_KEY: str = Field(
        default="",
        description="API Key do Anthropic Claude"
    )
    
    OPENAI_API_KEY: Optional[str] = Field(
        default=None,
        description="API Key do OpenAI (fallback)"
    )
    
    # ========================================================================
    # CONFIGURAÇÕES DOS MODELOS
    # ========================================================================
    
    # Claude (Primary)
    CLAUDE_MODEL: str = Field(
        default="claude-sonnet-4-5-20250929",
        description="Modelo Claude para agentes"
    )
    
    CLAUDE_TEMPERATURE: float = Field(
        default=0.1,
        description="Temperature para Claude (0.0 = determinístico, 1.0 = criativo)"
    )
    
    CLAUDE_MAX_TOKENS: int = Field(
        default=4096,
        description="Máximo de tokens na resposta do Claude"
    )
    
    # OpenAI (Fallback)
    OPENAI_MODEL: str = Field(
        default="gpt-4-turbo-preview",
        description="Modelo OpenAI para fallback"
    )
    
    OPENAI_TEMPERATURE: float = Field(
        default=0.1,
        description="Temperature para OpenAI"
    )
    
    OPENAI_MAX_TOKENS: int = Field(
        default=4096,
        description="Máximo de tokens na resposta do OpenAI"
    )
    
    # ========================================================================
    # URLS DE SERVIÇOS EXTERNOS
    # ========================================================================
    
    MCP_URL: Optional[str] = Field(
        default="http://localhost:8003",
        description="URL do serviço MCP"
    )
    
    BACKEND_URL: Optional[str] = Field(
        default="http://localhost:8000",
        description="URL do backend principal"
    )
    
    SEFAZ_API_URL: Optional[str] = Field(
        default="https://www.sefaz.sp.gov.br/ws",
        description="URL da API da SEFAZ (mock para desenvolvimento)"
    )
    
    # ========================================================================
    # CONFIGURAÇÕES DOS AGENTES
    # ========================================================================
    
    # Agente de Validação
    VALIDATION_AGENT_ENABLED: bool = Field(
        default=True,
        description="Habilitar agente de validação"
    )
    
    VALIDATION_STRICT_MODE: bool = Field(
        default=True,
        description="Modo estrito de validação (rejeita qualquer erro)"
    )
    
    # Agente de Auditoria
    AUDIT_AGENT_ENABLED: bool = Field(
        default=True,
        description="Habilitar agente de auditoria"
    )
    
    AUDIT_CONFIDENCE_THRESHOLD: float = Field(
        default=0.85,
        description="Threshold de confiança para aprovar auditoria (0.0 - 1.0)"
    )
    
    # Agente Sintético
    SYNTHETIC_AGENT_ENABLED: bool = Field(
        default=True,
        description="Habilitar agente de geração sintética"
    )
    
    # ========================================================================
    # CONFIGURAÇÕES DE TIMEOUT E RETRY
    # ========================================================================
    
    API_TIMEOUT: int = Field(
        default=30,
        description="Timeout para chamadas de API em segundos"
    )
    
    MAX_RETRIES: int = Field(
        default=3,
        description="Número máximo de tentativas para chamadas de API"
    )
    
    RETRY_DELAY: float = Field(
        default=1.0,
        description="Delay entre tentativas em segundos"
    )
    
    # ========================================================================
    # CONFIGURAÇÕES DE CACHE
    # ========================================================================
    
    ENABLE_CACHE: bool = Field(
        default=True,
        description="Habilitar cache de decisões"
    )
    
    CACHE_TTL: int = Field(
        default=3600,
        description="Time to live do cache em segundos"
    )
    
    # ========================================================================
    # CONFIGURAÇÕES DE LOGS
    # ========================================================================
    
    LOG_LEVEL: str = Field(
        default="INFO",
        description="Nível de log (DEBUG, INFO, WARNING, ERROR)"
    )
    
    LOG_FILE: str = Field(
        default="agents.log",
        description="Arquivo de log"
    )
    
    # ========================================================================
    # CONFIGURAÇÕES FISCAIS (BRASIL - SÃO PAULO)
    # ========================================================================
    
    DEFAULT_STATE: str = Field(
        default="SP",
        description="Estado padrão para regras fiscais"
    )
    
    ICMS_STANDARD_RATE: float = Field(
        default=18.0,
        description="Alíquota padrão de ICMS em SP (%)"
    )
    
    ICMS_REDUCED_RATE: float = Field(
        default=7.0,
        description="Alíquota reduzida de ICMS em SP (%)"
    )
    
    # ========================================================================
    # CONFIGURAÇÕES DE DESENVOLVIMENTO
    # ========================================================================
    
    MOCK_EXTERNAL_SERVICES: bool = Field(
        default=False,
        description="Usar mocks para serviços externos (desenvolvimento)"
    )
    
    ENABLE_STREAMING: bool = Field(
        default=True,
        description="Habilitar streaming de tokens dos LLMs"
    )
    
    class Config:
        """
        Configuração do Pydantic
        """
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Instância global das configurações
settings = Settings()


# ========================================================================
# VALIDAÇÕES
# ========================================================================

def validate_settings():
    """
    Valida configurações essenciais no startup
    """
    errors = []
    
    # Validar API Keys obrigatórias
    if not settings.ANTHROPIC_API_KEY:
        errors.append("ANTHROPIC_API_KEY não configurada")
    
    # Validar thresholds
    if not 0.0 <= settings.AUDIT_CONFIDENCE_THRESHOLD <= 1.0:
        errors.append("AUDIT_CONFIDENCE_THRESHOLD deve estar entre 0.0 e 1.0")
    
    if not 0.0 <= settings.CLAUDE_TEMPERATURE <= 2.0:
        errors.append("CLAUDE_TEMPERATURE deve estar entre 0.0 e 2.0")
    
    if errors:
        raise ValueError(f"Erros de configuração:\n" + "\n".join(f"  - {e}" for e in errors))
    
    return True


# ========================================================================
# CONFIGURAÇÕES POR AGENTE
# ========================================================================

VALIDATION_AGENT_CONFIG = {
    "name": "ValidationAgent",
    "model": settings.CLAUDE_MODEL,
    "temperature": 0.0,  # Validação deve ser determinística
    "max_tokens": 2048,
    "timeout": settings.API_TIMEOUT,
    "enabled": settings.VALIDATION_AGENT_ENABLED,
}

AUDIT_AGENT_CONFIG = {
    "name": "AuditAgent",
    "model": settings.CLAUDE_MODEL,
    "temperature": settings.CLAUDE_TEMPERATURE,
    "max_tokens": settings.CLAUDE_MAX_TOKENS,
    "timeout": settings.API_TIMEOUT,
    "enabled": settings.AUDIT_AGENT_ENABLED,
    "confidence_threshold": settings.AUDIT_CONFIDENCE_THRESHOLD,
}

SYNTHETIC_AGENT_CONFIG = {
    "name": "SyntheticAgent",
    "model": settings.CLAUDE_MODEL,
    "temperature": 0.7,  # Geração precisa de mais criatividade
    "max_tokens": 4096,
    "timeout": settings.API_TIMEOUT,
    "enabled": settings.SYNTHETIC_AGENT_ENABLED,
}


# ========================================================================
# HELPER FUNCTIONS
# ========================================================================

def get_llm_config(agent_name: str) -> dict:
    """
    Retorna configuração de LLM para um agente específico
    """
    configs = {
        "validation": VALIDATION_AGENT_CONFIG,
        "audit": AUDIT_AGENT_CONFIG,
        "synthetic": SYNTHETIC_AGENT_CONFIG,
    }
    
    return configs.get(agent_name.lower(), AUDIT_AGENT_CONFIG)


def is_production() -> bool:
    """
    Verifica se está em ambiente de produção
    """
    return settings.ENVIRONMENT.lower() == "production"


def should_use_mock() -> bool:
    """
    Verifica se deve usar mocks para serviços externos
    """
    return settings.MOCK_EXTERNAL_SERVICES or settings.DEBUG


# ========================================================================
# EXPORT
# ========================================================================

__all__ = [
    "settings",
    "validate_settings",
    "VALIDATION_AGENT_CONFIG",
    "AUDIT_AGENT_CONFIG",
    "SYNTHETIC_AGENT_CONFIG",
    "get_llm_config",
    "is_production",
    "should_use_mock",
]
