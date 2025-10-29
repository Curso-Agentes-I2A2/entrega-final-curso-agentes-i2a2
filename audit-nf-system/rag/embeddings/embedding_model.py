import logging
from typing import List
from functools import lru_cache

from langchain_openai import OpenAIEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings


from ..config import settings

class EmbeddingManager:
    """
    Gerencia a criação e o uso de modelos de embedding, com fallback.
    """
    def __init__(self):
        self.openai_embeddings = self._init_openai()
        self.local_embeddings = self._init_local()
        logging.info(f"Gerenciador de Embeddings inicializado com o provedor: {settings.EMBEDDING_PROVIDER}")

    def _init_openai(self):
        if settings.OPENAI_API_KEY:
            try:
                return OpenAIEmbeddings(
                    model=settings.OPENAI_EMBEDDING_MODEL,
                    api_key=settings.OPENAI_API_KEY
                )
            except Exception as e:
                logging.warning(f"Falha ao inicializar OpenAI Embeddings: {e}. Verifique sua API key.")
        return None

    def _init_local(self):
        try:
            return HuggingFaceEmbeddings(model_name=settings.LOCAL_EMBEDDING_MODEL)
        except Exception as e:
            logging.error(f"Falha ao carregar modelo de embedding local: {e}")
            raise RuntimeError("Não foi possível carregar o modelo de embedding local.") from e
            
    def get_embedding_model(self):
        """
        Retorna a instância do modelo de embedding com base na configuração e disponibilidade.
        Tenta OpenAI primeiro (se configurado), senão usa o modelo local como fallback.
        """
        if settings.EMBEDDING_PROVIDER == "openai" and self.openai_embeddings:
            return self.openai_embeddings
        return self.local_embeddings

    @lru_cache(maxsize=128)
    def embed_query(self, text: str) -> List[float]:
        """
        Gera o embedding para uma única query de texto.
        Usa cache para evitar reprocessamento de queries repetidas.
        """
        model = self.get_embedding_model()
        logging.info(f"Gerando embedding para query com {model.__class__.__name__}")
        try:
            return model.embed_query(text)
        except Exception as e:
            logging.error(f"Erro ao gerar embedding para query: {e}. Tentando fallback se disponível.")
            if model == self.openai_embeddings and self.local_embeddings:
                logging.warning("Fallback para modelo local de embedding.")
                return self.local_embeddings.embed_query(text)
            raise e

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Gera embeddings para uma lista de documentos."""
        model = self.get_embedding_model()
        logging.info(f"Gerando {len(texts)} embeddings para documentos com {model.__class__.__name__}")
        try:
            return model.embed_documents(texts)
        except Exception as e:
            logging.error(f"Erro ao gerar embeddings para documentos: {e}. Tentando fallback se disponível.")
            if model == self.openai_embeddings and self.local_embeddings:
                logging.warning("Fallback para modelo local de embedding.")
                return self.local_embeddings.embed_documents(texts)
            raise e

# Instância única para ser usada na aplicação
embedding_manager = EmbeddingManager()
