"""
Schemas Pydantic para validação de dados de Nota Fiscal.
"""
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from models.invoice import InvoiceStatus


class InvoiceBase(BaseModel):
    """Schema base com campos comuns de Nota Fiscal."""
    numero: str = Field(..., description="Número da nota fiscal")
    serie: str = Field(..., description="Série da nota fiscal")
    chave_acesso: str = Field(..., min_length=44, max_length=44, description="Chave de acesso de 44 dígitos")
    cnpj_emitente: str = Field(..., min_length=14, max_length=14, description="CNPJ do emitente")
    razao_social_emitente: str = Field(..., description="Razão social do emitente")
    cnpj_destinatario: str = Field(..., min_length=14, max_length=14, description="CNPJ do destinatário")
    razao_social_destinatario: str = Field(..., description="Razão social do destinatário")
    valor_total: Decimal = Field(..., gt=0, description="Valor total da nota")
    valor_produtos: Optional[Decimal] = Field(None, ge=0, description="Valor dos produtos")
    valor_icms: Optional[Decimal] = Field(None, ge=0, description="Valor do ICMS")
    valor_ipi: Optional[Decimal] = Field(None, ge=0, description="Valor do IPI")
    data_emissao: datetime = Field(..., description="Data de emissão da NF-e")
    natureza_operacao: Optional[str] = Field(None, description="Natureza da operação")
    observacoes: Optional[str] = None

    @field_validator("chave_acesso")
    @classmethod
    def validate_chave_acesso(cls, v: str) -> str:
        """Valida se a chave de acesso contém apenas dígitos."""
        if not v.isdigit():
            raise ValueError("Chave de acesso deve conter apenas dígitos")
        return v
    
    @field_validator("cnpj_emitente", "cnpj_destinatario")
    @classmethod
    def validate_cnpj(cls, v: str) -> str:
        """Valida se o CNPJ contém apenas dígitos."""
        if not v.isdigit():
            raise ValueError("CNPJ deve conter apenas dígitos")
        return v


class InvoiceCreate(InvoiceBase):
    """
    Schema para criação de nota fiscal.
    Inclui o conteúdo XML completo.
    """
    xml_content: str = Field(..., description="Conteúdo completo do XML da NF-e")


class InvoiceUpdate(BaseModel):
    """
    Schema para atualização de nota fiscal.
    Todos os campos são opcionais.
    """
    status: Optional[InvoiceStatus] = None
    observacoes: Optional[str] = None


class InvoiceResponse(InvoiceBase):
    """
    Schema de resposta com dados completos da nota fiscal.
    Inclui campos gerados pelo sistema (id, timestamps, status).
    """
    id: UUID
    status: InvoiceStatus
    created_at: datetime
    updated_at: datetime
    
    model_config = {
        "from_attributes": True  # Permite criar a partir de modelos ORM
    }


class InvoiceListItem(BaseModel):
    """
    Schema resumido para listagem de notas fiscais.
    Contém apenas os campos essenciais para exibição em lista.
    """
    id: UUID
    numero: str
    serie: str
    chave_acesso: str
    cnpj_emitente: str
    razao_social_emitente: str
    cnpj_destinatario: str
    razao_social_destinatario: str
    valor_total: Decimal
    data_emissao: datetime
    status: InvoiceStatus
    created_at: datetime
    
    model_config = {
        "from_attributes": True
    }


class InvoiceList(BaseModel):
    """
    Schema para resposta de lista paginada de notas fiscais.
    """
    total: int = Field(..., description="Total de registros")
    page: int = Field(..., description="Página atual")
    page_size: int = Field(..., description="Tamanho da página")
    items: list[InvoiceListItem] = Field(..., description="Lista de notas fiscais")


class InvoiceUploadResponse(BaseModel):
    """
    Schema de resposta após upload de arquivo XML.
    """
    message: str = Field(..., description="Mensagem de sucesso")
    invoice_id: UUID = Field(..., description="ID da nota fiscal criada")
    chave_acesso: str = Field(..., description="Chave de acesso da NF-e")
    status: InvoiceStatus = Field(..., description="Status inicial")