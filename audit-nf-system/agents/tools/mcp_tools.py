# agents/tools/mcp_tools.py
from langchain.tools import BaseTool
import logging
logger = logging.getLogger(__name__)

class ValidateCNPJTool(BaseTool):
    """Implementação de contorno (Stub) para o ValidateCNPJTool.
    Codigo real na pasta /rag apos pr de mcp e rag ser aprovado.
    Criar branch a partir de main: rag_integration
        - deletar este contorno
        - implementar consulta real ao sistema RAG
        - import da pasta /rag"""
    name = "validate_cnpj"
    description = "Valida um CNPJ via serviço MCP."

    def _run(self, cnpj: str) -> str:
        logger.info(f"CONTORNO: ValidateCNPJTool consultado para: {cnpj}")
        return f"[CONTORNO MCP]: CNPJ {cnpj} está ATIVO."

    async def _arun(self, cnpj: str) -> str:
        return self._run(cnpj)

class CheckSupplierHistoryTool(BaseTool):
    """Implementação de contorno (Stub) para o CheckSupplierHistoryTool."""
    name = "check_supplier_history"
    description = "Verifica o histórico de um fornecedor via MCP."

    def _run(self, cnpj: str) -> str:
        logger.info(f"CONTORNO: CheckSupplierHistoryTool consultado para: {cnpj}")
        return f"[CONTORNO MCP]: Fornecedor {cnpj} tem 10 notas anteriores, 0 problemas."

    async def _arun(self, cnpj: str) -> str:
        return self._run(cnpj)