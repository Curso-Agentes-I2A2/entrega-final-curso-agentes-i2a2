# backend/services/dashboard_service.py

import logging
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

# Importe seus modelos de banco de dados
from models.invoice import Invoice, InvoiceStatus
from models.audit import Audit

# Importe o schema de resposta que acabamos de criar
from schemas.dashboard_schema import DashboardStats

logger = logging.getLogger(__name__)

class DashboardService:
    """
    Serviço para agregar dados e estatísticas para o dashboard.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_dashboard_summary(self) -> DashboardStats:
        """
        Calcula e retorna as estatísticas principais do sistema.
        """
        logger.info("Calculando estatísticas do dashboard...")
        
        try:
            # 1. Consulta na tabela 'invoices'
            # Vamos pegar o total de notas e as pendentes
            invoices_stmt = select(
                func.count(Invoice.id).label("total"),
                func.count(Invoice.id).filter(
                    Invoice.status.in_([
                        InvoiceStatus.PENDENTE,
                        InvoiceStatus.EM_PROCESSAMENTO,
                        InvoiceStatus.AGUARDANDO_AUDITORIA
                    ])
                ).label("pending")
            )
            invoice_counts = (await self.db.execute(invoices_stmt)).one()

            # 2. Consulta na tabela 'audits'
            # Vamos assumir que o 'resultado' da auditoria é salvo na tabela 'audits'
            # e que o 'status' na tabela 'invoices' é atualizado.
            # (Esta é a melhor prática)
            
            # Vamos usar o status da 'Invoice' como fonte da verdade
            # para Aprovadas/Rejeitadas
            approved_stmt = select(func.count(Invoice.id)).where(
                Invoice.status == InvoiceStatus.APROVADA
            )
            rejected_stmt = select(func.count(Invoice.id)).where(
                Invoice.status == InvoiceStatus.REJEITADA
            )
            
            total_audits_stmt = select(func.count(Audit.id)) # Total de registros de auditoria

            # Executar as consultas em paralelo
            approved_count = (await self.db.execute(approved_stmt)).scalar_one()
            rejected_count = (await self.db.execute(rejected_stmt)).scalar_one()
            total_audits = (await self.db.execute(total_audits_stmt)).scalar_one()

            # 3. Calcular a Taxa de Aprovação
            total_decisoes = approved_count + rejected_count
            approval_rate = (approved_count / total_decisoes) if total_decisoes > 0 else 0.0

            # 4. Calcular Tempo Médio (exemplo, pode precisar de ajuste)
            # Isso assume que o seu `Audit` tem um campo `tempo_processamento`
            # Se não tiver, podemos comentar ou ajustar.
            avg_time = 0.0
            try:
                # Tentativa de calcular o tempo médio.
                # Se o seu modelo 'Audit' for diferente, este select falhará
                # e será pego pelo 'except'
                avg_time_stmt = select(func.avg(Audit.tempo_processamento))
                avg_time_result = (await self.db.execute(avg_time_stmt)).scalar()
                avg_time = round(avg_time_result, 2) if avg_time_result else 0.0
            except Exception as e:
                logger.warning(f"Não foi possível calcular o tempo médio de processamento: {e}")
                avg_time = None # Retorna None se a coluna não existir

            # 5. Montar o objeto de resposta
            stats = DashboardStats(
                total_invoices=invoice_counts.total,
                pending_invoices=invoice_counts.pending,
                total_audits=total_audits,
                approved_audits=approved_count,
                rejected_audits=rejected_count,
                approval_rate=round(approval_rate, 4),
                avg_processing_time=avg_time,
                timestamp=datetime.now()
            )
            
            return stats

        except Exception as e:
            logger.error(f"Erro ao calcular estatísticas: {e}", exc_info=True)
            raise  # Re-levanta a exceção para a rota tratar