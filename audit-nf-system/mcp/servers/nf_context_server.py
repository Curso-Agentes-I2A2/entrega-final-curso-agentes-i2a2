import logging
from fastapi import FastAPI
import uvicorn

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# API REST simples
app = FastAPI(title="MCP Server")

@app.get("/")
def root():
    return {"service": "MCP Server", "status": "online", "version": "1.0.0"}

@app.get("/health")
def health():
    return {"status": "healthy", "service": "mcp"}

@app.get("/resources")
def list_resources():
    return {
        "resources": [
            "nf://invoices",
            "nf://invoices/pending", 
            "nf://invoice/{id}"
        ]
    }

@app.post("/context")
def get_context(query: str):
    """Endpoint para fornecer contexto"""
    return {
        "status": "success",
        "query": query,
        "context": "Context service ready"
    }

if __name__ == "__main__":
    logger.info("✅ MCP Server iniciando...")
    uvicorn.run(app, host="0.0.0.0", port=8003)