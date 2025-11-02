# Módulo de Agentes - Sistema de Auditoria de NF

Este módulo é um microsserviço FastAPI independente que abriga os Agentes de IA (LangChain) responsáveis pela auditoria de Notas Fiscais.

Ele é projetado para ser "rodável" de forma isolada, utilizando "contornos" (stubs/mocks) para simular dependências externas (RAG, MCP) que ainda estão em desenvolvimento.

## Arquitetura

1.  **Servidor FastAPI (`main.py`):** O ponto de entrada da aplicação. Expõe os endpoints da API.
2.  **Rotas da API (`api/routes.py`):** Define os endpoints (ex: `/api/v1/audit`) e direciona as requisições para o orquestrador.
3.  **Orquestrador (`orchestrator/coordinator.py`):** O "cérebro" do módulo. Recebe a requisição da API e gerencia o fluxo de trabalho entre os diferentes agentes.
4.  **Motor de Regras (`audit_agent/rules_engine.py`):** Contém regras de negócio determinísticas (não-LLM), como a "Validação Tríplice", que rodam *antes* de invocar o agente de IA para economizar tokens.
5.  **Agente de Auditoria (`audit_agent/agent.py`):** O agente principal baseado em LLM (LangChain) que usa ferramentas para analisar a conformidade fiscal da nota.
6.  **Fábrica de LLMs (`utils/llm_factory.py`):** Cria a instância do LLM com lógica de *fallback* (Claude -> GPT-4) e gerenciamento de chaves de API.
7.  **Ferramentas de Contorno (`tools/`):** Implementações temporárias (stubs/mocks) das ferramentas externas. Elas garantem que o agente possa ser testado de ponta a ponta sem depender dos módulos RAG e MCP.

## Como Executar

Siga estes passos para rodar o servidor de agentes localmente.

### 1. Pré-requisitos

* Python 3.10+
* Chaves de API para Anthropic (Claude) e OpenAI (GPT).

### 2. Configurar o Ambiente

Navegue até esta pasta (`audit-nf-system/agents/`) no seu terminal.

```bash
# Estando na pasta .../audit-nf-system/agents/

# 1. Crie um ambiente virtual (recomendado)
python -m venv venv
source venv/bin/activate  # (ou venv\Scripts\activate no Windows)

# 2. Instale as dependências
pip install -r requirements.txt
```

### 3. Configurar Chaves de API
Crie um arquivo chamado .env dentro da pasta agents/. O config.py irá lê-lo automaticamente.

Arquivo: audit-nf-system/agents/.env
```Ini, TOML
# Chaves de API necessárias para o llm_factory.py
ANTHROPIC_API_KEY=sk-ant-sua-chave-claude-aqui
OPENAI_API_KEY=sk-sua-chave-openai-aqui
```

### 4. Rodar o Servidor
Execute o servidor FastAPI com Uvicorn (a porta 8000 está definida no main.py).

```Bash
uvicorn agents.main:app --reload --port 8000
```
Se tudo estiver correto, você verá: `INFO: Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)`

##  Como Testar
Você pode testar a API usando `curl` ou Postman.

### 1. Testar a Saúde (Health Check)
Abra outro terminal e rode:

```Bash
curl http://localhost:8000/api/v1/health
```
Resposta esperada:
```JSON
{"status":"ok","message":"Serviço de Agentes operando."}
```

### 2. Testar a Auditoria (Endpoint /audit)
1. Crie um arquivo test_invoice.json em qualquer lugar do seu computador. Use este exemplo, que falha na "Validação Tríplice" (ideal para testes):

    ```JSON
    {
        "Numero": "91101",
        "ChaveAcesso": "35210512345678000190550010000911011123456789",
        "Emitente_CNPJCPF": "01.234.567/0001-89",
        "Destinatario_CNPJCPF": "98.765.432/0001-01",
        "ValorTotalNota": "1500.00",
        "ValorDesconto": "100.00",
        "ValorICMS": "180.00",
        "ValorIPI": "50.00",
        "ValorPIS": "9.90",
        "ValorCOFINS": "45.60",
        "items": [
            {
                "Numero": "91101",
                "CodigoProduto": "PROD-A",
                "ValorTotalItem": "1600.00"
            }
        ]
    }
    ```

