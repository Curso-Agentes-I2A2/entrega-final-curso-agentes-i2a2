# rag/main.py

import logging
import uvicorn
from fastapi import FastAPI
from api import routes

# Configuração do logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

app = FastAPI(
    title="API de RAG para Auditoria Fiscal",
    description="Sistema para busca semântica em documentos de legislação fiscal.",
    version="1.0.0"
)

# Inclui as rotas da API
app.include_router(routes.router, prefix="/api/v1")

@app.get("/health", tags=["Monitoring"])
async def health_check():
    """Verifica se a aplicação está no ar."""
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
