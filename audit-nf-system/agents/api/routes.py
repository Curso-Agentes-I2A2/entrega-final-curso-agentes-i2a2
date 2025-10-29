# agents/api/routes.py
import logging
from fastapi import APIRouter, HTTPException, Request
from ..orchestrator.coordinator import AgentCoordinator 

logger = logging.getLogger(__name__)
router = APIRouter()

try:
    coordinator = AgentCoordinator()
    logger.info("Coordenador de Agentes inicializado para as rotas.")
except Exception as e:
    logger.critical(f"Falha ao inicializar o AgentCoordinator: {e}", exc_info=True)
    coordinator = None

@router.post("/audit")
async def audit_invoice(request: Request):
    """Endpoint para auditar uma nota fiscal."""
    if coordinator is None:
        raise HTTPException(status_code=503, detail="Serviço indisponível.")
        
    try:
        invoice_data = await request.json()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"JSON mal formatado: {e}")

    try:
        logger.info(f"API: Recebida auditoria para NF {invoice_data.get('Numero')}")
        result = await coordinator.process_invoice(invoice_data) 
        return result
    except Exception as e:
        logger.error(f"Erro inesperado na auditoria: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erro interno: {e}")

@router.get("/health")
def health_check():
    """Endpoint de verificação de saúde."""
    return {"status": "ok", "message": "Serviço de Agentes operando."}