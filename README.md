# 📄 Sistema de Auditoria de Notas Fiscais

Sistema modular para auditoria automatizada de notas fiscais usando IA, RAG, Agentes Inteligentes e MCP.

---

## 👥 Guia para Colaboradores

Bem-vindo ao projeto! Este README contém todas as informações necessárias 
para você trabalhar de forma autônoma no respectivo branch que é o seu nome.

##  🎯Pastas 
             ✅ audit-nf-system  : estrutura do projeto, pastas e arquivos
             ✅ planejamento     : documentos de apoio e orientações.
             ✅ prompt           : prompts para cada parte do projeto.

---

## 🎯 Filosofia de Trabalho

### Desenvolvimento Independente
- ✅ Cada colaborador trabalha em **seu próprio branch**
- ✅ Cada módulo pode funcionar **independentemente** (usando mocks quando necessário)
- ✅ Cada módulo tem seu próprio **Dockerfile**
- ✅ Integração acontece depois através de **Pull Requests**

## 🚀 Começando

### 1. Clone o Repositório

```bash
# Clone o repositório
git clone https://github.com/Curso-Agentes-I2A2/entrega-final-curso-agentes-i2a2.git
cd audit-nf-system
```

### 2. Acesse Seu Branch

```bash
# Listar todos os branches
git branch -a

# Mudar para seu branch
git checkout branch/[seu-nome]

# Exemplo: se você jose
git checkout branch/jose
```

### 3. Configure seu Ambiente

```bash
# Criar ambiente virtual Python
python -m venv venv

# Ativar ambiente virtual
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Instalar dependências do seu módulo
cd [MODULO]
pip install -r requirements.txt
```

---

## 📋 Comandos Git Essenciais

### Workflow Diário

```bash
# 1. Sempre começar atualizando seu branch
git pull origin branch/[seu-nome]

# 2. Verificar status dos arquivos
git status

# 3. Adicionar arquivos modificados
git add .
# Ou adicionar arquivos específicos:
git add arquivo1.py arquivo2.py

# 4. Fazer commit com mensagem descritiva
git commit -m "feat: adiciona processamento de XML de notas fiscais"

# 5. Enviar para o repositório remoto
git push origin branch/[seu-nome]
```

### Convenções de Mensagens de Commit

