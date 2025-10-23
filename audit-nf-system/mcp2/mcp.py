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

clients/brasilapi_client.py

# mcp/clients/brasilapi_client.py

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

# mcp/clients/receitaws_client.py

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

# mcp/tools/validation_tools.py

import re

def validate_cnpj_format(cnpj: str) -> bool:
    """Valida o formato de um CNPJ (14 dígitos)."""
    return bool(re.match(r'^\d{14}$', ''.join(filter(str.isdigit, cnpj))))

def validate_cnpj_digits(cnpj: str) -> bool:
    """Valida os dígitos verificadores de um CNPJ."""
    clean_cnpj = ''.join(filter(str.isdigit, cnpj))
    if len(clean_cnpj) != 14:
        return False

    def calculate_digit(digits: str, weights: list) -> int:
        s = sum(int(d) * w for d, w in zip(digits, weights))
        rest = s % 11
        return 0 if rest < 2 else 11 - rest

    # Validação do primeiro dígito
    weights1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    d1 = calculate_digit(clean_cnpj[:12], weights1)
    if d1 != int(clean_cnpj[12]):
        return False

    # Validação do segundo dígito
    weights2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    d2 = calculate_digit(clean_cnpj[:13], weights2)
    return d2 == int(clean_cnpj[13])

def validate_access_key_format(key: str) -> bool:
    """Valida o formato da chave de acesso da NF-e (44 dígitos)."""
    return bool(re.match(r'^\d{44}$', ''.join(filter(str.isdigit, key))))

def validate_access_key_digits(key: str) -> bool:
    """Valida o dígito verificador da chave de acesso da NF-e."""
    clean_key = ''.join(filter(str.isdigit, key))
    if len(clean_key) != 44:
        return False
        
    base_key = clean_key[:43]
    weights = [4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2] * 4
    s = sum(int(d) * w for d, w in zip(base_key, weights))
    rest = s % 11
    
    dv = 0 if rest in [0, 1] else 11 - rest
    return dv == int(clean_key[43])

def validate_cfop(cfop: str, operation_type: str) -> dict:
    """
    Valida um CFOP (Código Fiscal de Operações e Prestações).
    operation_type pode ser 'entrada' ou 'saida'.
    """
    cfop_str = str(cfop)
    if not re.match(r'^[1-7]\d{3}$', cfop_str):
        return {"valid": False, "reason": "Formato inválido. Deve ter 4 dígitos e começar com 1-7."}
    
    first_digit = cfop_str[0]
    is_valid = False
    
    if operation_type == 'entrada':
        if first_digit in ['1', '2', '3']:
            is_valid = True
    elif operation_type == 'saida':
        if first_digit in ['5', '6', '7']:
            is_valid = True
    else:
        return {"valid": False, "reason": f"Tipo de operação '{operation_type}' desconhecido."}

    if not is_valid:
        return {"valid": False, "reason": f"CFOP {cfop} incompatível com operação de '{operation_type}'."}

    # Lógica de validação simplificada (pode ser expandida com tabela de CFOPs)
    cfop_map = {
        '1': "Entrada / Aquisições do Estado",
        '2': "Entrada / Aquisições de Outro Estado",
        '3': "Entrada / Aquisições do Exterior",
        '5': "Saídas / Vendas para o Estado",
        '6': "Saídas / Vendas para Outro Estado",
        '7': "Saídas / Vendas para o Exterior",
    }
    
    return {
        "valid": True,
        "description": cfop_map.get(first_digit, "Descrição não encontrada"),
        "type": "Entrada" if first_digit in "123" else "Saída"
    }
	
# mcp/tools/calculation_tools.py

from typing import Dict, Union

# Tabelas simplificadas de alíquotas (exemplo)
ICMS_RATES = {
    "SP": 0.18, "RJ": 0.20, "MG": 0.18, "RS": 0.17,
    "SC": 0.17, "PR": 0.19, "BA": 0.19, "PE": 0.18,
    "DEFAULT": 0.17,
}

