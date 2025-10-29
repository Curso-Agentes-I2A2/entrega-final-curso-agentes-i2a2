"""
Controller para operações de Auditoria.

Camada intermediária entre rotas e services.
"""
from uuid import UUID
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from services.audit_service import AuditService
from services.invoice_service import InvoiceService
from schemas.audit_schema import (
    AuditCreate,
    AuditResponse,
    AuditStartResponse,
    AuditStatusResponse
)
import logging

logger = logging.getLogger(__name__)


class AuditController:
    """
    Controller de Auditorias.
    
    Gerencia operações de auditoria de notas fiscais.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.service = AuditService(db)
        self.invoice_service = InvoiceService(db)
    
    async def create_audit(self, audit_data: AuditCreate) -> AuditStartResponse:
        """
        Inicia nova auditoria.
        
        Args:
            audit_data: Dados da auditoria
        
        Returns:
            Confirmação com ID da auditoria
        
        Raises:
            HTTPException: Se dados inválidos ou NF não existe
        """
        try:
            audit = await self.service.create_audit(audit_data)
            
            logger.info(f"Auditoria iniciada: {audit.id} para NF: {audit_data.nota_fiscal_id}")
            
            return AuditStartResponse(
                message="Auditoria iniciada com sucesso",
                audit_id=audit.id,
                status=audit.status,
                estimated_time=30  # segundos
            )
            
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            logger.error(f"Erro ao criar auditoria: {e}")
            raise HTTPException(
                status_code=400,
                detail=f"Erro ao criar auditoria: {str(e)}"
            )
    
    async def create_audit_for_invoice(
        self,
        invoice_id: UUID
    ) -> AuditStartResponse:
        """
        Atalho para iniciar auditoria pelo ID da NF.
        
        Args:
            invoice_id: UUID da nota fiscal
        
        Returns:
            Confirmação com ID da auditoria
        
        Raises:
            HTTPException 404: Se NF não existe
        """
        # Verifica se NF existe
        invoice = await self.invoice_service.get_by_id(invoice_id)
        
        if not invoice:
            raise HTTPException(
                status_code=404,
                detail=f"Nota fiscal não encontrada: {invoice_id}"
            )
        
        # Cria auditoria
        audit_data = AuditCreate(nota_fiscal_id=invoice_id)
        return await self.create_audit(audit_data)
    
    async def get_audit(self, audit_id: UUID) -> AuditResponse:
        """
        Busca detalhes completos de uma auditoria.
        
        Args:
            audit_id: UUID da auditoria
        
        Returns:
            Detalhes completos da auditoria
        
        Raises:
            HTTPException 404: Se não encontrada
        """
        audit = await self.service.get_by_id(audit_id)
        
        if not audit:
            raise HTTPException(
                status_code=404,
                detail=f"Auditoria não encontrada: {audit_id}"
            )
        
        return AuditResponse.model_validate(audit)
    
    async def get_audit_status(self, audit_id: UUID) -> AuditStatusResponse:
        """
        Consulta rápida do status de uma auditoria.
        
        Args:
            audit_id: UUID da auditoria
        
        Returns:
            Status resumido
        
        Raises:
            HTTPException 404: Se não encontrada
        """
        audit = await self.service.get_by_id(audit_id)
        
        if not audit:
            raise HTTPException(
                status_code=404,
                detail=f"Auditoria não encontrada: {audit_id}"
            )
        
        return AuditStatusResponse(
            audit_id=audit.id,
            nota_fiscal_id=audit.nota_fiscal_id,
            status=audit.status,
            resultado=audit.resultado,
            confianca=audit.confianca,
            created_at=audit.created_at,
            updated_at=audit.updated_at
        )
    
    async def get_invoice_audits(
        self,
        invoice_id: UUID
    ) -> list[AuditResponse]:
        """
        Lista todas auditorias de uma nota fiscal.
        
        Args:
            invoice_id: UUID da nota fiscal
        
        Returns:
            Lista de auditorias
        
        Raises:
            HTTPException 404: Se NF não existe
        """
        # Verifica se NF existe
        invoice = await self.invoice_service.get_by_id(invoice_id)
        
        if not invoice:
            raise HTTPException(
                status_code=404,
                detail=f"Nota fiscal não encontrada: {invoice_id}"
            )
        
        # Busca auditorias
        audits = await self.service.get_by_invoice_id(invoice_id)
        
        return [AuditResponse.model_validate(audit) for audit in audits]