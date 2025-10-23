"""
Modelo SQLAlchemy para Nota Fiscal Eletrônica (NF-e).
"""
from sqlalchemy import Column, String, Text, Numeric, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from datetime import datetime
import uuid
import enum

from database.connection import Base


class InvoiceStatus(str, enum.Enum):
    """Status possíveis de uma nota fiscal no sistema."""
    PENDENTE = "pendente"
    EM_PROCESSAMENTO = "em_processamento"
    AGUARDANDO_AUDITORIA = "aguardando_auditoria"
    EM_AUDITORIA = "em_auditoria"
    APROVADA = "aprovada"
    REJEITADA = "rejeitada"
    ERRO = "erro"


class Invoice(Base):
    """
    Modelo de Nota Fiscal Eletrônica.
    
    Armazena informações principais da NF-e extraídas do XML,
    incluindo dados do emitente, destinatário, valores e o XML completo.
    
    Attributes:
        id: Identificador único (UUID)
        numero: Número da nota fiscal
        serie: Série da nota fiscal
        chave_acesso: Chave de acesso de 44 dígitos
        cnpj_emitente: CNPJ da empresa emitente
        razao_social_emitente: Razão social do emitente
        cnpj_destinatario: CNPJ da empresa destinatária
        razao_social_destinatario: Razão social do destinatário
        valor_total: Valor total da nota fiscal
        valor_produtos: Valor total dos produtos
        valor_icms: Valor do ICMS
        valor_ipi: Valor do IPI
        data_emissao: Data de emissão da NF-e
        natureza_operacao: Natureza da operação (ex: "Venda", "Devolução")
        xml_content: Conteúdo completo do XML da NF-e
        status: Status atual da nota no sistema
        observacoes: Campo para observações adicionais
        created_at: Data de criação do registro
        updated_at: Data da última atualização
    """
    __tablename__ = "invoices"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    
    # Identificadores da NF-e
    numero = Column(String(20), nullable=False, index=True)
    serie = Column(String(10), nullable=False)
    chave_acesso = Column(String(44), unique=True, nullable=False, index=True)
    
    # Dados do emitente
    cnpj_emitente = Column(String(14), nullable=False, index=True)
    razao_social_emitente = Column(String(255), nullable=False)
    
    # Dados do destinatário
    cnpj_destinatario = Column(String(14), nullable=False, index=True)
    razao_social_destinatario = Column(String(255), nullable=False)
    
    # Valores
    valor_total = Column(Numeric(15, 2), nullable=False)
    valor_produtos = Column(Numeric(15, 2), nullable=True)
    valor_icms = Column(Numeric(15, 2), nullable=True, default=0)
    valor_ipi = Column(Numeric(15, 2), nullable=True, default=0)
    
    # Informações fiscais
    data_emissao = Column(DateTime, nullable=False, index=True)
    natureza_operacao = Column(String(100), nullable=True)
    
    # Conteúdo XML completo
    xml_content = Column(Text, nullable=False)
    
    # Status e controle
    status = Column(
        Enum(InvoiceStatus),
        nullable=False,
        default=InvoiceStatus.PENDENTE,
        index=True
    )
    observacoes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    def __repr__(self) -> str:
        return (
            f"<Invoice(numero={self.numero}, "
            f"chave_acesso={self.chave_acesso[:10]}..., "
            f"status={self.status})>"
        )