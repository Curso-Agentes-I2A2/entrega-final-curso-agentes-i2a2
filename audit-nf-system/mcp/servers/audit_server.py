
import httpx
from pydantic import BaseModel, Field

# ... (outras classes Pydantic)
class FiscalQueryInput(BaseModel):
    query: str = Field(..., description="Pergunta em linguagem natural sobre legislação fiscal.")

# ... (outras ferramentas)
@audit_server.tool()
async def consult_fiscal_regulation(request: Request, p: FiscalQueryInput) -> Response:
    """
    Consulta a base de conhecimento RAG para obter informações sobre regulamentos fiscais.
    """
    rag_api_url = "http://localhost:8000/api/v1/search" # URL da nossa API RAG
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                rag_api_url, 
                json={"query": p.query, "k": 3},
                timeout=15.0
            )
            response.raise_for_status()
            
            # Retorna os documentos encontrados pelo RAG
            return server.create_json_response(response.json())
            
    except httpx.RequestError as e:
        logging.error(f"Erro ao se comunicar com a API RAG: {e}")
        return server.create_error_response(
            code=503, 
            message=f"Serviço de conhecimento fiscal indisponível: {e}"
        )
    except Exception as e:
        logging.error(f"Erro inesperado ao consultar RAG: {e}")
        return server.create_error_response(code=500, message=str(e))