# MUDANÇA 1: O caminho do arquivo agora é 'audit_servers/audit_server.py'
# (Assumindo que você renomeou a pasta 'mcp' para 'audit_servers')

import logging
# MUDANÇA 2: Importamos FastMCP da biblioteca 'mcp' instalada
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field
from typing import Optional
import json

# MUDANÇA (Corrigido): Importações absolutas de dentro do pacote mcp_module
from mcp.tools import calculation_tools, validation_tools, external_api_tools
from mcp.clients.rag_client import rag_client

# Configuração do logging (mantido)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# MUDANÇA 4: Instanciamos o FastMCP com um nome e descrição.
audit_server = FastMCP(
    "AuditServer",
    "Servidor de ferramentas para auditoria fiscal e consulta de NF-e."
)

# ============================================================================
# SCHEMAS DE INPUT/OUTPUT COM PYDANTIC
# (Mantidos exatamente como estavam. Perfeito!)
# ============================================================================

class FiscalQueryInput(BaseModel):
    query: str = Field(description="Pergunta sobre legislação fiscal")
    k: int = Field(default=3, ge=1, le=10)
    state: Optional[str] = Field(default=None)
    tax_type: Optional[str] = Field(default=None)

class CnpjInput(BaseModel):
    cnpj: str = Field(description="CNPJ a validar")

class AccessKeyInput(BaseModel):
    access_key: str = Field(description="Chave de acesso da NF-e com 44 dígitos")

class CfopInput(BaseModel):
    cfop: str = Field(description="Código Fiscal de Operações e Prestações (4 dígitos)")
    operation_type: str = Field(description="Tipo de operação ('entrada' ou 'saida')")

class IcmsInput(BaseModel):
    base_value: float = Field(description="Valor base para o cálculo do ICMS", gt=0)
    state_uf: str = Field(description="Sigla do estado (UF) para buscar a alíquota")

class IpiInput(BaseModel):
    base_value: float = Field(description="Valor base para o cálculo do IPI", gt=0)
    ncm: str = Field(description="Código NCM do produto (8 dígitos)")

class PisCofinsInput(BaseModel):
    base_value: float = Field(description="Valor base para o cálculo", gt=0)
    regime: str = Field(description="Regime tributário ('cumulativo' ou 'nao_cumulativo')")

class CepInput(BaseModel):
    cep: str = Field(description="CEP a ser consultado, com ou sem formatação")

class BankInput(BaseModel):
    bank_code: str = Field(description="Código do banco (3 dígitos)")

class TaxReductionInput(BaseModel):
    value: float = Field(description="Valor original", gt=0)
    reduction_percent: float = Field(description="Percentual de redução (0-100)", ge=0, le=100)

class SupplierHistoryInput(BaseModel):
    """Schema para o histórico de fornecedor (faltava este)"""
    cnpj: str = Field(description="CNPJ do fornecedor")


# ============================================================================
# MUDANÇA 5: O 'HANDLER CENTRAL' FOI REMOVIDO.
# ============================================================================

# ============================================================================
# MUDANÇA 6: A 'LISTA DE FERRAMENTAS' MANUAL FOI REMOVIDA.
# O FastMCP gera isso automaticamente a partir dos decoradores abaixo.
# ============================================================================


# ============================================================================
# IMPLEMENTAÇÕES DAS FERRAMENTAS
# MUDANÇA 7: Cada função é agora uma ferramenta pública com o decorador
# @audit_server.tool(). A 'docstring' é a nova 'description'.
# ============================================================================

@audit_server.tool()
async def consult_fiscal_regulation(p: FiscalQueryInput) -> dict:
    """
    Consulta base de conhecimento RAG sobre legislação fiscal.
    """
    logger.info(f"📚 RAG: {p.query}")
    result = await rag_client.search(
        query=p.query,
        k=p.k,
        state=p.state,
        tax_type=p.tax_type
    )
    # MUDANÇA 8: Apenas retorne o dicionário/objeto. O MCP cuida do resto.
    return result

