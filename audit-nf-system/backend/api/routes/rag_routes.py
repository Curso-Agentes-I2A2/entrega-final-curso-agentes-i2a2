# backend/routes/rag_routes.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/rag", tags=["RAG"])

class QueryRequest(BaseModel):
    question: str
    state: str = ""
    tax_type: str = ""
    top_k: int = 3

@router.post("/consultar")
async def consultar_legislacao(request: QueryRequest):
    """
    Consulta a base regulatória usando RAG
    """
    from rag.retrieval.query_engine import QueryEngine
    
    engine = QueryEngine()
    
    # Filtros por metadados (se fornecidos)
    filters = {}
    if request.state:
        filters["state"] = request.state
    if request.tax_type:
        filters["tax_type"] = request.tax_type
    
    results = engine.search_with_score(
        query=request.question,
        k=request.top_k,
        filters=filters
    )
    
    return {
        "question": request.question,
        "results": [
            {
                "content": doc.page_content,
                "score": score,
                "metadata": doc.metadata
            }
            for doc, score in results
        ]
    }