Use o padrão [Conventional Commits](https://www.conventionalcommits.org/):

```bash
feat: nova funcionalidade
fix: correção de bug
docs: documentação
style: formatação de código
refactor: refatoração de código
test: adição de testes
chore: tarefas de manutenção
```

**Exemplos:**
```bash
git commit -m "feat: implementa agente de validação de NF"
git commit -m "fix: corrige cálculo de impostos"
git commit -m "docs: atualiza README com exemplos de uso"
git commit -m "test: adiciona testes unitários para RAG"
```

### Pull Request e Merge

Quando seu módulo estiver pronto para integração:

```bash
# 1. Certifique-se que está no seu branch
git checkout branch/[seu-nome]

# 2. Atualize com as últimas mudanças
git pull origin branch/[seu-nome]

# 3. Faça push das suas mudanças
git push origin branch/[seu-nome]

# 4. Acesse o GitHub e crie um Pull Request
# - Vá até: https://github.com/[ORGANIZAÇÃO]/audit-nf-system
# - Clique em "Pull Requests" > "New Pull Request"
# - Base: main
# - Compare: branch/[seu-nome]
# - Descreva suas mudanças e crie o PR

# 5. Aguarde revisão da equipe antes do merge
```

### Resolvendo Conflitos

Se houver conflitos ao fazer merge:

```bash
# 1. Atualizar com a main
git checkout branch/[seu-nomeO]
git pull origin main

# 2. Resolver conflitos manualmente nos arquivos
# (Seu editor mostrará as linhas conflitantes)

# 3. Adicionar arquivos resolvidos
git add .

# 4. Finalizar o merge
git commit -m "merge: resolve conflitos com main"

# 5. Fazer push
git push origin branch/[seu-nome]
```

### Comandos Úteis

```bash
# Ver histórico de commits
git log --oneline --graph

# Ver diferenças antes de commitar
git diff

# Desfazer mudanças não commitadas
git checkout -- arquivo.py

# Voltar último commit (mantém mudanças)
git reset --soft HEAD~1

# Ver branches remotos
git branch -r

# Atualizar lista de branches remotos
git fetch
```

---

## 🏗️ Estrutura do Projeto

```
audit-nf-system/
├── backend/          # API REST e processamento
├── rag/              # Sistema de busca vetorial
├── agents/           # Agentes de IA
├── mcp/              # Model Context Protocol
├── frontend/         # Interface Streamlit
├── tests/            # Testes automatizados
├── security/         # Autenticação e segurança
├── docker/           # Containers
├── docs/             # Documentação
└── shared/           # Código compartilhado
```

---

## 🎓 Entendendo os Componentes Técnicos

### 🧠 RAG (Retrieval Augmented Generation)

#### O que é RAG?
Sistema que combina busca de documentos com geração de texto por LLM. Permite que a IA "consulte" uma base de conhecimento antes de responder.

#### Tipos de Organização de Dados

**1. Vetorial (Embeddings)**
- **Como funciona:** Converte textos em vetores numéricos de alta dimensão
- **Busca:** Por similaridade semântica (cosseno, euclidiana)
- **Melhor para:** Busca por significado, não por palavras exatas

**Bancos Vetoriais:**
- **ChromaDB** ✅ Recomendado para desenvolvimento
  - ✅ Open source, fácil de usar
  - ✅ Roda localmente
  - ❌ Menos escalável para produção
  
- **Pinecone** ✅ Recomendado para produção
  - ✅ Gerenciado, altamente escalável
  - ✅ Performance excelente
  - ❌ Pago, requer API key
  
- **Weaviate**
  - ✅ Open source, escalável
  - ✅ Suporta múltiplos tipos de busca
  - ❌ Mais complexo de configurar
  
- **Qdrant**
  - ✅ Rápido, open source
  - ✅ API simples
  - ❌ Menos maduro que concorrentes

**2. Grafo de Conhecimento**
- **Como funciona:** Representa entidades e relacionamentos
- **Busca:** Por conexões e caminhos entre entidades
- **Melhor para:** Relações complexas, raciocínio sobre conexões

**Bancos de Grafo:**
- **Neo4j**
  - ✅ Mais popular, maduro
  - ✅ Linguagem Cypher intuitiva
  - ❌ Licença comercial para produção
  
- **ArangoDB**
  - ✅ Multi-modelo (documento + grafo)
  - ✅ Open source completo
  - ❌ Menos adotado

**Nossa Recomendação para o Projeto:**
```
Desenvolvimento: ChromaDB (vetorial)
Produção: Pinecone ou ChromaDB + PostgreSQL (híbrido)
```

#### Base de Conhecimento - O que Indexar?

**Documentos Essenciais:**
1. **Legislação Fiscal**
   - Regulamentos de NF-e
   - Tabelas de impostos (ICMS, IPI, PIS, COFINS)
   - Instruções normativas da Receita Federal

2. **Documentação Técnica**
   - Schemas XML de NF-e
   - Códigos de erro e validação
   - Manual de integração SEFAZ

3. **Base de Decisões Anteriores**
   - Histórico de auditorias
   - Casos aprovados/rejeitados
   - Padrões de anomalias detectadas

4. **Conhecimento do Negócio**
   - Políticas internas da empresa
   - Procedimentos de auditoria
   - Regras específicas por setor

---

### 🔌 MCP (Model Context Protocol)

#### O que é MCP?
Protocolo que permite que LLMs acessem ferramentas, recursos e dados externos de forma padronizada. Criado pela Anthropic.

#### Como Implementar?

**Estrutura Básica de um Servidor MCP:**

```python
# mcp/servers/nf_context_server.py
from mcp.server import Server
from mcp.types import Resource, Tool

server = Server("nf-audit-server")

# 1. Recursos (dados que podem ser lidos)
@server.resource("invoices://{invoice_id}")
async def get_invoice(invoice_id: str) -> Resource:
    """Retorna dados de uma nota fiscal específica"""
    return Resource(
        uri=f"invoices://{invoice_id}",
        name=f"Nota Fiscal {invoice_id}",
        mimeType="application/json",
        text=await fetch_invoice_data(invoice_id)
    )

# 2. Tools (ações que podem ser executadas)
@server.tool("validate_invoice")
async def validate_invoice(invoice_xml: str) -> dict:
    """Valida schema e regras fiscais de uma NF"""
    return {
        "valid": True,
        "errors": [],
        "warnings": ["CFOP não usual para operação"]
    }
```

#### O que o Negócio Precisa do MCP?

**1. Ferramentas de Validação**
- ✅ Validação de XML contra schema XSD
- ✅ Verificação de CNPJ na Receita Federal
- ✅ Cálculo automático de impostos
- ✅ Validação de códigos fiscais (NCM, CFOP)

**2. Integração com Serviços Externos**

**APIs Públicas Úteis:**
- **ReceitaWS** - Consulta CNPJ
  - URL: `https://www.receitaws.com.br/v1/cnpj/`
  - Gratuita, sem autenticação
  
- **BrasilAPI** - Diversos dados brasileiros
  - URL: `https://brasilapi.com.br`
  - CNPJs, CEPs, Bancos, Feriados
  
- **ViaCEP** - Validação de endereços
  - URL: `https://viacep.com.br/ws/`
  
- **SEFAZ APIs** - Validação de NF-e (requer certificado)
  - Consulta situação de NF-e
  - Validação de chave de acesso

**APIs Comerciais (se necessário):**
- **Serpro** - Consultas Receita Federal
- **Serasa Experian** - Análise de crédito
- **InfoSimples** - Consultas empresariais

**3. Fontes de Dados Internas**
- ✅ Base histórica de notas fiscais
- ✅ Cadastro de fornecedores aprovados
- ✅ Políticas e limites da empresa
- ✅ Histórico de auditorias

**Exemplo de Implementação com API Externa:**

```python
# mcp/tools/external_validation.py
import httpx

@server.tool("verify_cnpj")
async def verify_cnpj(cnpj: str) -> dict:
    """Consulta CNPJ na ReceitaWS"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://www.receitaws.com.br/v1/cnpj/{cnpj}"
        )
        return response.json()

@server.tool("validate_nfe_key")
async def validate_nfe_key(chave_acesso: str) -> dict:
    """Valida chave de acesso de NF-e"""
    # Implementar consulta ao SEFAZ
    # Requer certificado digital
    pass
```

---

## 📝 Tarefas Iniciais (até Segunda/Terça)

### 🔧 Time Técnico (Backend, RAG, MCP, Agentes)

**Objetivo:** Propor desenho da arquitetura técnica

**Tarefas:**
1. **RAG**
   - [ ] Avaliar ChromaDB vs Pinecone
   - [ ] Propor estratégia de chunking de documentos
   - [ ] Definir modelo de embeddings (OpenAI, Cohere, etc)
   - [ ] Sugerir estrutura de indexação

2. **MCP**
   - [ ] Listar APIs externas necessárias
   - [ ] Propor ferramentas (tools) que os agentes precisarão
   - [ ] Definir recursos (resources) que serão expostos
   - [ ] Avaliar necessidade de serviços pagos

3. **Arquitetura Geral**
   - [ ] Propor fluxo de dados entre módulos
   - [ ] Definir formato de comunicação (REST, gRPC, etc)
   - [ ] Sugerir estratégia de mocks para desenvolvimento
   - [ ] Documentar decisões técnicas

**Entregável:** Documento técnico em `docs/ARCHITECTURE.md`

---

### 📊 Time Regras de Negócio (Agentes, Validação)

**Objetivo:** Definir base de conhecimento e regras de auditoria

**Tarefas:**
1. **Base de Conhecimento RAG**
   - [ ] Listar documentos fiscais necessários
   - [ ] Identificar fontes de legislação atualizada
   - [ ] Definir categorias de conhecimento
   - [ ] Sugerir estrutura de organização dos dados

2. **APIs e Serviços Externos**
   - [ ] Avaliar necessidade de consultas externas
   - [ ] Listar APIs gratuitas úteis
   - [ ] Identificar APIs pagas necessárias
   - [ ] Propor fallbacks se APIs falharem

3. **Regras de Validação**
   - [ ] Documentar regras fiscais principais
   - [ ] Definir critérios de aprovação/rejeição
   - [ ] Listar anomalias comuns a detectar
   - [ ] Propor fluxo de decisão dos agentes

**Entregável:** Documento de requisitos em `docs/BUSINESS_RULES.md`

---

## 🐳 Desenvolvimento com Docker

### Executar Seu Módulo

Cada módulo tem seu próprio Dockerfile e pode rodar independentemente:

```bash
# Backend
cd backend
docker build -t audit-backend -f ../docker/backend.Dockerfile .
docker run -p 8000:8000 audit-backend

# Frontend (Streamlit)
cd frontend
docker build -t audit-frontend -f ../docker/frontend.Dockerfile .
docker run -p 8501:8501 audit-frontend

# RAG
cd rag
docker build -t audit-rag -f ../docker/rag.Dockerfile .
docker run -p 8001:8001 audit-rag
```

### Usar Mocks

Quando outros módulos não estiverem prontos, use mocks:

```python
# backend/services/mock_rag_service.py
class MockRAGService:
    """Mock do serviço RAG para desenvolvimento"""
    
    async def search(self, query: str) -> list:
        return [
            {
                "content": "Regulamento fiscal mockado...",
                "score": 0.95,
                "source": "mock"
            }
        ]

# Use na configuração
if os.getenv("USE_MOCKS") == "true":
    rag_service = MockRAGService()
else:
    rag_service = RealRAGService()
```

---

## 🌐 Deploy

### Fase 1: Streamlit Cloud (Atual)

```bash
# Configurar repositório
# Streamlit Cloud lerá automaticamente:
# - requirements.txt
# - app.py (ou caminho definido)

# Deploy automático via GitHub:
# 1. Conectar repositório no Streamlit Cloud
# 2. Definir branch: branch/frontend
# 3. Definir arquivo: frontend/app.py
# 4. Configurar secrets (API keys)
```

### Fase 2: Google Cloud Platform (Futuro)

Detalhes serão definidos conforme evolução do projeto.

---

## 📚 Recursos de Referência

### Repositórios Base
- **llm-examples** (nosso main) - Estrutura e padrões
- [Adicionar links dos repositórios de referência]

### Documentação Oficial
- **RAG:** https://python.langchain.com/docs/use_cases/question_answering/
- **MCP:** https://modelcontextprotocol.io/
- **Streamlit:** https://docs.streamlit.io/
- **Anthropic Claude:** https://docs.anthropic.com/

### Tutoriais Úteis
- ChromaDB: https://docs.trychroma.com/
- LangChain Agents: https://python.langchain.com/docs/modules/agents/
- Git Workflow: https://www.atlassian.com/git/tutorials

---

## 🤝 Comunicação

### Canais
- **WhatsApp:** Discussões rápidas e alinhamentos
- **GitHub Issues:** Bugs e features
- **Pull Requests:** Revisão de código
- **Reuniões:** [Definir frequência e horário]

### Solicitar Ajuda

**Git/GitHub:**
- Não hesite em pedir ajuda com Git!
- Comandos básicos estão documentados acima
- Erros comuns: sempre pode reverter com `git reset`

**Dúvidas Técnicas:**
- Abra uma Issue no GitHub
- Marque o responsável técnico
- Descreva o problema e o que já tentou

---

## 📊 Status do Projeto

### Cronograma

```
✅ 1: Setup inicial e estrutura
🔄 2: Proposta de arquitetura (VOCÊ ESTÁ AQUI)
⏳ 3: Implementação dos módulos
⏳ 4: Integração e testes
⏳ 5: Deploy e refinamentos
```

### Checklist de Setup

- [ ] Recebi acesso ao repositório GitHub
- [ ] Consegui fazer clone do repositório
- [ ] Estou no meu branch correto
- [ ] Configurei ambiente Python
- [ ] Entendi meu módulo e responsabilidades
- [ ] Li documentação sobre RAG/MCP
- [ ] Fiz meu primeiro commit
- [ ] Entendo o processo de Pull Request

---

## 🎯 Próximos Passos

1. ✅ **Aceitar convite do GitHub**
2. ✅ **Clonar repositório e acessar seu branch**
3. ✅ **Estudar RAG e MCP** (conforme seu time)
4. ✅ **Propor arquitetura/regras** (até terça)
5. ⏳ **Começar implementação** (após aprovação)

---

## 💡 Dicas Importantes

### Para Todos
- 🔄 Faça commits pequenos e frequentes
- 📝 Use mensagens de commit descritivas
- 🧪 Teste seu código antes de fazer push
- 📖 Documente seu código (docstrings)
- 🤝 Revise PRs dos colegas quando possível

### Para Iniciantes em Git
- 💾 Sempre faça `git pull` antes de começar
- 🚫 Nunca trabalhe direto na `main`
- 🔍 Use `git status` frequentemente
- 💬 Peça ajuda sem receio!


**Última atualização:** 18/10/2025  
**Versão:** 1.0

Boa sorte e bom código! 🚀
