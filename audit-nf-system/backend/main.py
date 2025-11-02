"""
Aplicação principal FastAPI - Sistema de Auditoria de Notas Fiscais.

Entry point da API REST.
"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import logging
import sys

from config import settings
from database.connection import init_db, close_db
from api.routes import invoice_routes, audit_routes
from api.routes import synthetic_routes
from api.routes import dashboard_routes
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configuração de logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Context manager para gerenciar lifecycle da aplicação.
    
    Executa tarefas de inicialização no startup e limpeza no shutdown.
    """
    # Startup
    logger.info("Iniciando aplicação...")
    logger.info(f"Ambiente: {'DEBUG' if settings.DEBUG else 'PRODUCTION'}")
    
    try:
        await init_db()
        logger.info("Banco de dados inicializado com sucesso")
    except Exception as e:
        logger.error(f"Erro ao inicializar banco de dados: {e}")
        raise
    
    logger.info(f"API disponível em: http://{settings.HOST}:{settings.PORT}")
    logger.info(f"Documentação: http://{settings.HOST}:{settings.PORT}/docs")
    
    yield
    
    # Shutdown
    logger.info("Encerrando aplicação...")
    await close_db()
    logger.info("Aplicação encerrada")


# Cria aplicação FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "API REST para sistema de auditoria automatizada de Notas Fiscais Eletrônicas (NF-e). "
        "Permite upload de XMLs, validação automática e integração com IA."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)


# Configuração de CORS para permitir frontend Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Middleware de logging de requisições
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Middleware para logging de todas as requisições HTTP.
    """
    logger.info(f"{request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"Status: {response.status_code}")
    return response


# Tratamento global de erros de validação
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handler customizado para erros de validação Pydantic.
    
    Retorna mensagens de erro mais amigáveis.
    """
    errors = []
    for error in exc.errors():
        errors.append({
            "field": " -> ".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Erro de validação",
            "errors": errors
        }
    )


# Tratamento global de exceções não tratadas
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Handler para exceções não tratadas.
    
    Loga o erro completo e retorna mensagem genérica ao cliente.
    """
    logger.error(f"Erro não tratado: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Erro interno do servidor",
            "message": str(exc) if settings.DEBUG else "Ocorreu um erro inesperado"
        }
    )


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Endpoint de health check.
    
    Verifica se a aplicação está rodando e se consegue conectar ao banco.
    
    Returns:
        Status da aplicação e seus componentes
    """
    from database.connection import async_engine
    from sqlalchemy import text
    
    # Verifica conexão com banco
    db_status = "healthy"
    try:
        async with async_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
        logger.error(f"Health check - Erro no banco: {e}")
    
    # Verifica RAG service (opcional)
    rag_status = "configured" if settings.RAG_SERVICE_URL else "not_configured (using mock)"
    
    # Verifica Agent service (opcional)
    agent_status = "configured" if settings.AGENT_SERVICE_URL else "not_configured (using mock)"
    
    overall_status = "healthy" if db_status == "healthy" else "degraded"
    
    return {
        "status": overall_status,
        "version": settings.APP_VERSION,
        "components": {
            "database": db_status,
            "rag_service": rag_status,
            "agent_service": agent_status
        }
    }


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Endpoint raiz com informações básicas da API.
    """
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health"
    }


# Inclusão de routers
app.include_router(invoice_routes.router)
app.include_router(audit_routes.router)
app.include_router(synthetic_routes.router)
app.include_router(dashboard_routes.router)

# Ponto de entrada para execução direta
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )