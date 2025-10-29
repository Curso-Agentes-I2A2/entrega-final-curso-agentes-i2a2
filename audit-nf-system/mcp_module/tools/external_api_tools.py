# mcp/tools/external_api_tools.py

import logging
from typing import Dict, Any

from ..clients.brasilapi_client import brasilapi_client
from ..clients.receitaws_client import receitaws_client
from ..clients.viacep_client import viacep_client

async def verify_cnpj_external(cnpj: str) -> Dict[str, Any]:
    """
    Verifica um CNPJ usando BrasilAPI com fallback para ReceitaWS.
    Retorna um dicionário padronizado.
    """
    try:
        logging.info(f"Tentando consultar CNPJ {cnpj} via BrasilAPI...")
        data = await brasilapi_client.consult_cnpj(cnpj)
        return {
            "source": "BrasilAPI",
            "valid": True,
            "company_name": data.get("razao_social"),
            "trade_name": data.get("nome_fantasia"),
            "situation": data.get("descricao_situacao_cadastral"),
            "opening_date": data.get("data_inicio_atividade"),
            "raw_data": data,
        }
    except Exception as e:
        logging.warning(f"Falha ao consultar BrasilAPI para CNPJ {cnpj}: {e}. Tentando fallback para ReceitaWS.")
        try:
            data = await receitaws_client.consult_cnpj(cnpj)
            return {
                "source": "ReceitaWS",
                "valid": True,
                "company_name": data.get("nome"),
                "trade_name": data.get("fantasia"),
                "situation": data.get("situacao"),
                "opening_date": data.get("abertura"),
                "raw_data": data,
            }
        except Exception as e2:
            logging.error(f"Falha ao consultar ReceitaWS para CNPJ {cnpj}: {e2}.")
            return {"valid": False, "error": f"Não foi possível validar o CNPJ em nenhuma das fontes: {e2}"}

async def verify_cep(cep: str) -> Dict[str, Any]:
    """Consulta um CEP usando ViaCEP e retorna o endereço."""
    try:
        data = await viacep_client.consult_cep(cep)
        return {
            "valid": True,
            "cep": data.get("cep"),
            "street": data.get("logradouro"),
            "neighborhood": data.get("bairro"),
            "city": data.get("localidade"),
            "state": data.get("uf"),
            "ibge": data.get("ibge"),
        }
    except Exception as e:
        logging.error(f"Falha ao consultar CEP {cep}: {e}")
        return {"valid": False, "error": str(e)}

async def check_bank(bank_code: str) -> Dict[str, Any]:
    """Verifica informações de um banco pelo código."""
    try:
        data = await brasilapi_client.get_bank_info(bank_code)
        return {
            "valid": True,
            "code": data.get("code"),
            "name": data.get("name"),
            "full_name": data.get("fullName"),
        }
    except Exception as e:
        logging.error(f"Falha ao consultar banco com código {bank_code}: {e}")
        return {"valid": False, "error": str(e)}
