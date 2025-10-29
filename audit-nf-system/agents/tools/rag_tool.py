# agents/tools/rag_tool.py
from langchain.tools import BaseTool
import logging
logger = logging.getLogger(__name__)

class RAGTool(BaseTool):
    """
    Implementação de contorno (Stub) para o RAGTool.
    Codigo real na pasta /rag apos pr de mcp e rag ser aprovado.
    Criar branch a partir de main: rag_integration
        - deletar este contorno
        - implementar consulta real ao sistema RAG
        - import da pasta /rag
    """
    name = "consult_rag"
    description = "Consulta a base de conhecimento RAG para legislação."

    def _run(self, query: str) -> str:
        logger.info(f"CONTORNO: RAGTool consultado com: '{query}'")
        return f"[CONTORNO RAG]: A regra para '{query}' é 18% de ICMS."

    async def _arun(self, query: str) -> str:
        return self._run(query)