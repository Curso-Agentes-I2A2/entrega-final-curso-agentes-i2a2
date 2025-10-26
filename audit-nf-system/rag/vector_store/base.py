# rag/vector_store/base.py

from abc import ABC, abstractmethod
from typing import List, Tuple, Dict, Any
from langchain_core.documents import Document

class VectorStore(ABC):
    """
    Classe base abstrata para implementações de Vector Stores.
    """
    @abstractmethod
    def add_documents(self, documents: List[Document]) -> None:
        """Adiciona documentos ao vector store."""
        pass

    @abstractmethod
    def search_with_scores(self, query: str, k: int = 5, filters: Dict[str, Any] = None) -> List[Tuple[Document, float]]:
        """Busca por documentos similares e retorna com seus scores de similaridade."""
        pass

    @abstractmethod
    def delete_collection(self) -> None:
        """Deleta a coleção/índice inteiro."""
        pass

    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas sobre o vector store."""
        pass
