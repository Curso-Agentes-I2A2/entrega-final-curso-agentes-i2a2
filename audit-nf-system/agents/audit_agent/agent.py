# agents/audit_agent/agent.py

import logging
from typing import List, Dict, Any

from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import BaseTool

from ..tools.rag_tool import RAGTool
from ..tools.calculator_tool import TaxCalculatorTool
from ..tools.mcp_tools import ValidateCNPJTool, CheckSupplierHistoryTool
from ..config import settings
from .prompts import AUDIT_PROMPT_TEMPLATE
from ..utils.llm_factory import create_llm_with_fallback

# Configuração do logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AuditAgent:
    """
    Agente especializado na auditoria fiscal e de conformidade de notas fiscais.
    Utiliza o padrão ReAct para raciocinar e atuar, usando um conjunto de
    ferramentas para buscar informações, realizar cálculos e validações.
    """
    def __init__(self):
        self.llm = create_llm_with_fallback()
        self.tools: List[BaseTool] = self._setup_tools()
        self.prompt = PromptTemplate.from_template(AUDIT_PROMPT_TEMPLATE)
        
        # Cria o agente ReAct
        agent = create_react_agent(self.llm, self.tools, self.prompt)
        
        # Cria o executor do agente, que gerencia o loop de execução
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,  # Mostra os passos do agente no console (bom para debug)
            handle_parsing_errors=True, # Trata erros de parsing da saída do LLM
            max_iterations=10, # Evita loops infinitos
        )

    def _setup_tools(self) -> List[BaseTool]:
        """Inicializa e retorna a lista de ferramentas disponíveis para o agente."""
        return [
            RAGTool(),
            TaxCalculatorTool(),
            ValidateCNPJTool(),
            CheckSupplierHistoryTool(),
        ]

    async def audit_invoice(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executa a auditoria completa de uma nota fiscal.

        Args:
            invoice_data: Um dicionário contendo os dados da nota fiscal.

        Returns:
            Um dicionário com o resultado da auditoria no formato JSON.
        """
        logger.info(f"Iniciando auditoria para a nota fiscal: {invoice_data.get('numero')}")
        
        try:
            # A chave 'input' é padrão para o AgentExecutor
            input_data = {"invoice_data": str(invoice_data)}
            
            # Invoca o agente de forma assíncrona
            result = await self.agent_executor.ainvoke(input_data)
            
            # O resultado final do agente está na chave 'output'
            output = result.get("output", {})
            
            logger.info(f"Auditoria concluída. Resultado: {output}")
            return output

        except Exception as e:
            logger.error(f"Erro inesperado durante a auditoria: {e}", exc_info=True)
            return {
                "aprovada": False,
                "irregularidades": ["Erro interno no sistema de auditoria."],
                "confianca": 0.0,
                "justificativa": f"Ocorreu uma exceção: {str(e)}",
            }

# Exemplo de uso (para testes locais)
if __name__ == '__main__':
    import asyncio

    async def main():
        # Exemplo de NF-e para auditoria
        sample_invoice = {
            "numero": "98765",
            "serie": "1",
            "cnpj_emitente": "12.345.678/0001-99", # CNPJ fictício
            "cnpj_destinatario": "98.765.432/0001-11", # CNPJ fictício
            "data_emissao": "2025-10-23",
            "valor_total": 1500.00,
            "valor_produtos": 1500.00,
            "itens": [
                {
                    "codigo": "PROD001",
                    "descricao": "Componente Eletrônico XYZ",
                    "ncm": "85423190",
                    "cfop": "5102", # Venda de mercadoria adquirida ou recebida de terceiros
                    "quantidade": 10,
                    "valor_unitario": 150.00,
                    "valor_total": 1500.00
                }
            ],
            "impostos": {
                "base_calculo_icms": 1500.00,
                "valor_icms": 270.00, # 18% de 1500
                "valor_pis": 24.75, # 1.65% de 1500
                "valor_cofins": 114.00 # 7.6% de 1500
            },
            "xml_content": "<xml>...</xml>" # Conteúdo simplificado
        }

        auditor = AuditAgent()
        result = await auditor.audit_invoice(sample_invoice)
        print("\n--- Resultado Final da Auditoria ---")
        import json
        print(json.dumps(result, indent=2, ensure_ascii=False))

    asyncio.run(main())