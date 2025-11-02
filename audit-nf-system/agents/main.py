"""
Sistema de Auditoria de NF-e com Agentes IA
FastAPI Application

Este é o ponto de entrada da aplicação que orquestra múltiplos agentes
para validação e auditoria de Notas Fiscais Eletrônicas.
"""
import time
import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Dict, Optional

from fastapi import FastAPI, Request, status, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from config import settings
from api.routes import router
from orchestrator.coordinator import AgentCoordinator

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('agents.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Instância global do coordenador (será inicializada no startup)
coordinator: Optional[AgentCoordinator] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerencia o ciclo de vida da aplicação
    """
    # Startup
    logger.info("🚀 Iniciando Sistema de Auditoria de NF-e")
    
    global coordinator
    coordinator = AgentCoordinator()
    
    logger.info("✅ Agentes inicializados com sucesso")
    logger.info(f"🔧 Ambiente: {settings.ENVIRONMENT}")
    
    yield
    
    # Shutdown
    logger.info("🛑 Encerrando aplicação...")
    # Cleanup se necessário


# Criar aplicação FastAPI
app = FastAPI(
    title="Sistema de Auditoria NF-e",
    description="API para validação e auditoria automatizada de Notas Fiscais Eletrônicas usando agentes IA",
    version="1.0.0",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware para logar informações de cada requisição HTTP.
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    logger.info(f"Requisição recebida: {request.method} {request.url.path}")
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000  # em milissegundos
    logger.info(f"Requisição finalizada: {request.method} {request.url.path} - Status: {response.status_code} - Duração: {process_time:.2f}ms")
    return response

# --- Inclusão das Rotas da API ---
# Adiciona todos os endpoints definidos em `api/routes.py` com um prefixo.
app.include_router(router, prefix="/api/v1", tags=["Agentes"])

# --- Eventos de Ciclo de Vida da Aplicação ---
@app.on_event("startup")
async def startup_event():
    """Executa ações quando a aplicação inicia."""
    logger.info("Aplicação iniciada com sucesso.")
    logger.info(f"LLM Primário: {settings.llm.primary_provider} ({settings.llm.primary_model})")
    logger.info(f"LLM Fallback: {settings.llm.fallback_provider} ({settings.llm.secondary_model})")

@app.on_event("shutdown")
def shutdown_event():
    """Executa ações quando a aplicação desliga."""
    logger.info("Aplicação encerrada.")

# Para rodar a aplicação: uvicorn main:app --reload --app-dir .

# Incluir rotas
app.include_router(router, prefix="/api/v1")


@app.get("/")
async def root():
    """
    Endpoint raiz com informações da API
    """
    return {
        "service": "Sistema de Auditoria NF-e",
        "version": "1.0.0",
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat(),
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint
    Verifica status de todos os componentes
    """
    try:
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "components": {
                "api": "operational",
                "agents": "operational" if coordinator else "not_initialized",
                "rag_service": "unknown",  # Pode adicionar verificação real
            },
            "environment": settings.ENVIRONMENT
        }
        
        # Verificar se agentes estão inicializados
        if not coordinator:
            health_status["status"] = "degraded"
            health_status["components"]["agents"] = "not_initialized"
        
        return health_status
        
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )


@app.websocket("/ws/stream")
async def websocket_stream(websocket: WebSocket):
    """
    WebSocket endpoint para streaming de execução dos agentes
    Permite acompanhar o processamento em tempo real
    """
    await websocket.accept()
    logger.info("🔌 Cliente WebSocket conectado")
    
    try:
        while True:
            # Receber dados do cliente
            data = await websocket.receive_json()
            
            # Processar com streaming
            await websocket.send_json({
                "type": "status",
                "message": "Iniciando processamento...",
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Simular steps do processamento
            steps = [
                "Validando estrutura da nota fiscal...",
                "Verificando CNPJ do emitente...",
                "Consultando base de conhecimento...",
                "Auditando impostos...",
                "Gerando relatório final..."
            ]
            
            for i, step in enumerate(steps):
                await websocket.send_json({
                    "type": "progress",
                    "step": i + 1,
                    "total": len(steps),
                    "message": step,
                    "timestamp": datetime.utcnow().isoformat()
                })
                
                # Aqui você integraria com o processamento real
                # result = await coordinator.process_invoice_stream(data, websocket)
            
            # Resultado final
            await websocket.send_json({
                "type": "complete",
                "message": "Processamento concluído",
                "timestamp": datetime.utcnow().isoformat()
            })
            
    except WebSocketDisconnect:
        logger.info("🔌 Cliente WebSocket desconectado")
    except Exception as e:
        logger.error(f"❌ Erro no WebSocket: {e}")
        await websocket.send_json({
            "type": "error",
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat()
        })


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """
    Handler global para HTTPException
    """
    logger.error(f"❌ HTTP Error: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """
    Handler global para exceções não tratadas
    """
    logger.error(f"❌ Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "timestamp": datetime.utcnow().isoformat()
        }
    )


def get_coordinator() -> AgentCoordinator:
    """
    Dependency injection para obter instância do coordenador
    """
    if coordinator is None:
        raise HTTPException(
            status_code=503,
            detail="Agent coordinator not initialized"
        )
    return coordinator


if __name__ == "__main__":
    """
    Executar aplicação diretamente
    """
    logger.info("🚀 Iniciando servidor...")
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=False,
        log_level="info"
    )