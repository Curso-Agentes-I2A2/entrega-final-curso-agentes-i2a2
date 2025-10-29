# 🎓 Guia Técnico - RAG e MCP

Documento complementar para aprofundamento técnico em RAG e MCP.

---

## 🧠 RAG - Deep Dive

### Fluxo Completo do RAG

```
1. INDEXAÇÃO (Offline)
   Documentos → Chunking → Embeddings → Vector Store

2. RETRIEVAL (Query time)
   Pergunta → Embedding → Busca Vetorial → Top-K Documentos

3. AUGMENTATION (Query time)
   Contexto + Pergunta → Prompt → LLM → Resposta
```

### Exemplo Prático para Nosso Sistema

```python
# rag/indexing/indexer.py
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma

class NFIndexer:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings()
        self.vector_store = Chroma(
            persist_directory="./chroma_db",
            embedding_function=self.embeddings
        )
    
    def index_fiscal_document(self, document_path: str):
        """Indexa documento fiscal no RAG"""
        
        # 1. Carregar documento
        with open(document_path, 'r') as f:
            text = f.read()
        
        # 2. Chunking - dividir em pedaços
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,      # Tamanho do chunk
            chunk_overlap=200,    # Overlap entre chunks
            separators=["\n\n", "\n", ".", "!"]
        )
        chunks = splitter.split_text(text)
        
        # 3. Adicionar metadados
        metadatas = [
            {
                "source": document_path,
                "chunk_id": i,
                "doc_type": "fiscal_regulation"
            }
            for i in range(len(chunks))
        ]
        
        # 4. Indexar no vector store
        self.vector_store.add_texts(
            texts=chunks,
            metadatas=metadatas
        )
        
        print(f"✅ Indexado: {len(chunks)} chunks de {document_path}")
```

```python
# rag/retrieval/query_engine.py
class AuditQueryEngine:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings()
        self.vector_store = Chroma(
            persist_directory="./chroma_db",
            embedding_function=self.embeddings
        )
    
    async def search(self, query: str, k: int = 5) -> list:
        """Busca contexto relevante para auditoria"""
        
        # Buscar documentos similares
        results = self.vector_store.similarity_search_with_score(
            query=query,
            k=k
        )
        
        # Formatar resultados
        formatted = []
        for doc, score in results:
            formatted.append({
                "content": doc.page_content,
                "score": float(score),
                "source": doc.metadata.get("source"),
                "chunk_id": doc.metadata.get("chunk_id")
            })
        
        return formatted
    
    async def audit_invoice(self, invoice_data: dict) -> dict:
        """Audita nota fiscal usando RAG"""
        
        # 1. Criar query baseada na NF
        query = f"""
        Nota fiscal com os seguintes dados:
        - CNPJ Emitente: {invoice_data['cnpj_emit']}
        - Valor Total: {invoice_data['valor_total']}
        - CFOP: {invoice_data['cfop']}
        - Impostos: {invoice_data['impostos']}
        
        Há alguma irregularidade fiscal?
        """
        
        # 2. Buscar contexto relevante
        context_docs = await self.search(query, k=3)
        
        # 3. Montar contexto
        context = "\n\n".join([
            f"Fonte: {doc['source']}\n{doc['content']}"
            for doc in context_docs
        ])
        
        # 4. Enviar para LLM com contexto
        from anthropic import Anthropic
        client = Anthropic()
        
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": f"""
Contexto (base de conhecimento):
{context}

Tarefa: Analisar a nota fiscal abaixo e identificar possíveis irregularidades:
{query}

Responda em formato JSON:
{{
    "aprovada": true/false,
    "irregularidades": [],
    "observacoes": "",
    "confianca": 0.95
}}
"""
            }]
        )
        
        return response.content[0].text
```

### Estratégias de Chunking

**1. Tamanho Fixo**
```python
# Simples mas pode quebrar no meio de frases
chunks = [text[i:i+1000] for i in range(0, len(text), 1000)]
```

