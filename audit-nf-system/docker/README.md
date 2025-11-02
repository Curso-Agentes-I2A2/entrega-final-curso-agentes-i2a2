# 🐳 Exemplos de Dockerfiles

Estrutura básica de cada Dockerfile do projeto.

---

## 📦 backend.Dockerfile

```dockerfile
# Multi-stage build

# ===========================================================================
# Stage 1: Base
# ===========================================================================
FROM python:3.11-slim as base

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ===========================================================================
# Stage 2: Development
# ===========================================================================
FROM base as development

ENV PYTHONUNBUFFERED=1
ENV DEBUG=true

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ===========================================================================
# Stage 3: Production
# ===========================================================================
FROM base as production

ENV PYTHONUNBUFFERED=1
ENV DEBUG=false

COPY . .

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

---

## 🖥️ frontend.Dockerfile

```dockerfile
# Multi-stage build

# ===========================================================================
# Stage 1: Base
# ===========================================================================
FROM python:3.11-slim as base

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ===========================================================================
# Stage 2: Development
# ===========================================================================
FROM base as development

ENV PYTHONUNBUFFERED=1

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]

# ===========================================================================
# Stage 3: Production
# ===========================================================================
FROM base as production

ENV PYTHONUNBUFFERED=1

COPY . .

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8501

CMD ["streamlit", "run", "app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--browser.gatherUsageStats=false"]
```

---

## 🧠 rag.Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8001

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
```

---

## 🤖 agents.Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8002

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]
```

---

## 🔌 mcp.Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8003

CMD ["python", "main.py"]
```

---

## 📋 .dockerignore

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
.venv

# IDE
.vscode/
.idea/
*.swp
*.swo

# Environment
.env
.env.local

# Databases
*.db
*.sqlite

# Logs
*.log
logs/

# Testing
.pytest_cache/
.coverage
htmlcov/

# OS
.DS_Store
Thumbs.db

# Git
.git/
.gitignore

# Docker
Dockerfile
docker-compose*.yml
.dockerignore

# Docs
docs/
*.md
!README.md

# Data
data/
uploads/
temp/
```

---

## 🔨 Como Usar

### Build Individual

```bash
# Backend
docker build -t audit-backend -f docker/backend.Dockerfile backend/

# Frontend
docker build -t audit-frontend -f docker/frontend.Dockerfile frontend/

# RAG
docker build -t audit-rag -f docker/rag.Dockerfile rag/

# Agents
docker build -t audit-agents -f docker/agents.Dockerfile agents/

# MCP
docker build -t audit-mcp -f docker/mcp.Dockerfile mcp/
```

### Build Multi-stage

```bash
# Development
docker build --target development -t audit-backend:dev \
  -f docker/backend.Dockerfile backend/

# Production
docker build --target production -t audit-backend:prod \
  -f docker/backend.Dockerfile backend/
```

### Testar Localmente

```bash
# Backend
docker run -p 8000:8000 \
  -e DATABASE_URL=sqlite:///./test.db \
  audit-backend:dev

# Frontend
docker run -p 8501:8501 \
  -e BACKEND_URL=http://localhost:8000 \
  audit-frontend:dev
```

---

## 💡 Boas Práticas

### Multi-stage Builds
✅ Usa multi-stage para separar dev/prod
✅ Reduz tamanho da imagem final
✅ Mantém apenas dependências necessárias

### Segurança
✅ Usa usuário não-root
✅ Não copia arquivos desnecessários (.dockerignore)
✅ Remove cache do apt
✅ Não inclui secrets nas imagens

### Performance
✅ Cache de layers otimizado (COPY requirements antes)
✅ Combina comandos RUN para menos layers
✅ Remove arquivos temporários

### Desenvolvimento
✅ Hot reload em desenvolvimento
✅ Volumes montados para código
✅ Debug ports expostos

---

## 🎯 Estrutura Final

```
docker/
├── backend.Dockerfile       ✅
├── frontend.Dockerfile      ✅
├── rag.Dockerfile          ✅
├── agents.Dockerfile       ✅
├── mcp.Dockerfile          ✅
├── .dockerignore           ✅
├── docker-compose.yml      ✅
├── docker-compose.dev.yml  ✅
├── .env.example            ✅
└── init-db.sql            ✅
```

---

**Dockerfiles prontos! Build e deploy! 🚀**