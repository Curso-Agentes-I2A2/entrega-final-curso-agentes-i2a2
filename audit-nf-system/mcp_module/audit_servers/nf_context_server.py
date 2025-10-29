
# import logging
# from mcp.server import Server
# import mcp.types as types
# import json
# from pydantic import AnyUrl

# from ..resources import invoice_resource

# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
# )

# # Cria instância do servidor MCP
# nf_server = Server("nf_context_server")

# # ============================================================================
# # LISTA DE RECURSOS
# # ============================================================================

# @nf_server.list_resources()
# async def list_resources() -> list[types.Resource]:
#     """Lista todos os recursos disponíveis."""
#     return [
#         types.Resource(
#             uri=AnyUrl("nf://invoices"),
#             name="Lista de Notas Fiscais",
#             mimeType="application/json",
#             description="Todas as notas fiscais cadastradas no sistema"
#         ),
#         types.Resource(
#             uri=AnyUrl("nf://invoices/pending"),
#             name="NFs Pendentes de Auditoria",
#             mimeType="application/json",
#             description="Notas fiscais aguardando auditoria"
#         ),
#         types.Resource(
#             uri=AnyUrl("nf://invoice/{id}"),
#             name="Nota Fiscal Individual",
#             mimeType="application/json",
#             description="Dados completos de uma nota fiscal específica (substitua {id} pelo ID)"
#         ),
#     ]

# # ============================================================================
# # LEITURA DE RECURSOS
# # ============================================================================

# @nf_server.read_resource()
# async def read_resource(uri:AnyUrl) -> str:
#     """
#     Lê o conteúdo de um recurso específico.
    
#     URIs suportadas:
#     - nf://invoices                  -> Lista todas as NFs
#     - nf://invoices/pending          -> Lista NFs pendentes
#     - nf://invoice/{id}              -> Detalhes de uma NF específica
#     """
#     try:
#         uri_str = str(uri)
#         logging.info(f"📖 Lendo recurso: {uri_str}")
        
#         # Lista todas as NFs
#         if uri_str == "nf://invoices":
#             result = await invoice_resource.list_invoices()
#             logging.info(f"✅ Retornando lista de NFs")
#             return result
        
#         # Lista NFs pendentes de auditoria
#         elif uri_str == "nf://invoices/pending":
#             result = await invoice_resource.get_pending_audits()
#             logging.info(f"✅ Retornando NFs pendentes")
#             return result
        
#         # Detalhes de uma NF específica
#         elif uri_str.startswith("nf://invoice/"):
#             invoice_id = uri_str.split("/")[-1]
#             result = await invoice_resource.get_invoice(invoice_id)
            
#             if result:
#                 logging.info(f"✅ NF {invoice_id} encontrada")
#                 return result
#             else:
#                 logging.warning(f"❌ NF {invoice_id} não encontrada")
#                 error_response = {
#                     "error": f"Nota Fiscal com ID '{invoice_id}' não encontrada",
#                     "uri": uri
#                 }
#                 return json.dumps(error_response, ensure_ascii=False)
        
#         # URI não reconhecida
#         else:
#             logging.error(f"❌ URI não reconhecida: {uri}")
#             error_response = {
#                 "error": f"Recurso não encontrado: {uri}",
#                 "available_uris": [
#                     "nf://invoices",
#                     "nf://invoices/pending",
#                     "nf://invoice/{id}"
#                 ]
#             }
#             return json.dumps(error_response, ensure_ascii=False)
            
#     except Exception as e:
#         logging.error(f"💥 Erro ao ler recurso {uri}: {e}", exc_info=True)
#         error_response = {
#             "error": str(e),
#             "uri": uri
#         }
#         return json.dumps(error_response, ensure_ascii=False)

# # ============================================================================
# # LOG FINAL
# # ============================================================================

# logging.info("✅ NF Context Server MCP inicializado")
# logging.info("📚 3 recursos disponíveis")

# MUDANÇA 1: O caminho do arquivo agora é 'audit_servers/nf_context_server.py'

import logging
import json
# MUDANÇA 2: Importamos FastMCP da biblioteca 'mcp' instalada
from mcp.server.fastmcp import FastMCP
# from mcp.model import Resource  # Usado para type hints

# MUDANÇA 3: A importação de 'invoice_resource' usa '..'
from mcp_module.resources import invoice_resource

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# MUDANÇA 4: Instanciamos o FastMCP com um nome e descrição.
nf_server = FastMCP(
    "NFContextServer",
    "Servidor de contexto que expõe dados de Notas Fiscais (NFs)."
)

# ============================================================================
# MUDANÇA 5: @list_resources E @read_resource FORAM REMOVIDOS.
# FastMCP agora lida com isso através dos decoradores @nf_server.resource()
# ============================================================================

# ============================================================================
# DEFINIÇÃO DOS RECURSOS
# ============================================================================

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
    
    # MUDANÇA 6: Assumindo que 'list_invoices' retorna um JSON string.
    # Nós o convertemos de volta para um dict/list para que o FastMCP
    # possa serializá-lo corretamente.
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
        # MUDANÇA 7: Em FastMCP, levantamos uma exceção para erros.
        # O servidor cuidará de formatar a resposta de erro MCP.
        logger.warning(f"❌ NF {invoice_id} não encontrada")
        raise ValueError(f"Nota Fiscal com ID '{invoice_id}' não encontrada")

# ============================================================================
# LOG FINAL
# ============================================================================

logger.info("✅ NF Context Server (FastMCP) carregado")
logger.info("📚 3 recursos disponíveis (detectados automaticamente)")

# MUDANÇA 8: REMOVIDO o 'if __name__ == "__main__":'
# O 'main.py' é o único responsável por executar o servidor.