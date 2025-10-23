# mcp/config.py

import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# --- Configurações de API Externas ---
class APISettings:
    BRASILAPI_BASE_URL = "https://brasilapi.com.br/api"
    RECEITAWS_BASE_URL = "https://www.receitaws.com.br/v1"
    VIACEP_BASE_URL = "https://viacep.com.br/ws"

# --- Configurações de Comunicação ---
class NetworkSettings:
    # Timeout padrão para requisições HTTP em segundos
    DEFAULT_TIMEOUT = 10.0
    
    # Número de tentativas para requisições que falham
    DEFAULT_RETRIES = 3
    
    # Delay em segundos entre as tentativas para a ReceitaWS (respeitando rate limit)
    RECEITAWS_RETRY_DELAY = 60 

# --- Configurações de Cache ---
class CacheSettings:
    # Tamanho máximo do cache (número de itens)
    DEFAULT_MAX_SIZE = 128
    
    # Tempo de vida do cache em segundos (5 minutos)
    DEFAULT_TTL = 300

# --- Configurações de Banco de Dados (Mock) ---
class DatabaseSettings:
    # Em um projeto real, isso viria de variáveis de ambiente
    # Ex: os.getenv("DATABASE_URL", "sqlite:///./invoices.db")
    INVOICES_DB_URL = "mock://invoices"
    SUPPLIERS_DB_URL = "mock://suppliers"

# Instanciando as configurações para fácil importação
api_settings = APISettings()
network_settings = NetworkSettings()
cache_settings = CacheSettings()
db_settings = DatabaseSettings()