2. Envie a requisição curl (substitua pelo caminho correto do seu arquivo JSON):

    ```Bash
    curl -X POST http://localhost:8000/api/v1/audit \
    -H "Content-Type: application/json" \
    -d @/caminho/completo/para/seu/test_invoice.json
    ```

3. Resposta Esperada (Falha na Regra):
Você verá o rules_engine.py funcionar, e o agente LLM não será invocado:

    ```JSON
    {
        "aprovada": false,
        "irregularidades": [
            "Falha na Validação Tríplice: O valor total da nota (1500.0) é incompatível com o valor calculado (1785.5). Diferença de 285.5."
        ],
        "confianca": 1.0,
        "justificativa": "Falha na validação financeira determinística (Validação Tríplice). O agente LLM não foi invocado."
    }
    ```

## ⚠️ Status de Desenvolvimento (Contornos)
Este módulo está funcional para desenvolvimento local.

Os arquivos dentro de agents/tools/ (rag_tool.py, mcp_tools.py, calculator_tool.py) são contornos temporários (stubs/mocks).

- Realizado para permitir o desenvolvimento e teste independentes do AuditAgent sem depender dos microsserviços RAG e MCP, que estão em desenvolvimento paralelo.

- Quando os módulos reais de RAG e MCP forem integrados à branch develop, estes contornos serão removidos e os imports no agent.py serão atualizados para chamar as ferramentas reais.

# 🤖 Sistema de Auditoria de NF-e com Agentes IA

Sistema automatizado de validação e auditoria de Notas Fiscais Eletrônicas usando agentes baseados em LangChain e Claude Sonnet.

## 📋 Índice

