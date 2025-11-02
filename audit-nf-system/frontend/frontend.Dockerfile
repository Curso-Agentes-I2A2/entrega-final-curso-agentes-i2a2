FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .

# Instalar dependências Python (Streamlit, plotly, pandas)
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código do frontend
COPY . .

# Criar diretório de configuração do Streamlit
RUN mkdir -p /root/.streamlit

# Copiar configuração do Streamlit
COPY .streamlit/config.toml /root/.streamlit/config.toml

# Expor porta
EXPOSE 8501

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Comando padrão
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]