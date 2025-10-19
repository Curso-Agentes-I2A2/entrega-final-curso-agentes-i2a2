# Arquitetura Técnica - Sistema de Auditoria de NF

**Data:** [Data da proposta]  
**Versão:** 0.1 (Draft)  
**Status:** 🟡 Em Revisão

---

## 📋 Time Técnico

| Nome | Módulo | GitHub |
|------|--------|--------|
| [Nome] | Backend | @username |
| [Nome] | RAG | @username |
| [Nome] | Agents | @username |
| [Nome] | MCP | @username |
| [Nome] | Frontend | @username |

---

## 🎯 Visão Geral

[Descrever em 2-3 parágrafos a arquitetura proposta]

### Objetivos
- [ ] [Objetivo 1]
- [ ] [Objetivo 2]
- [ ] [Objetivo 3]

---

## 🏗️ Arquitetura de Alto Nível

### Diagrama

```
[Adicionar diagrama - pode ser ASCII art ou link para imagem]

┌─────────────┐
│  Frontend   │
│  Streamlit  │
└──────┬──────┘
       │
       ▼
┌─────────────┐      ┌─────────────┐
│   Backend   │◄────►│     RAG     │
│   FastAPI   │      │  ChromaDB   │
└──────┬──────┘      └─────────────┘
       │
       ▼
┌─────────────┐      ┌─────────────┐
│   Agents    │◄────►│     MCP     │
│  LangChain  │      │   Servers   │
└─────────────┘      └─────────────┘
```

### Fluxo de Dados

1. **Upload de NF**
   ```
   Frontend → Backend → Validação → RAG (consulta contexto) → Agents (análise) → Resultado
   ```

2. **Auditoria Automatizada**
   ```
   [Descrever fluxo]
   ```

3. **Geração de NF Sintética**
   ```
   [Descrever fluxo]
   ```

---

## 🧠 RAG - Proposta Técnica

### Decisões

| Aspecto | Escolha | Justificativa |
|---------|---------|---------------|
| **Vector Store** | [ChromaDB / Pinecone / Outro] | [Por quê?] |
| **Embeddings** | [OpenAI / Cohere / Local] | [Por quê?] |
| **Chunking Strategy** | [Recursive / Semantic / Fixo] | [Por quê?] |
| **Chunk Size** | [1000 / 1500 / Outro] | [Por quê?] |
| **Overlap** | [200 / 300 / Outro] | [Por quê?] |

### Estrutura de Indexação

```python
# Exemplo da estrutura proposta
{
    "document_id": "reg_fiscal_001",
    "content": "Art. 1º - Nas operações...",
    "metadata": {
        "tipo": "regulamento",
        "categoria": "icms",
        "estado": "SP",
        "data_vigencia": "2024-01-01",
        "fonte": "SEFAZ-SP"
    },
    "embedding": [0.123, 0.456, ...]  # 1536 dimensões
}
```

### Base de Conhecimento

**Documentos a Indexar:**

1. **Legislação Fiscal** (Prioridade Alta)
   - [ ] Regulamento ICMS SP
   - [ ] Regulamento IPI Federal
   - [ ] Tabela NCM atualizada
   - [ ] [Adicionar mais]

2. **Documentação Técnica** (Prioridade Média)
   - [ ] Schema XML NF-e versão 4.0
   - [ ] Manual de integração SEFAZ
   - [ ] [Adicionar mais]

3. **Base Histórica** (Prioridade Baixa)
   - [ ] Notas fiscais aprovadas
   - [ ] Casos de rejeição
   - [ ] [Adicionar mais]

**Tamanho Estimado:**
- Total de documentos: [~100 / ~500 / ~1000]
- Tamanho total: [~10MB / ~100MB / ~1GB]
- Chunks estimados: [~1000 / ~5000 / ~10000]

### Pipeline de Indexação

```python
# Pseudocódigo do pipeline proposto

def index_documents():
    """Pipeline de indexação"""
    
    # 1. Carregar documentos
    docs = load_documents_from_folder("./data/fiscal_docs/")
    
    # 2. Processar e chunkar
    chunks = []
    for doc in docs:
        chunks.extend(
            split_document(
                doc,
                chunk_size=1000,
                overlap=200
            )
        )
    
    # 3. Gerar embeddings
    embeddings = generate_embeddings(chunks)
    
    # 4. Armazenar no vector store
    vector_store.add_documents(
        documents=chunks,
        embeddings=embeddings
    )
    
    # 5. Criar índice
    vector_store.build_index()
```

### Estratégia de Busca

**Tipo de Busca:** [Similarity / Hybrid / MMR]

**Parâmetros:**
- k (resultados): [5 / 10 / outro]
- Score threshold: [0.7 / 0.8 / outro]
- Reranking: [Sim / Não]

**Otimizações:**
- [ ] Cache de queries frequentes
- [ ] Filtros por metadata
- [ ] Busca híbrida (vetorial + keyword)

---

## 🤖 Agents - Proposta Técnica

