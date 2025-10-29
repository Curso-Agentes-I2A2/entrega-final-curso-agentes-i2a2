# mcp/clients/rag_client.py

import httpx
import asyncio
import logging
from typing import Dict, Any, Optional, List
from cachetools import TTLCache

from ..config import network_settings, cache_settings

# Cache específico para queries RAG (5 minutos)
rag_cache = TTLCache(
    maxsize=cache_settings.DEFAULT_MAX_SIZE, 
    ttl=cache_settings.DEFAULT_TTL
)

class RAGClient:
    """
    Cliente HTTP para comunicação com a API RAG.
    Implementa cache, retry e tratamento de erros.
    """
    
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.timeout = network_settings.DEFAULT_TIMEOUT
        self.retries = network_settings.DEFAULT_RETRIES
        
    async def _make_request(
        self, 
        endpoint: str, 
        method: str = "POST",
        json_data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Método genérico para fazer requisições com retry."""
        
        url = f"{self.base_url}/{endpoint}"
        
        for attempt in range(self.retries):
            try:
                async with httpx.AsyncClient() as client:
                    if method == "POST":
                        response = await client.post(
                            url, 
                            json=json_data, 
                            timeout=self.timeout
                        )
                    else:
                        response = await client.get(url, timeout=self.timeout)
                    
                    response.raise_for_status()
                    return response.json()
                    
            except httpx.HTTPStatusError as e:
                logging.error(
                    f"Erro HTTP na tentativa {attempt + 1} para {url}: "
                    f"Status {e.response.status_code}"
                )
                
                # Não retry para erros 4xx (exceto 429 - rate limit)
                if 400 <= e.response.status_code < 500 and e.response.status_code != 429:
                    raise ConnectionError(
                        f"Erro do cliente ao consultar RAG: {e.response.status_code}"
                    )
                    
            except httpx.RequestError as e:
                logging.error(
                    f"Erro de requisição na tentativa {attempt + 1} para {url}: {e}"
                )
            
            # Exponential backoff
            if attempt < self.retries - 1:
                await asyncio.sleep(2 ** attempt)
        
        raise ConnectionError(
            f"Falha ao consultar RAG API no endpoint {endpoint} "
            f"após {self.retries} tentativas"
        )
    
    async def search(
        self,
        query: str,
        k: int = 3,
        state: Optional[str] = None,
        tax_type: Optional[str] = None,
        min_score: float = 0.7
    ) -> Dict[str, Any]:
        """
        Busca informações na base de conhecimento regulatória.
        
        Args:
            query: Pergunta sobre legislação fiscal
            k: Número de resultados (1-10)
            state: Filtro por UF (opcional)
            tax_type: Filtro por tipo de imposto (opcional)
            min_score: Score mínimo de relevância
            
        Returns:
            Dict com resultados da busca
        """
        # Gerar chave de cache
        cache_key = f"rag:{query}:{k}:{state}:{tax_type}:{min_score}"
        
        # Verificar cache
        if cache_key in rag_cache:
            logging.info(f"Cache HIT para query: {query[:50]}...")
            return rag_cache[cache_key]
        
        logging.info(f"Cache MISS. Consultando RAG API: {query[:50]}...")
        
        # Montar payload
        payload = {
            "query": query,
            "k": k,
            "min_score": min_score
        }
        
        if state:
            payload["state"] = state
        if tax_type:
            payload["tax_type"] = tax_type
        
        # Fazer requisição
        try:
            result = await self._make_request(
                "api/v1/search",
                method="POST",
                json_data=payload
            )
            
            # Armazenar no cache
            rag_cache[cache_key] = result
            
            return result
            
        except Exception as e:
            logging.error(f"Erro ao consultar RAG: {e}")
            raise
    
    async def health_check(self) -> Dict[str, Any]:
        """Verifica se a API RAG está disponível."""
        try:
            return await self._make_request("api/v1/health", method="GET")
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }

# Singleton
rag_client = RAGClient()