import logging
from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel, Field
from typing import List, Dict, Any


from retrieval.query_engine import QueryEngine
from indexing.indexer import DocumentIndexer

router = APIRouter()
query_engine = QueryEngine()
indexer = DocumentIndexer()

# --- Pydantic Models for API ---
class SearchRequest(BaseModel):
    query: str = Field(..., min_length=3, description="Texto da busca.")
    k: int = Field(5, gt=0, le=20, description="Número de documentos a retornar.")
    filters: Dict[str, Any] | None = Field(None, description="Filtros de metadados para a busca.")

class SearchResponse(BaseModel):
    source: str
    content: str
    score: float
    metadata: Dict[str, Any]

class IndexRequest(BaseModel):
    content: str = Field(..., description="Conteúdo do documento a ser indexado.")
    metadata: Dict[str, Any] = Field(..., description="Metadados associados (source, doc_type, etc).")

# --- API Endpoints ---
@router.post("/search", response_model=List[SearchResponse])
async def search_documents(request: SearchRequest):
    """
    Endpoint para realizar uma busca semântica nos documentos indexados.
    """
    try:
        results = query_engine.search_with_score(request.query, request.k, request.filters)
        
        response = [
            SearchResponse(
                source=doc.metadata.get("source", "N/A"),
                content=doc.page_content,
                score=score,
                metadata=doc.metadata
            ) for doc, score in results
        ]
        return response
    except Exception as e:
        logging.error(f"Erro na busca: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Erro interno ao processar a busca.")

@router.post("/index", status_code=201)
async def index_document(request: IndexRequest):
    """
    Endpoint para indexar um novo documento.
    """
    try:
        indexer.index_single_document(request.content, request.metadata)
        return {"message": "Documento indexado com sucesso."}
    except Exception as e:
        logging.error(f"Erro na indexação: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Erro interno ao indexar o documento.")

@router.get("/stats")
async def get_vector_store_stats():
    """Retorna estatísticas do vector store."""
    return query_engine.vector_store.get_stats()

@router.delete("/clear", status_code=200)
async def clear_index():
    """Limpa completamente o índice/coleção de vetores."""
    try:
        query_engine.vector_store.delete_collection()
        return {"message": "Índice limpo com sucesso."}
    except Exception as e:
        logging.error(f"Erro ao limpar o índice: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Erro ao limpar o índice.")
