"""
Rotas da API para gerenciamento de Auditorias.
"""
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from database.connection import get_db
from services.audit_service import AuditService
from services.invoice_service import InvoiceService
from schemas.audit_schema import (
    AuditCreate,
    AuditResponse,
    AuditStartResponse,
    AuditStatusResponse
)

router = APIRouter(prefix="/api/audits", tags=["Auditorias"])



@router.post("", response_model=AuditStartResponse, status_code=201)
async def create_audit(
    audit_data: AuditCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Inicia uma nova auditoria para uma nota fiscal.
    
    O processamento é executado de forma assíncrona. Use o endpoint
    de status para acompanhar o andamento.
    
    Args:
        audit_data: Dados da auditoria (nota_fiscal_id obrigatório)
    
    Returns:
        Confirmação com ID da auditoria criada
    
    Raises:
        HTTPException 404: Se nota fiscal não existir
        HTTPException 400: Se dados forem inválidos
    """
    try:
        service = AuditService(db)
        audit = await service.create_audit(audit_data)
        
        return AuditStartResponse(
            message="Auditoria iniciada com sucesso",
            audit_id=audit.id,
            status=audit.status,
            estimated_time=30  # Tempo estimado em segundos
        )
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao criar auditoria: {str(e)}")


@router.post("/invoices/{invoice_id}", response_model=AuditStartResponse, status_code=201)
async def create_audit_for_invoice(
    invoice_id: UUID = Path(..., description="ID da nota fiscal"),
    db: AsyncSession = Depends(get_db)
):
    """
    Atalho para iniciar auditoria diretamente pelo ID da nota fiscal.
    
    Equivalente a POST /audits com nota_fiscal_id no body.
    
    Args:
        invoice_id: UUID da nota fiscal a ser auditada
    
    Returns:
        Confirmação com ID da auditoria criada
    
    Raises:
        HTTPException 404: Se nota fiscal não existir
    """
    # Verifica se nota fiscal existe
    invoice_service = InvoiceService(db)
    invoice = await invoice_service.get_by_id(invoice_id)
    
    if not invoice:
        raise HTTPException(
            status_code=404,
            detail=f"Nota fiscal não encontrada: {invoice_id}"
        )
    
    # Cria auditoria
    audit_data = AuditCreate(nota_fiscal_id=invoice_id)
    service = AuditService(db)
    audit = await service.create_audit(audit_data)
    
    return AuditStartResponse(
        message="Auditoria iniciada com sucesso",
        audit_id=audit.id,
        status=audit.status,
        estimated_time=30
    )


@router.get("/{audit_id}", response_model=AuditResponse)
async def get_audit(
    audit_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Busca detalhes completos de uma auditoria.
    
    Retorna resultado completo incluindo irregularidades,
    análise detalhada e dados do RAG.
    
    Args:
        audit_id: UUID da auditoria
    
    Returns:
        Detalhes completos da auditoria
    
    Raises:
        HTTPException 404: Se auditoria não for encontrada
    """
    service = AuditService(db)
    audit = await service.get_by_id(audit_id)
    
    if not audit:
        raise HTTPException(
            status_code=404,
            detail=f"Auditoria não encontrada: {audit_id}"
        )
    
    return AuditResponse.model_validate(audit)


@router.get("/{audit_id}/status", response_model=AuditStatusResponse)
async def get_audit_status(
    audit_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Consulta rápida do status de uma auditoria.
    
    Retorna apenas informações essenciais (status, resultado, confiança).
    Use este endpoint para polling durante o processamento.
    
    Args:
        audit_id: UUID da auditoria
    
    Returns:
        Status resumido da auditoria
    
    Raises:
        HTTPException 404: Se auditoria não for encontrada
    """
    service = AuditService(db)
    audit = await service.get_by_id(audit_id)
    
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


@router.get("/invoices/{invoice_id}/audits", response_model=list[AuditResponse])
async def get_invoice_audits(
    invoice_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Lista todas as auditorias de uma nota fiscal específica.
    
    Retorna histórico completo de auditorias ordenado por data (mais recente primeiro).
    
    Args:
        invoice_id: UUID da nota fiscal
    
    Returns:
        Lista de auditorias da nota fiscal
    
    Raises:
        HTTPException 404: Se nota fiscal não existir
    """
    # Verifica se nota fiscal existe
    invoice_service = InvoiceService(db)
    invoice = await invoice_service.get_by_id(invoice_id)
    
    if not invoice:
        raise HTTPException(
            status_code=404,
            detail=f"Nota fiscal não encontrada: {invoice_id}"
        )
    
    # Busca auditorias
    service = AuditService(db)
    audits = await service.get_by_invoice_id(invoice_id)
    
    return [AuditResponse.model_validate(audit) for audit in audits]