# mcp/clients/viacep_client.py

import httpx
import logging
from cachetools import TTLCache
from typing import Dict, Any

from ..config import api_settings, network_settings, cache_settings

# Cache específico para CEPs
cep_cache = TTLCache(maxsize=cache_settings.DEFAULT_MAX_SIZE, ttl=cache_settings.DEFAULT_TTL * 12) # Cache mais longo

class ViaCEPClient:
    def __init__(self):
        self.base_url = api_settings.VIACEP_BASE_URL
        self.timeout = network_settings.DEFAULT_TIMEOUT

    async def consult_cep(self, cep: str) -> Dict[str, Any]:
        """Consulta um CEP na API ViaCEP."""
        clean_cep = ''.join(filter(str.isdigit, cep))
        if len(clean_cep) != 8:
            raise ValueError("Formato de CEP inválido. Deve conter 8 dígitos.")

        if clean_cep in cep_cache:
            logging.info(f"Cache HIT para CEP {clean_cep}")
            return cep_cache[clean_cep]

        url = f"{self.base_url}/{clean_cep}/json/"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=self.timeout)
                response.raise_for_status()
                data = response.json()
                if data.get("erro"):
                    raise ValueError(f"CEP {clean_cep} não encontrado.")
                cep_cache[clean_cep] = data
                return data
        except httpx.RequestError as e:
            logging.error(f"Erro ao consultar ViaCEP: {e}")
            raise ConnectionError("Falha ao se comunicar com a ViaCEP.")

# Singleton para o cliente
viacep_client = ViaCEPClient()
