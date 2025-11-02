# 🚀 Setup e Execução - Sistema de Auditoria de Notas Fiscais

## 📋 Pré-requisitos

### Obrigatórios
- Docker 24.0+ e Docker Compose 2.0+
- Git
- 8GB RAM disponível (mínimo)
- 20GB espaço em disco

### API Keys Necessárias
- **OpenAI API Key** (para embeddings e GPT)
- **Anthropic API Key** (para Claude em agentes)

---

## 🔧 Configuração Inicial

### 1. Clonar o Repositório
```bash
git clone <url-do-repositorio>
cd audit-nf-system
```

### 2. Configurar Variáveis de Ambiente
```bash
# Copiar o arquivo de exemplo
cp .env.example .env

# Editar com suas API keys
nano .env  # ou vim, code, etc.
```

**⚠️ IMPORTANTE:** Preencha suas API keys no arquivo `.env`:
```bash
OPENAI_API_KEY=sk-proj-seu-token-aqui
ANTHROPIC_API_KEY=sk-ant-seu-token-aqui
JWT_SECRET=$(openssl rand -hex 32)  # gere uma chave segura
```

### 3. Verificar Estrutura de Arquivos
```bash
# Sua estrutura deve estar assim:
audit-nf-system/
├── docker/
│   ├── backend.Dockerfile
│   ├── rag.Dockerfile
│   ├── agents.Dockerfile
│   ├── mcp.Dockerfile
│   ├── frontend.Dockerfile
│   ├── tests.Dockerfile
│   └── docker-compose.yml
├── backend/
├── rag/
├── agents/
├── mcp/
├── frontend/
├── tests/
├── .env
└── .env.example
```

---

## 🐳 Build e Execução

### Opção 1: Build e Start em Um Comando
```bash
# Build e start de todos os serviços
docker-compose -f docker/docker-compose.yml up --build -d

# Ver logs em tempo real
docker-compose -f docker/docker-compose.yml logs -f
```

### Opção 2: Build Separado
```bash
# Build de todas as imagens
docker-compose -f docker/docker-compose.yml build

# Iniciar serviços
docker-compose -f docker/docker-compose.yml up -d

# Verificar status
docker-compose -f docker/docker-compose.yml ps
```

### Opção 3: Build Individual por Serviço
```bash
# Build apenas backend
docker-compose -f docker/docker-compose.yml build backend

# Build apenas frontend
docker-compose -f docker/docker-compose.yml build frontend

# Start serviço específico
docker-compose -f docker/docker-compose.yml up -d backend
```

---

## 🔍 Verificação de Saúde dos Serviços

### Checar Status
```bash
# Ver todos os containers
docker-compose -f docker/docker-compose.yml ps

# Health check manual
docker-compose -f docker/docker-compose.yml exec backend curl http://localhost:8080/health
docker-compose -f docker/docker-compose.yml exec frontend curl http://localhost:8501/_stcore/health
```

### Acessar Logs
```bash
# Todos os serviços
docker-compose -f docker/docker-compose.yml logs -f

# Serviço específico
docker-compose -f docker/docker-compose.yml logs -f backend
docker-compose -f docker/docker-compose.yml logs -f frontend
docker-compose -f docker/docker-compose.yml logs -f agents
```

### URLs de Acesso
- **Frontend (Streamlit):** http://localhost:8501
- **Backend API:** http://localhost:8080
- **API Docs (Swagger):** http://localhost:8080/docs
- **RAG Service:** http://localhost:8001
- **Agents Service:** http://localhost:8002
- **MCP Server:** http://localhost:8003
- **ChromaDB:** http://localhost:8000
- **PostgreSQL:** localhost:5432

---

## 🧪 Executando Testes

### Testes Unitários

#### Todos os Testes Unitários
```bash
# Rodar container de testes
docker-compose -f docker/docker-compose.yml --profile testing run --rm tests \
  pytest tests/unit/ -v
```

#### Testes por Módulo
```bash
# Backend
docker-compose -f docker/docker-compose.yml --profile testing run --rm tests \
  pytest tests/unit/test_backend/ -v

# RAG
docker-compose -f docker/docker-compose.yml --profile testing run --rm tests \
  pytest tests/unit/test_rag/ -v

# Agents
docker-compose -f docker/docker-compose.yml --profile testing run --rm tests \
  pytest tests/unit/test_agents/ -v
```

