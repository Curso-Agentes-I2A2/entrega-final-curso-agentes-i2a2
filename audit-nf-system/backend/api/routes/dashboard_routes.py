# backend/api/routes/dashboard_routes.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from database.connection import get_db
from services.dashboard_service import DashboardService
from schemas.dashboard_schema import DashboardStats

logger = logging.getLogger(__name__)

# --- Configuração do Router ---
router = APIRouter(
    prefix="/api/dashboard", # <--- Segue o padrão do seu projeto
    tags=["Dashboard & Stats"]
)

@router.get(
    "/summary",
    response_model=DashboardStats,
    summary="Sumário de Estatísticas do Dashboard"
)
async def get_dashboard_summary(db: AsyncSession = Depends(get_db)):
    """
    Retorna as principais métricas e estatísticas do sistema
    consolidadas para o frontend (Streamlit).
    """
    try:
        service = DashboardService(db)
        summary = await service.get_dashboard_summary()
        return summary
    except Exception as e:
        logger.error(f"Erro ao buscar sumário do dashboard: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno ao processar estatísticas: {e}"
        )