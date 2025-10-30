import httpx
import asyncio
import logging
from typing import Dict, Any

from ..config import api_settings, network_settings

class ReceitaWSClient:
    def __init__(self):
        self.base_url = api_settings.RECEITAWS_BASE_URL
        self.timeout = network_settings.DEFAULT_TIMEOUT

    async def consult_cnpj(self, cnpj: str) -> Dict[str, Any]:
        """Consulta dados de um CNPJ na ReceitaWS."""
        clean_cnpj = ''.join(filter(str.isdigit, cnpj))
        url = f"{self.base_url}/cnpj/{clean_cnpj}"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=self.timeout)

                # Tratamento de Rate Limiting
                if response.status_code == 429:
                    logging.warning("Rate limit atingido na ReceitaWS. Aguardando para tentar novamente.")
                    # Em uma aplicação real, seria melhor usar uma fila ou um mecanismo mais robusto
                    await asyncio.sleep(network_settings.RECEITAWS_RETRY_DELAY)
                    response = await client.get(url, timeout=self.timeout)

                response.raise_for_status()
                data = response.json()
                if data.get("status") == "ERROR":
                    raise ValueError(data.get("message", "Erro na API ReceitaWS"))
                return data

        except httpx.RequestError as e:
            logging.error(f"Erro de requisição ao consultar ReceitaWS: {e}")
            raise ConnectionError("Falha ao comunicar com a ReceitaWS.")
        except httpx.HTTPStatusError as e:
            logging.error(f"Erro de status HTTP ao consultar ReceitaWS: {e}")
            raise ConnectionError(f"ReceitaWS retornou erro: {e.response.status_code}")
        except ValueError as e:
            logging.error(f"Erro nos dados retornados pela ReceitaWS: {e}")
            raise

# Singleton para o cliente
receitaws_client = ReceitaWSClient()