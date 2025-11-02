backend/
├── src/
│   ├── invoice_processing/
│   │   ├── __init__.py
│   │   ├── processor.py          # Processa XMLs de NF-e
│   │   └── parser.py              # Parse de XML
│   │
│   ├── validation/
│   │   ├── __init__.py
│   │   ├── validator.py           # Validações de negócio
│   │   └── rules.py               # Regras fiscais
│   │
│   └── synthetic_nf/
│       ├── __init__.py
│       └── generator.py           # Gera NFs sintéticas para teste
│
├── api/
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── invoice_routes.py      # Rotas de NF
│   │   ├── audit_routes.py        # Rotas de auditoria
│   │   └── auth_routes.py         # Rotas de autenticação
│   │
│   ├── controllers/
│   │   ├── __init__.py
│   │   ├── invoice_controller.py
│   │   └── audit_controller.py
│   │
│   └── middlewares/
│       ├── __init__.py
│       ├── auth_middleware.py
│       └── logging_middleware.py
│
├── models/
│   ├── __init__.py
│   ├── invoice.py                 # Modelo de NF
│   ├── audit.py                   # Modelo de auditoria
│   └── user.py                    # Modelo de usuário
│
├── services/
│   ├── __init__.py
│   ├── invoice_service.py         # Lógica de negócio de NF
│   ├── audit_service.py           # Lógica de auditoria
│   └── rag_client.py              # Cliente para serviço RAG
│
├── database/
│   ├── __init__.py
│   └── connection.py              # Configuração DB
│
├── schemas/
│   ├── __init__.py
│   ├── invoice_schema.py          # Schemas Pydantic
│   └── audit_schema.py
│
├── config.py    ✅                  # Configurações
├── main.py                        # Entry point
└── requirements.txt ✅

# 🧾 Sistema de Auditoria de Notas Fiscais - Backend

Backend FastAPI para sistema de auditoria automatizada de Notas Fiscais Eletrônicas (NF-e) brasileiras usando IA.

## 📋 Funcionalidades

- ✅ Upload e processamento de XMLs de NF-e
- ✅ Validação automática de dados fiscais
- ✅ Auditoria automatizada com IA
- ✅ Integração com RAG para contexto fiscal
- ✅ API REST completa e documentada
- ✅ Processamento assíncrono
- ✅ Banco de dados PostgreSQL

## 🛠️ Tecnologias

- **FastAPI** - Framework web moderno e rápido
- **SQLAlchemy** - ORM para PostgreSQL
- **Pydantic** - Validação de dados
- **asyncpg** - Driver assíncrono PostgreSQL
- **lxml** - Parser de XML
- **httpx** - Cliente HTTP assíncrono

## 📁 Estrutura do Projeto

```
backend/
├── api/
│   └── routes/          # Endpoints da API
├── models/              # Modelos SQLAlchemy (ORM)
├── schemas/             # Schemas Pydantic (validação)
├── services/            # Lógica de negócio
├── database/            # Configuração do banco
├── config.py            # Configurações
├── main.py              # Entry point
└── requirements.txt     # Dependências
```

## 🚀 Instalação

### 1. Pré-requisitos

- Python 3.11+
- PostgreSQL 14+
- pip e virtualenv

### 2. Configurar Ambiente

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt
```

### 3. Configurar Banco de Dados

```bash
# Criar banco de dados PostgreSQL
createdb nf_audit

# Ou via psql:
psql -U postgres
CREATE DATABASE nf_audit;
\q
```

### 4. Configurar Variáveis de Ambiente

```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar .env com suas configurações
nano .env
```

**Variáveis importantes:**
```bash
DATABASE_URL=postgresql://usuario:senha@localhost:5432/nf_audit
SECRET_KEY=seu-secret-key-super-seguro-min-32-chars
DEBUG=True
```

### 5. Inicializar Banco de Dados

As tabelas serão criadas automaticamente no primeiro startup da aplicação.

## ▶️ Executar

### Modo Desenvolvimento

```bash
# Com auto-reload
uvicorn main:app --reload --port 8000

