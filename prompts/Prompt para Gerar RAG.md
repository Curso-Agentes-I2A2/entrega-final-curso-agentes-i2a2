# 🧠 Prompt para Gerar RAG (Sistema de Busca Vetorial)

**Instruções:** Copie este prompt e cole no Claude ou GPT-4 para gerar o código inicial do RAG.

---

## PROMPT:

```
Você é um especialista em RAG (Retrieval Augmented Generation) e LangChain. Preciso que você crie a estrutura inicial completa de um sistema RAG para auditoria de notas fiscais brasileiras.

CONTEXTO DO PROJETO:
- Sistema RAG para fornecer contexto sobre legislação fiscal brasileira
- Indexação de documentos fiscais (regulamentos, tabelas de impostos, etc.)
- Busca semântica para auxiliar agentes de IA na auditoria
- API REST para consultas
- Base de conhecimento sobre NF-e, ICMS, IPI, PIS, COFINS

REQUISITOS TÉCNICOS:
- Framework: LangChain
- Vector Store: ChromaDB (desenvolvimento) + suporte para Pinecone (produção)
- Embeddings: OpenAI text-embedding-3-small (com fallback para modelo local)
- API: FastAPI
- Chunking: RecursiveCharacterTextSplitter
- Reranking: Opcional (Cohere)

ESTRUTURA DE PASTAS:
```
rag/
├── embeddings/
│   ├── __init__.py
│   ├── nf_embeddings.py       # Gera embeddings de NFs
│   └── embedding_model.py     # Configuração do modelo
├── vector_store/
│   ├── __init__.py
│   ├── chromadb/
│   │   ├── __init__.py
│   │   └── client.py          # Cliente ChromaDB
│   ├── pinecone/
│   │   ├── __init__.py
│   │   └── client.py          # Cliente Pinecone
│   └── base.py                # Interface abstrata
├── retrieval/
│   ├── __init__.py
│   ├── query_engine.py        # Motor de busca
│   └── reranker.py            # Reranking opcional
├── indexing/
│   ├── __init__.py
│   ├── indexer.py             # Pipeline de indexação
│   └── chunker.py             # Estratégias de chunking
├── api/
│   ├── __init__.py
│   └── routes.py              # Endpoints FastAPI
├── data/
│   └── sample_docs/           # Documentos de exemplo
├── config.py
├── main.py
└── requirements.txt
```

POR FAVOR, GERE:

1. **main.py** - Aplicação FastAPI para o RAG:
   - Endpoints para busca
   - Endpoint para indexação
   - Health check
   - Documentação automática

2. **config.py** - Configurações:
   - Vector store (ChromaDB vs Pinecone)
   - Modelo de embeddings
   - Parâmetros de chunking
   - API keys

3. **embeddings/embedding_model.py** - Gerenciador de embeddings:
   - Suporte a OpenAI embeddings
   - Fallback para HuggingFace local (sentence-transformers)
   - Cache de embeddings
   - Função get_embeddings(texts: List[str]) -> List[List[float]]

4. **vector_store/chromadb/client.py** - Cliente ChromaDB:
   - Inicialização do cliente
   - add_documents(documents, embeddings, metadatas)
   - search(query_embedding, k=5)
   - delete_collection()
   - Persistência em disco

5. **vector_store/base.py** - Interface abstrata:
   - Classe base VectorStore
   - Métodos abstratos que ChromaDB e Pinecone devem implementar
   - Permite trocar facilmente entre vector stores

6. **indexing/chunker.py** - Estratégias de chunking:
   - RecursiveCharacterTextSplitter (padrão)
   - Parâmetros: chunk_size=1000, chunk_overlap=200
   - Separadores: ["\n\n", "\n", ". ", " "]
   - Função chunk_document(text: str) -> List[str]

7. **indexing/indexer.py** - Pipeline completo de indexação:
   - Carregar documentos de pasta
   - Chunkar documentos
   - Gerar embeddings
   - Armazenar no vector store
   - Adicionar metadados (source, tipo, data)
   - Script para indexar pasta inteira

8. **retrieval/query_engine.py** - Motor de busca:
   - Classe QueryEngine
   - search(query: str, k: int = 5) -> List[Document]
   - search_with_score(query: str, k: int = 5) -> List[Tuple[Document, float]]
   - Filtros por metadata
   - Threshold de similaridade

9. **api/routes.py** - Rotas FastAPI:
   - POST /search - Busca semântica
     * Body: {"query": str, "k": int, "filters": dict}
     * Response: List de documentos com scores
   - POST /index - Indexar documento
     * Body: {"content": str, "metadata": dict}
   - GET /stats - Estatísticas do vector store
   - DELETE /clear - Limpar índice

10. **data/sample_docs/fiscal_regulation_sample.txt** - Documento de exemplo:
    - Regulamento fiscal fictício para testes
    - Pelo menos 3 parágrafos sobre ICMS
    - Para testar indexação e busca

11. **requirements.txt**:
    - langchain
    - langchain-community
    - chromadb
    - openai
    - sentence-transformers
    - fastapi
    - uvicorn[standard]
    - pydantic-settings
    - python-dotenv

FUNCIONALIDADES ADICIONAIS:

12. **Script de inicialização** (init_rag.py):
    - Script para primeira indexação
    - Carregar documentos da pasta data/
    - Criar índice inicial
    - Testar busca

IMPORTANTE:
- Use async/await onde possível
- Implemente tratamento de erros robusto
- Adicione logs detalhados
- Crie fallback para quando OpenAI API falhar
- Documente metadados importantes:
  * source (origem do documento)
  * doc_type (tipo: regulamento, tabela, etc)
  * date (data do documento)
  * state (estado, ex: SP, RJ)
- Implemente cache para evitar re-embedding de queries repetidas
- Adicione exemplos de uso nas docstrings

EXEMPLO DE USO ESPERADO:

```python
# Indexar documento
from indexing.indexer import DocumentIndexer
indexer = DocumentIndexer()
indexer.index_folder("./data/fiscal_docs/")

# Buscar
from retrieval.query_engine import QueryEngine
engine = QueryEngine()
results = engine.search("Como calcular ICMS?", k=5)
for doc, score in results:
    print(f"Score: {score:.2f} - {doc.content[:100]}")
```

FORMATO DE RESPOSTA:
Por favor, gere cada arquivo completo, com comentários explicativos. Inclua exemplos de uso e testes básicos.
```

---

## EXEMPLO DE USO:

1. Copie o prompt acima
2. Cole no Claude ou ChatGPT
3. Receba o código completo
4. Teste com:

```bash
cd rag
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Indexar documentos de exemplo
python init_rag.py

# Iniciar API
uvicorn main:app --reload --port 8001

# Testar busca
curl -X POST http://localhost:8001/search \
  -H "Content-Type: application/json" \
  -d '{"query": "ICMS", "k": 3}'
```