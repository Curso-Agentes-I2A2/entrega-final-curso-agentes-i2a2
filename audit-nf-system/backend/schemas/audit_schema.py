"""
Schemas Pydantic para validação de dados de Auditoria.
"""
from pydantic import BaseModel, Field
from datetime import datetime
from decimal import Decimal
from typing import Optional, Any
from uuid import UUID

from models.audit import AuditStatus, AuditResult


class AuditCreate(BaseModel):
    """
    Schema para iniciar uma nova auditoria.
    """
    nota_fiscal_id: UUID = Field(..., description="ID da nota fiscal a ser auditada")
    observacoes: Optional[str] = Field(None, description="Observações iniciais")


class AuditUpdate(BaseModel):
    """
    Schema para atualização de auditoria.
    Usado internamente pelo sistema durante o processamento.
    """
    status: Optional[AuditStatus] = None
    resultado: Optional[AuditResult] = None
    resultado_detalhado: Optional[dict[str, Any]] = None
    irregularidades: Optional[list[str]] = None
    confianca: Optional[Decimal] = Field(None, ge=0, le=1)
    agente_responsavel: Optional[str] = None
    tempo_processamento: Optional[Decimal] = None
    observacoes: Optional[str] = None
    dados_rag: Optional[dict[str, Any]] = None


class AuditResponse(BaseModel):
    """
    Schema de resposta com dados completos da auditoria.
    """
    id: UUID
    nota_fiscal_id: UUID
    status: AuditStatus
    resultado: Optional[AuditResult]
    resultado_detalhado: Optional[dict[str, Any]]
    irregularidades: Optional[list[str]]
    confianca: Optional[Decimal]
    agente_responsavel: Optional[str]
    tempo_processamento: Optional[Decimal]
    observacoes: Optional[str]
    dados_rag: Optional[dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    
    model_config = {
        "from_attributes": True
    }


class AuditStatusResponse(BaseModel):
    """
    Schema simplificado para consulta rápida de status.
    """
    audit_id: UUID
    nota_fiscal_id: UUID
    status: AuditStatus
    resultado: Optional[AuditResult]
    confianca: Optional[Decimal]
    created_at: datetime
    updated_at: datetime


class AuditStartResponse(BaseModel):
    """
    Schema de resposta ao iniciar uma auditoria.
    """
    message: str = Field(..., description="Mensagem de confirmação")
    audit_id: UUID = Field(..., description="ID da auditoria criada")
    status: AuditStatus = Field(..., description="Status inicial")
    estimated_time: Optional[int] = Field(None, description="Tempo estimado em segundos")