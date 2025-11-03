FROM python:3.11-slim
WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    wget \
    gnupg \
    chromium \
    chromium-driver \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY ./backend/requirements.txt backend-requirements.txt
COPY ./rag/requirements.txt rag-requirements.txt
COPY ./agents/requirements.txt agents-requirements.txt
COPY ./mcp/requirements.txt mcp-requirements.txt
COPY ./frontend/requirements.txt frontend-requirements.txt
COPY ./tests/requirements.txt tests-requirements.txt

# Instalar dependências
RUN pip install --no-cache-dir -r backend-requirements.txt && \
    pip install --no-cache-dir --upgrade \
    -r rag-requirements.txt \
    -r agents-requirements.txt \
    -r mcp-requirements.txt \
    -r frontend-requirements.txt \
    -r tests-requirements.txt

# Instalar Playwright
RUN pip install playwright && \
    playwright install chromium --with-deps

# Copiar código fonte dos módulos
COPY ./backend /app/backend
COPY ./rag /app/rag
COPY ./agents /app/agents
COPY ./mcp /app/mcp
COPY ./tests /app/tests

# Configurar PYTHONPATH
ENV PYTHONPATH=/app
ENV DATABASE_URL="sqlite:///./test.db"
ENV CORS_ORIGINS="[]"
ENV DEBUG="true"
ENV LOG_LEVEL="INFO"
ENV SECRET_KEY="test-secret-key-for-testing-only"
ENV ALGORITHM="HS256"
ENV ACCESS_TOKEN_EXPIRE_MINUTES="30"
ENV RAG_SERVICE_URL=""
ENV AGENT_SERVICE_URL=""
ENV CORS_ORIGINS='["http://localhost:8501","http://localhost:3000"]'
ENV DATABASE_URL="postgresql://user:pass@localhost:5432/test_db"
ENV DEBUG=true
ENV LOG_LEVEL=INFO

ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# Criar diretórios para relatórios
RUN mkdir -p /app/reports /app/htmlcov



# Comando padrão
CMD ["pytest", "-v", "--cov=.", "--cov-report=html", "--cov-report=term"]