@audit_server.tool()
async def validate_cnpj(p: CnpjInput) -> dict:
    """
    Valida CNPJ e consulta na Receita Federal.
    """
    logger.info(f"🔍 CNPJ: {p.cnpj}")
    
    if not validation_tools.validate_cnpj_format(p.cnpj):
        result = {"valid": False, "reason": "Formato inválido"}
    elif not validation_tools.validate_cnpj_digits(p.cnpj):
        result = {"valid": False, "reason": "Dígitos inválidos"}
    else:
        result = await external_api_tools.verify_cnpj_external(p.cnpj)
    
    return result

@audit_server.tool()
async def verify_access_key(p: AccessKeyInput) -> dict:
    """
    Valida chave de acesso de NF-e (formato e dígito verificador).
    """
    # MUDANÇA 9: Usamos o Pydantic model 'p' para validação e clareza.
    from ..tools.validation_tools import validate_access_key_format, validate_access_key_digits
    
    key = p.access_key
    logger.info(f"🔑 Chave: {key[:10]}...")
    
    if not validate_access_key_format(key):
        result = {"valid": False, "reason": "Formato inválido"}
    elif not validate_access_key_digits(key):
        result = {"valid": False, "reason": "Dígito verificador inválido"}
    else:
        result = {"valid": True, "uf": key[:2]}
    
    return result

@audit_server.tool()
async def check_cfop(p: CfopInput) -> dict:
    """
    Verifica validade de código CFOP para um tipo de operação (entrada/saída).
    """
    result = validation_tools.validate_cfop(p.cfop, p.operation_type)
    return result

@audit_server.tool()
async def calculate_icms(p: IcmsInput) -> dict:
    """
    Calcula ICMS com base no valor e na alíquota do estado (UF).
    """
    result = calculation_tools.calculate_icms(p.base_value, p.state_uf)
    return result

@audit_server.tool()
async def calculate_ipi(p: IpiInput) -> dict:
    """
    Calcula IPI com base no valor e na alíquota do NCM.
    """
    result = calculation_tools.calculate_ipi(p.base_value, p.ncm)
    return result

@audit_server.tool()
async def calculate_pis_cofins(p: PisCofinsInput) -> dict:
    """
    Calcula PIS/COFINS com base no valor e no regime tributário (cumulativo/não-cumulativo).
    """
    result = calculation_tools.calculate_pis_cofins(p.base_value, p.regime)
    return result

@audit_server.tool()
async def verify_cep(p: CepInput) -> dict:
    """
    Consulta um CEP em uma API externa.
    """
    result = await external_api_tools.verify_cep(p.cep)
    return result

@audit_server.tool()
async def check_bank(p: BankInput) -> dict:
    """
    Consulta informações de um banco pelo seu código (3 dígitos).
    """
    result = await external_api_tools.check_bank(p.bank_code)
    return result

@audit_server.tool()
async def apply_tax_reduction(p: TaxReductionInput) -> dict:
    """
    Aplica uma redução percentual a um valor base (cálculo simples).
    """
    final_value = calculation_tools.apply_tax_reduction(p.value, p.reduction_percent)
    result = {"original_value": p.value, "reduction_percent": p.reduction_percent, "final_value": final_value}
    return result

@audit_server.tool()
async def check_supplier_history(p: SupplierHistoryInput) -> dict:
    """
    Verifica o histórico de um fornecedor (simulado).
    """
    # (Adicionei o 'p' e o 'SupplierHistoryInput' para consistência)
    result = {"cnpj": p.cnpj, "total_invoices": 15, "status": "Regular"}
    return result


logger.info("✅ Audit Server MCP (FastMCP) carregado")

# MUDANÇA 10: REMOVIDO o 'if __name__ == "__main__":'
# O 'main.py' é o único responsável por executar o servidor.