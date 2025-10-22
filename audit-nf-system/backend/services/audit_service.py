"""
Service de lógica de negócio para Auditorias de Notas Fiscais.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from uuid import UUID
from decimal import Decimal
import logging
import time
import asyncio

from models.audit import Audit, AuditStatus, AuditResult
from models.invoice import Invoice
from schemas.audit_schema import AuditCreate, AuditUpdate
from services.rag_client import RAGClient
from config import settings

logger = logging.getLogger(__name__)


class AuditService:
    """
    Service para gerenciar auditorias de notas fiscais.
    
    Responsável por:
    - Criar e gerenciar auditorias
    - Executar validações automatizadas
    - Integrar com RAG para contexto adicional
    - Integrar com Agents de IA (mock por enquanto)
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.rag_client = RAGClient()
    
    async def create_audit(self, audit_data: AuditCreate) -> Audit:
        """
        Cria uma nova auditoria para uma nota fiscal.
        
        Args:
            audit_data: Dados da auditoria
        
        Returns:
            Audit criada
        
        Raises:
            ValueError: Se nota fiscal não existir
        """
        # Verifica se nota fiscal existe
        result = await self.db.execute(
            select(Invoice).where(Invoice.id == audit_data.nota_fiscal_id)
        )
        invoice = result.scalar_one_or_none()
        
        if not invoice:
            raise ValueError(f"Nota fiscal não encontrada: {audit_data.nota_fiscal_id}")
        
        # Cria auditoria
        audit = Audit(
            nota_fiscal_id=audit_data.nota_fiscal_id,
            status=AuditStatus.PENDENTE,
            observacoes=audit_data.observacoes
        )
        
        self.db.add(audit)
        await self.db.commit()
        await self.db.refresh(audit)
        
        logger.info(f"Auditoria criada: {audit.id} para NF: {audit_data.nota_fiscal_id}")
        
        # Inicia processamento assíncrono (não bloqueia resposta)
        asyncio.create_task(self._process_audit(audit.id))
        
        return audit
    
    async def get_by_id(self, audit_id: UUID) -> Optional[Audit]:
        """Busca auditoria por ID."""
        result = await self.db.execute(
            select(Audit).where(Audit.id == audit_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_invoice_id(self, invoice_id: UUID) -> list[Audit]:
        """Busca todas auditorias de uma nota fiscal."""
        result = await self.db.execute(
            select(Audit)
            .where(Audit.nota_fiscal_id == invoice_id)
            .order_by(Audit.created_at.desc())
        )
        return list(result.scalars().all())
    
    async def update(self, audit_id: UUID, update_data: AuditUpdate) -> Optional[Audit]:
        """Atualiza dados de uma auditoria."""
        audit = await self.get_by_id(audit_id)
        if not audit:
            return None
        
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(audit, field, value)
        
        await self.db.commit()
        await self.db.refresh(audit)
        
        logger.info(f"Auditoria atualizada: {audit_id}")
        return audit
    
    async def _process_audit(self, audit_id: UUID) -> None:
        """
        Processa auditoria de forma assíncrona.
        
        Executa validações, consulta RAG e agentes de IA.
        """
        start_time = time.time()
        
        try:
            # Busca auditoria e nota fiscal em nova sessão
            from database.connection import AsyncSessionLocal
            async with AsyncSessionLocal() as db:
                result = await db.execute(
                    select(Audit).where(Audit.id == audit_id)
                )
                audit = result.scalar_one()
                
                result = await db.execute(
                    select(Invoice).where(Invoice.id == audit.nota_fiscal_id)
                )
                invoice = result.scalar_one()
                
                # Atualiza status para em andamento
                audit.status = AuditStatus.EM_ANDAMENTO
                await db.commit()
                
                logger.info(f"Iniciando processamento da auditoria: {audit_id}")
                
                # 1. Executa validações básicas
                irregularidades = await self._validate_invoice(invoice)
                
                # 2. Consulta RAG para contexto adicional
                rag_data = await self._get_rag_context(invoice)
                
                # 3. Executa análise com agente de IA (mock)
                agent_result = await self._run_agent_analysis(invoice, rag_data)
                
                # 4. Determina resultado final
                resultado = self._determine_result(irregularidades, agent_result)
                confianca = agent_result.get("confidence", 0.85)
                
                # 5. Atualiza auditoria com resultados
                tempo_processamento = time.time() - start_time
                
                audit.status = AuditStatus.CONCLUIDA
                audit.resultado = resultado
                audit.irregularidades = irregularidades
                audit.confianca = Decimal(str(confianca))
                audit.tempo_processamento = Decimal(str(round(tempo_processamento, 2)))
                audit.agente_responsavel = agent_result.get("agent_name", "AI-Auditor-v1")
                audit.resultado_detalhado = agent_result
                audit.dados_rag = {"documents": rag_data}
                
                await db.commit()
                
                logger.info(
                    f"Auditoria concluída: {audit_id} - "
                    f"Resultado: {resultado} - "
                    f"Confiança: {confianca}"
                )
                
        except Exception as e:
            logger.error(f"Erro ao processar auditoria {audit_id}: {e}")
            
            # Atualiza status para erro
            from database.connection import AsyncSessionLocal
            async with AsyncSessionLocal() as db:
                result = await db.execute(
                    select(Audit).where(Audit.id == audit_id)
                )
                audit = result.scalar_one()
                audit.status = AuditStatus.ERRO
                audit.observacoes = f"Erro no processamento: {str(e)}"
                await db.commit()
    
    async def _validate_invoice(self, invoice: Invoice) -> list[str]:
        """
        Executa validações básicas na nota fiscal.
        
        Returns:
            Lista de irregularidades encontradas
        """
        irregularidades = []
        
        # 1. Valida formato da chave de acesso
        if not invoice.chave_acesso.isdigit() or len(invoice.chave_acesso) != 44:
            irregularidades.append("Chave de acesso inválida")
        
        # 2. Valida CNPJ
        if not invoice.cnpj_emitente.isdigit() or len(invoice.cnpj_emitente) != 14:
            irregularidades.append("CNPJ do emitente inválido")
        
        if not invoice.cnpj_destinatario.isdigit() or len(invoice.cnpj_destinatario) != 14:
            irregularidades.append("CNPJ do destinatário inválido")
        
        # 3. Valida valores
        if invoice.valor_total <= 0:
            irregularidades.append("Valor total inválido")
        
        if invoice.valor_produtos and invoice.valor_produtos > invoice.valor_total:
            irregularidades.append("Valor dos produtos maior que valor total")
        
        # 4. Valida soma de impostos
        total_impostos = (invoice.valor_icms or 0) + (invoice.valor_ipi or 0)
        diferenca_esperada = abs(
            float(invoice.valor_total) - 
            float(invoice.valor_produtos or 0) - 
            float(total_impostos)
        )
        
        if diferenca_esperada > 1.0:  # Margem de 1 real
            irregularidades.append(
                f"Divergência nos valores: diferença de R$ {diferenca_esperada:.2f}"
            )
        
        # 5. Valida data de emissão
        from datetime import datetime, timedelta
        if invoice.data_emissao > datetime.now():
            irregularidades.append("Data de emissão futura")
        
        if invoice.data_emissao < datetime.now() - timedelta(days=365 * 5):
            irregularidades.append("Data de emissão muito antiga (>5 anos)")
        
        return irregularidades
    
    async def _get_rag_context(self, invoice: Invoice) -> list[dict]:
        """
        Consulta sistema RAG para obter contexto relevante.
        
        Returns:
            Lista de documentos relevantes do RAG
        """
        try:
            # Monta query baseada na NF
            query = f"""
            Validar nota fiscal com:
            - Valor total: R$ {invoice.valor_total}
            - ICMS: R$ {invoice.valor_icms}
            - IPI: R$ {invoice.valor_ipi}
            - Natureza: {invoice.natureza_operacao}
            """
            
            # Busca documentos relevantes
            documents = await self.rag_client.search(query, top_k=3)
            
            return [
                {
                    "content": doc.content,
                    "score": doc.score,
                    "metadata": doc.metadata
                }
                for doc in documents
            ]
            
        except Exception as e:
            logger.warning(f"Erro ao consultar RAG: {e}")
            return []
    
    async def _run_agent_analysis(self, invoice: Invoice, rag_data: list[dict]) -> dict:
        """
        Executa análise usando agente de IA.
        
        Por enquanto é um mock. No futuro, integrará com serviço de Agents.
        
        Returns:
            Dicionário com resultado da análise
        """
        # TODO: Integrar com serviço real de Agents
        # Por enquanto, retorna análise mock baseada em regras simples
        
        logger.info("Executando análise com agente de IA (mock)")
        
        # Simula processamento
        await asyncio.sleep(2)
        
        # Análise mock
        problemas = []
        recomendacoes = []
        
        # Verifica alíquota de ICMS (mock)
        if invoice.valor_icms:
            aliquota_icms = float(invoice.valor_icms) / float(invoice.valor_produtos or invoice.valor_total) * 100
            if aliquota_icms < 7 or aliquota_icms > 18:
                problemas.append(f"Alíquota de ICMS suspeita: {aliquota_icms:.2f}%")
                recomendacoes.append("Verificar alíquota aplicada conforme legislação estadual")
        
        # Verifica valores zerados
        if invoice.valor_icms == 0 and invoice.valor_ipi == 0:
            problemas.append("Nota fiscal sem ICMS e IPI - verificar se aplicável")
            recomendacoes.append("Confirmar regime tributário do emitente")
        
        # Determina confiança baseada em problemas encontrados
        confidence = 0.95 - (len(problemas) * 0.1)
        confidence = max(0.5, min(1.0, confidence))
        
        return {
            "agent_name": "AI-Auditor-v1",
            "confidence": confidence,
            "problemas_detectados": problemas,
            "recomendacoes": recomendacoes,
            "validacoes": {
                "estrutura_xml": {"status": "OK", "detalhes": "XML bem formado"},
                "valores_matematicos": {"status": "OK", "detalhes": "Cálculos conferem"},
                "dados_cadastrais": {"status": "OK", "detalhes": "CNPJs válidos"},
                "impostos": {
                    "status": "ATENCAO" if problemas else "OK",
                    "detalhes": problemas[0] if problemas else "Impostos dentro do esperado"
                }
            },
            "contexto_rag_utilizado": len(rag_data) > 0,
            "documentos_consultados": len(rag_data)
        }
    
    def _determine_result(self, irregularidades: list[str], agent_result: dict) -> AuditResult:
        """
        Determina resultado final da auditoria baseado em irregularidades e análise do agente.
        
        Args:
            irregularidades: Lista de irregularidades encontradas
            agent_result: Resultado da análise do agente
        
        Returns:
            Resultado final (APROVADA, REJEITADA ou REVISAO_NECESSARIA)
        """
        confidence = agent_result.get("confidence", 0.0)
        problemas = agent_result.get("problemas_detectados", [])
        
        # Irregularidades críticas = rejeição automática
        irregularidades_criticas = [
            irr for irr in irregularidades
            if any(palavra in irr.lower() for palavra in ["inválid", "divergência"])
        ]
        
        if len(irregularidades_criticas) > 0:
            return AuditResult.REJEITADA
        
        # Confiança baixa ou muitos problemas = revisão necessária
        if confidence < settings.MIN_CONFIDENCE_SCORE or len(problemas) > 2:
            return AuditResult.REVISAO_NECESSARIA
        
        # Irregularidades menores = revisão necessária
        if len(irregularidades) > 0:
            return AuditResult.REVISAO_NECESSARIA
        
        # Tudo OK = aprovada
        return AuditResult.APROVADA