PIS_COFINS_RATES = {
    "cumulativo": {"pis": 0.0065, "cofins": 0.03},
    "nao_cumulativo": {"pis": 0.0165, "cofins": 0.076},
}

def calculate_icms(base_value: float, state_uf: str) -> Dict[str, float]:
    """Calcula o ICMS com base no valor e estado."""
    aliquota = ICMS_RATES.get(state_uf.upper(), ICMS_RATES["DEFAULT"])
    icms_value = base_value * aliquota
    return {
        "base_value": base_value,
        "state": state_uf.upper(),
        "aliquota": aliquota,
        "icms_value": round(icms_value, 2)
    }

def calculate_ipi(base_value: float, ncm: str) -> Dict[str, Union[float, str]]:
    """
    Calcula o IPI (Imposto sobre Produtos Industrializados).
    A lógica real depende de uma tabela TIPI complexa. Aqui, usamos um mock.
    """
    # Mock: alíquotas de IPI baseadas no NCM (exemplo simplificado)
    ipi_aliquota = 0.0
    if ncm.startswith("8703"): # Automóveis
        ipi_aliquota = 0.25
    elif ncm.startswith("2204"): # Vinhos
        ipi_aliquota = 0.10
    
    ipi_value = base_value * ipi_aliquota
    return {
        "base_value": base_value,
        "ncm": ncm,
        "aliquota": ipi_aliquota,
        "ipi_value": round(ipi_value, 2)
    }

def calculate_pis_cofins(base_value: float, regime: str) -> Dict[str, float]:
    """
    Calcula PIS e COFINS com base no regime tributário.
    Regime pode ser 'cumulativo' ou 'nao_cumulativo'.
    """
    regime_lower = regime.lower()
    if regime_lower not in PIS_COFINS_RATES:
        raise ValueError("Regime tributário inválido. Use 'cumulativo' ou 'nao_cumulativo'.")
        
    rates = PIS_COFINS_RATES[regime_lower]
    pis_value = base_value * rates["pis"]
    cofins_value = base_value * rates["cofins"]
    
    return {
        "base_value": base_value,
        "regime": regime,
        "pis_aliquota": rates["pis"],
        "cofins_aliquota": rates["cofins"],
        "pis_value": round(pis_value, 2),
        "cofins_value": round(cofins_value, 2),
        "total_pis_cofins": round(pis_value + cofins_value, 2)
    }

def apply_tax_reduction(value: float, reduction_percent: float) -> float:
    """Aplica uma redução percentual a um valor."""
    if not 0 <= reduction_percent <= 100:
        raise ValueError("A porcentagem de redução deve estar entre 0 e 100.")
    
    final_value = value * (1 - (reduction_percent / 100))
    return round(final_value, 2)

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

# mcp/resources/invoice_resource.py

import json
from mcp.types import Resource
from typing import List, Optional

# --- Mock do Banco de Dados de Notas Fiscais ---
MOCK_INVOICES_DB = {
    "1001": {
        "id": "1001", "numero": "123456", "serie": "1", "chave_acesso": "41241012345678000190550010001234561000000017",
        "cnpj_emitente": "12345678000190", "cnpj_destinatario": "98765432000110",
        "valor_total": 10000.00, "valor_icms": 1700.00, "status": "pendente_auditoria",
        "data_emissao": "2024-10-18"
    },
    "1002": {
        "id": "1002", "numero": "789012", "serie": "1", "chave_acesso": "35241098765432000110550010007890121000000025",
        "cnpj_emitente": "98765432000110", "cnpj_destinatario": "12345678000190",
        "valor_total": 2500.50, "valor_icms": 425.09, "status": "auditada_ok",
        "data_emissao": "2024-10-19"
    },
    "1003": {
        "id": "1003", "numero": "345678", "serie": "2", "chave_acesso": "52241011223344000155550020003456781000000033",
        "cnpj_emitente": "11223344000155", "cnpj_destinatario": "12345678000190",
        "valor_total": 500.00, "valor_icms": 85.00, "status": "pendente_auditoria",
        "data_emissao": "2024-10-20"
    },
}

