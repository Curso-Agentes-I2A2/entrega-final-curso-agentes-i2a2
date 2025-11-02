import logging
import chromadb
from typing import List, Tuple, Dict, Any

# from langchain_core.documents import Document
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma

from config import settings
from vector_store.base import VectorStore as BaseVectorStore
from embeddings.embedding_model import embedding_manager

class ChromaDBClient(BaseVectorStore):
    """Implementação do cliente de Vector Store para ChromaDB."""
    def __init__(self):
        self.persist_directory = settings.CHROMA_PERSIST_DIRECTORY
        self.collection_name = settings.CHROMA_COLLECTION_NAME
        self.embedding_function = embedding_manager.get_embedding_model()
        
        # O cliente ChromaDB é usado para operações de gerenciamento
        self._client = chromadb.PersistentClient(path=self.persist_directory)
        
        # A integração LangChain é usada para busca e adição de forma conveniente
        self.langchain_chroma = Chroma(
            client=self._client,
            collection_name=self.collection_name,
            embedding_function=self.embedding_function,
            persist_directory=self.persist_directory
        )
        logging.info(f"ChromaDBClient inicializado para a coleção '{self.collection_name}' em '{self.persist_directory}'")

    def add_documents(self, documents: List[Document]) -> None:
        """Adiciona documentos ao ChromaDB."""
        if not documents:
            logging.warning("Nenhum documento para adicionar.")
            return
        
        logging.info(f"Adicionando {len(documents)} documentos ao ChromaDB...")
        self.langchain_chroma.add_documents(documents=documents)
        logging.info("Documentos adicionados com sucesso.")

    def search_with_scores(self, query: str, k: int = 5, filters: Dict[str, Any] = None) -> List[Tuple[Document, float]]:
        """Busca por documentos similares no ChromaDB."""
        logging.info(f"Realizando busca por similaridade para a query: '{query[:50]}...'")
        results = self.langchain_chroma.similarity_search_with_score(
            query=query,
            k=k,
            filter=filters
        )
        return results

    def delete_collection(self) -> None:
        """Deleta a coleção do ChromaDB."""
        logging.warning(f"Deletando a coleção '{self.collection_name}' do ChromaDB.")
        self.langchain_chroma.delete_collection()

    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas da coleção."""
        collection = self.langchain_chroma._collection
        count = collection.count()
        return {
            "provider": "ChromaDB",
            "collection_name": self.collection_name,
            "document_count": count,
            "persist_directory": self.persist_directory
        }
