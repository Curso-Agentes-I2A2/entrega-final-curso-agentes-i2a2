# 📦 Requirements.txt para Cada Módulo

## backend/requirements.txt
```txt
# Web Framework
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6

# Database
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
alembic==1.12.1

# Redis
redis==5.0.1
hiredis==2.2.3

# Authentication & Security
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.0

# XML Processing (Notas Fiscais)
lxml==4.9.3
xmltodict==0.13.0

# Utilities
pydantic==2.5.2
pydantic-settings==2.1.0
httpx==0.25.2
```

---

## rag/requirements.txt
```txt
# Vector Database
chromadb==0.4.18

# Embeddings
openai==1.3.7
sentence-transformers==2.2.2
transformers==4.35.2
torch==2.1.1

# Document Processing
langchain==0.0.340
langchain-community==0.0.1
pypdf==3.17.1
python-docx==1.1.0

# Utilities
numpy==1.26.2
pandas==2.1.3
tiktoken==0.5.2
```

---

## agents/requirements.txt
```txt
# LLM & Agents
openai==1.3.7
anthropic==0.7.7
langchain==0.0.340
langgraph==0.0.20

# Tools & Utilities
httpx==0.25.2
redis==5.0.1
pydantic==2.5.2

# JSON Processing
jmespath==1.0.1

# Async
asyncio==3.4.3
aiohttp==3.9.1
```

---

## mcp/requirements.txt
```txt
# MCP SDK
mcp==0.1.0

# Server
fastapi==0.104.1
uvicorn[standard]==0.24.0

# Client Libraries
httpx==0.25.2
websockets==12.0

# Utilities
pydantic==2.5.2
python-dotenv==1.0.0
```

---

## frontend/requirements.txt
```txt
# Streamlit
streamlit==1.29.0

# Data Visualization
plotly==5.18.0
pandas==2.1.3
numpy==1.26.2

# HTTP Client
httpx==0.25.2
requests==2.31.0

# PDF Generation
reportlab==4.0.7

# Utilities
python-dotenv==1.0.0
```

---

## tests/requirements.txt
```txt
# Testing Framework
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
pytest-mock==3.12.0
pytest-xdist==3.5.0

# HTTP Testing
httpx==0.25.2
requests==2.31.0
responses==0.24.1

# E2E Testing
playwright==1.40.0
selenium==4.16.0

# Load Testing
locust==2.19.1

# Mocking
faker==20.1.0
factory-boy==3.3.0

# Database Testing
pytest-postgresql==5.0.0
fakeredis==2.20.0

# Coverage & Reports
coverage==7.3.3
pytest-html==4.1.1
pytest-json-report==1.5.0
```

---

## shared/requirements.txt
```txt
# Shared utilities entre módulos
pydantic==2.5.2
python-dotenv==1.0.0
structlog==23.2.0
```

---

## 🔧 Como Criar os Arquivos

Execute em cada diretório:

```bash
# Backend
cat > backend/requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
alembic==1.12.1
redis==5.0.1
hiredis==2.2.3
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.0
lxml==4.9.3
xmltodict==0.13.0
pydantic==2.5.2
pydantic-settings==2.1.0
httpx==0.25.2
EOF

# RAG
cat > rag/requirements.txt << 'EOF'
chromadb==0.4.18
openai==1.3.7
sentence-transformers==2.2.2
transformers==4.35.2
torch==2.1.1
langchain==0.0.340
langchain-community==0.0.1
pypdf==3.17.1
python-docx==1.1.0
numpy==1.26.2
pandas==2.1.3
tiktoken==0.5.2
EOF

# Agents
cat > agents/requirements.txt << 'EOF'
openai==1.3.7
anthropic==0.7.7
langchain==0.0.340
langgraph==0.0.20
httpx==0.25.2
redis==5.0.1
pydantic==2.5.2
jmespath==1.0.1
asyncio==3.4.3
aiohttp==3.9.1
EOF

# MCP
cat > mcp/requirements.txt << 'EOF'
mcp==0.1.0
fastapi==0.104.1
uvicorn[standard]==0.24.0
httpx==0.25.2
websockets==12.0
pydantic==2.5.2
python-dotenv==1.0.0
EOF

# Frontend
cat > frontend/requirements.txt << 'EOF'
streamlit==1.29.0
plotly==5.18.0
pandas==2.1.3
numpy==1.26.2
httpx==0.25.2
requests==2.31.0
reportlab==4.0.7
python-dotenv==1.0.0
EOF

# Tests
cat > tests/requirements.txt << 'EOF'
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
pytest-mock==3.12.0
pytest-xdist==3.5.0
httpx==0.25.2
requests==2.31.0
responses==0.24.1
playwright==1.40.0
selenium==4.16.0
locust==2.19.1
faker==20.1.0
factory-boy==3.3.0
pytest-postgresql==5.0.0
fakeredis==2.20.0
coverage==7.3.3
pytest-html==4.1.1
pytest-json-report==1.5.0
EOF
```

---

## 📝 Notas Importantes

### Versões Pinadas
- Todas as versões estão pinadas para garantir reprodutibilidade
- Atualize conforme necessário, mas teste tudo após atualizar

### Dependências Pesadas
- `torch` no RAG (~800MB) - considere usar CPU-only em dev
- `playwright` precisa de browsers (~300MB)
- `transformers` com models (~500MB)

### Alternativas Leves para Dev
Para desenvolvimento local mais rápido, você pode:

```txt
# rag/requirements-dev.txt (sem torch)
chromadb==0.4.18
openai==1.3.7
langchain==0.0.340
# Remove: torch, transformers, sentence-transformers
```

### Instalação Rápida
```bash
# Instalar em cada módulo
for dir in backend rag agents mcp frontend tests; do
    cd $dir && pip install -r requirements.txt && cd ..
done
```

---

## ✅ Verificar Instalação

```bash
# Verificar se tudo foi instalado
python -c "import fastapi; import openai; import langchain; print('✅ OK')"
```