async def get_invoice(invoice_id: str) -> Optional[Resource]:
    """Busca uma NF pelo ID e a retorna como um MCP Resource."""
    invoice_data = MOCK_INVOICES_DB.get(invoice_id)
    if not invoice_data:
        return None
        
    return Resource(
        uri=f"nf://invoice/{invoice_id}",
        name=f"Nota Fiscal {invoice_data['numero']}/{invoice_data['serie']}",
        mimeType="application/json",
        text=json.dumps(invoice_data, indent=2)
    )

async def list_invoices(status: Optional[str] = None, limit: int = 10) -> Resource:
    """Lista NFs, com filtro opcional por status, e retorna como um MCP Resource."""
    if status:
        filtered_invoices = [
            inv for inv in MOCK_INVOICES_DB.values() if inv["status"] == status
        ]
    else:
        filtered_invoices = list(MOCK_INVOICES_DB.values())
        
    result = filtered_invoices[:limit]
    
    return Resource(
        uri="nf://invoices" + (f"?status={status}" if status else ""),
        name=f"Lista de Notas Fiscais" + (f" com status '{status}'" if status else ""),
        mimeType="application/json",
        text=json.dumps(result, indent=2)
    )

async def get_pending_audits() -> Resource:
    """Retorna um MCP Resource com todas as NFs pendentes de auditoria."""
    return await list_invoices(status="pendente_auditoria")

# Inicializando __init__.py nas pastas para que o Python as trate como pacotes
# mcp/resources/__init__.py (vazio)
# mcp/tools/__init__.py (vazio)
# mcp/clients/__init__.py (vazio)
# mcp/servers/__init__.py (vazio)		

# mcp/servers/nf_context_server.py

import logging
from mcp import server, ui
from mcp.types import Resource, Request, Response

from ..resources import invoice_resource

# Cria uma instância do servidor MCP com um nome único
nf_server = server.Server("nf_context_server")

@nf_server.resource("nf://invoices")
async def list_all_invoices(request: Request) -> Response:
    """Expõe a lista de todas as notas fiscais."""
    logging.info(f"Recebida requisição para o recurso: {request.uri}")
    resource = await invoice_resource.list_invoices()
    return server.create_resource_response(resource)

@nf_server.resource("nf://invoice/{invoice_id}")
async def get_single_invoice(request: Request, invoice_id: str) -> Response:
    """Expõe os dados de uma nota fiscal específica pelo seu ID."""
    logging.info(f"Recebida requisição para o recurso: {request.uri}")
    resource = await invoice_resource.get_invoice(invoice_id)
    if resource:
        return server.create_resource_response(resource)
    else:
        return server.create_error_response(
            code=404, message=f"Nota Fiscal com ID '{invoice_id}' não encontrada."
        )

@nf_server.resource("nf://invoices/pending")
async def list_pending_invoices(request: Request) -> Response:
    """Expõe a lista de notas fiscais com auditoria pendente."""
    logging.info(f"Recebida requisição para o recurso: {request.uri}")
    resource = await invoice_resource.get_pending_audits()
    return server.create_resource_response(resource)
	
# mcp/servers/audit_server.py

import logging
from mcp import server, ui
from mcp.types import Request, Response, Tool
from pydantic import BaseModel, Field

from ..tools import calculation_tools, validation_tools, external_api_tools

# Cria uma instância do servidor MCP
audit_server = server.Server("audit_server")

# --- Schemas de Input/Output com Pydantic ---

class CnpjInput(BaseModel):
    cnpj: str = Field(..., description="CNPJ a ser validado, com ou sem formatação.")

class AccessKeyInput(BaseModel):
    access_key: str = Field(..., description="Chave de acesso da NF-e com 44 dígitos.")

