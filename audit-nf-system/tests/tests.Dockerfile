FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema para testes (incluindo chromium para Playwright)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    wget \
    gnupg \
    chromium \
    chromium-driver \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements de todos os módulos
COPY ./backend/requirements.txt requirements.txt
COPY ./rag/requirements.txt requirements.txt
COPY ./agents/requirements.txt requirements.txt
COPY ./mcp/requirements.txt requirements.txt
COPY ./frontend/requirements.txt requirements.txt
COPY ./tests/requirements.txt requirements.txt

# Instalar todas as dependências
RUN pip install --no-cache-dir \
    -r backend-requirements.txt \
    -r rag-requirements.txt \
    -r agents-requirements.txt \
    -r mcp-requirements.txt \
    -r frontend-requirements.txt \
    -r tests-requirements.txt

# Instalar Playwright e browsers
RUN pip install playwright && \
    playwright install chromium --with-deps

# Criar diretórios para relatórios
RUN mkdir -p /app/reports /app/htmlcov

# Variável de ambiente para Playwright
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# Comando padrão (pode ser sobrescrito)
CMD ["pytest", "-v", "--cov=.", "--cov-report=html", "--cov-report=term"]