### Arquitetura de Agentes

**Framework:** [LangChain / AutoGen / CrewAI / Outro]

**Agentes Propostos:**

1. **Agente de Auditoria**
   - Função: [Descrever]
   - Tools: [validate_cnpj, check_history, ...]
   - Modelo LLM: [Claude Sonnet / GPT-4 / Outro]

2. **Agente de Validação**
   - Função: [Descrever]
   - Tools: [validate_schema, calculate_taxes, ...]
   - Modelo LLM: [...]

3. **Agente Gerador**
   - Função: [Descrever]
   - Tools: [generate_cnpj, create_xml, ...]
   - Modelo LLM: [...]

4. **Orquestrador**
   - Função: [Descrever]
   - Lógica: [Sequential / Parallel / Condicional]

### Fluxo de Decisão

```
[Descrever como os agentes colaboram]

Exemplo:
1. Orquestrador recebe NF
2. Agente de Validação verifica schema
3. Se válido → Agente de Auditoria analisa
4. Se suspeito → Consulta RAG + análise profunda
5. Resultado consolidado → Frontend
```

### Prompts

**Template de Prompt Principal:**
```
[Incluir exemplo do prompt que será usado]
```

---

## 🔌 MCP - Proposta Técnica

### Servidores MCP

**Servidores Propostos:**

