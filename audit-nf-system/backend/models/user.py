"""
Modelo SQLAlchemy para Usuário do sistema.
"""
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from database.connection import Base


class User(Base):
    """
    Modelo de Usuário do sistema.
    
    Armazena informações de usuários que podem acessar o sistema,
    incluindo credenciais e permissões.
    
    Attributes:
        id: Identificador único (UUID)
        email: Email do usuário (único)
        username: Nome de usuário
        hashed_password: Senha hasheada (bcrypt)
        full_name: Nome completo
        is_active: Se o usuário está ativo
        is_superuser: Se o usuário tem privilégios de admin
        created_at: Data de criação
        updated_at: Data da última atualização
    """
    __tablename__ = "users"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    
    full_name = Column(String(255), nullable=True)
    
    # Flags de controle
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    def __repr__(self) -> str:
        return f"<User(username={self.username}, email={self.email})>"