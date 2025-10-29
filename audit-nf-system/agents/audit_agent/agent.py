# agents/audit_agent/agent.py

import logging
from typing import List, Dict, Any

from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import BaseTool
from ..utils.llm_factory import create_llm_with_fallback
from ..tools.rag_tool import RAGTool
from ..tools.calculator_tool import TaxCalculatorTool
from ..tools.mcp_tools import ValidateCNPJTool, CheckSupplierHistoryTool
from ..config import settings
from .prompts import AUDIT_PROMPT_TEMPLATE
from .rules_engine import run_financial_rules # Importa a função de regras de validacao triplice

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

        Passos:
            1. Realiza verificacao de regras deterministicas (Validação Tríplice) antes de enviar a llm.
            2. Se a regra falhar, retorna o resultado imediatamente.
            3. Se a regra passar, invoca o agente LLM para auditoria avançada.

        Args:
            invoice_data: Um dicionário contendo os dados da nota fiscal.

        Returns:
            Um dicionário com o resultado da auditoria no formato JSON.
        """
        # 1. Executa as regras financeiras determinísticas (Validação Tríplice)
        financial_check = run_financial_rules(invoice_data)
        if not financial_check["passed"]:
            logger.warning("Auditoria falhou na regra determinística: Validação Tríplice.")
            return {
                "aprovada": False,
                "irregularidades": [financial_check["message"]],
                "confianca": 1.0, # 100% de confiança, pois é uma regra
                "justificativa": "Falha na validação financeira determinística (Validação Tríplice). O agente LLM não foi invocado."
            }

        # 2. Se passou nas regras, invoca o agente LLM para auditoria avançada
        input_data = f"""
        Audite a seguinte nota fiscal.

        [INFORMAÇÃO IMPORTANTE]: A nota já passou na Validação Tríplice (financeira) com a seguinte mensagem: {financial_check['message']}.
        Concentre-se em outras irregularidades (fiscais, cadastrais, etc.).

        Dados da Nota:
        - Número: {invoice_data.get('Numero')}
        - Chave de Acesso: {invoice_data.get('ChaveAcesso')}
        - CNPJ Emitente: {invoice_data.get('Emitente_CNPJCPF')}
        - CNPJ Destinatário: {invoice_data.get('Destinatario_CNPJCPF')}
        - Valor Total Declarado: {invoice_data.get('ValorTotalNota')}
        - Impostos (resumo): 
            - ICMS: {invoice_data.get('ValorICMS')}
            - IPI: {invoice_data.get('ValorIPI')}
            - PIS: {invoice_data.get('ValorPIS')}
            - COFINS: {invoice_data.get('ValorCOFINS')}
        
        - Itens da Nota (para análise fiscal):
        {invoice_data.get('items', 'Nenhum item listado.')}
        """

        logger.info("Regra determinística (Validação Tríplice) APROVADA.\nInvocando agente LLM...")

        # 3. Invoca o agente llm
        try:            
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