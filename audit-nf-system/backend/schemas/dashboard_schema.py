# backend/schemas/dashboard_schema.py

from pydantic import BaseModel
from datetime import datetime

class DashboardStats(BaseModel):
    """
    Schema para as estatísticas consolidadas do dashboard.
    """
    total_invoices: int
    pending_invoices: int
    total_audits: int
    approved_audits: int
    rejected_audits: int
    approval_rate: float
    avg_processing_time: float | None
    timestamp: datetime

    class Config:
        from_attributes = True # Pydantic v2 (ou orm_mode = True)