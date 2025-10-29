# agents/orchestrator/coordinator.py

import logging
from typing import Dict, Any

from ..validation_agent.agent import ValidationAgent
from ..audit_agent.agent import AuditAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentCoordinator:
    """
    Orquestra o fluxo de trabalho entre os diferentes agentes
    para processar uma nota fiscal de ponta a ponta.
    """
    def __init__(self):
        self.validation_agent = ValidationAgent()
        self.audit_agent = AuditAgent()
        logger.info("AgentCoordinator inicializado com todos os agentes.")

    async def process_invoice(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa uma nota fiscal, coordenando os agentes de validação e auditoria.

        Fluxo:
        1. Executa o Agente de Validação para checagens estruturais.
        2. Se a validação falhar, encerra o processo e retorna o erro.
        3. Se a validação for aprovada, invoca o Agente de Auditoria para análise de conteúdo.
        4. Consolida os resultados e retorna uma decisão final.

        Args:
            invoice_data: Dicionário contendo os dados completos da NF-e.

        Returns:
            Dicionário com o resultado consolidado da análise.
        """
        logger.info(f"Iniciando processamento da NF: {invoice_data.get('numero')}")

        # Passo 1: Validação Estrutural
        validation_result = await self.validation_agent.validate_invoice(invoice_data)

        if validation_result["status"] == "REPROVADA":
            logger.warning(f"NF reprovada na fase de validação. Motivo: {validation_result['details']}")
            return {
                "aprovada": False,
                "fase": "validacao_estrutural",
                "irregularidades": [
                    f"Erro de validação: {error['message']}" 
                    for key, error in validation_result["details"].items() if not error.get('valid')
                ],
                "confianca": 1.0, # Confiança alta, pois é uma falha determinística
                "detalhes": validation_result
            }

        logger.info("Validação estrutural aprovada. Prosseguindo para a auditoria.")

        # Passo 2: Auditoria de Conteúdo
        audit_result = await self.audit_agent.audit_invoice(invoice_data)
        
        # Passo 3: Consolidação dos Resultados
        final_decision = {
            "aprovada": audit_result.get("aprovada", False),
            "fase": "auditoria_de_conteudo",
            "irregularidades": audit_result.get("irregularidades", ["Auditor não retornou irregularidades."]),
            "confianca": audit_result.get("confianca", 0.0),
            "justificativa": audit_result.get("justificativa", "Sem justificativa do auditor."),
            "detalhes": {
                "validacao": validation_result,
                "auditoria": audit_result
            }
        }
        
        logger.info(f"Processamento da NF concluído. Decisão final: {'Aprovada' if final_decision['aprovada'] else 'Reprovada'}")
        return final_decision