# Sistema de Auditoria de Notas Fiscais - Estrutura do Projeto

## 📋 Visão Geral
Sistema modular para auditoria automatizada de notas fiscais usando IA, RAG, agentes inteligentes e MCP.

---

## 🎯 Módulos e Responsabilidades

### 1️⃣ **BACKEND** (Desenvolvedor Backend)
**Pasta:** `/backend`

**Responsabilidades:**
- API REST para gerenciamento de notas fiscais
- Processamento e validação de documentos
- Integração com banco de dados
- Lógica de negócio principal
- Endpoints para upload, consulta e relatórios

**Tecnologias:** Python/FastAPI ou Node.js/Express, PostgreSQL/MongoDB

**Arquivos Principais:**
- `api/routes/` - Rotas da API
- `services/` - Lógica de negócio
- `models/` - Modelos de dados
- `database/` - Migrações e queries

---

### 2️⃣ **RAG - Retrieval Augmented Generation** (Especialista em IA/ML)
**Pasta:** `/rag`

**Responsabilidades:**
- Indexação de notas fiscais em banco vetorial
- Sistema de busca semântica
- Embeddings de documentos
- Recuperação de contexto para agentes

**Tecnologias:** LangChain, ChromaDB/Pinecone, OpenAI/Anthropic Embeddings

**Arquivos Principais:**
- `embeddings/` - Geração de embeddings
- `vector_store/` - Configuração do banco vetorial
- `retrieval/` - Motor de busca semântica
- `indexing/` - Pipeline de indexação

---

### 3️⃣ **AGENTS - Agentes Inteligentes** (Desenvolvedor de Agentes IA)
**Pasta:** `/agents`

**Responsabilidades:**
- Agente de auditoria automática
- Agente de validação de conformidade
- Agente gerador de notas fiscais sintéticas
- Orquestração entre agentes
- Detecção de anomalias

**Tecnologias:** LangChain Agents, AutoGen, Claude/GPT-4

**Arquivos Principais:**
- `audit_agent/` - Agente principal de auditoria
- `validation_agent/` - Validação de regras fiscais
- `synthetic_agent/` - Geração de NFs sintéticas
- `orchestrator/` - Coordenação entre agentes

---

### 4️⃣ **MCP - Model Context Protocol** (Especialista em MCP)
**Pasta:** `/mcp`

**Responsabilidades:**
- Servidores MCP para contexto de notas fiscais
- Recursos compartilhados entre agentes
- Tools personalizadas para auditoria
- Integração com Claude Desktop/API

**Tecnologias:** MCP SDK, Python/TypeScript

**Arquivos Principais:**
- `servers/` - Servidores MCP
- `resources/` - Recursos compartilhados
- `tools/` - Ferramentas customizadas

---

### 5️⃣ **FRONTEND** (Desenvolvedor Frontend/Data App)
**Pasta:** `/frontend`

**Responsabilidades:**
- Interface de usuário web com Streamlit
- Dashboard interativo de auditoria
- Upload e visualização de notas fiscais
- Geração de relatórios visuais
- Gerenciamento de NFs sintéticas
- Gráficos e tabelas de análise

**Tecnologias:** Streamlit, Plotly, Pandas, Python

**Arquivos Principais:**
- `app.py` - Aplicação principal
- `pages/` - Páginas multi-page (Dashboard, Upload, Auditoria, etc)
- `components/` - Componentes reutilizáveis (sidebar, charts, tables)
- `services/api_client.py` - Cliente para comunicação com Backend
- `utils/` - Formatadores e helpers

---

### 6️⃣ **TESTS - Testes** (QA Engineer)
**Pasta:** `/tests`

**Responsabilidades:**
- Testes unitários de todos os módulos
- Testes de integração
- Testes end-to-end
- Testes de carga e performance
- Cobertura de código

**Tecnologias:** Pytest, Jest, Cypress, Locust

**Arquivos Principais:**
- `unit/` - Testes unitários
- `integration/` - Testes de integração
- `e2e/` - Testes end-to-end
- `load/` - Testes de carga

---

### 7️⃣ **SECURITY - Segurança** (Security Engineer)
**Pasta:** `/security`

**Responsabilidades:**
- Autenticação e autorização
- Criptografia de dados sensíveis
- Logs de auditoria
- Compliance e conformidade (LGPD)
- Controle de acesso baseado em roles

**Tecnologias:** JWT, OAuth2, bcrypt, HTTPS/TLS

**Arquivos Principais:**
- `auth/` - Sistema de autenticação
- `encryption/` - Criptografia de dados
- `audit_logs/` - Logs de atividades
- `compliance/` - Regras de conformidade

---

## 🐳 Docker & Infraestrutura

### **DOCKER** (DevOps Engineer)
**Pasta:** `/docker`