class CfopInput(BaseModel):
    cfop: str = Field(..., description="Código Fiscal de Operações e Prestações (4 dígitos).")
    operation_type: str = Field(..., description="Tipo de operação ('entrada' ou 'saida').")

class IcmsInput(BaseModel):
    base_value: float = Field(..., description="Valor base para o cálculo do ICMS.")
    state_uf: str = Field(..., description="Sigla do estado (UF) para buscar a alíquota.")

class PisCofinsInput(BaseModel):
    base_value: float = Field(..., description="Valor base para o cálculo.")
    regime: str = Field(..., description="Regime tributário ('cumulativo' ou 'nao_cumulativo').")

# --- Definição das Ferramentas ---

@audit_server.tool()
async def verify_access_key(request: Request, p: AccessKeyInput) -> Response:
    """
    Valida o formato e o dígito verificador da chave de acesso de uma NF-e.
    """
    key = p.access_key
    is_format_valid = validation_tools.validate_access_key_format(key)
    if not is_format_valid:
        return server.create_json_response({"valid": False, "reason": "Formato inválido (deve ter 44 dígitos)."})

    are_digits_valid = validation_tools.validate_access_key_digits(key)
    return server.create_json_response({
        "valid": are_digits_valid,
        "reason": "Dígito verificador válido." if are_digits_valid else "Dígito verificador inválido."
    })

@audit_server.tool()
async def validate_cnpj(request: Request, p: CnpjInput) -> Response:
    """
    Valida o formato, dígitos e consulta a situação de um CNPJ em APIs externas.
    """
    cnpj = p.cnpj
    is_format_valid = validation_tools.validate_cnpj_format(cnpj)
    if not is_format_valid:
        return server.create_json_response({"valid": False, "reason": "Formato inválido (deve ter 14 dígitos)."})
    
    are_digits_valid = validation_tools.validate_cnpj_digits(cnpj)
    if not are_digits_valid:
        return server.create_json_response({"valid": False, "reason": "Dígitos verificadores inválidos."})

    # Consulta externa
    result = await external_api_tools.verify_cnpj_external(cnpj)
    return server.create_json_response(result)

@audit_server.tool()
async def check_cfop(request: Request, p: CfopInput) -> Response:
    """Verifica a validade e a natureza de um código CFOP."""
    result = validation_tools.validate_cfop(p.cfop, p.operation_type)
    return server.create_json_response(result)

@audit_server.tool()
async def calculate_icms(request: Request, p: IcmsInput) -> Response:
    """Calcula o valor do ICMS com base no estado."""
    result = calculation_tools.calculate_icms(p.base_value, p.state_uf)
    return server.create_json_response(result)

@audit_server.tool()
async def calculate_pis_cofins(request: Request, p: PisCofinsInput) -> Response:
    """Calcula PIS/COFINS com base no regime tributário."""
    try:
        result = calculation_tools.calculate_pis_cofins(p.base_value, p.regime)
        return server.create_json_response(result)
    except ValueError as e:
        return server.create_error_response(code=400, message=str(e))

@audit_server.tool()
async def check_supplier_history(request: Request, p: CnpjInput) -> Response:
    """
    Verifica o histórico de um fornecedor (mock).
    Em um sistema real, consultaria um DB interno de NFs e reputação.
    """
    # Mock
    history = {
        "cnpj": p.cnpj,
        "total_invoices": 15,
        "last_invoice_date": "2024-10-19",
        "average_value": 5780.23,
        "issues_found": 1,
        "status": "Confiável com observações"
    }
    return server.create_json_response(history)

# mcp/main.py

import asyncio
import logging
from mcp.main import main as mcp_main

# Importa as instâncias dos servidores
from servers.nf_context_server import nf_server
from servers.audit_server import audit_server

# Configura o logging básico para a aplicação
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Lista de todos os servidores MCP que serão executados
# O MCP se encarregará de gerenciá-los
ALL_SERVERS = [
    nf_server,
    audit_server,
]

