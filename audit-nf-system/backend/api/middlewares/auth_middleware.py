# """
# Middleware de autenticação JWT.

# Valida tokens JWT e gerencia autenticação de usuários.
# """
# from fastapi import Depends, HTTPException, status
# from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
# from jose import JWTError, jwt
# from datetime import datetime, timedelta
# from typing import Optional
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy import select

# from config import settings
# from models.user import User
# from database.connection import get_db
# import logging

# logger = logging.getLogger(__name__)

# # Security scheme
# security = HTTPBearer()


# class AuthMiddleware:
#     """
#     Middleware para autenticação JWT.
    
#     Valida tokens e gerencia sessões de usuários.
#     """
    
#     @staticmethod
#     def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
#         """
#         Cria token JWT de acesso.
        
#         Args:
#             data: Dados a serem codificados no token
#             expires_delta: Tempo de expiração customizado
        
#         Returns:
#             Token JWT codificado
#         """
#         to_encode = data.copy()
        
#         if expires_delta:
#             expire = datetime.utcnow() + expires_delta
#         else:
#             expire = datetime.utcnow() + timedelta(
#                 minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
#             )
        
#         to_encode.update({"exp": expire})
        
#         encoded_jwt = jwt.encode(
#             to_encode,
#             settings.SECRET_KEY,
#             algorithm=settings.ALGORITHM
#         )
        
#         return encoded_jwt
    
#     @staticmethod
#     def verify_token(token: str) -> dict:
#         """
#         Verifica e decodifica token JWT.
        
#         Args:
#             token: Token JWT
        
#         Returns:
#             Dados decodificados do token
        
#         Raises:
#             HTTPException: Se token inválido ou expirado
#         """
#         try:
#             payload = jwt.decode(
#                 token,
#                 settings.SECRET_KEY,
#                 algorithms=[settings.ALGORITHM]
#             )
#             return payload
#         except JWTError as e:
#             logger.error(f"Erro ao validar token: {e}")
#             raise HTTPException(
#                 status_code=status.HTTP_401_UNAUTHORIZED,
#                 detail="Token inválido ou expirado",
#                 headers={"WWW-Authenticate": "Bearer"},
#             )


# async def get_current_user(
#     credentials: HTTPAuthorizationCredentials = Depends(security),
#     db: AsyncSession = Depends(get_db)
# ) -> User:
#     """
#     Dependency para obter usuário atual autenticado.
    
#     Args:
#         credentials: Credenciais HTTP Bearer
#         db: Sessão do banco de dados
    
#     Returns:
#         Usuário autenticado
    
#     Raises:
#         HTTPException: Se token inválido ou usuário não existe
    
#     Uso:
#         @app.get("/protected")
#         async def protected_route(current_user: User = Depends(get_current_user)):
#             return {"user": current_user.username}
#     """
#     token = credentials.credentials
    
#     # Verifica token
#     payload = AuthMiddleware.verify_token(token)
    
#     # Extrai user_id do payload
#     user_id: str = payload.get("sub")
#     if user_id is None:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Token inválido",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
    
#     # Busca usuário no banco
#     result = await db.execute(
#         select(User).where(User.id == user_id)
#     )
#     user = result.scalar_one_or_none()
    
#     if user is None:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Usuário não encontrado",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
    
#     # Verifica se usuário está ativo
#     if not user.is_active:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Usuário inativo"
#         )
    
#     return user


# async def get_current_active_superuser(
#     current_user: User = Depends(get_current_user)
# ) -> User:
#     """
#     Dependency para verificar se usuário é superuser.
    
#     Args:
#         current_user: Usuário atual
    
#     Returns:
#         Usuário se for superuser
    
#     Raises:
#         HTTPException 403: Se não for superuser
    
#     Uso:
#         @app.delete("/admin/users/{id}")
#         async def delete_user(
#             user_id: UUID,
#             admin: User = Depends(get_current_active_superuser)
#         ):
#             # Apenas admins podem deletar usuários
#             ...
#     """
#     if not current_user.is_superuser:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Privilégios insuficientes"
#         )
#     return current_user


# # Dependency opcional (permite acesso sem autenticação)
# async def get_current_user_optional(
#     credentials: Optional[HTTPAuthorizationCredentials] = Depends(
#         HTTPBearer(auto_error=False)
#     ),
#     db: AsyncSession = Depends(get_db)
# ) -> Optional[User]:
#     """
#     Dependency para obter usuário se autenticado (opcional).
    
#     Args:
#         credentials: Credenciais HTTP Bearer (opcional)
#         db: Sessão do banco de dados
    
#     Returns:
#         Usuário autenticado ou None
    
#     Uso:
#         @app.get("/items")
#         async def list_items(current_user: Optional[User] = Depends(get_current_user_optional)):
#             # Comportamento diferente se usuário estiver autenticado
#             if current_user:
#                 # Mostra itens privados
#                 ...
#             else:
#                 # Mostra apenas itens públicos
#                 ...
#     """
#     if credentials is None:
#         return None
    
#     try:
#         return await get_current_user(credentials, db)
#     except HTTPException:
#         return None