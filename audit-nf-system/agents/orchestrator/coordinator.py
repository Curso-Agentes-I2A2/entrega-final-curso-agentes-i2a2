"""
Agent Coordinator - Orquestrador de Agentes
Coordena o fluxo de trabalho entre ValidationAgent e AuditAgent
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from audit_agent.agent import AuditAgent
from validation_agent.agent import ValidationAgent
from config import settings

logger = logging.getLogger(__name__)


class AgentCoordinator:
    """
    Orquestrador que coordena múltiplos agentes
    
    Fluxo de trabalho:
    1. ValidationAgent: Valida estrutura e conformidade técnica
    2. Se válido → AuditAgent: Audita conformidade fiscal
    3. Consolida resultados e toma decisão final
    """
    
    def __init__(self):
        """
        Inicializa coordenador e agentes
        """
        logger.info("🎯 Inicializando Coordenador de Agentes...")
        
        # Inicializar agentes
        self.validation_agent = ValidationAgent() if settings.VALIDATION_AGENT_ENABLED else None
        self.audit_agent = AuditAgent() if settings.AUDIT_AGENT_ENABLED else None
        
        logger.info("✅ Coordenador inicializado com sucesso")
        logger.info(f"  ✓ ValidationAgent: {'Habilitado' if self.validation_agent else 'Desabilitado'}")
        logger.info(f"  ✓ AuditAgent: {'Habilitado' if self.audit_agent else 'Desabilitado'}")
    
    async def process_invoice(
        self,
        invoice_data: Dict[str, Any],
        xml_content: Optional[str] = None,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Processa nota fiscal através do pipeline completo
        
        Args:
            invoice_data: Dados da nota fiscal
            xml_content: XML da nota (opcional)
            context: Contexto adicional (histórico, etc)
        
        Returns:
            Dict com decisão final e detalhes
        """
        logger.info("=" * 70)
        logger.info("🚀 INICIANDO PROCESSAMENTO DE NOTA FISCAL")
        logger.info("=" * 70)
        
        start_time = datetime.utcnow()
        
        try:
            # ETAPA 1: Validação Estrutural
            validation_result = await self._validate(invoice_data, xml_content)
            
            # Se validação falhou, retornar imediatamente
            if not validation_result["valid"]:
                logger.warning("❌ Validação falhou - Processo interrompido")
                return self._build_final_result(
                    aprovada=False,
                    motivo="Validação estrutural falhou",
                    validation_result=validation_result,
                    audit_result=None,
                    start_time=start_time
                )
            
            logger.info("✅ Validação: APROVADA")
            
            # ETAPA 2: Auditoria Fiscal
            audit_result = await self._audit(invoice_data, context)
            
            # Determinar decisão final
            decisao_final = self._make_final_decision(validation_result, audit_result)
            
            # Construir resultado consolidado
            result = self._build_final_result(
                aprovada=decisao_final["aprovada"],
                motivo=decisao_final["motivo"],
                validation_result=validation_result,
                audit_result=audit_result,
                start_time=start_time
            )
            
            # Log final
            status = "✅ APROVADA" if result["aprovada"] else "❌ REPROVADA"
            logger.info("=" * 70)
            logger.info(f"🎯 DECISÃO FINAL: {status}")
            logger.info(f"   Confiança: {result.get('confianca', 0):.2%}")
            logger.info(f"   Irregularidades: {len(result.get('irregularidades', []))}")
            logger.info(f"   Tempo Total: {result['detalhes']['processing_time_seconds']}s")
            logger.info("=" * 70)
            
            return result
        
        except Exception as e:
            logger.error(f"❌ Erro crítico no processamento: {e}", exc_info=True)
            return self._build_error_result(str(e), start_time)
    
    async def _validate(
        self,
        invoice_data: Dict,
        xml_content: Optional[str]
    ) -> Dict[str, Any]:
        """
        Executa validação estrutural
        """
        logger.info("\n📋 ETAPA 1: VALIDAÇÃO ESTRUTURAL")
        logger.info("-" * 70)
        
        if not self.validation_agent:
            logger.warning("⚠️  ValidationAgent desabilitado - pulando validação")
            return {
                "valid": True,
                "errors": [],
                "warnings": ["ValidationAgent desabilitado"],
                "details": {"skipped": True}
            }
        
        return await self.validation_agent.validate_invoice(invoice_data, xml_content)
    
    async def _audit(
        self,
        invoice_data: Dict,
        context: Optional[Dict]
    ) -> Dict[str, Any]:
        """
        Executa auditoria fiscal
        """
        logger.info("\n🔍 ETAPA 2: AUDITORIA FISCAL")
        logger.info("-" * 70)
        
        if not self.audit_agent:
            logger.warning("⚠️  AuditAgent desabilitado - pulando auditoria")
            return {
                "aprovada": True,
                "irregularidades": [],
                "confianca": 1.0,
                "justificativa": "AuditAgent desabilitado",
                "detalhes": {"skipped": True}
            }
        
        return await self.audit_agent.audit_invoice(invoice_data, context)
    
    def _make_final_decision(
        self,
        validation_result: Dict,
        audit_result: Dict
    ) -> Dict[str, Any]:
        """
        Toma decisão final baseada em validação e auditoria
        """
        # Validação falhou
        if not validation_result.get("valid"):
            return {
                "aprovada": False,
                "motivo": "Falha na validação estrutural"
            }
        
        # Auditoria reprovou
        if not audit_result.get("aprovada"):
            return {
                "aprovada": False,
                "motivo": "Falha na auditoria fiscal"
            }
        
        # Verificar confiança
        confianca = audit_result.get("confianca", 0)
        threshold = settings.AUDIT_CONFIDENCE_THRESHOLD
        
        if confianca < threshold:
            return {
                "aprovada": False,
                "motivo": f"Confiança abaixo do threshold ({confianca:.2%} < {threshold:.2%})"
            }
        
        # Aprovado!
        return {
            "aprovada": True,
            "motivo": "Nota fiscal aprovada em validação e auditoria"
        }
    
    def _build_final_result(
        self,
        aprovada: bool,
        motivo: str,
        validation_result: Optional[Dict],
        audit_result: Optional[Dict],
        start_time: datetime
    ) -> Dict[str, Any]:
        """
        Constrói resultado final consolidado
        """
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        # Consolidar irregularidades
        irregularidades = []
        
        if validation_result and validation_result.get("errors"):
            irregularidades.extend([
                f"[VALIDAÇÃO] {error}"
                for error in validation_result["errors"]
            ])
        
        if audit_result and audit_result.get("irregularidades"):
            irregularidades.extend([
                f"[AUDITORIA] {irreg}"
                for irreg in audit_result["irregularidades"]
            ])
        
        # Determinar confiança
        if audit_result and "confianca" in audit_result:
            confianca = audit_result["confianca"]
        elif not aprovada:
            confianca = 0.0
        else:
            confianca = 0.9
        
        # Construir justificativa
        justificativa = self._build_justification(
            aprovada=aprovada,
            motivo=motivo,
            validation_result=validation_result,
            audit_result=audit_result
        )
        
        return {
            "aprovada": aprovada,
            "irregularidades": irregularidades,
            "confianca": round(confianca, 3),
            "justificativa": justificativa,
            "detalhes": {
                "validacao": {
                    "aprovada": validation_result.get("valid", False) if validation_result else None,
                    "erros": len(validation_result.get("errors", [])) if validation_result else 0,
                    "avisos": len(validation_result.get("warnings", [])) if validation_result else 0,
                },
                "auditoria": {
                    "aprovada": audit_result.get("aprovada", False) if audit_result else None,
                    "irregularidades": len(audit_result.get("irregularidades", [])) if audit_result else 0,
                    "confianca": audit_result.get("confianca") if audit_result else None,
                },
                "processing_time_seconds": round(processing_time, 2),
                "threshold_confianca": settings.AUDIT_CONFIDENCE_THRESHOLD,
            },
            "resultados_completos": {
                "validacao": validation_result,
                "auditoria": audit_result,
            },
            "timestamp": datetime.utcnow().isoformat(),
            "coordinator": "AgentCoordinator",
            "version": "1.0.0"
        }
    
    def _build_justification(
        self,
        aprovada: bool,
        motivo: str,
        validation_result: Optional[Dict],
        audit_result: Optional[Dict]
    ) -> str:
        """
        Constrói justificativa consolidada
        """
        if aprovada:
            base = "Nota fiscal APROVADA. "
            
            # Adicionar detalhes
            if validation_result and audit_result:
                avisos = len(validation_result.get("warnings", []))
                if avisos > 0:
                    base += f"Validação aprovada com {avisos} aviso(s). "
                else:
                    base += "Validação aprovada sem avisos. "
                
                base += audit_result.get("justificativa", "Auditoria aprovada.")
            else:
                base += motivo
            
            return base
        else:
            base = "Nota fiscal REPROVADA. "
            
            # Adicionar motivo
            base += motivo + ". "
            
            # Adicionar detalhes de validação
            if validation_result and not validation_result.get("valid"):
                erros = len(validation_result.get("errors", []))
                base += f"Encontrados {erros} erro(s) na validação estrutural. "
            
            # Adicionar detalhes de auditoria
            if audit_result and not audit_result.get("aprovada"):
                irreg = len(audit_result.get("irregularidades", []))
                base += f"Encontradas {irreg} irregularidade(s) na auditoria fiscal. "
            
            return base
    
    def _build_error_result(
        self,
        error_message: str,
        start_time: datetime
    ) -> Dict[str, Any]:
        """
        Constrói resultado de erro
        """
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        return {
            "aprovada": False,
            "irregularidades": [f"Erro no processamento: {error_message}"],
            "confianca": 0.0,
            "justificativa": "Processamento não pôde ser concluído devido a erro técnico",
            "error": error_message,
            "detalhes": {
                "processing_time_seconds": round(processing_time, 2),
                "error_type": "processing_error"
            },
            "timestamp": datetime.utcnow().isoformat(),
            "coordinator": "AgentCoordinator",
            "version": "1.0.0"
        }