1. **nf-context-server**
   - Porta: 8003
   - Função: Acesso a dados de NFs
   - Resources: [nf://invoices, nf://invoice/{id}]
   
2. **audit-server**
   - Porta: 8004
   - Função: Tools de auditoria
   - Tools: [validate_cnpj, calculate_taxes, check_sefaz]

### Tools Implementadas

| Tool | Descrição | API Externa | Status |
|------|-----------|-------------|--------|
| validate_cnpj | Valida CNPJ | BrasilAPI | ✅ Proposta |
| calculate_taxes | Calcula impostos | Interno | ✅ Proposta |
| check_sefaz | Consulta SEFAZ | SEFAZ API | ⏳ Pendente certificado |
| validate_schema | Valida XML | Interno | ✅ Proposta |
| [Adicionar mais] | ... | ... | ... |

### APIs Externas

**APIs Gratuitas:**
- [x] BrasilAPI - CNPJ, CEP, Bancos
- [x] ReceitaWS - CNPJ (backup)
- [x] ViaCEP - Validação de endereços
- [ ] [Adicionar mais]

**APIs Pagas (se necessário):**
- [ ] Serpro - Consultas Receita Federal
- [ ] [Adicionar mais]

**Fallback Strategy:**
```
1. Tentar API primária
2. Se falhar → Tentar API backup
3. Se falhar → Validação local (limitada)
4. Se falhar → Marcar para revisão manual
```

### Implementação de Tool

```python
# Exemplo de implementação proposta

@server.tool("validate_cnpj")
async def validate_cnpj(cnpj: str) -> dict:
    """
    Valida CNPJ em múltiplas fontes
    
    Args:
        cnpj: CNPJ a validar (com ou sem formatação)
    
    Returns:
        {
            "valid": bool,
            "company_name": str,
            "situation": str,
            "source": str
        }
    """
    # 1. Limpar CNPJ
    cnpj_clean = clean_cnpj(cnpj)
    
    # 2. Validação de dígitos verificadores
    if not validate_cnpj_digits(cnpj_clean):
        return {"valid": False, "error": "Dígitos inválidos"}
    
    # 3. Consultar API externa
    try:
        result = await brasilapi_consult_cnpj(cnpj_clean)
        return {
            "valid": True,
            "company_name": result["razao_social"],
            "situation": result["situacao"],
            "source": "brasilapi"
        }
    except Exception as e:
        # Fallback
        return await receitaws_consult_cnpj(cnpj_clean)
```

---

## 🔐 Segurança e Autenticação

### Estratégia de Autenticação

- [ ] JWT tokens
- [ ] OAuth2
- [ ] API Keys
- [ ] [Outro]

### Secrets Management

**Onde armazenar:**
- Desenvolvimento: `.env` local
- Streamlit Cloud: Secrets management
- Produção GCP: Secret Manager

**Secrets necessárias:**
```bash
# .env.example
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
PINECONE_API_KEY=...
DATABASE_URL=postgresql://...
```

---

## 🐳 Docker e Deploy

### Containers

| Container | Base Image | Porta | Dependências |
|-----------|------------|-------|--------------|
| backend | python:3.11 | 8000 | PostgreSQL |
| frontend | python:3.11 | 8501 | Backend API |
| rag | python:3.11 | 8001 | ChromaDB |
| agents | python:3.11 | 8002 | Backend, RAG |
| mcp | python:3.11 | 8003 | - |

### Docker Compose

```yaml
# docker-compose.yml (proposta)
version: '3.8'

services:
  backend:
    build: ./docker/backend.Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
    depends_on:
      - db
  
  frontend:
    build: ./docker/frontend.Dockerfile
    ports:
      - "8501:8501"
    environment:
      - BACKEND_URL=http://backend:8000
    depends_on:
      - backend
  
  # [Adicionar outros serviços]

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=audit_nf
      - POSTGRES_USER=admin
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### Deploy

**Fase 1: Streamlit Cloud**
- Deploy automático do frontend
- Backend em [onde?]
- RAG em [onde?]

**Fase 2: GCP**
- [Definir depois com Ricardo]

---

## 📊 Banco de Dados

### Schema Proposto

```sql
-- Tabela principal de notas fiscais
CREATE TABLE notas_fiscais (
    id UUID PRIMARY KEY,
    numero VARCHAR(20) NOT NULL,
    serie VARCHAR(10),
    chave_acesso VARCHAR(44) UNIQUE,
    cnpj_emitente VARCHAR(14),
    cnpj_destinatario VARCHAR(14),
    valor_total DECIMAL(15,2),
    data_emissao TIMESTAMP,
    status VARCHAR(20),  -- 'pendente', 'aprovada', 'rejeitada'
    xml_content TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- [Adicionar outras tabelas]

CREATE TABLE auditorias (
    id UUID PRIMARY KEY,
    nota_fiscal_id UUID REFERENCES notas_fiscais(id),
    resultado JSONB,
    irregularidades TEXT[],
    confianca DECIMAL(3,2),
    agente_responsavel VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 🧪 Testes

### Estratégia de Testes

**Tipos:**
- [ ] Unitários (pytest)
- [ ] Integração (pytest + docker)
- [ ] E2E (Selenium / Playwright)
- [ ] Carga (Locust)

**Cobertura Mínima:** [80% / 90%]

**Mocks:**
```python
# Exemplo de mock para desenvolvimento
class MockRAGService:
    async def search(self, query: str) -> list:
        return [{"content": "Mock result", "score": 0.9}]
```

---

## 📈 Monitoramento

### Métricas

- [ ] Tempo de resposta por endpoint
- [ ] Taxa de sucesso de auditorias
- [ ] Uso de APIs externas
- [ ] Custo de LLM (tokens)

### Logs

**Estrutura:**
```json
{
    "timestamp": "2024-10-18T10:00:00Z",
    "level": "INFO",
    "module": "agents.audit_agent",
    "action": "audit_invoice",
    "invoice_id": "123",
    "result": "aprovada",
    "duration_ms": 2340
}
```

---

## 💰 Estimativa de Custos

### APIs Pagas

| Serviço | Custo Estimado/Mês | Justificativa |
|---------|-------------------|---------------|
| OpenAI (embeddings) | $XX | [tokens estimados] |
| Anthropic (LLM) | $XX | [tokens estimados] |
| Pinecone (vetorial) | $XX ou Grátis | [registros estimados] |
| **Total** | **$XX** | |

### Otimizações de Custo

- [ ] Cache de embeddings
- [ ] Modelos menores para tarefas simples
- [ ] Batch processing
- [ ] [Adicionar mais]

---

## 🚧 Riscos e Mitigações

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| APIs externas indisponíveis | Média | Alto | Implementar fallbacks |
| Custo de LLM muito alto | Baixa | Médio | Monitorar e otimizar prompts |
| Certificado SEFAZ | Alta | Médio | Iniciar sem, adicionar depois |
| [Adicionar mais] | | | |

---

## 📅 Cronograma

### Sprint 1 (Semana 1-2)
- [ ] Setup de infraestrutura
- [ ] Backend básico funcionando
- [ ] RAG com documentos mockados

### Sprint 2 (Semana 3-4)
- [ ] Implementação de agentes
- [ ] MCP com tools básicas
- [ ] Frontend com upload de NF

### Sprint 3 (Semana 5-6)
- [ ] Integração completa
- [ ] Testes end-to-end
- [ ] Deploy em Streamlit Cloud

### Sprint 4 (Semana 7-8)
- [ ] Refinamentos
- [ ] Documentação
- [ ] Migração para GCP (se aplicável)

---

## ✅ Decisões Pendentes

- [ ] Definir exatamente qual vector store (ChromaDB vs Pinecone)
- [ ] Escolher modelo de LLM (Claude vs GPT-4)
- [ ] Decidir sobre certificado SEFAZ
- [ ] [Adicionar mais]

---

## 📚 Referências

- [Link para llm-examples]
- [Link para documentação do MCP]
- [Link para documentação do RAG]
- [Adicionar mais]

---

## 👥 Aprovação

| Membro | Módulo | Aprovado | Data | Comentários |
|--------|--------|----------|------|-------------|
| [Nome] | Backend | ⏳ | - | |
| [Nome] | RAG | ⏳ | - | |
| [Nome] | Agents | ⏳ | - | |
| [Nome] | MCP | ⏳ | - | |
| [Nome] | Frontend | ⏳ | - | |

**Coordenador:** [Nome]  
**Status:** 🟡 Aguardando aprovação

---

**Última atualização:** [Data]  
**Versão:** 0.1