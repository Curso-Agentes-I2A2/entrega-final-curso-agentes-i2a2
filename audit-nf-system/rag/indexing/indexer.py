# rag/indexing/indexer.py

import os
import logging
from typing import List

from langchain_community.document_loaders import TextLoader, DirectoryLoader
# from langchain_core.documents import Document
from langchain_core.documents import Document

from indexing.chunker import chunk_document
from vector_store.chromadb.client import ChromaDBClient # Exemplo, poderia ser abstrato
from config import settings



class DocumentIndexer:
    def __init__(self):
        # Em um sistema maior, você poderia injetar a dependência do vector store
        # com base na configuração.
        if settings.VECTOR_STORE_PROVIDER == "chromadb":
            self.vector_store = ChromaDBClient()
        else:
            # Aqui você inicializaria o PineconeClient
            raise NotImplementedError("Pinecone ainda não implementado.")
            
    def index_single_document(self, content: str, metadata: dict) -> None:
        """Indexa o conteúdo de um único documento."""
        doc = Document(page_content=content, metadata=metadata)
        chunked_docs = chunk_document(doc)
        self.vector_store.add_documents(chunked_docs)

    def index_folder(self, folder_path: str) -> None:
        """
        Carrega, chunk, e indexa todos os documentos de uma pasta.
        Suporta arquivos .txt por padrão.
        """
        logging.info(f"Iniciando indexação da pasta: {folder_path}")
        loader = DirectoryLoader(folder_path, glob="**/*.txt", loader_cls=TextLoader)
        documents = loader.load()
        
        if not documents:
            logging.warning(f"Nenhum documento encontrado em {folder_path}")
            return
            
        all_chunks = []
        for doc in documents:
            # Adiciona metadados padrão se não existirem
            doc.metadata.setdefault("doc_type", "regulamento")
            doc.metadata.setdefault("state", "BR")
            
            chunks = chunk_document(doc)
            all_chunks.extend(chunks)
            
        self.vector_store.add_documents(all_chunks)
        logging.info(f"Indexação da pasta {folder_path} concluída. {len(all_chunks)} chunks adicionados.")

# Exemplo de uso
# if __name__ == "__main__":
#     indexer = DocumentIndexer()
#     indexer.index_folder("./data/sample_docs/")
#     print("Indexação de exemplo concluída.")
