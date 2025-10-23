# rag/requirements.txt

# Core RAG framework
langchain
langchain-community
langchain-openai

# Vector Store
chromadb

# Embeddings
openai
sentence-transformers # For local fallback
torch # Dependency for sentence-transformers

# API Framework
fastapi
uvicorn[standard]

# Configuration Management
pydantic-settings
python-dotenv

# Opcional: Reranking
cohere

# rag/.env.example

# Chave da API da OpenAI para embeddings. Se não for fornecida, o sistema usará o modelo local.
OPENAI_API_KEY="sk-..."

# Chave da API do Pinecone (para uso em produção)
PINECONE_API_KEY=""

# Chave da API da Cohere (para reranking opcional)
COHERE_API_KEY=""

# Escolha do Vector Store: "chromadb" ou "pinecone"
VECTOR_STORE_PROVIDER="chromadb"

# Escolha do Modelo de Embeddings: "openai" ou "local"
EMBEDDING_PROVIDER="openai"

# rag/config.py

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

# rag/embeddings/embedding_model.py

import logging
from typing import List
from functools import lru_cache

from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings

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

# rag/vector_store/base.py

from abc import ABC, abstractmethod
from typing import List, Tuple, Dict, Any
from langchain.docstore.document import Document

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
		
# rag/vector_store/chromadb/client.py

import logging
import chromadb
from typing import List, Tuple, Dict, Any

from langchain.docstore.document import Document
from langchain_community.vectorstores import Chroma

from ...config import settings
from ..base import VectorStore as BaseVectorStore
from ...embeddings.embedding_model import embedding_manager

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

# rag/indexing/chunker.py

import logging
from typing import List
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

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

# rag/indexing/indexer.py

import os
import logging
from typing import List

from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain.docstore.document import Document

from .chunker import chunk_document
from ..vector_store.chromadb.client import ChromaDBClient # Exemplo, poderia ser abstrato

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

# rag/retrieval/query_engine.py

import logging
from typing import List, Tuple, Dict, Any

from langchain.docstore.document import Document
from ..vector_store.chromadb.client import ChromaDBClient
from ..config import settings

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

# rag/api/routes.py

import logging
from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel, Field
from typing import List, Dict, Any

from ..retrieval.query_engine import QueryEngine
from ..indexing.indexer import DocumentIndexer

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

# rag/main.py

import logging
import uvicorn
from fastapi import FastAPI
from api import routes

# Configuração do logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

app = FastAPI(
    title="API de RAG para Auditoria Fiscal",
    description="Sistema para busca semântica em documentos de legislação fiscal.",
    version="1.0.0"
)

# Inclui as rotas da API
app.include_router(routes.router, prefix="/api/v1")

@app.get("/health", tags=["Monitoring"])
async def health_check():
    """Verifica se a aplicação está no ar."""
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

# rag/data/sample_docs/fiscal_regulation_sample.txt

Regulamento do ICMS - Seção I: Fato Gerador

Art. 1º O Imposto sobre Operações Relativas à Circulação de Mercadorias e sobre Prestações de Serviços de Transporte Interestadual e Intermunicipal e de Comunicação (ICMS) incide sobre:
I - operações relativas à circulação de mercadorias, inclusive o fornecimento de alimentação e bebidas em bares, restaurantes e estabelecimentos similares;
II - prestações de serviços de transporte interestadual e intermunicipal, por qualquer via, de pessoas, bens, mercadorias ou valores;

O cálculo do ICMS em operações dentro do estado de Santa Catarina utiliza a alíquota padrão de 17%, salvo exceções previstas em lei para produtos da cesta básica ou supérfluos. A base de cálculo é o valor da operação, incluindo frete e outras despesas debitadas ao adquirente.

Para operações interestaduais, a alíquota varia conforme o estado de destino. Operações destinadas a contribuintes do ICMS nos estados do Sul e Sudeste (exceto Espírito Santo) aplicam uma alíquota de 12%. Para os demais estados e o Distrito Federal, a alíquota é de 7%. O diferencial de alíquota (DIFAL) deve ser recolhido quando a mercadoria é destinada a consumidor final não contribuinte do imposto em outro estado.

A substituição tributária (ST) é um regime no qual a responsabilidade pelo recolhimento do ICMS é atribuída a um contribuinte diferente daquele que realiza o fato gerador. Geralmente, a indústria ou o importador recolhe o imposto devido por toda a cadeia de circulação subsequente, até o consumidor final. A base de cálculo da ST é o preço final ao consumidor, único ou máximo, fixado por autoridade competente, ou, na falta deste, o preço praticado pelo substituto, acrescido dos valores de frete e outras despesas e da margem de valor agregado (MVA).