# Ou usando Python
python main.py
```

### Modo Produção

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

A API estará disponível em:
- **API:** http://localhost:8000
- **Documentação interativa:** http://localhost:8000/docs
- **Documentação alternativa:** http://localhost:8000/redoc

## 📚 Uso da API

### 1. Upload de Nota Fiscal

```bash
curl -X POST "http://localhost:8000/api/invoices/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@nota_fiscal.xml"
```

**Resposta:**
```json
{
  "message": "Nota fiscal processada com sucesso",
  "invoice_id": "550e8400-e29b-41d4-a716-446655440000",
  "chave_acesso": "35210512345678000190550010000000011123456789",
  "status": "pendente"
}
```

### 2. Listar Notas Fiscais

```bash
curl "http://localhost:8000/api/invoices?page=1&page_size=20"
```

### 3. Iniciar Auditoria

```bash
curl -X POST "http://localhost:8000/api/audits/invoices/{invoice_id}"
```

**Resposta:**
```json
{
  "message": "Auditoria iniciada com sucesso",
  "audit_id": "660e8400-e29b-41d4-a716-446655440001",
  "status": "pendente",
  "estimated_time": 30
}
```

### 4. Verificar Status da Auditoria

```bash
curl "http://localhost:8000/api/audits/{audit_id}/status"
```

### 5. Buscar Resultado Completo

```bash
curl "http://localhost:8000/api/audits/{audit_id}"
```

## 🔌 Integração com RAG

O sistema integra-se com um serviço RAG para busca de contexto fiscal. Configure a URL do RAG no `.env`:

```bash
RAG_SERVICE_URL=http://localhost:8001
```

Se não configurado, o sistema usa dados mock para desenvolvimento.

## 🧪 Testando

### Health Check

```bash
curl http://localhost:8000/health
```

### Teste Manual com XML de Exemplo

Crie um arquivo `test_nfe.xml` com uma NF-e válida e faça upload:

```bash
curl -X POST "http://localhost:8000/api/invoices/upload" \
  -F "file=@test_nfe.xml"
```

## 📊 Modelos de Dados

### Nota Fiscal (Invoice)
- Identificadores (número, série, chave de acesso)
- Emitente e destinatário (CNPJ, razão social)
- Valores (total, produtos, impostos)
- XML completo
- Status e timestamps

### Auditoria (Audit)
- Referência à nota fiscal
- Status (pendente, em_andamento, concluída)
- Resultado (aprovada, rejeitada, revisao_necessaria)
- Irregularidades encontradas
- Score de confiança
- Análise detalhada (JSON)
- Dados do RAG utilizados

## 🔐 Autenticação

⚠️ **Nota:** A autenticação JWT está preparada mas não implementada completamente nesta versão inicial. Para implementar:

1. Criar endpoints de login/registro em `api/routes/auth_routes.py`
2. Implementar middleware de autenticação
3. Adicionar dependência de auth nas rotas protegidas

## 🐛 Troubleshooting

### Erro de conexão com banco

```bash
# Verificar se PostgreSQL está rodando
sudo systemctl status postgresql

# Testar conexão
psql -U postgres -d nf_audit
```

### Erro ao importar lxml

```bash
# Linux (Ubuntu/Debian)
sudo apt-get install libxml2-dev libxslt-dev python3-dev

# Mac
brew install libxml2 libxslt

# Reinstalar
pip install --force-reinstall lxml
```

### Porta já em uso

```bash
# Mudar porta no .env
PORT=8001

# Ou ao executar
uvicorn main:app --port 8001
```

## 📈 Próximos Passos

- [ ] Implementar autenticação JWT completa
- [ ] Adicionar testes unitários e de integração
- [ ] Implementar rate limiting
- [ ] Adicionar mais validações fiscais
- [ ] Integração real com serviço de Agents
- [ ] Dashboard de estatísticas
- [ ] Exportação de relatórios
- [ ] Webhooks para notificações

## 📄 Licença

MIT License

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📞 Suporte

Para questões e suporte, abra uma issue no GitHub ou entre em contato.

---

Desenvolvido com ❤️ usando FastAPI