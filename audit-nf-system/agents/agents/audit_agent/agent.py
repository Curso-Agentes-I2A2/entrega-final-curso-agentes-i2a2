"""
Agente de Auditoria de NF-e
Responsável por analisar notas fiscais e identificar irregularidades
"""

import logging
import json
from typing import Dict, List, Optional, Any
from datetime import datetime

from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from config import settings, AUDIT_AGENT_CONFIG
from audit_agent.prompts import SYSTEM_PROMPT, AUDIT_TEMPLATE
from audit_agent.rules_engine import RulesEngine
from tools.calculator_tool import TaxCalculatorTool

logger = logging.getLogger(__name__)


class AuditAgent:
    """
    Agente especializado em auditoria fiscal de Notas Fiscais Eletrônicas
    
    Responsabilidades:
    - Validar cálculo de impostos (ICMS, IPI, PIS, COFINS)
    - Verificar conformidade com legislação brasileira
    - Identificar inconsistências e fraudes
    - Consultar base de conhecimento (RAG) quando necessário
    - Gerar relatório detalhado de auditoria
    """
    
    def __init__(self):
        """
        Inicializa o agente de auditoria
        """
        logger.info("🔍 Inicializando Agente de Auditoria...")
        
        # Configurar LLM primário (Claude)
        self.llm = self._setup_llm()
        
        # Fallback LLM (GPT-4)
        self.fallback_llm = self._setup_fallback_llm() if settings.OPENAI_API_KEY else None
        
        # Motor de regras fiscais
        self.rules_engine = RulesEngine()
        
        # Tools disponíveis para o agente
        self.tools = self._setup_tools()
        
        # Criar agente LangChain
        self.agent = self._create_agent()
        
        # Executor do agente
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=settings.DEBUG,
            max_iterations=10,
            max_execution_time=settings.API_TIMEOUT,
            return_intermediate_steps=True,
        )
        
        logger.info("✅ Agente de Auditoria inicializado")
    
    def _setup_llm(self) -> ChatAnthropic:
        """
        Configura o LLM principal (Claude)
        """
        return ChatAnthropic(
            model=AUDIT_AGENT_CONFIG["model"],
            temperature=AUDIT_AGENT_CONFIG["temperature"],
            max_tokens=AUDIT_AGENT_CONFIG["max_tokens"],
            anthropic_api_key=settings.ANTHROPIC_API_KEY,
            timeout=settings.API_TIMEOUT,
        )
    
    def _setup_fallback_llm(self) -> Optional[ChatOpenAI]:
        """
        Configura LLM de fallback (GPT-4)
        """
        if not settings.OPENAI_API_KEY:
            return None
        
        return ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=settings.OPENAI_TEMPERATURE,
            max_tokens=settings.OPENAI_MAX_TOKENS,
            openai_api_key=settings.OPENAI_API_KEY,
            timeout=settings.API_TIMEOUT,
        )
    
    def _setup_tools(self) -> List:
        """
        Configura ferramentas disponíveis para o agente
        """
        tools = []
        
        # Tool de cálculo de impostos
        tools.append(TaxCalculatorTool())
        logger.info("  ✓ Tax Calculator Tool habilitada")
        
        # Adicionar mais tools conforme necessário
        
        return tools
    
    def _create_agent(self):
        """
        Cria o agente LangChain com prompt e tools
        """
        # Criar prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("human", AUDIT_TEMPLATE),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        # Criar agente
        agent = create_openai_tools_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        return agent
    
    async def audit_invoice(
        self,
        invoice_data: Dict[str, Any],
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Audita uma nota fiscal
        
        Args:
            invoice_data: Dados da nota fiscal
            context: Contexto adicional (histórico do fornecedor, etc)
        
        Returns:
            Dict com resultado da auditoria:
            {
                "aprovada": bool,
                "irregularidades": List[str],
                "confianca": float,
                "justificativa": str,
                "detalhes": {...},
                "timestamp": str
            }
        """
        logger.info(f"🔍 Iniciando auditoria da NF {invoice_data.get('numero', 'N/A')}")
        
        start_time = datetime.utcnow()
        
        try:
            # 1. Validações rápidas com motor de regras
            rule_violations = await self._apply_rules(invoice_data)
            
            # 2. Se houver violações críticas, rejeitar imediatamente
            critical_violations = [v for v in rule_violations if v.get("severity") == "critical"]
            
            if critical_violations and settings.VALIDATION_STRICT_MODE:
                logger.warning(f"⚠️ Violações críticas encontradas: {len(critical_violations)}")
                return self._build_rejection_response(critical_violations, invoice_data)
            
            # 3. Análise profunda com LLM
            llm_analysis = await self._analyze_with_llm(invoice_data, context, rule_violations)
            
            # 4. Consolidar resultado
            result = self._consolidate_results(
                invoice_data=invoice_data,
                rule_violations=rule_violations,
                llm_analysis=llm_analysis,
                start_time=start_time
            )
            
            # Log resultado
            status = "✅ APROVADA" if result["aprovada"] else "❌ REPROVADA"
            logger.info(
                f"{status} - NF {invoice_data.get('numero')} - "
                f"Confiança: {result['confianca']:.2%} - "
                f"Irregularidades: {len(result['irregularidades'])}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Erro na auditoria: {e}", exc_info=True)
            
            # Tentar com fallback LLM
            if self.fallback_llm:
                logger.info("🔄 Tentando com LLM de fallback...")
                try:
                    return await self._audit_with_fallback(invoice_data, context)
                except Exception as fallback_error:
                    logger.error(f"❌ Fallback também falhou: {fallback_error}")
            
            # Retornar erro estruturado
            return {
                "aprovada": False,
                "irregularidades": [f"Erro no processamento: {str(e)}"],
                "confianca": 0.0,
                "justificativa": "Auditoria não pôde ser concluída devido a erro técnico",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _apply_rules(self, invoice_data: Dict) -> List[Dict]:
        """
        Aplica regras do motor de regras
        """
        violations = []
        
        # Validar ICMS
        icms_errors = self.rules_engine.check_icms(invoice_data)
        violations.extend([
            {
                "type": "ICMS",
                "message": error,
                "severity": "critical" if "incorreto" in error.lower() else "medium"
            }
            for error in icms_errors
        ])
        
        # Validar CFOP
        cfop = invoice_data.get("cfop", "")
        operation = invoice_data.get("tipo_operacao", "venda")
        
        if not self.rules_engine.check_cfop(cfop, operation):
            violations.append({
                "type": "CFOP",
                "message": f"CFOP {cfop} incompatível com operação {operation}",
                "severity": "critical"
            })
        
        # Validar consistência de valores
        value_errors = self.rules_engine.check_value_consistency(invoice_data)
        violations.extend([
            {
                "type": "VALOR",
                "message": error,
                "severity": "medium"
            }
            for error in value_errors
        ])
        
        return violations
    
    async def _analyze_with_llm(
        self,
        invoice_data: Dict,
        context: Optional[Dict],
        rule_violations: List[Dict]
    ) -> Dict:
        """
        Análise profunda com LLM
        """
        # Preparar input para o agente
        input_data = {
            "invoice": json.dumps(invoice_data, indent=2, ensure_ascii=False),
            "context": json.dumps(context or {}, indent=2, ensure_ascii=False),
            "rule_violations": json.dumps(rule_violations, indent=2, ensure_ascii=False),
        }
        
        # Executar agente
        result = await self.agent_executor.ainvoke(input_data)
        
        # Parsear output
        output = result.get("output", "")
        
        try:
            # Tentar parsear JSON
            analysis = json.loads(output)
        except json.JSONDecodeError:
            # Se não for JSON, extrair informações do texto
            analysis = {
                "reasoning": output,
                "approved": "aprovar" in output.lower() or "sem irregularidades" in output.lower(),
                "confidence": 0.7,
                "findings": []
            }
        
        return analysis
    
    def _consolidate_results(
        self,
        invoice_data: Dict,
        rule_violations: List[Dict],
        llm_analysis: Dict,
        start_time: datetime
    ) -> Dict:
        """
        Consolida resultados da auditoria
        """
        # Coletar todas as irregularidades
        irregularidades = []
        
        # Violações de regras
        for violation in rule_violations:
            irregularidades.append({
                "tipo": violation["type"],
                "mensagem": violation["message"],
                "severidade": violation["severity"],
                "fonte": "motor_de_regras"
            })
        
        # Findings do LLM
        llm_findings = llm_analysis.get("findings", [])
        for finding in llm_findings:
            if isinstance(finding, str):
                irregularidades.append({
                    "tipo": "ANALISE_LLM",
                    "mensagem": finding,
                    "severidade": "medium",
                    "fonte": "llm"
                })
            elif isinstance(finding, dict):
                irregularidades.append({
                    **finding,
                    "fonte": "llm"
                })
        
        # Determinar aprovação
        critical_count = len([i for i in irregularidades if i.get("severidade") == "critical"])
        llm_approved = llm_analysis.get("approved", True)
        
        aprovada = (critical_count == 0) and llm_approved
        
        # Calcular confiança
        base_confidence = llm_analysis.get("confidence", 0.8)
        penalty = min(len(irregularidades) * 0.05, 0.3)  # Max 30% de penalidade
        confianca = max(base_confidence - penalty, 0.0)
        
        # Se não aprovada, confiança deve ser baixa
        if not aprovada and confianca > 0.7:
            confianca = 0.7
        
        # Construir justificativa
        justificativa = self._build_justification(
            aprovada=aprovada,
            irregularidades=irregularidades,
            llm_reasoning=llm_analysis.get("reasoning", "")
        )
        
        # Tempo de processamento
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        return {
            "aprovada": aprovada,
            "irregularidades": [i["mensagem"] for i in irregularidades],
            "irregularidades_detalhadas": irregularidades,
            "confianca": round(confianca, 3),
            "justificativa": justificativa,
            "detalhes": {
                "numero_nf": invoice_data.get("numero"),
                "cnpj_emitente": invoice_data.get("cnpj_emitente"),
                "valor_total": invoice_data.get("valor_total"),
                "total_irregularidades": len(irregularidades),
                "criticas": critical_count,
                "medias": len([i for i in irregularidades if i.get("severidade") == "medium"]),
                "llm_analysis": llm_analysis,
                "processing_time_seconds": round(processing_time, 2)
            },
            "timestamp": datetime.utcnow().isoformat(),
            "agent": "AuditAgent",
            "version": "1.0.0"
        }
    
    def _build_rejection_response(self, violations: List[Dict], invoice_data: Dict) -> Dict:
        """
        Constrói resposta de rejeição rápida
        """
        return {
            "aprovada": False,
            "irregularidades": [v["message"] for v in violations],
            "irregularidades_detalhadas": violations,
            "confianca": 0.95,  # Alta confiança na rejeição
            "justificativa": (
                f"Nota fiscal rejeitada automaticamente devido a {len(violations)} "
                f"violação(ões) crítica(s) de regras fiscais. "
                "Correções necessárias antes de prosseguir."
            ),
            "detalhes": {
                "numero_nf": invoice_data.get("numero"),
                "cnpj_emitente": invoice_data.get("cnpj_emitente"),
                "rejeicao_automatica": True,
                "violacoes_criticas": len(violations)
            },
            "timestamp": datetime.utcnow().isoformat(),
            "agent": "AuditAgent",
            "version": "1.0.0"
        }
    
    def _build_justification(
        self,
        aprovada: bool,
        irregularidades: List[Dict],
        llm_reasoning: str
    ) -> str:
        """
        Constrói justificativa da decisão
        """
        if aprovada and len(irregularidades) == 0:
            return (
                "Nota fiscal aprovada. Todos os campos foram validados e "
                "não foram identificadas irregularidades fiscais ou inconsistências nos cálculos."
            )
        
        if aprovada and len(irregularidades) > 0:
            return (
                f"Nota fiscal aprovada com ressalvas. Foram identificadas {len(irregularidades)} "
                f"irregularidade(s) de baixa severidade que não impedem a aprovação, mas requerem atenção. "
                f"{llm_reasoning[:200]}"
            )
        
        critical = [i for i in irregularidades if i.get("severidade") == "critical"]
        
        if critical:
            return (
                f"Nota fiscal reprovada. Foram identificadas {len(critical)} irregularidade(s) crítica(s) "
                f"que impedem a aprovação: {', '.join([i['mensagem'][:50] for i in critical[:3]])}. "
                "Correções são necessárias antes de reprocessar."
            )
        
        return (
            f"Nota fiscal reprovada. Análise identificou {len(irregularidades)} irregularidade(s) "
            f"que comprometem a conformidade fiscal. {llm_reasoning[:200]}"
        )
    
    async def _audit_with_fallback(
        self,
        invoice_data: Dict,
        context: Optional[Dict]
    ) -> Dict:
        """
        Tenta auditoria com LLM de fallback
        """
        logger.info("🔄 Executando auditoria com fallback LLM")
        
        # Construir prompt simples
        prompt = f"""
        Você é um auditor fiscal especializado em Notas Fiscais Eletrônicas do Brasil.
        
        Analise a seguinte nota fiscal e identifique irregularidades:
        
        {json.dumps(invoice_data, indent=2, ensure_ascii=False)}
        
        Retorne sua análise em formato JSON:
        {{
            "approved": true/false,
            "confidence": 0.0-1.0,
            "findings": ["irregularidade 1", "irregularidade 2"],
            "reasoning": "justificativa da decisão"
        }}
        """
        
        messages = [
            SystemMessage(content="Você é um auditor fiscal especializado."),
            HumanMessage(content=prompt)
        ]
        
        response = await self.fallback_llm.ainvoke(messages)
        
        # Parsear resposta
        try:
            analysis = json.loads(response.content)
        except:
            analysis = {
                "approved": False,
                "confidence": 0.5,
                "findings": ["Análise inconclusiva"],
                "reasoning": response.content
            }
        
        return self._consolidate_results(
            invoice_data=invoice_data,
            rule_violations=[],
            llm_analysis=analysis,
            start_time=datetime.utcnow()
        )