# rag/init_rag.py

import logging
from indexing.indexer import DocumentIndexer
from retrieval.query_engine import QueryEngine

# Configuração do logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_initialization():
    """
    Executa a indexação inicial e um teste de busca.
    """
    logging.info("--- Iniciando o processo de inicialização do RAG ---")
    
    # 1. Indexar os documentos
    logging.info("Passo 1: Indexando documentos da pasta './data/sample_docs/'...")
    try:
        indexer = DocumentIndexer()
        indexer.index_folder("./data/sample_docs/")
        logging.info("Indexação concluída com sucesso.")
    except Exception as e:
        logging.error(f"Falha na indexação: {e}", exc_info=True)
        return

    # 2. Testar a busca
    logging.info("\nPasso 2: Realizando uma busca de teste...")
    try:
        engine = QueryEngine()
        query = "Qual a alíquota do ICMS para estados do Sul?"
        logging.info(f"Query de teste: '{query}'")
        
        results = engine.search_with_score(query, k=2)
        
        if not results:
            logging.warning("A busca de teste não retornou resultados. Verifique a indexação.")
        else:
            logging.info("Resultados da busca de teste:")
            for doc, score in results:
                print("-" * 20)
                print(f"Score de Similaridade: {score:.4f}")
                print(f"Fonte: {doc.metadata.get('source')}")
                print(f"Conteúdo do Chunk: {doc.page_content[:300]}...")
                print("-" * 20)
        
    except Exception as e:
        logging.error(f"Falha na busca de teste: {e}", exc_info=True)

    logging.info("\n--- Processo de inicialização do RAG concluído ---")

if __name__ == "__main__":
    run_initialization()
    
agora poderia explicar a implementação , a relação com o mcp e onde entra os agentes

Excelente pergunta. É fundamental entender como essas duas arquiteturas (RAG e MCP) se complementam e onde o agente de IA atua como o elo central.

Vamos dividir a explicação em três partes:

Explicação da Implementação RAG: O que o sistema que acabamos de criar faz.

A Relação entre RAG e MCP: Como os dois sistemas "conversam".

Onde os Agentes de IA Entram: O papel do orquestrador inteligente.

1. Explicação da Implementação RAG (O Cérebro do Conhecimento)
Pense no sistema RAG que criamos como a memória de longo prazo ou a biblioteca de consulta do seu sistema. Ele não executa ações, mas fornece conhecimento profundo e contextualizado sobre um domínio específico (neste caso, legislação fiscal).

O fluxo de trabalho dele é dividido em duas etapas:

Fase 1: Indexação (Aprender e Organizar)
Isto é o que o script init_rag.py faz. É um processo offline onde o sistema constrói sua base de conhecimento:

Carregar Documentos: Ele lê os arquivos de texto (.txt) da pasta data/.

Chunking (indexing/chunker.py): Documentos grandes são ruins para busca semântica. Por isso, ele quebra os regulamentos em "chunks" (pedaços) menores e mais coesos, como parágrafos. Cada chunk mantém uma referência ao seu documento de origem (metadados).

Embedding (embeddings/embedding_model.py): Esta é a etapa mágica. Cada chunk de texto é convertido em um vetor (uma longa lista de números) que representa seu significado semântico. Textos com significados parecidos terão vetores numericamente próximos.

Armazenar (vector_store/): Esses vetores e os textos originais são salvos no ChromaDB. O ChromaDB é um banco de dados especializado em encontrar rapidamente os vetores mais próximos de um vetor de consulta.

Resultado: Temos uma biblioteca digital onde, em vez de procurar por palavras-chave, podemos procurar por "significado".

Fase 2: Recuperação (Consultar a Biblioteca)
Isto é o que a API FastAPI (/api/v1/search) faz. É um processo em tempo real:

Receber a Pergunta: Um usuário (ou outro sistema) envia uma pergunta em linguagem natural, como "Qual a MVA para substituição tributária?".

Embedding da Pergunta: O sistema usa o mesmo modelo de embedding para converter essa pergunta em um vetor.

Busca por Similaridade: Ele vai ao ChromaDB e diz: "Encontre os chunks de texto cujos vetores são mais parecidos com este vetor da minha pergunta".

Retornar Contexto: O ChromaDB retorna os k chunks mais relevantes. Estes chunks são o contexto que o sistema "recuperou" (o "R" de RAG).

Em resumo, o sistema RAG não responde perguntas diretamente. Ele encontra os trechos de texto mais relevantes de sua base de conhecimento para ajudar a responder a pergunta.

