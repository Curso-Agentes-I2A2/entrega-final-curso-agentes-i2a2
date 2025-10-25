"""
Controller para operações de Notas Fiscais.

Camada intermediária entre rotas e services, responsável por
orquestrar a lógica de apresentação.
"""
from typing import Optional
from datetime import datetime
from uuid import UUID
from fastapi import UploadFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from services.invoice_service import InvoiceService
from src.invoice_processing.processor import InvoiceProcessor
from schemas.invoice_schema import (
    InvoiceResponse,
    InvoiceList,
    InvoiceUploadResponse,
    InvoiceUpdate
)
from models.invoice import InvoiceStatus
import logging

logger = logging.getLogger(__name__)


class InvoiceController:
    """
    Controller de Notas Fiscais.
    
    Orquestra operações entre rotas e services, aplicando
    lógica de apresentação e validações adicionais.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.service = InvoiceService(db)
        self.processor = InvoiceProcessor()
    
    async def upload_invoice(self, file: UploadFile) -> InvoiceUploadResponse:
        """
        Processa upload de arquivo XML de NF-e.
        
        Args:
            file: Arquivo XML enviado
        
        Returns:
            Resposta com dados da NF-e criada
        
        Raises:
            HTTPException: Em caso de erro no processamento
        """
        # Valida tipo de arquivo
        if not file.filename.endswith('.xml'):
            raise HTTPException(
                status_code=400,
                detail="Apenas arquivos XML são aceitos"
            )
        
        try:
            # Lê conteúdo do arquivo
            xml_content = await file.read()
            xml_string = xml_content.decode('utf-8')
            
            logger.info(f"Processando upload: {file.filename}")
            
            # Processa XML e cria invoice
            invoice = await self.service.create_from_xml(xml_string)
            
            return InvoiceUploadResponse(
                message="Nota fiscal processada com sucesso",
                invoice_id=invoice.id,
                chave_acesso=invoice.chave_acesso,
                status=invoice.status
            )
            
        except ValueError as e:
            logger.error(f"Erro de validação: {e}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Erro ao processar upload: {e}")
            if "duplicate key" in str(e).lower():
                raise HTTPException(
                    status_code=409,
                    detail="Nota fiscal já cadastrada no sistema"
                )
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao processar arquivo: {str(e)}"
            )
    
    async def list_invoices(
        self,
        page: int = 1,
        page_size: int = 20,
        status: Optional[InvoiceStatus] = None,
        cnpj_emitente: Optional[str] = None,
        data_inicio: Optional[datetime] = None,
        data_fim: Optional[datetime] = None
    ) -> InvoiceList:
        """
        Lista notas fiscais com filtros e paginação.
        
        Args:
            page: Número da página
            page_size: Itens por página
            status: Filtro por status
            cnpj_emitente: Filtro por CNPJ
            data_inicio: Data inicial
            data_fim: Data final
        
        Returns:
            Lista paginada de notas fiscais
        """
        # Valida parâmetros de paginação
        if page < 1:
            raise HTTPException(
                status_code=400,
                detail="Número da página deve ser maior que 0"
            )
        
        if page_size < 1 or page_size > 100:
            raise HTTPException(
                status_code=400,
                detail="Tamanho da página deve estar entre 1 e 100"
            )
        
        # Valida CNPJ se fornecido
        if cnpj_emitente and len(cnpj_emitente) != 14:
            raise HTTPException(
                status_code=400,
                detail="CNPJ deve conter 14 dígitos"
            )
        
        # Valida período de datas
        if data_inicio and data_fim and data_inicio > data_fim:
            raise HTTPException(
                status_code=400,
                detail="Data inicial não pode ser maior que data final"
            )
        
        return await self.service.list_invoices(
            page=page,
            page_size=page_size,
            status=status,
            cnpj_emitente=cnpj_emitente,
            data_inicio=data_inicio,
            data_fim=data_fim
        )
    
    async def get_invoice(self, invoice_id: UUID) -> InvoiceResponse:
        """
        Busca detalhes de uma nota fiscal.
        
        Args:
            invoice_id: UUID da nota fiscal
        
        Returns:
            Detalhes da nota fiscal
        
        Raises:
            HTTPException 404: Se não encontrada
        """
        invoice = await self.service.get_by_id(invoice_id)
        
        if not invoice:
            raise HTTPException(
                status_code=404,
                detail=f"Nota fiscal não encontrada: {invoice_id}"
            )
        
        return InvoiceResponse.model_validate(invoice)
    
    async def get_invoice_by_chave(self, chave_acesso: str) -> InvoiceResponse:
        """
        Busca nota fiscal por chave de acesso.
        
        Args:
            chave_acesso: Chave de acesso de 44 dígitos
        
        Returns:
            Detalhes da nota fiscal
        
        Raises:
            HTTPException: Se chave inválida ou NF não encontrada
        """
        # Valida formato da chave
        if len(chave_acesso) != 44 or not chave_acesso.isdigit():
            raise HTTPException(
                status_code=400,
                detail="Chave de acesso deve conter exatamente 44 dígitos"
            )
        
        invoice = await self.service.get_by_chave_acesso(chave_acesso)
        
        if not invoice:
            raise HTTPException(
                status_code=404,
                detail=f"Nota fiscal não encontrada: {chave_acesso}"
            )
        
        return InvoiceResponse.model_validate(invoice)
    
    async def update_invoice(
        self,
        invoice_id: UUID,
        update_data: InvoiceUpdate
    ) -> InvoiceResponse:
        """
        Atualiza dados de uma nota fiscal.
        
        Args:
            invoice_id: UUID da nota fiscal
            update_data: Dados para atualização
        
        Returns:
            Nota fiscal atualizada
        
        Raises:
            HTTPException 404: Se não encontrada
        """
        invoice = await self.service.update(invoice_id, update_data)
        
        if not invoice:
            raise HTTPException(
                status_code=404,
                detail=f"Nota fiscal não encontrada: {invoice_id}"
            )
        
        logger.info(f"Nota fiscal atualizada: {invoice_id}")
        return InvoiceResponse.model_validate(invoice)
    
    async def get_invoice_xml(self, invoice_id: UUID) -> tuple[str, str]:
        """
        Retorna XML da nota fiscal.
        
        Args:
            invoice_id: UUID da nota fiscal
        
        Returns:
            Tuple (conteúdo_xml, nome_arquivo)
        
        Raises:
            HTTPException 404: Se não encontrada
        """
        invoice = await self.service.get_by_id(invoice_id)
        
        if not invoice:
            raise HTTPException(
                status_code=404,
                detail=f"Nota fiscal não encontrada: {invoice_id}"
            )
        
        filename = f"NFe_{invoice.chave_acesso}.xml"
        return invoice.xml_content, filename