#### Teste Específico
```bash
# Testar apenas invoice service
docker-compose -f docker/docker-compose.yml --profile testing run --rm tests \
  pytest tests/unit/test_backend/test_invoice_service.py -v
```

### Testes de Integração

```bash
# Todos os testes de integração
docker-compose -f docker/docker-compose.yml --profile testing run --rm tests \
  pytest tests/integration/ -v

# Workflow específico
docker-compose -f docker/docker-compose.yml --profile testing run --rm tests \
  pytest tests/integration/test_workflows/test_audit_workflow.py -v
```

### Testes End-to-End (E2E)

```bash
# Todos os testes E2E
docker-compose -f docker/docker-compose.yml --profile testing run --rm tests \
  pytest tests/e2e/ -v --headed

# Teste completo de auditoria
docker-compose -f docker/docker-compose.yml --profile testing run --rm tests \
  pytest tests/e2e/test_scenarios/test_complete_audit.py -v
```

### Testes de Carga (Load Testing)

```bash
# Iniciar teste de carga com Locust
docker-compose -f docker/docker-compose.yml --profile testing run --rm tests \
  locust -f tests/load/locustfile.py --host=http://backend:8080

# Com interface web (acessar em http://localhost:8089)
docker-compose -f docker/docker-compose.yml --profile testing run --rm -p 8089:8089 tests \
  locust -f tests/load/locustfile.py --host=http://backend:8080 --web-host=0.0.0.0
```

### Testes com Cobertura

```bash
# Gerar relatório de cobertura
docker-compose -f docker/docker-compose.yml --profile testing run --rm tests \
  pytest --cov=. --cov-report=html --cov-report=term

# Copiar relatório HTML
docker cp audit-tests:/app/htmlcov ./htmlcov

# Abrir no browser
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

### Testes Rápidos (Skip de Testes Lentos)

```bash
# Pular testes marcados como slow
docker-compose -f docker/docker-compose.yml --profile testing run --rm tests \
  pytest -v -m "not slow"

# Apenas testes rápidos
docker-compose -f docker/docker-compose.yml --profile testing run --rm tests \
  pytest -v -m "fast"
```

---

## 📊 Visualizar Relatórios de Testes

### Relatórios Disponíveis
```bash
# HTML Coverage Report
docker-compose -f docker/docker-compose.yml --profile testing run --rm tests \
  pytest --cov=. --cov-report=html

# JUnit XML (para CI/CD)
docker-compose -f docker/docker-compose.yml --profile testing run --rm tests \
  pytest --junitxml=reports/junit.xml

# JSON Report
docker-compose -f docker/docker-compose.yml --profile testing run --rm tests \
  pytest --json-report --json-report-file=reports/report.json
```

### Copiar Relatórios
```bash
# Criar diretório local
mkdir -p ./test-reports

# Copiar relatórios
docker cp audit-tests:/app/reports ./test-reports
docker cp audit-tests:/app/htmlcov ./test-reports/coverage
```

---

## 🔄 Comandos Úteis

### Reiniciar Serviços
```bash
# Reiniciar todos
docker-compose -f docker/docker-compose.yml restart

# Reiniciar serviço específico
docker-compose -f docker/docker-compose.yml restart backend
```

### Rebuild Após Mudanças
```bash
# Rebuild e restart
docker-compose -f docker/docker-compose.yml up -d --build

# Rebuild sem cache (limpo)
docker-compose -f docker/docker-compose.yml build --no-cache
docker-compose -f docker/docker-compose.yml up -d
```

### Acessar Container
```bash
# Shell no backend
docker-compose -f docker/docker-compose.yml exec backend bash

# Shell no postgres
docker-compose -f docker/docker-compose.yml exec postgres psql -U audit_user -d audit_nf_db

# Shell no redis
docker-compose -f docker/docker-compose.yml exec redis redis-cli
```

### Limpar Tudo
```bash
# Parar e remover containers
docker-compose -f docker/docker-compose.yml down

# Remover volumes também (⚠️ apaga dados)
docker-compose -f docker/docker-compose.yml down -v