**2. Recursivo (Recomendado)**
```python
# Respeita estrutura do documento
RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    separators=["\n\n", "\n", ". ", " "]
)
```

**3. Semântico**
```python
# Divide por significado (mais lento, mais preciso)
from langchain.text_splitter import SemanticChunker
chunker = SemanticChunker(embeddings)
```

### Escolha do Embedding Model

| Modelo | Dimensões | Custo | Qualidade | Recomendação |
|--------|-----------|-------|-----------|--------------|
| OpenAI text-embedding-3-small | 1536 | $ | ⭐⭐⭐⭐ | ✅ Dev |
| OpenAI text-embedding-3-large | 3072 | $$ | ⭐⭐⭐⭐⭐ | ✅ Prod |
| Cohere embed-multilingual-v3 | 1024 | $ | ⭐⭐⭐⭐ | ✅ PT-BR |
| Sentence-Transformers (local) | 384-768 | Grátis | ⭐⭐⭐ | ✅ Testes |

**Para nosso projeto:**
```python
# Desenvolvimento
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Produção
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small"
)
```

### Técnicas Avançadas

**1. Reranking**
```python
# Usar modelo de reranking após busca inicial
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import CohereRerank

compressor = CohereRerank(model="rerank-english-v2.0")
retriever = ContextualCompressionRetriever(
    base_compressor=compressor,
    base_retriever=vector_store.as_retriever()
)
```

**2. Hybrid Search (Vetorial + Keyword)**
```python
# Combina busca semântica com busca por palavras-chave
from langchain.retrievers import EnsembleRetriever

ensemble_retriever = EnsembleRetriever(
    retrievers=[vector_retriever, bm25_retriever],
    weights=[0.7, 0.3]  # 70% semântico, 30% keyword
)
```

**3. Parent Document Retrieval**
```python
# Busca chunks pequenos, retorna documento completo
from langchain.retrievers import ParentDocumentRetriever
```

---

## 🔌 MCP - Deep Dive

### Anatomia de um Servidor MCP

```python
# mcp/servers/nf_context_server.py
from mcp.server import Server
from mcp.types import Resource, Tool, Prompt
import asyncio

# 1. Criar servidor
server = Server("nf-audit-mcp")

# 2. Definir RECURSOS (dados que podem ser lidos)
@server.resource("nf://invoices")
async def list_invoices() -> Resource:
    """Lista todas as notas fiscais"""
    invoices = await db.get_all_invoices()
    return Resource(
        uri="nf://invoices",
        name="Lista de Notas Fiscais",
        mimeType="application/json",
        text=json.dumps(invoices)
    )

@server.resource("nf://invoice/{invoice_id}")
async def get_invoice(invoice_id: str) -> Resource:
    """Retorna nota fiscal específica"""
    invoice = await db.get_invoice(invoice_id)
    return Resource(
        uri=f"nf://invoice/{invoice_id}",
        name=f"NF {invoice_id}",
        mimeType="application/json",
        text=json.dumps(invoice)
    )

# 3. Definir TOOLS (ações que podem ser executadas)
@server.tool("validate_cnpj")
async def validate_cnpj(cnpj: str) -> dict:
    """Valida CNPJ em serviço externo"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://brasilapi.com.br/api/cnpj/v1/{cnpj}"
        )
        data = response.json()
        return {
            "valid": response.status_code == 200,
            "company_name": data.get("razao_social"),
            "situation": data.get("situacao")
        }

@server.tool("calculate_taxes")
async def calculate_taxes(
    base_value: float,
    tax_regime: str,
    product_ncm: str
) -> dict:
    """Calcula impostos para nota fiscal"""
    # Lógica de cálculo de impostos
    icms_rate = get_icms_rate(product_ncm, tax_regime)
    pis_rate = get_pis_rate(tax_regime)
    cofins_rate = get_cofins_rate(tax_regime)
    
    return {
        "icms": base_value * icms_rate,
        "pis": base_value * pis_rate,
        "cofins": base_value * cofins_rate,
        "total_taxes": base_value * (icms_rate + pis_rate + cofins_rate)
    }

@server.tool("check_invoice_sefaz")
async def check_invoice_sefaz(access_key: str) -> dict:
    """Consulta situação da NF no SEFAZ"""
    # Requer certificado digital
    # Implementação específica por estado
    result = await sefaz_client.query_invoice(access_key)
    return {
        "status": result.status,
        "authorization_date": result.date,
        "protocol": result.protocol
    }

# 4. Definir PROMPTS (templates reutilizáveis)
@server.prompt("audit_invoice")
async def audit_invoice_prompt(invoice_id: str) -> Prompt:
    """Template para auditoria de NF"""
    invoice = await db.get_invoice(invoice_id)
    
    return Prompt(
        name="audit_invoice",
        description="Prompt para auditoria de nota fiscal",
        messages=[{
            "role": "user",
            "content": f"""
Analise a nota fiscal abaixo e identifique irregularidades:

Dados da NF:
- Número: {invoice['numero']}
- Emitente: {invoice['emitente']}
- CNPJ: {invoice['cnpj']}
- Valor: R$ {invoice['valor']}
- CFOP: {invoice['cfop']}
- Impostos: {invoice['impostos']}

Verifique:
1. Validade do CNPJ
2. Correção dos impostos
3. CFOP apropriado
4. Consistência dos dados

Responda em JSON com status e irregularidades encontradas.
"""
        }]
    )

# 5. Iniciar servidor
if __name__ == "__main__":
    asyncio.run(server.run())
```

