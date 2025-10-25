# /main.py

import logging
import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

# Importa as rotas que serão definidas no arquivo api/routes.py
from agents.api import routes as api_routes
from agents.config import settings

# --- Configuração do Logger Global ---
# Define um formato padrão para os logs para facilitar a depuração.
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
logger = logging.getLogger(__name__)

# --- Criação da Aplicação FastAPI ---
app = FastAPI(
    title="Sistema de Agentes para Auditoria de NF-e",
    description="Uma API para orquestrar agentes de IA na validação e auditoria de notas fiscais eletrônicas brasileiras.",
    version="1.0.0"
)

# --- Middlewares ---
# Middlewares são funções que processam cada requisição antes de chegar ao endpoint e cada resposta antes de ser enviada.

# Habilita o CORS para permitir que aplicações de outras origens (como um frontend em React) acessem a API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, restrinja para os domínios do seu frontend.
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
app.include_router(api_routes.router, prefix="/api/v1", tags=["Agentes"])

# --- Eventos de Ciclo de Vida da Aplicação ---
@app.on_event("startup")
async def startup_event():
    """Executa ações quando a aplicação inicia."""
    logger.info("Aplicação iniciada com sucesso.")
    logger.info(f"LLM Primário: {settings.llm.primary_provider} ({settings.llm.primary_model})")
    logger.info(f"LLM Fallback: {settings.llm.fallback_provider} ({settings.llm.fallback_model})")

@app.on_event("shutdown")
def shutdown_event():
    """Executa ações quando a aplicação desliga."""
    logger.info("Aplicação encerrada.")

# Para rodar a aplicação: uvicorn main:app --reload --app-dir .