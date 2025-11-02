FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .

# Instalar dependências Python (incluindo transformers, sentence-transformers, chromadb)
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código do RAG
COPY . .

# Criar diretórios para cache e dados
RUN mkdir -p /app/cache /app/embeddings /app/logs

# Expor porta
EXPOSE 8001

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:8001/health || exit 1

# Comando padrão
CMD ["python", "main.py"]