**Responsabilidades:**
- Dockerfiles para cada módulo
- Docker Compose para orquestração
- Configuração de ambiente dev/prod
- CI/CD pipelines
- Monitoramento e logs

**Arquivos:**
- `docker-compose.yml` - Produção
- `docker-compose.dev.yml` - Desenvolvimento
- `backend.Dockerfile`, `frontend.Dockerfile`, etc.

**Configuração Streamlit:**
```yaml
# docker-compose.yml (exemplo frontend)
frontend:
  build: ./docker/frontend.Dockerfile
  ports:
    - "8501:8501"
  environment:
    - BACKEND_URL=http://backend:8000
  command: streamlit run app.py --server.port=8501 --server.address=0.0.0.0
```

---

## 🖥️ Estrutura do Frontend Streamlit

### Organização de Páginas (Multi-Page App)
```
frontend/
├── app.py                      # Página inicial/Home
├── pages/
│   ├── 01_📊_Dashboard.py      # Dashboard principal
│   ├── 02_📤_Upload_NF.py      # Upload de notas fiscais
│   ├── 03_🔍_Auditoria.py      # Visualização de auditorias
│   ├── 04_🧪_NF_Sinteticas.py  # Geração de NFs sintéticas
│   └── 05_📈_Relatorios.py     # Relatórios e análises
├── components/
│   ├── sidebar.py              # Sidebar customizada
│   ├── charts.py               # Gráficos reutilizáveis
│   └── tables.py               # Tabelas formatadas
├── services/
│   └── api_client.py           # Cliente HTTP para Backend
├── utils/
│   └── formatters.py           # Formatação de dados
└── requirements.txt
```

### Funcionalidades por Página

**Dashboard** 📊
- Métricas resumidas (total de NFs, % aprovadas, anomalias detectadas)
- Gráficos de tendências
- Lista de últimas auditorias

**Upload de NF** 📤
- Upload de XML/PDF
- Visualização prévia
- Status de processamento
- Histórico de uploads

**Auditoria** 🔍
- Resultados detalhados
- Comparação com base de conhecimento (RAG)
- Sugestões dos agentes IA
- Exportação de relatórios

**NFs Sintéticas** 🧪
- Configuração de parâmetros
- Geração em lote
- Preview de NFs geradas
- Download de datasets

**Relatórios** 📈
- Análises consolidadas
- Gráficos interativos (Plotly)
- Filtros avançados
- Exportação (PDF/Excel)

---

## 📦 Módulos Compartilhados

### **SHARED** (Todos os membros)
**Pasta:** `/shared`

**Responsabilidades:**
- Schemas compartilhados
- Utilitários comuns
- Constantes e configurações
- Validadores

---

## 🚀 Fluxo de Trabalho Sugerido

1. **Reunião Inicial:** Definir padrões de código e comunicação entre módulos
2. **Desenvolvimento Paralelo:** Cada membro trabalha em seu módulo
3. **Integração Contínua:** Testes automatizados a cada push
4. **Code Review:** Revisão cruzada entre membros
5. **Deploy:** Pipeline automatizado com Docker

---

## 📊 Funcionalidades Principais

### Auditoria de Notas Fiscais
- Upload de NFs em XML/PDF
- Validação automática de conformidade
- Detecção de anomalias e fraudes
- Relatórios detalhados

### Notas Fiscais Sintéticas
- Geração automática de NFs para testes
- Dados realistas mas fictícios
- Casos de uso variados (válidas, inválidas, suspeitas)

### Segurança
- Autenticação multi-fator
- Criptografia de dados sensíveis
- Logs completos de auditoria
- Compliance com LGPD

---

## 🔗 Comunicação Entre Módulos

```
Frontend → Backend API → [RAG, Agents, MCP]
                ↓
           Database
                ↓
         Security Layer
```

**Observação:** Todos os módulos devem seguir os schemas definidos em `/shared/schemas/`

---

## 🎨 Dicas para Desenvolvimento Streamlit

### State Management
```python
# Usar session_state para manter dados entre interações
if 'uploaded_nfs' not in st.session_state:
    st.session_state.uploaded_nfs = []
```

### Cache para Performance
```python
# Cachear chamadas à API e processamento de dados
@st.cache_data(ttl=600)  # Cache por 10 minutos
def get_audit_results(nf_id):
    return api_client.get_audit(nf_id)
```

### Componentes Customizados
- Use `st.columns()` para layouts responsivos
- `st.expander()` para seções colapsáveis
- `st.tabs()` para organização de conteúdo
- `plotly` para gráficos interativos

### Integração com Backend
```python
# services/api_client.py
import requests

class BackendClient:
    def __init__(self, base_url):
        self.base_url = base_url
    
    def upload_nf(self, file):
        return requests.post(f"{self.base_url}/api/nf/upload", files={"file": file})
```