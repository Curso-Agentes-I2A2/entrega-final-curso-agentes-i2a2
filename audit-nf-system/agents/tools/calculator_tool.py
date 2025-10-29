# agents/tools/calculator_tool.py
from langchain.tools import BaseTool
import logging
logger = logging.getLogger(__name__)

class TaxCalculatorTool(BaseTool):
    """Implementação de contorno (Stub) para o TaxCalculatorTool.
    Codigo real na pasta /rag apos pr de mcp e rag ser aprovado.
    Criar branch a partir de main: rag_integration
        - deletar este contorno
        - implementar consulta real ao sistema RAG
        - import da pasta /rag"""
    name = "calculate_taxes"
    description = "Calcula impostos complexos (ICMS-ST, etc)."

    def _run(self, nota_info: str) -> str:
        logger.info(f"CONTORNO: TaxCalculatorTool chamado.")
        return "[CONTORNO CALC]: Cálculo de impostos mockado: R$ 123,45."

    async def _arun(self, nota_info: str) -> str:
        return self._run(nota_info)