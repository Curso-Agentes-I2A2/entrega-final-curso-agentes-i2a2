# rag/indexing/chunker.py

import logging
from typing import List
# from langchain_core.documents import Document
from langchain_core.documents import Document
# from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_text_splitters import RecursiveCharacterTextSplitter

from ..config import settings

def chunk_document(document: Document) -> List[Document]:
    """
    Divide um documento em chunks menores usando RecursiveCharacterTextSplitter.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
        length_function=len
    )
    
    logging.info(f"Chunking documento: {document.metadata.get('source', 'N/A')}")
    chunks = text_splitter.split_text(document.page_content)
    
    # Cria novos documentos para cada chunk, mantendo os metadados
    chunked_documents = []
    for i, chunk_text in enumerate(chunks):
        chunk_doc = Document(
            page_content=chunk_text,
            metadata={**document.metadata, "chunk_index": i}
        )
        chunked_documents.append(chunk_doc)
        
    logging.info(f"Documento dividido em {len(chunked_documents)} chunks.")
    return chunked_documents
