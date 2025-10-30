import logging
import json
from mcp.server.fastmcp import FastMCP
from mcp_module.resources import invoice_resource

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

nf_server = FastMCP(
    "NFContextServer",
    "Servidor de contexto que expõe dados de Notas Fiscais (NFs)."
)

@nf_server.resource(
    uri="nf://invoices",
    name="Lista de Notas Fiscais",
    mime_type="application/json"
)
async def get_all_invoices() -> dict | list:
    """
    Retorna uma lista de todas as notas fiscais cadastradas no sistema.
    """
    logger.info(f"📖 Lendo recurso: nf://invoices")
 
    json_string = await invoice_resource.list_invoices()
    
    logger.info(f"✅ Retornando lista de NFs")
    return json.loads(json_string)

@nf_server.resource(
    uri="nf://invoices/pending",
    name="NFs Pendentes de Auditoria",
    mime_type="application/json"
)
async def get_pending_invoices() -> dict | list:
    """
    Retorna uma lista de notas fiscais que estão aguardando auditoria.
    """
    logger.info(f"📖 Lendo recurso: nf://invoices/pending")
    
    json_string = await invoice_resource.get_pending_audits()
    
    logger.info(f"✅ Retornando NFs pendentes")
    return json.loads(json_string)


@nf_server.resource(
    uri="nf://invoice/{invoice_id}",
    name="Nota Fiscal Individual",
    mime_type="application/json"
)
async def get_single_invoice(invoice_id: str) -> dict:
    """
    Retorna os dados completos de uma nota fiscal específica (substitua {id} pelo ID).
    O ID é extraído da URI.
    """
    logger.info(f"📖 Lendo recurso: nf://invoice/{invoice_id}")
    
    json_string = await invoice_resource.get_invoice(invoice_id)
    
    if json_string:
        logger.info(f"✅ NF {invoice_id} encontrada")
        return json.loads(json_string)
    else:
       
        logger.warning(f"❌ NF {invoice_id} não encontrada")
        raise ValueError(f"Nota Fiscal com ID '{invoice_id}' não encontrada")

logger.info("✅ NF Context Server (FastMCP) carregado")
logger.info("📚 3 recursos disponíveis (detectados automaticamente)")

