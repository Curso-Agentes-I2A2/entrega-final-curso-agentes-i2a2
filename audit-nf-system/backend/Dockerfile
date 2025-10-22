# backend/Dockerfile

# 1. Usar uma imagem base oficial do Python.
# A tag "slim" é uma versão menor, ideal para produção.
FROM python:3.11-slim

# 2. Definir o diretório de trabalho dentro do contêiner.
# Todos os comandos a seguir serão executados a partir daqui.
WORKDIR /app

# 3. Copiar o arquivo de dependências primeiro.
# Isso aproveita o cache do Docker: se o requirements.txt não mudar,
# o Docker não reinstala tudo a cada build, tornando o processo mais rápido.
COPY requirements.txt .

# 4. Instalar as dependências.
# O --no-cache-dir ajuda a manter a imagem menor.
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copiar todo o resto do código do seu projeto para dentro do contêiner.
COPY . .

# 6. Expor a porta que a aplicação vai usar dentro do contêiner.
# O Uvicorn vai rodar na porta 8000.
EXPOSE 8000

# 7. Definir o comando padrão para iniciar a aplicação.
# Este comando será executado quando o contêiner iniciar.
# Nota: O `command` no seu docker-compose.yml vai sobrescrever este, o que é normal.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]