2. A Relação entre RAG e MCP (Ferramentas e Conhecimento)
Agora, vamos conectar os dois mundos. Se o RAG é a biblioteca, o MCP é a mesa de trabalho com todas as ferramentas e arquivos do agente.

Componente	Analogia	Função	Exemplo
Sistema RAG	Biblioteca de Referência	Fornece conhecimento profundo e não-estruturado.	Consulta sobre uma lei específica do ICMS.
Servidor MCP	Mesa de Trabalho com Ferramentas	Fornece acesso a ações e dados estruturados.	Calcular imposto, validar um CNPJ, buscar uma NF.
A relação é simples: O MCP usa o RAG como uma de suas ferramentas.

O RAG expõe sua funcionalidade através de uma API REST (http://localhost:8000/api/v1/search). Podemos criar uma nova ferramenta no audit_server.py do MCP que consome essa API.

Veja como seria essa nova ferramenta:

Python
# Adicionar este código em mcp/servers/audit_server.py

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
Com isso, acabamos de dar ao nosso sistema MCP uma nova "super-ferramenta": a capacidade de pesquisar em uma vasta base de conhecimento fiscal.

3. Onde os Agentes de IA Entram (O Orquestrador)
O agente de IA (um Large Language Model como o Claude da Anthropic) é o cérebro que usa tudo isso. Ele é o "trabalhador" que senta na mesa de trabalho (MCP) e consulta a biblioteca (RAG) para realizar tarefas complexas.

Vamos simular um fluxo de auditoria completo:

Objetivo do Usuário: "Audite a nota fiscal nf://invoice/1001. Verifique se o CNPJ do emissor é válido e se o cálculo do ICMS está correto, considerando a legislação para operações interestaduais."

O Agente de IA em Ação:

Entendimento da Tarefa: O agente lê o prompt e quebra a tarefa em passos:

Pegar os dados da NF 1001.

Validar o CNPJ do emissor.

Verificar o cálculo do ICMS.

Para isso, preciso saber a regra de ICMS interestadual.

Passo 1: Acessar Recurso (MCP)

O agente reconhece nf://invoice/1001 como um recurso.

Ação: Ele chama o nf_context_server para obter os dados da nota.

Resultado: Recebe um JSON com o valor, CNPJs, estados de origem/destino, etc.

Passo 2: Usar Ferramenta de Validação (MCP)

O agente extrai o CNPJ do emissor dos dados da NF.

Ação: Ele chama a ferramenta validate_cnpj no audit_server.

Resultado: Recebe um JSON confirmando que o CNPJ é válido, ativo e o nome da empresa confere.

Passo 3: Usar Ferramenta de Consulta de Conhecimento (MCP -> RAG)

O agente vê que a operação é de Santa Catarina para São Paulo. Ele pensa: "Não tenho certeza da alíquota correta para essa operação específica. Preciso consultar a legislação."

Ação: Ele usa a nova ferramenta consult_fiscal_regulation com a query: "alíquota ICMS operações interestaduais de SC para SP".

Como funciona: Essa ferramenta do MCP faz uma chamada HTTP para a API do RAG. O RAG converte a query em um vetor, busca no ChromaDB e retorna os trechos mais relevantes do fiscal_regulation_sample.txt.

Resultado: O agente recebe um texto: "...Para operações interestaduais, a alíquota varia... Operações destinadas a contribuintes do ICMS nos estados do Sul e Sudeste (exceto Espírito Santo) aplicam uma alíquota de 12%...".

Passo 4: Raciocínio e Síntese Final

Agora o agente tem todas as peças:

Dados da NF (do recurso MCP).

Validação do CNPJ (da ferramenta MCP).

Regra do ICMS (da ferramenta MCP que usou o RAG).

Ele pode comparar o valor do ICMS na nota com o valor que ele calcularia usando a regra de 12% que encontrou.

Ação: Ele formula a resposta final para o usuário.

Resposta Final do Agente: "Auditoria da NF 1001 concluída:

Validade do Emissor: O CNPJ 12.345.678/0001-90 é válido e ativo, correspondendo à empresa 'Exemplo LTDA'.

Análise do ICMS: A operação é de SC para SP. De acordo com a base de conhecimento fiscal, a alíquota aplicável é de 12%. O valor na nota fiscal, no entanto, foi calculado com 17%. Portanto, há uma divergência e o cálculo do ICMS parece estar incorreto."

Essa é a sinergia perfeita: o agente de IA é o maestro que orquestra as ferramentas de ação e dados do MCP com o conhecimento contextual do sistema RAG para realizar tarefas complexas e fornecer respostas bem fundamentadas.

A propósito, para desbloquear as funcionalidades completas de todas as Apps, ative a Atividade das Apps Gemini.    

	