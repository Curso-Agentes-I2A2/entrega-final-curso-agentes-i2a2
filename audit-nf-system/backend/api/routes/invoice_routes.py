"""
Rotas da API para gerenciamento de Notas Fiscais.
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime
from uuid import UUID

from database.connection import get_db
from services.invoice_service import InvoiceService
from schemas.invoice_schema import (
    InvoiceResponse,
    InvoiceList,
    InvoiceUploadResponse,
    InvoiceUpdate
)
from models.invoice import InvoiceStatus

router = APIRouter(prefix="/api/invoices", tags=["Notas Fiscais"])


@router.post("/upload", response_model=InvoiceUploadResponse, status_code=201)
async def upload_invoice(
    file: UploadFile = File(..., description="Arquivo XML da NF-e"),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload de arquivo XML de Nota Fiscal Eletrônica.
    
    Processa o XML, extrai informações e cria registro no banco de dados.
    
    Args:
        file: Arquivo XML da NF-e
    
    Returns:
        Informações da nota fiscal criada
    
    Raises:
        HTTPException 400: Se arquivo não for XML ou estiver inválido
        HTTPException 409: Se nota fiscal já existir (chave duplicada)
    """
    # Valida extensão do arquivo
    if not file.filename.endswith('.xml'):
        raise HTTPException(
            status_code=400,
            detail="Apenas arquivos XML são aceitos"
        )
    
    try:
        # Lê conteúdo do arquivo
        xml_content = await file.read()
        xml_string = xml_content.decode('utf-8')
        
        # Cria nota fiscal
        service = InvoiceService(db)
        invoice = await service.create_from_xml(xml_string)
        
        return InvoiceUploadResponse(
            message="Nota fiscal processada com sucesso",
            invoice_id=invoice.id,
            chave_acesso=invoice.chave_acesso,
            status=invoice.status
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Verifica se é erro de chave duplicada
        if "duplicate key" in str(e).lower() or "unique constraint" in str(e).lower():
            raise HTTPException(
                status_code=409,
                detail="Nota fiscal já cadastrada no sistema"
            )
        raise HTTPException(status_code=500, detail=f"Erro ao processar arquivo: {str(e)}")


@router.get("", response_model=InvoiceList)
async def list_invoices(
    page: int = Query(1, ge=1, description="Número da página"),
    page_size: int = Query(20, ge=1, le=100, description="Itens por página"),
    status: Optional[InvoiceStatus] = Query(None, description="Filtrar por status"),
    cnpj_emitente: Optional[str] = Query(None, min_length=14, max_length=14, description="Filtrar por CNPJ do emitente"),
    data_inicio: Optional[datetime] = Query(None, description="Data inicial (ISO format)"),
    data_fim: Optional[datetime] = Query(None, description="Data final (ISO format)"),
    db: AsyncSession = Depends(get_db)
):
    """
    Lista notas fiscais com paginação e filtros.
    
    Permite filtrar por status, CNPJ do emitente e período de emissão.
    
    Args:
        page: Número da página (1-indexed)
        page_size: Quantidade de itens por página
        status: Filtrar por status da nota
        cnpj_emitente: Filtrar por CNPJ (apenas números)
        data_inicio: Filtrar por data de emissão mínima
        data_fim: Filtrar por data de emissão máxima
    
    Returns:
        Lista paginada de notas fiscais
    """
    service = InvoiceService(db)
    return await service.list_invoices(
        page=page,
        page_size=page_size,
        status=status,
        cnpj_emitente=cnpj_emitente,
        data_inicio=data_inicio,
        data_fim=data_fim
    )


@router.get("/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(
    invoice_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Busca detalhes de uma nota fiscal específica por ID.
    
    Args:
        invoice_id: UUID da nota fiscal
    
    Returns:
        Detalhes completos da nota fiscal
    
    Raises:
        HTTPException 404: Se nota fiscal não for encontrada
    """
    service = InvoiceService(db)
    invoice = await service.get_by_id(invoice_id)
    
    if not invoice:
        raise HTTPException(
            status_code=404,
            detail=f"Nota fiscal não encontrada: {invoice_id}"
        )
    
    return InvoiceResponse.model_validate(invoice)


@router.get("/chave/{chave_acesso}", response_model=InvoiceResponse)
async def get_invoice_by_chave(
    chave_acesso: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Busca nota fiscal por chave de acesso.
    
    Args:
        chave_acesso: Chave de acesso de 44 dígitos
    
    Returns:
        Detalhes completos da nota fiscal
    
    Raises:
        HTTPException 400: Se chave de acesso for inválida
        HTTPException 404: Se nota fiscal não for encontrada
    """
    # Valida formato da chave
    if len(chave_acesso) != 44 or not chave_acesso.isdigit():
        raise HTTPException(
            status_code=400,
            detail="Chave de acesso deve conter exatamente 44 dígitos"
        )
    
    service = InvoiceService(db)
    invoice = await service.get_by_chave_acesso(chave_acesso)
    
    if not invoice:
        raise HTTPException(
            status_code=404,
            detail=f"Nota fiscal não encontrada: {chave_acesso}"
        )
    
    return InvoiceResponse.model_validate(invoice)


@router.patch("/{invoice_id}", response_model=InvoiceResponse)
async def update_invoice(
    invoice_id: UUID,
    update_data: InvoiceUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Atualiza dados de uma nota fiscal.
    
    Permite atualizar status e observações.
    
    Args:
        invoice_id: UUID da nota fiscal
        update_data: Dados para atualização
    
    Returns:
        Nota fiscal atualizada
    
    Raises:
        HTTPException 404: Se nota fiscal não for encontrada
    """
    service = InvoiceService(db)
    invoice = await service.update(invoice_id, update_data)
    
    if not invoice:
        raise HTTPException(
            status_code=404,
            detail=f"Nota fiscal não encontrada: {invoice_id}"
        )
    
    return InvoiceResponse.model_validate(invoice)


@router.get("/{invoice_id}/xml")
async def get_invoice_xml(
    invoice_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Retorna o conteúdo XML completo da nota fiscal.
    
    Args:
        invoice_id: UUID da nota fiscal
    
    Returns:
        XML da NF-e como texto
    
    Raises:
        HTTPException 404: Se nota fiscal não for encontrada
    """
    service = InvoiceService(db)
    invoice = await service.get_by_id(invoice_id)
    
    if not invoice:
        raise HTTPException(
            status_code=404,
            detail=f"Nota fiscal não encontrada: {invoice_id}"
        )
    
    from fastapi.responses import Response
    return Response(
        content=invoice.xml_content,
        media_type="application/xml",
        headers={
            "Content-Disposition": f'attachment; filename="NFe_{invoice.chave_acesso}.xml"'
        }
    )