- [Visão Geral](#visão-geral)
- [Arquitetura](#arquitetura)
- [Instalação](#instalação)
- [Configuração](#configuração)
- [Uso Rápido](#uso-rápido)
- [API Endpoints](#api-endpoints)
- [Testes](#testes)
- [Estrutura do Projeto](#estrutura-do-projeto)

---

## 🎯 Visão Geral

Este sistema utiliza múltiplos agentes especializados para:

1. **ValidationAgent**: Valida estrutura, formato e conformidade técnica
2. **AuditAgent**: Audita conformidade fiscal e identifica irregularidades
3. **SyntheticAgent**: Gera notas fiscais sintéticas para testes

### Funcionalidades

✅ Validação de CNPJ/CPF  
✅ Verificação de CFOPs  
✅ Cálculo e validação de impostos (ICMS, IPI, PIS, COFINS)  
✅ Detecção de inconsistências e fraudes  
✅ Relatórios detalhados de auditoria  
✅ API REST com FastAPI  
✅ Geração de notas sintéticas para testes  

---

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────┐
│                    FastAPI (main.py)                    │
│                 Rotas: /audit, /validate                │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              AgentCoordinator (orchestrator)            │
│           Orquestra fluxo entre agentes                 │
└──────┬──────────────────────────────────────┬───────────┘
       │                                      │
       ▼                                      ▼
┌──────────────────┐              ┌─────────────────────┐
│ ValidationAgent  │              │   AuditAgent        │
│ - Estrutura      │              │ - ICMS, IPI         │
│ - Formatos       │              │ - CFOPs             │
│ - Schema XML     │              │ - Consistência      │
└────────┬─────────┘              └──────┬──────────────┘
         │                               │
         │                               └─► TaxCalculator
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│                   Resposta Consolidada                  │
│     aprovada: bool, irregularidades: [], confianca: 0.95│
└─────────────────────────────────────────────────────────┘
```

---

## 📦 Instalação

### 1. Pré-requisitos

- Python 3.9+
- pip

### 2. Clonar e Instalar Dependências

```bash
# Navegar até a pasta do projeto
cd agents

# Criar ambiente virtual (recomendado)
python -m venv venv

# Ativar ambiente virtual
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

---

## ⚙️ Configuração

### 1. Configurar Variáveis de Ambiente

```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar .env e adicionar sua API key
nano .env
```

**Obrigatório:**
```env
ANTHROPIC_API_KEY=sk-ant-api03-sua-chave-aqui
```

**Opcional:**
```env
OPENAI_API_KEY=sk-sua-chave-openai  # Para fallback
MOCK_EXTERNAL_SERVICES=True         # Usar mocks para dev
```

### 2. Validar Configuração

```python
from config import settings, validate_settings

validate_settings()  # Levanta erro se configuração inválida
```

## 🚀 Uso Rápido

### Iniciar Servidor

```bash
# Método 1: Uvicorn direto
uvicorn main:app --reload --port 8002

# Método 2: Python direto
python main.py
```

Servidor rodando em: **http://localhost:8002**

### Acessar Documentação Interativa

- **Swagger UI**: http://localhost:8002/docs
- **ReDoc**: http://localhost:8002/redoc

---

## 📡 API Endpoints

### 1. Auditar Nota Fiscal

```bash
curl -X POST http://localhost:8002/api/v1/audit \
  -H "Content-Type: application/json" \
  -d @test_invoice.json
```

**Request Body:**
```json
{
  "invoice": {
    "numero": "000123",
    "serie": "1",
    "data_emissao": "2025-10-27",
    "cnpj_emitente": "12345678000190",
    "cnpj_destinatario": "98765432000199",
    "cfop": "5102",
    "valor_produtos": 1000.00,
    "valor_total": 1180.00,
    "base_calculo_icms": 1000.00,
    "aliquota_icms": 18.0,
    "valor_icms": 180.00
  },
  "context": {}
}
```

**Response:**
```json
{
  "aprovada": true,
  "irregularidades": [],
  "confianca": 0.95,
  "justificativa": "Nota fiscal aprovada...",
  "detalhes": {
    "validacao": {"aprovada": true, "erros": 0},
    "auditoria": {"aprovada": true, "irregularidades": 0}
  }
}
```

### 2. Validar Estrutura

```bash
curl -X POST http://localhost:8002/api/v1/validate \
  -H "Content-Type: application/json" \
  -d '{"invoice": {...}}'
```

### 3. Gerar NF Sintética

```bash
curl -X POST http://localhost:8002/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{
    "tipo": "valida",
    "valor_max": 5000.0,
    "estado": "SP"
  }'
```

**Tipos disponíveis:**
- `valida`: Nota completamente válida
- `invalida`: Nota com erros propositais
- `suspeita`: Nota válida mas com padrões suspeitos

### 4. Health Check

```bash
curl http://localhost:8002/health
curl http://localhost:8002/api/v1/agents/health
```

---

## 🧪 Testes

### Executar Todos os Testes

```bash
# Com pytest
pytest test_agents.py -v

# Testes específicos
pytest test_agents.py::test_validation_agent -v
pytest test_agents.py::test_audit_agent -v

# Com coverage
pytest --cov=. test_agents.py
```

### Executar Diretamente

```bash
python test_agents.py
```

### Testes de Integração

```bash
# Requer API rodando
pytest test_agents.py -m integration
```

---

## 📁 Estrutura do Projeto

```
agents/
├── main.py                      # FastAPI application
├── config.py                    # Configurações
├── requirements.txt             # Dependências
├── .env.example                 # Exemplo de configuração
├── test_agents.py               # Testes
│
├── audit_agent/                 # Agente de Auditoria
│   ├── __init__.py
│   ├── agent.py                 # Classe AuditAgent
│   ├── prompts.py               # Prompts do agente
│   └── rules_engine.py          # Motor de regras fiscais
│
├── validation_agent/            # Agente de Validação
│   ├── __init__.py
│   └── agent.py                 # Classe ValidationAgent
│
├── synthetic_agent/             # Agente Sintético
│   ├── __init__.py
│   └── nf_generator.py          # Gerador de NFs
│
├── orchestrator/                # Orquestrador
│   ├── __init__.py
│   └── coordinator.py           # AgentCoordinator
│
├── tools/                       # Tools do LangChain
│   ├── __init__.py
│   └── calculator_tool.py       # Tool de cálculo de impostos
│
└── api/                         # Rotas da API
    ├── __init__.py
    └── routes.py                # Endpoints FastAPI
```

---

## 🔧 Desenvolvimento

### Adicionar Novo Agente

1. Criar pasta `novo_agente/`
2. Criar `agent.py` com classe do agente
3. Registrar no `coordinator.py`
4. Adicionar rotas em `api/routes.py`

### Adicionar Nova Tool

1. Criar em `tools/nova_tool.py`
2. Herdar de `BaseTool` do LangChain
3. Implementar `_run()` e `_arun()`
4. Adicionar ao agente em `agent.py`

### Customizar Prompts

Editar `audit_agent/prompts.py`:
```python
SYSTEM_PROMPT = """
Você é um auditor fiscal...
[adicionar suas instruções]
"""
```



## 🎯 Exemplos de Uso

### Exemplo 1: Auditoria Simples

```python
import httpx
import asyncio

async def auditar_nota():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8002/api/v1/audit",
            json={
                "invoice": {
                    "numero": "123",
                    "cnpj_emitente": "12345678000190",
                    # ... outros campos
                }
            }
        )
        resultado = response.json()
        print(f"Aprovada: {resultado['aprovada']}")
        print(f"Confiança: {resultado['confianca']}")

asyncio.run(auditar_nota())
```

### Exemplo 2: Gerar e Auditar

```python
# Gerar nota válida
response = client.post("/api/v1/generate", json={"tipo": "valida"})
invoice = response.json()["invoice"]

# Auditar nota gerada
response = client.post("/api/v1/audit", json={"invoice": invoice})
print(response.json())
```

### Exemplo 3: Usar Agente Diretamente

```python
from audit_agent.agent import AuditAgent

agent = AuditAgent()

invoice_data = {
    "numero": "123",
    "cfop": "5102",
    # ... outros campos
}

result = await agent.audit_invoice(invoice_data)
print(f"Aprovada: {result['aprovada']}")
print(f"Irregularidades: {result['irregularidades']}")
```

---

## 📊 Logs

Logs são salvos em:
- **Console**: output em tempo real
- **Arquivo**: `agents.log`

Configurar nível de log em `.env`:
```env
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
```

---

## 🐛 Troubleshooting

### Erro: "ANTHROPIC_API_KEY não configurada"

**Solução:** Configure a chave no arquivo `.env`

### Erro: "Module not found"

**Solução:**
```bash
pip install -r requirements.txt
```

### Validação passa mas Auditoria reprova

**Normal:** ValidationAgent valida apenas estrutura, AuditAgent valida regras fiscais

---

## 📚 Documentação Adicional

- **LangChain**: https://python.langchain.com/
- **FastAPI**: https://fastapi.tiangolo.com/
- **Claude API**: https://docs.anthropic.com/

---

## 🎉 Começando

**Checklist para iniciar:**

- [ ] ✅ Instalar dependências: `pip install -r requirements.txt`
- [ ] ✅ Configurar `.env` com `ANTHROPIC_API_KEY`
- [ ] ✅ Iniciar servidor: `uvicorn main:app --reload --port 8002`
- [ ] ✅ Testar health check: `curl http://localhost:8002/health`
- [ ] ✅ Gerar NF de teste: `curl -X POST http://localhost:8002/api/v1/generate ...`
- [ ] ✅ Auditar NF: `curl -X POST http://localhost:8002/api/v1/audit ...`
- [ ] ✅ Explorar docs: http://localhost:8002/docs

**Pronto para produção! 🚀**

---

## 📝 Licença

Sistema desenvolvido para auditoria de NF-e conforme legislação brasileira.

**Versão:** 1.0.0  
**Data:** Outubro 2025