# Remover imagens
docker-compose -f docker/docker-compose.yml down --rmi all
```

---

## 🐛 Troubleshooting

### Problema: Container não inicia
```bash
# Ver logs detalhados
docker-compose -f docker/docker-compose.yml logs <servico>

# Verificar dependências
docker-compose -f docker/docker-compose.yml ps
```

### Problema: Porta já em uso
```bash
# Mudar portas no docker-compose.yml
# Ex: "8080:8080" -> "8081:8080"

# Ou parar processo usando a porta
sudo lsof -i :8080
kill -9 <PID>
```

### Problema: Testes falhando
```bash
# Verificar se todos os serviços estão up
docker-compose -f docker/docker-compose.yml ps

# Rodar testes com mais verbosidade
docker-compose -f docker/docker-compose.yml --profile testing run --rm tests \
  pytest -vvv --tb=short

# Rodar apenas um teste para debug
docker-compose -f docker/docker-compose.yml --profile testing run --rm tests \
  pytest tests/unit/test_backend/test_invoice_service.py::test_create_invoice -vvv
```

### Problema: Falta de memória
```bash
# Aumentar memória do Docker Desktop
# Settings -> Resources -> Memory (mínimo 8GB)

# Ou limpar recursos não usados
docker system prune -a --volumes
```

---

## 📈 Monitoramento

### Métricas de Recursos
```bash
# Ver uso de recursos
docker stats

# Usar ctop (interface melhor)
docker run --rm -ti \
  --name=ctop \
  --volume /var/run/docker.sock:/var/run/docker.sock:ro \
  quay.io/vektorlab/ctop:latest
```

### Logs Estruturados
```bash
# Logs com timestamp
docker-compose -f docker/docker-compose.yml logs -f --timestamps

# Filtrar por nível
docker-compose -f docker/docker-compose.yml logs -f | grep ERROR
```

---

## 🎯 Fluxo de Desenvolvimento Recomendado

### Primeira Execução
```bash
1. cp .env.example .env
2. # Preencher API keys
3. docker-compose -f docker/docker-compose.yml up --build -d
4. docker-compose -f docker/docker-compose.yml logs -f
5. # Aguardar todos os healthchecks passarem
6. curl http://localhost:8080/health
7. open http://localhost:8501
```

### Desenvolvimento Diário
```bash
1. docker-compose -f docker/docker-compose.yml up -d
2. # Desenvolver...
3. docker-compose -f docker/docker-compose.yml restart <servico-modificado>
4. docker-compose -f docker/docker-compose.yml logs -f <servico>
```

### Antes de Commit
```bash
1. # Rodar testes
   docker-compose -f docker/docker-compose.yml --profile testing run --rm tests
2. # Verificar cobertura
   docker-compose -f docker/docker-compose.yml --profile testing run --rm tests \
     pytest --cov=. --cov-report=term
3. # Se tudo OK, commit
```

---

## 📚 Referências Rápidas

### Comandos Docker Compose
- `up`: Criar e iniciar containers
- `down`: Parar e remover containers
- `build`: Build/rebuild de serviços
- `logs`: Ver logs
- `ps`: Listar containers
- `exec`: Executar comando em container
- `restart`: Reiniciar serviços

### Flags Úteis
- `-d`: Detached mode (background)
- `-f`: Especificar arquivo compose
- `--build`: Rebuild antes de start
- `--profile`: Usar profile específico
- `-v`: Verbose (para testes)

---

## ✅ Checklist Final

Antes de considerar o ambiente pronto:

- [ ] Todos os containers estão **healthy**
- [ ] Frontend acessível em http://localhost:8501
- [ ] Backend retorna 200 em http://localhost:8080/health
- [ ] PostgreSQL conecta
- [ ] Redis conecta
- [ ] ChromaDB acessível
- [ ] Testes unitários passam
- [ ] Pode fazer upload de NF no frontend

---

## 🆘 Suporte

Se encontrar problemas:

1. Verificar logs: `docker-compose -f docker/docker-compose.yml logs -f`
2. Verificar health: `docker-compose -f docker/docker-compose.yml ps`
3. Limpar e reconstruir: `docker-compose -f docker/docker-compose.yml down -v && docker-compose -f docker/docker-compose.yml up --build -d`
4. Abrir issue no repositório com logs completos

---

**Bom desenvolvimento! 🚀**