### Usando MCP com Claude

```python
# agents/audit_agent/agent.py
from anthropic import Anthropic

client = Anthropic()

# O agente pode usar as tools do MCP automaticamente
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    tools=[
        {
            "name": "validate_cnpj",
            "description": "Valida CNPJ em serviço externo",
            "input_schema": {
                "type": "object",
                "properties": {
                    "cnpj": {
                        "type": "string",
                        "description": "CNPJ a validar"
                    }
                },
                "required": ["cnpj"]
            }
        },
        {
            "name": "calculate_taxes",
            "description": "Calcula impostos para nota fiscal",
            "input_schema": {
                "type": "object",
                "properties": {
                    "base_value": {"type": "number"},
                    "tax_regime": {"type": "string"},
                    "product_ncm": {"type": "string"}
                },
                "required": ["base_value", "tax_regime", "product_ncm"]
            }
        }
    ],
    messages=[{
        "role": "user",
        "content": "Valide o CNPJ 12.345.678/0001-90 e calcule os impostos para uma NF de R$ 10.000 no regime Simples Nacional, NCM 8471.30.00"
    }]
)

# Claude decide automaticamente quais tools usar
if response.stop_reason == "tool_use":
    for tool_call in response.content:
        if tool_call.type == "tool_use":
            # Executar tool
            if tool_call.name == "validate_cnpj":
                result = await validate_cnpj(tool_call.input["cnpj"])
            elif tool_call.name == "calculate_taxes":
                result = await calculate_taxes(**tool_call.input)
```

### Integrações Úteis para Nosso Sistema

**1. APIs Brasileiras (Gratuitas)**

```python
@server.tool("consult_cnpj_receitaws")
async def consult_cnpj_receitaws(cnpj: str) -> dict:
    """ReceitaWS - Consulta CNPJ"""
    url = f"https://www.receitaws.com.br/v1/cnpj/{cnpj}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()

@server.tool("consult_cep")
async def consult_cep(cep: str) -> dict:
    """ViaCEP - Valida CEP"""
    url = f"https://viacep.com.br/ws/{cep}/json/"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()

@server.tool("verify_bank")
async def verify_bank(bank_code: str) -> dict:
    """BrasilAPI - Informações bancárias"""
    url = f"https://brasilapi.com.br/api/banks/v1/{bank_code}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()
```