async def run_servers():
    """
    Função principal que registra e inicia os servidores MCP.
    """
    logging.info("Iniciando a aplicação de Servidores MCP para Auditoria Fiscal...")
    logging.info(f"Registrando {len(ALL_SERVERS)} servidor(es): {[s.name for s in ALL_SERVERS]}")
    
    # mcp_main é o entry point do framework MCP que gerencia os servidores
    await mcp_main(ALL_SERVERS)

if __name__ == "__main__":
    try:
        asyncio.run(run_servers())
    except KeyboardInterrupt:
        logging.info("Servidores MCP desligados.")

Entendido. Agradeço por pedir esclarecimentos. Peço desculpas se a estrutura pareceu diferente à primeira vista. A intenção foi seguir exatamente o que você pediu, mas organizando o código de uma maneira mais modular e escalável, que é uma prática recomendada para projetos reais e que o framework MCP incentiva.Vamos detalhar ponto a ponto para mostrar como a implementação corresponde diretamente à sua solicitação e explicar o porquê de cada decisão de design.A principal "diferença" que você pode ter notado é a separação de responsabilidades:Lógica Pura (tools/, resources/, clients/): Contém as funções Python que fazem o trabalho pesado (cálculos, validações, chamadas de API). Elas não sabem nada sobre o MCP. Isso as torna fáceis de testar e reutilizar.Camada MCP (servers/): Atua como um "controlador". A única responsabilidade desses arquivos é usar os decoradores @server.tool e @server.resource para expor a lógica pura (do passo 1) para os agentes de IA. Eles recebem a requisição do modelo, chamam a função de lógica correspondente e formatam a resposta para o protocolo MCP.Essa abordagem segue 100% dos seus requisitos, mas evita colocar lógica de negócio complexa diretamente dentro das funções de servidor, mantendo o código mais limpo.Mapeando Sua Solicitação Para a ImplementaçãoVejamos como cada um dos seus pedidos foi atendido.1. Servidor de Ferramentas (servers/audit_server.py)Seu Exemplo:Python@server.tool("validate_cnpj")
async def validate_cnpj(cnpj: str) -> dict:
    # ... toda a lógica de limpeza, validação e chamada httpx aqui ...
Minha Implementação:Python# mcp/servers/audit_server.py

# 1. Define o schema de entrada com Pydantic (Requisito Técnico)
class CnpjInput(BaseModel):
    cnpj: str = Field(..., description="CNPJ a ser validado...")

# 2. Expõe a ferramenta para o MCP com o decorator @server.tool
@audit_server.tool()
async def validate_cnpj(request: Request, p: CnpjInput) -> Response:
    # 3. Chama a lógica de validação pura
    is_format_valid = validation_tools.validate_cnpj_format(p.cnpj)
    # ...
    
    # 4. Chama a lógica de API externa (com fallback)
    result = await external_api_tools.verify_cnpj_external(p.cnpj)
    
    # 5. Retorna a resposta no formato MCP
    return server.create_json_response(result)
Justificativa:Atende ao Requisito: A ferramenta validate_cnpj foi criada e exposta.Usa Pydantic: A entrada é validada automaticamente pelo MCP usando p: CnpjInput, conforme seu requisito de usar Pydantic.É Modular: Em vez de colocar 20-30 linhas de código de validação e chamadas de API aqui, delegamos para as funções em validation_tools.py e external_api_tools.py. Isso torna o servidor audit_server.py legível e focado apenas em expor as ferramentas.2. Servidor de Recursos (servers/nf_context_server.py)Seu Exemplo:Python@server.resource("nf://invoice/{invoice_id}")
async def get_invoice(invoice_id: str) -> Resource:
    # ... mock de dados aqui ...
    return Resource(...)
Minha Implementação:Python# mcp/servers/nf_context_server.py

