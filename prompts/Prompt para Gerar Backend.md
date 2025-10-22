# 🚀 Prompt para Gerar Backend (FastAPI)

**Instruções:** Copie este prompt e cole no Claude ou GPT-4 para gerar o código inicial do backend.

---

## PROMPT:

```
Você é um especialista em Python e FastAPI. Preciso que você crie a estrutura inicial completa de um backend para um sistema de auditoria de notas fiscais brasileiras.

CONTEXTO DO PROJETO:
- Sistema de auditoria automatizada de notas fiscais (NF-e)
- Upload de XML/PDF de notas fiscais
- Validação automática usando IA
- API REST para comunicação com frontend Streamlit
- Integração com serviços RAG (busca vetorial) e Agentes de IA

REQUISITOS TÉCNICOS:
- Framework: FastAPI
- Banco de dados: PostgreSQL (usar SQLAlchemy)
- Autenticação: JWT
- Validação: Pydantic
- Processamento assíncrono: async/await
- Estrutura modular e escalável

ESTRUTURA DE PASTAS:
```
backend/
├── src/
│   ├── invoice_processing/
│   │   ├── __init__.py
│   │   ├── processor.py      # Processa XMLs de NF-e
│   │   └── parser.py          # Parse de XML
│   ├── validation/
│   │   ├── __init__.py
│   │   ├── validator.py       # Validações de negócio
│   │   └── rules.py           # Regras fiscais
│   └── synthetic_nf/
│       ├── __init__.py
│       └── generator.py       # Gera NFs sintéticas para teste
├── api/
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── invoice_routes.py  # Rotas de NF
│   │   ├── audit_routes.py    # Rotas de auditoria
│   │   └── auth_routes.py     # Rotas de autenticação
│   ├── controllers/
│   │   ├── __init__.py
│   │   ├── invoice_controller.py
│   │   └── audit_controller.py
│   └── middlewares/
│       ├── __init__.py
│       ├── auth_middleware.py
│       └── logging_middleware.py
├── models/
│   ├── __init__.py
│   ├── invoice.py             # Modelo de NF
│   ├── audit.py               # Modelo de auditoria
│   └── user.py                # Modelo de usuário
├── services/
│   ├── __init__.py
│   ├── invoice_service.py     # Lógica de negócio de NF
│   ├── audit_service.py       # Lógica de auditoria
│   └── rag_client.py          # Cliente para serviço RAG
├── database/
│   ├── __init__.py
│   └── connection.py          # Configuração DB
├── schemas/
│   ├── __init__.py
│   ├── invoice_schema.py      # Schemas Pydantic
│   └── audit_schema.py
├── config.py                  # Configurações
├── main.py                    # Entry point
└── requirements.txt
```

POR FAVOR, GERE:

1. **main.py** - Aplicação FastAPI principal com:
   - Configuração de CORS
   - Inclusão de routers
   - Middleware de autenticação
   - Health check endpoint
   - Tratamento de erros global

2. **config.py** - Configurações usando pydantic-settings:
   - Variáveis de ambiente
   - Configuração de banco de dados
   - Configuração de JWT
   - URLs de serviços externos (RAG, Agents)

3. **models/invoice.py** - Modelo SQLAlchemy de Nota Fiscal com campos:
   - id (UUID)
   - numero, serie, chave_acesso
   - cnpj_emitente, cnpj_destinatario
   - valor_total, data_emissao
   - xml_content (TEXT)
   - status (enum: pendente, aprovada, rejeitada)
   - created_at, updated_at

4. **models/audit.py** - Modelo de Auditoria:
   - id, nota_fiscal_id (FK)
   - resultado (JSONB)
   - irregularidades (Array)
   - confianca (Decimal)
   - agente_responsavel
   - created_at

5. **schemas/invoice_schema.py** - Schemas Pydantic:
   - InvoiceCreate
   - InvoiceResponse
   - InvoiceUpdate
   - InvoiceList

6. **api/routes/invoice_routes.py** - Rotas principais:
   - POST /api/invoices/upload - Upload de XML
   - GET /api/invoices - Listar NFs
   - GET /api/invoices/{id} - Detalhe de NF
   - POST /api/invoices/{id}/audit - Iniciar auditoria
   - GET /api/invoices/{id}/status - Status da auditoria

7. **services/invoice_service.py** - Lógica de negócio:
   - Processar XML de NF-e
   - Validar estrutura
   - Salvar no banco
   - Integrar com RAG (mock por enquanto)
   - Integrar com Agents (mock por enquanto)

8. **services/rag_client.py** - Cliente HTTP para serviço RAG:
   - search(query: str) -> List[Document]
   - Mock por enquanto se RAG_URL não estiver configurado

9. **database/connection.py** - Setup do banco:
   - Engine SQLAlchemy
   - SessionLocal
   - Base declarativa

10. **requirements.txt** - Dependências principais:
    - fastapi
    - uvicorn[standard]
    - sqlalchemy
    - psycopg2-binary
    - pydantic-settings
    - python-jose[cryptography]
    - passlib[bcrypt]
    - python-multipart
    - httpx
    - lxml (para XML)

IMPORTANTE:
- Use async/await em todas as rotas e services
- Adicione type hints em tudo
- Inclua docstrings em funções principais
- Implemente tratamento de erros adequado
- Use HTTPException do FastAPI
- Configure CORS para permitir frontend Streamlit
- Implemente mock do serviço RAG que retorna dados fictícios quando RAG não está disponível
- Adicione exemplos de uso nas docstrings

FORMATO DE RESPOSTA:
Por favor, gere cada arquivo completo, com comentários explicativos. Organize a resposta por arquivo, com título claro indicando o caminho do arquivo.
```

---

## EXEMPLO DE USO:

1. Copie o prompt acima
2. Cole no Claude (claude.ai) ou ChatGPT
3. Claude gerará todos os arquivos
4. Copie os arquivos para seu projeto
5. Ajuste conforme necessário

---

## PÓS-GERAÇÃO:

Após receber o código, execute:

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Teste se funciona
uvicorn main:app --reload
# Acesse: http://localhost:8000/docs
```