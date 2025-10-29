
import httpx
import asyncio
import logging
from cachetools import TTLCache
from typing import Dict, Any

from ..config import api_settings, network_settings, cache_settings

# Configuração do cache
# Cache com TTL de 5 minutos e máximo de 128 entradas
api_cache = TTLCache(maxsize=cache_settings.DEFAULT_MAX_SIZE, ttl=cache_settings.DEFAULT_TTL)

class BrasilAPIClient:
    def __init__(self):
        self.base_url = api_settings.BRASILAPI_BASE_URL
        self.timeout = network_settings.DEFAULT_TIMEOUT
        self.retries = network_settings.DEFAULT_RETRIES

    async def _make_request(self, endpoint: str) -> Dict[str, Any]:
        """Método genérico para fazer requisições com cache e retries."""
        cache_key = f"brasilapi:{endpoint}"
        if cache_key in api_cache:
            logging.info(f"Cache HIT para {cache_key}")
            return api_cache[cache_key]
        
        logging.info(f"Cache MISS para {cache_key}. Realizando requisição...")
        url = f"{self.base_url}/{endpoint}"
        
        for attempt in range(self.retries):
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(url, timeout=self.timeout)
                    response.raise_for_status()  # Lança exceção para status 4xx/5xx
                    data = response.json()
                    api_cache[cache_key] = data  # Armazena no cache em caso de sucesso
                    return data
            except httpx.HTTPStatusError as e:
                logging.error(f"Erro de status HTTP na tentativa {attempt + 1} para {url}: {e}")
                if e.response.status_code in [404]: # Não tentar novamente para 'Not Found'
                    break
            except httpx.RequestError as e:
                logging.error(f"Erro de requisição na tentativa {attempt + 1} para {url}: {e}")
            
            if attempt < self.retries - 1:
                await asyncio.sleep(2 ** attempt) # Exponential backoff
        
        raise ConnectionError(f"Falha ao consultar a BrasilAPI no endpoint {endpoint} após {self.retries} tentativas.")

    async def consult_cnpj(self, cnpj: str) -> Dict[str, Any]:
        """Consulta dados de um CNPJ na BrasilAPI."""
        clean_cnpj = ''.join(filter(str.isdigit, cnpj))
        return await self._make_request(f"cnpj/v1/{clean_cnpj}")

    async def get_bank_info(self, code: str) -> Dict[str, Any]:
        """Consulta informações de um banco pelo código."""
        return await self._make_request(f"banks/v1/{code}")

    async def get_holiday(self, year: int) -> Dict[str, Any]:
        """Consulta feriados nacionais de um determinado ano."""
        return await self._make_request(f"feriados/v1/{year}")

# Singleton para o cliente
brasilapi_client = BrasilAPIClient()