**2. Validações Internas**

```python
@server.tool("check_supplier_history")
async def check_supplier_history(cnpj: str) -> dict:
    """Consulta histórico do fornecedor"""
    history = await db.query("""
        SELECT 
            COUNT(*) as total_nfs,
            SUM(CASE WHEN status = 'aprovada' THEN 1 ELSE 0 END) as aprovadas,
            AVG(valor) as ticket_medio,
            MAX(data) as ultima_nf
        FROM notas_fiscais
        WHERE cnpj_emitente = ?
    """, (cnpj,))
    
    return {
        "total_invoices": history['total_nfs'],
        "approved_rate": history['aprovadas'] / history['total_nfs'],
        "average_value": history['ticket_medio'],
        "last_invoice": history['ultima_nf'],
        "trusted": history['aprovadas'] / history['total_nfs'] > 0.95
    }

@server.tool("check_value_threshold")
async def check_value_threshold(value: float, category: str) -> dict:
    """Verifica se valor está dentro dos limites"""
    threshold = await db.get_threshold(category)
    
    return {
        "within_limit": value <= threshold['max_value'],
        "threshold": threshold['max_value'],
        "requires_approval": value > threshold['auto_approval_limit']
    }
```

**3. Integrações com SEFAZ (Requer Certificado)**

```python
@server.tool("query_nfe_sefaz")
async def query_nfe_sefaz(
    access_key: str,
    state: str,
    certificate_path: str
) -> dict:
    """Consulta NF-e no SEFAZ"""
    # Implementação varia por estado
    # Requer certificado digital A1 ou A3
    
    from nfe_client import NFEClient
    
    client = NFEClient(
        certificate=certificate_path,
        environment="production"
    )
    
    result = client.query_invoice(
        access_key=access_key,
        state_code=state
    )
    
    return {
        "status": result.status,
        "authorized": result.authorized,
        "protocol": result.protocol_number,
        "authorization_date": result.date
    }
```

---

## 🎯 Decisões de Arquitetura

### RAG: Nossa Escolha

**Desenvolvimento:**
```yaml
Vector Store: ChromaDB
Embeddings: sentence-transformers/all-MiniLM-L6-v2
Chunking: RecursiveCharacterTextSplitter (1000 chars, 200 overlap)
```

**Produção:**
```yaml
Vector Store: Pinecone ou ChromaDB + PostgreSQL
Embeddings: OpenAI text-embedding-3-small
Chunking: RecursiveCharacterTextSplitter + Reranking
```

### MCP: Nossa Escolha

**Tools Prioritárias:**
1. ✅ `validate_cnpj` - ReceitaWS/BrasilAPI
2. ✅ `calculate_taxes` - Lógica interna
3. ✅ `check_supplier_history` - Banco interno
4. ✅ `validate_nfe_schema` - Validação XML
5. ⏳ `query_nfe_sefaz` - Se conseguirmos certificado

**Resources:**
1. ✅ `nf://invoices` - Lista de NFs
2. ✅ `nf://invoice/{id}` - NF específica
3. ✅ `nf://suppliers` - Cadastro fornecedores
4. ✅ `nf://regulations` - Base de regulamentos

---

## 📝 Checklist de Implementação

### RAG
- [ ] Instalar ChromaDB
- [ ] Criar pipeline de indexação
- [ ] Coletar documentos fiscais
- [ ] Implementar query engine
- [ ] Testar retrieval
- [ ] Integrar com agentes

### MCP
- [ ] Estudar MCP SDK
- [ ] Definir tools necessárias
- [ ] Implementar servidor MCP
- [ ] Testar APIs externas
- [ ] Integrar com Claude
- [ ] Documentar endpoints

---

**Próxima leitura:** `docs/ARCHITECTURE.md` (após criar proposta)