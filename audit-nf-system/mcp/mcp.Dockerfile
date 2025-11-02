FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .

# Instalar dependências Python (MCP SDK)
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código do MCP
COPY . .

# Criar diretórios necessários
RUN mkdir -p /app/logs

# Expor porta
EXPOSE 8003

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8003/health || exit 1

# Comando padrão
CMD ["python", "servers/nf_context_server.py"]