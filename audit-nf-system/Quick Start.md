# ⚡ Quick Start - Sistema de Auditoria

## 🚀 Setup Inicial (1 minuto)

```bash
# 1. Configurar .env
cp .env.example .env
nano .env  # Adicione suas API keys

# 2. Iniciar tudo
docker-compose -f docker/docker-compose.yml up -d --build

# 3. Verificar
docker-compose -f docker/docker-compose.yml ps
```

**Pronto!** Acesse: http://localhost:8501

---

## 🎯 Comandos Mais Usados

### Com Script Helper (Recomendado)
```bash
# Dar permissão (primeira vez)
chmod +x scripts/audit-cli.sh

# Comandos
./scripts/audit-cli.sh start              # Iniciar
./scripts/audit-cli.sh stop               # Parar
./scripts/audit-cli.sh restart            # Reiniciar
./scripts/audit-cli.sh logs               # Ver logs
./scripts/audit-cli.sh status             # Status
./scripts/audit-cli.sh test               # Rodar testes
./scripts/audit-cli.sh test:coverage      # Testes + cobertura
./scripts/audit-cli.sh help               # Ajuda
```

### Comandos Docker Diretos
```bash
# Iniciar
docker-compose -f docker/docker-compose.yml up -d

# Parar
docker-compose -f docker/docker-compose.yml down

# Logs
docker-compose -f docker/docker-compose.yml logs -f

# Rebuild
docker-compose -f docker/docker-compose.yml up -d --build

# Status
docker-compose -f docker/docker-compose.yml ps
```

---

## 🧪 Rodar Testes

### Testes Rápidos
```bash
# Todos os testes
./scripts/audit-cli.sh test

# Apenas unitários
./scripts/audit-cli.sh test:unit

# Com cobertura
./scripts/audit-cli.sh test:coverage
```

### Testes Específicos
```bash
# Teste de um módulo
docker-compose -f docker/docker-compose.yml --profile testing run --rm tests \
  pytest tests/unit/test_backend/ -v

# Teste de um arquivo
docker-compose -f docker/docker-compose.yml --profile testing run --rm tests \
  pytest tests/unit/test_backend/test_invoice_service.py -v

# Teste de uma função
docker-compose -f docker/docker-compose.yml --profile testing run --rm tests \
  pytest tests/unit/test_backend/test_invoice_service.py::test_create_invoice -v
```

---

## 🔍 Debug

### Ver Logs
```bash
# Todos
docker-compose -f docker/docker-compose.yml logs -f

# Backend
docker-compose -f docker/docker-compose.yml logs -f backend

# Filtrar erros
docker-compose -f docker/docker-compose.yml logs -f | grep ERROR
```

### Acessar Container
```bash
# Backend
docker-compose -f docker/docker-compose.yml exec backend bash

# PostgreSQL
docker-compose -f docker/docker-compose.yml exec postgres psql -U audit_user -d audit_nf_db

# Redis
docker-compose -f docker/docker-compose.yml exec redis redis-cli
```

### Health Check Manual
```bash
curl http://localhost:8080/health        # Backend
curl http://localhost:8501/_stcore/health  # Frontend
curl http://localhost:8001/health        # RAG
```

---

## 🆘 Problemas Comuns

### Porta em uso
```bash
# Matar processo na porta 8080
sudo lsof -i :8080
kill -9 <PID>

# Ou mudar porta no docker-compose.yml
# "8081:8080" ao invés de "8080:8080"
```

### Container não sobe
```bash
# Ver erro
docker-compose -f docker/docker-compose.yml logs <serviço>

# Rebuild sem cache
docker-compose -f docker/docker-compose.yml build --no-cache <serviço>
docker-compose -f docker/docker-compose.yml up -d <serviço>
```

### Falta API Key
```bash
# Verificar .env
cat .env

# Editar
nano .env

# Reiniciar
docker-compose -f docker/docker-compose.yml restart
```

### Limpar e Recomeçar
```bash
# Limpar tudo
./scripts/audit-cli.sh clean

# Ou
docker-compose -f docker/docker-compose.yml down -v

# Rebuild completo
docker-compose -f docker/docker-compose.yml up -d --build
```

---

## 📊 URLs Importantes

| Serviço | URL |
|---------|-----|
| **Frontend** | http://localhost:8501 |
| **Backend API** | http://localhost:8080 |
| **API Docs** | http://localhost:8080/docs |
| **RAG** | http://localhost:8001 |
| **Agents** | http://localhost:8002 |
| **MCP** | http://localhost:8003 |
| **ChromaDB** | http://localhost:8000 |

---

## ✅ Checklist Rápido

Antes de começar a desenvolver:

- [ ] `.env` configurado com API keys
- [ ] Todos containers **healthy** (`docker-compose ps`)
- [ ] Frontend acessível (http://localhost:8501)
- [ ] Backend retorna 200 (http://localhost:8080/health)
- [ ] Testes passando (`./scripts/audit-cli.sh test:unit`)

---

## 📚 Docs Completos

Para instruções detalhadas, veja:
- **SETUP_E_TESTES.md** - Documentação completa
- **README.md** - Visão geral do projeto
- **docs/ARCHITECTURE.md** - Arquitetura do sistema

---

## 🎓 Fluxo de Trabalho

```bash
# 1. Primeira vez
cp .env.example .env
# Editar .env com suas keys
docker-compose -f docker/docker-compose.yml up -d --build

# 2. Desenvolvimento diário
docker-compose -f docker/docker-compose.yml up -d
# ... desenvolver ...
docker-compose -f docker/docker-compose.yml restart backend
docker-compose -f docker/docker-compose.yml logs -f backend

# 3. Antes de commit
./scripts/audit-cli.sh test
# Se tudo OK, commit

# 4. Ao final do dia
docker-compose -f docker/docker-compose.yml down
```

---

**Documentação completa:** [SETUP_E_TESTES.md](./SETUP_E_TESTES.md)

**Ajuda:** `./scripts/audit-cli.sh help`