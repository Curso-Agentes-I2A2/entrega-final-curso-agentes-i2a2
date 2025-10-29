import os
from pydantic_settings import BaseSettings
from typing import Literal

# Carrega o arquivo .env se ele existir
from dotenv import load_dotenv
load_dotenv()

class Settings(BaseSettings):
    # --- Configurações de Provedores ---
    VECTOR_STORE_PROVIDER: Literal["chromadb", "pinecone"] = "chromadb"
    EMBEDDING_PROVIDER: Literal["openai", "local"] = "openai"
    
    # --- Chaves de API ---
    OPENAI_API_KEY: str | None = None
    PINECONE_API_KEY: str | None = None
    COHERE_API_KEY: str | None = None
    
    # --- Configurações de Embeddings ---
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    LOCAL_EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # --- Configurações de Chunking ---
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    
    # --- Configurações do ChromaDB ---
    CHROMA_PERSIST_DIRECTORY: str = "./vector_store/chromadb/db"
    CHROMA_COLLECTION_NAME: str = "fiscal_docs"

    # --- Configurações do Query Engine ---
    DEFAULT_SEARCH_K: int = 5
    SIMILARITY_THRESHOLD: float = 0.7
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

# Instância única das configurações para ser importada em todo o projeto
settings = Settings()
