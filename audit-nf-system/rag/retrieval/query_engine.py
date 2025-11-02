import logging
from typing import List, Tuple, Dict, Any

from langchain_core.documents import Document
from vector_store.chromadb.client import ChromaDBClient
from config import settings

class QueryEngine:
    def __init__(self):
        if settings.VECTOR_STORE_PROVIDER == "chromadb":
            self.vector_store = ChromaDBClient()
        else:
            raise NotImplementedError("Pinecone ainda não implementado.")
            
    def search_with_score(
        self,
        query: str,
        k: int = settings.DEFAULT_SEARCH_K,
        filters: Dict[str, Any] = None
    ) -> List[Tuple[Document, float]]:
        """
        Realiza uma busca e retorna documentos com seus scores.
        """
        if not query:
            return []
            
        results = self.vector_store.search_with_scores(query, k, filters)
        
        # Filtra resultados com base no threshold de similaridade
        filtered_results = [
            (doc, score) for doc, score in results if score >= settings.SIMILARITY_THRESHOLD
        ]
        
        logging.info(f"Busca encontrou {len(results)} resultados, {len(filtered_results)} acima do threshold.")
        return filtered_results

    def search(
        self,
        query: str,
        k: int = settings.DEFAULT_SEARCH_K,
        filters: Dict[str, Any] = None
    ) -> List[Document]:
        """
        Realiza uma busca e retorna apenas a lista de documentos.
        """
        results_with_scores = self.search_with_score(query, k, filters)
        return [doc for doc, score in results_with_scores]

# Exemplo de uso
# if __name__ == "__main__":
#     engine = QueryEngine()
#     query = "Como é calculado o ICMS em operações interestaduais?"
#     results = engine.search_with_score(query)
#     for doc, score in results:
#         print(f"Score: {score:.4f}")
#         print(f"Fonte: {doc.metadata.get('source')}")
#         print(f"Conteúdo: {doc.page_content[:200]}...\n")

