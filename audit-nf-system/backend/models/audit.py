"""
Modelo SQLAlchemy para Auditoria de Notas Fiscais.
"""
from sqlalchemy import Column, String, Text, Numeric, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from database.connection import Base


class AuditStatus(str, enum.Enum):
    """Status possíveis de uma auditoria."""
    PENDENTE = "pendente"
    EM_ANDAMENTO = "em_andamento"
    CONCLUIDA = "concluida"
    ERRO = "erro"


class AuditResult(str, enum.Enum):
    """Resultado final de uma auditoria."""
    APROVADA = "aprovada"
    REJEITADA = "rejeitada"
    REVISAO_NECESSARIA = "revisao_necessaria"


class Audit(Base):
    """
    Modelo de Auditoria de Nota Fiscal.
    
    Armazena o resultado da análise automatizada de uma NF-e,
    incluindo irregularidades encontradas, nível de confiança
    e informações do agente de IA responsável.
    
    Attributes:
        id: Identificador único (UUID)
        nota_fiscal_id: FK para a nota fiscal auditada
        status: Status atual da auditoria
        resultado: Resultado final (aprovada/rejeitada/revisão)
        resultado_detalhado: JSON com análise detalhada
        irregularidades: Array de strings com irregularidades encontradas
        confianca: Score de confiança da análise (0-1)
        agente_responsavel: Nome/ID do agente de IA que realizou a auditoria
        tempo_processamento: Tempo gasto na auditoria (em segundos)
        observacoes: Observações adicionais do auditor/sistema
        dados_rag: Dados retornados pelo sistema RAG
        created_at: Data de criação da auditoria
        updated_at: Data da última atualização
    """
    __tablename__ = "audits"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    
    # Relacionamento com nota fiscal
    nota_fiscal_id = Column(
        UUID(as_uuid=True),
        ForeignKey("invoices.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Status e resultado
    status = Column(
        Enum(AuditStatus),
        nullable=False,
        default=AuditStatus.PENDENTE,
        index=True
    )
    
    resultado = Column(
        Enum(AuditResult),
        nullable=True,
        index=True
    )
    
    # Análise detalhada em formato JSON
    # Estrutura exemplo:
    # {
    #   "validacoes": {
    #     "chave_acesso": {"valido": true, "mensagem": "OK"},
    #     "valores": {"valido": false, "mensagem": "Divergência detectada"}
    #   },
    #   "analise_fiscal": {...},
    #   "recomendacoes": [...]
    # }
    resultado_detalhado = Column(JSONB, nullable=True)
    
    # Irregularidades encontradas (array de strings)
    irregularidades = Column(
        ARRAY(String),
        nullable=True,
        default=[]
    )
    
    # Score de confiança (0.0 a 1.0)
    confianca = Column(
        Numeric(3, 2),
        nullable=True,
        comment="Score de confiança entre 0 e 1"
    )
    
    # Informações do agente
    agente_responsavel = Column(String(100), nullable=True)
    
    # Métricas
    tempo_processamento = Column(
        Numeric(10, 2),
        nullable=True,
        comment="Tempo de processamento em segundos"
    )
    
    # Campos adicionais
    observacoes = Column(Text, nullable=True)
    
    # Dados do RAG (contexto usado na análise)
    dados_rag = Column(JSONB, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    # Relacionamento
    nota_fiscal = relationship("Invoice", backref="auditorias")

    def __repr__(self) -> str:
        return (
            f"<Audit(id={self.id}, "
            f"nota_fiscal_id={self.nota_fiscal_id}, "
            f"resultado={self.resultado}, "
            f"confianca={self.confianca})>"
        )