# 1. Expõe o recurso para o MCP com o decorator @server.resource
@nf_server.resource("nf://invoice/{invoice_id}")
async def get_single_invoice(request: Request, invoice_id: str) -> Response:
    # 2. Chama a lógica de busca de dados (que contém o mock)
    resource = await invoice_resource.get_invoice(invoice_id)
    
    # 3. Lida com o caso de não encontrar e retorna a resposta no formato MCP
    if resource:
        return server.create_resource_response(resource)
    else:
        return server.create_error_response(...)
Justificativa:Atende ao Requisito: O recurso nf://invoice/{invoice_id} foi criado e exposto.É Modular: A lógica de como obter e formatar os dados da nota fiscal está isolada em resources/invoice_resource.py. Se amanhã você decidir buscar os dados de um banco de dados real em vez de um mock, você só precisará alterar invoice_resource.py, e o servidor nf_context_server.py continuará funcionando sem nenhuma modificação.3. Lógica de Ferramentas (Ex: tools/validation_tools.py)Você pediu funções de validação com lógica real, como validate_cnpj_digits.Minha Implementação:Python# mcp/tools/validation_tools.py

def validate_cnpj_digits(cnpj: str) -> bool:
    """Valida os dígitos verificadores de um CNPJ."""
    clean_cnpj = ''.join(filter(str.isdigit, cnpj))
    # ... implementação completa do algoritmo de validação do CNPJ ...
    return d2 == int(clean_cnpj[13])
Justificativa:Atende ao Requisito: A lógica de validação real foi implementada exatamente como solicitado e colocada no arquivo apropriado. Ela é uma função Python pura, independente do MCP.4. Clientes de API (clients/brasilapi_client.py)Você pediu um cliente com httpx, retries, cache e timeout.Minha Implementação:Python# mcp/clients/brasilapi_client.py

# Usa cachetools conforme solicitado
api_cache = TTLCache(maxsize=cache_settings.DEFAULT_MAX_SIZE, ttl=cache_settings.DEFAULT_TTL)

class BrasilAPIClient:
    async def _make_request(self, endpoint: str) -> Dict[str, Any]:
        # Lógica de cache
        if cache_key in api_cache:
            return api_cache[cache_key]
        
        # Lógica de retry (loop)
        for attempt in range(self.retries):
            try:
                # Usa httpx com timeout
                async with httpx.AsyncClient() as client:
                    response = await client.get(url, timeout=self.timeout)
                    # ...
                    return data
            except httpx.RequestError as e:
                # Trata erro e tenta novamente
                ...
Justificativa:Atende ao Requisito: A classe BrasilAPIClient implementa todos os requisitos técnicos: httpx, um loop para retries, cachetools para cache, e o timeout configurado em config.py.ResumoA implementação fornecida é a que você pediu, mas com uma arquitetura mais profissional e robusta. A estrutura que você projetou (servers/, tools/, resources/, etc.) sugere essa separação de responsabilidades. Minha implementação simplesmente preencheu essa estrutura seguindo as melhores práticas.Seu RequisitoOnde foi Implementado na Minha EstruturaDefinição dos servidores MCP (main.py)main.pyExposição de Recursos (@server.resource)servers/nf_context_server.pyExposição de Ferramentas (@server.tool)servers/audit_server.pyLógica de validação (ex: validate_cfop)tools/validation_tools.pyLógica de cálculo (ex: calculate_icms)tools/calculation_tools.pyLógica de API com fallback (ex: verify_cnpj_external)tools/external_api_tools.pyLógica de acesso a dados (ex: get_invoice)resources/invoice_resource.pyClientes HTTP (httpx, cache, retry)clients/brasilapi_client.py (e os outros)Configurações centralizadasconfig.pyDependênciasrequirements.txtEspero que esta explicação detalhada esclareça a estrutura e demonstre como ela atende fielmente à sua solicitação, ao mesmo tempo que adota práticas recomendadas para um projeto robusto.Se algum ponto ainda parecer obscuro ou se você preferir uma abordagem diferente (como colocar toda a lógica dentro dos arquivos de servidor), por favor, me diga!		
