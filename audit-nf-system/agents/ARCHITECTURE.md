# 🏗️ ARQUITETURA DO SISTEMA

Documentação técnica da arquitetura do sistema de auditoria de NF-e.

---

## 📐 Visão Geral

O sistema segue uma arquitetura de **Multi-Agent System** com orquestração centralizada:

```
┌────────────────────────────────────────────────────────────┐
│                      FastAPI Layer                          │
│  - REST API endpoints                                       │
│  - Request/Response handling                                │
│  - WebSocket support                                        │
└─────────────────────┬──────────────────────────────────────┘
                      │
                      ▼
┌────────────────────────────────────────────────────────────┐
│                 Orchestration Layer                         │
│              AgentCoordinator                               │
│  - Manages agent workflow                                   │
│  - Consolidates results                                     │
│  - Makes final decisions                                    │
└──────┬──────────────────────────────────────┬──────────────┘
       │                                      │
       ▼                                      ▼
┌──────────────────┐              ┌─────────────────────────┐
│ ValidationAgent  │              │    AuditAgent           │
│                  │              │                         │
│ - Schema check   │              │ - Fiscal rules          │
│ - Format val.    │              │ - Tax calculations      │
│ - Field presence │              │ - CFOP validation       │
└────────┬─────────┘              └──────┬──────────────────┘
         │                               │
         │                               ├──► RAGTool
         │                               ├──► TaxCalculator
         │                               └──► RulesEngine
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│                     External Services                        │
│  - RAG Service (Knowledge Base)                             │
│  - MCP (if available)                                       │
│  - SEFAZ APIs (mock in dev)                                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 🧩 Componentes Principais

### 1. FastAPI Application (`main.py`)

**Responsabilidade:** 
- Ponto de entrada da aplicação
- Gerenciamento do ciclo de vida (startup/shutdown)
- Middleware (CORS, logging)
- Exception handling global

**Principais Rotas:**
- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /docs` - Swagger UI
- `WS /ws/stream` - WebSocket para streaming

### 2. Configuration (`config.py`)

**Responsabilidade:**
- Gerenciar todas as configurações via variáveis de ambiente
- Validar configurações no startup
- Fornecer constantes para todo o sistema

**Configurações:**
- API Keys (Anthropic, OpenAI)
- URLs de serviços externos
- Parâmetros dos modelos (temperature, max_tokens)
- Configurações dos agentes
- Timeouts e retry logic

### 3. Agent Coordinator (`orchestrator/coordinator.py`)

**Responsabilidade:**
- Orquestrar fluxo de trabalho entre agentes
- Tomar decisão final baseada em múltiplas validações
- Consolidar resultados

**Fluxo de Processamento:**
```python
1. Recebe invoice_data
2. Chama ValidationAgent
   └─► Se inválido → Retorna REPROVADA
3. Chama AuditAgent
   └─► Se reprovado → Retorna REPROVADA
4. Verifica threshold de confiança
5. Retorna decisão final consolidada
```

---

## 🤖 Agentes

### ValidationAgent (`validation_agent/agent.py`)

**Papel:** Validador estrutural e técnico

**Validações Realizadas:**
- ✅ Campos obrigatórios presentes
- ✅ Formato de CNPJ/CPF (14/11 dígitos)
- ✅ Formato de data (YYYY-MM-DD)
- ✅ Formato de CFOP (4 dígitos)
- ✅ Valores numéricos válidos
- ✅ Chave de acesso (44 dígitos + DV)
- ✅ Schema XML (se fornecido)
- ✅ Assinatura digital (mock)

**Tecnologia:**
- LangChain + Claude (temperature=0.0 para determinismo)
- Validações algorítmicas (regex, cálculos)

**Output:**
```json
{
  "valid": true,
  "errors": [],
  "warnings": [],
  "details": {...}
}
```

### AuditAgent (`audit_agent/agent.py`)

**Papel:** Auditor fiscal especializado

**Validações Realizadas:**
- ✅ CNPJ/CPF válidos (dígitos verificadores)
- ✅ CFOP existe e é compatível com operação
- ✅ Cálculo de ICMS correto
- ✅ Cálculo de IPI correto
- ✅ Cálculo de PIS/COFINS correto
- ✅ Consistência de valores totais
- ✅ Data de emissão válida
- ✅ Detecção de duplicidade
- ✅ Análise de risco/fraude

**Tecnologia:**
- LangChain Agent Executor
- Claude Sonnet (temperature=0.1)
- RulesEngine (validações rápidas)
- RAGTool (consultas à legislação)
- TaxCalculatorTool (cálculos complexos)

**Process Flow:**
```
1. Validações rápidas (RulesEngine)
   └─► Se violação crítica → Rejeição imediata
   
2. Análise com LLM
   ├─► Consulta RAG se necessário
   ├─► Calcula impostos
   └─► Raciocínio sobre irregularidades
   
3. Consolidação
   └─► Decisão + Confiança + Justificativa
```

**Output:**
```json
{
  "aprovada": true/false,
  "irregularidades": [],
  "confianca": 0.0-1.0,
  "justificativa": "...",
  "detalhes": {...}
}
```

### SyntheticAgent (`synthetic_agent/nf_generator.py`)

**Papel:** Gerador de notas fiscais sintéticas

**Funcionalidades:**
- Gerar CNPJ válido com dígitos verificadores
- Gerar chave de acesso válida (44 dígitos + DV)
- Criar notas válidas para testes
- Criar notas inválidas com erros específicos
- Criar notas suspeitas (padrões anormais)

**Tipos de Notas:**
- `valida`: Completamente conforme
- `invalida`: Com erros propositais (CFOP, ICMS, etc)
- `suspeita`: Válida mas com padrões suspeitos

---

## 🛠️ Tools (LangChain)

### RAGTool (`tools/rag_tool.py`)

**Função:** Consultar base de conhecimento sobre legislação fiscal

**Quando Usar:**
- Dúvidas sobre alíquotas específicas
- Confirmação de isenções/reduções
- Interpretação de regras complexas
- Embasamento legal

**Implementação:**
```python
class RAGTool(BaseTool):
    name = "consult_rag"
    
    async def _arun(self, query: str) -> str:
        # Consulta serviço RAG via HTTP
        # Retorna contexto relevante
```

**Mock Mode:**
- Retorna respostas simuladas quando `MOCK_EXTERNAL_SERVICES=True`
- Útil para desenvolvimento sem dependências externas

### TaxCalculatorTool (`tools/calculator_tool.py`)

**Função:** Calcular impostos brasileiros

**Impostos Calculados:**
- ICMS (18% padrão SP, 7% reduzida, 12% específica)
- IPI (varia por NCM, 10% típico)
- PIS (0.65% cumulativo, 1.65% não-cumulativo)
- COFINS (3% cumulativo, 7.6% não-cumulativo)

**Input:**
```json
{
  "base_value": 1000.00,
  "state": "SP",
  "tax_regime": "nao_cumulativo",
  "product_type": "normal"
}
```

**Output:**
```json
{
  "icms": {"aliquota": 18.0, "valor": 180.00},
  "ipi": {"aliquota": 10.0, "valor": 100.00},
  "pis": {"aliquota": 1.65, "valor": 16.50},
  "cofins": {"aliquota": 7.6, "valor": 76.00},
  "total_taxes": 372.50
}
```

---

## 🎯 Rules Engine (`audit_agent/rules_engine.py`)

**Função:** Validações determinísticas rápidas

**Vantagens:**
- Muito rápido (não requer LLM)
- Determinístico (sempre mesmo resultado)
- Sem custo de API
- Detecta erros óbvios antes da análise com LLM

**Regras Implementadas:**
- Validação de CNPJ (dígitos verificadores)
- Validação de CFOP (existência e compatibilidade)
- Cálculo de ICMS com tolerância
- Consistência de valores totais
- Validação de datas

**Uso:**
```python
engine = RulesEngine()

# Validar CNPJ
valid = engine.validate_cnpj("12345678000190")

# Verificar CFOP
valid = engine.check_cfop("5102", "venda")

# Validar ICMS
errors = engine.check_icms(invoice_data)
```

---

## 📡 API Routes (`api/routes.py`)

### Endpoints Disponíveis:

#### POST /api/v1/audit
Auditar nota fiscal completa

**Request:**
```json
{
  "invoice": {...},
  "context": {...}
}
```

**Response:**
```json
{
  "aprovada": true,
  "irregularidades": [],
  "confianca": 0.95,
  "justificativa": "...",
  "detalhes": {...}
}
```

#### POST /api/v1/validate
Validar apenas estrutura (sem auditoria fiscal)

#### POST /api/v1/generate
Gerar nota fiscal sintética

**Request:**
```json
{
  "tipo": "valida",
  "valor_max": 10000.0,
  "estado": "SP"
}
```

#### POST /api/v1/audit/batch
Auditar múltiplas notas em lote

#### GET /api/v1/agents/health
Health check dos agentes

---

## 🔄 Fluxo de Dados

### Auditoria Completa:

```
1. Cliente → POST /api/v1/audit
   └─► invoice_data + context
   
2. API → AgentCoordinator.process_invoice()
   
3. Coordinator → ValidationAgent.validate_invoice()
   └─► Validações estruturais
   └─► Retorna: {valid, errors, warnings}
   
4. Se valid=False:
   └─► Retorna REPROVADA imediatamente
   
5. Se valid=True:
   └─► Coordinator → AuditAgent.audit_invoice()
   
6. AuditAgent:
   ├─► RulesEngine (validações rápidas)
   ├─► LLM Analysis
   │   ├─► RAGTool (se necessário)
   │   └─► TaxCalculator (se necessário)
   └─► Consolida resultado
   
7. Coordinator consolida:
   ├─► Validação + Auditoria
   ├─► Verifica confidence threshold
   └─► Decisão final
   
8. API retorna ao cliente:
   └─► {aprovada, irregularidades, confianca, justificativa}
```

---

## 🧠 Prompts

### System Prompt (AuditAgent)

Componentes principais:
1. **Definição de Papel:** Auditor fiscal especializado
2. **Legislação Aplicável:** ICMS, IPI, PIS, COFINS, CFOPs
3. **Tools Disponíveis:** consult_rag, calculate_taxes
4. **Processo de Auditoria:** 5 fases de validação
5. **Formato de Resposta:** JSON estruturado
6. **Diretrizes:** O que fazer e não fazer
7. **Exemplos:** Few-shot learning

### Audit Template

Template usado para cada auditoria:
- Dados da nota fiscal
- Contexto adicional
- Violações já identificadas
- Instruções específicas

---

## ⚡ Performance

### Otimizações Implementadas:

1. **Rules Engine First:**
   - Validações rápidas antes do LLM
   - Rejeição imediata de erros críticos
   - Economia de chamadas de API

2. **Streaming:**
   - Tokens são streamados quando possível
   - Feedback em tempo real via WebSocket

3. **Caching:**
   - Decisões similares podem ser cacheadas
   - Configurável via `ENABLE_CACHE`

4. **Timeouts:**
   - Configuráveis por agente
   - Previne travamentos

5. **Retry Logic:**
   - 3 tentativas por padrão
   - Backoff exponencial

6. **Fallback LLM:**
   - Se Claude falhar, usa GPT-4
   - Garante disponibilidade

---

## 🔐 Segurança

### Boas Práticas Implementadas:

1. **API Keys:** Nunca hardcoded, sempre via `.env`
2. **Input Validation:** Pydantic models validam todos inputs
3. **Error Handling:** Exceptions tratadas globalmente
4. **Logs:** Todas as operações são logadas
5. **CORS:** Configurável, restrito por padrão
6. **Rate Limiting:** Pronto para implementar

---

## 📊 Monitoramento

### Logs:

**Estrutura:**
```
timestamp - logger_name - level - message
```

**Níveis:**
- DEBUG: Detalhes de execução
- INFO: Operações normais
- WARNING: Situações anormais mas não críticas
- ERROR: Erros que precisam atenção

**Arquivos:**
- Console: Output em tempo real
- `agents.log`: Arquivo persistente

### Métricas (TODO):

- Total de auditorias
- Taxa de aprovação
- Tempo médio de processamento
- Uso de tokens (custos)
- Erros por tipo

---

## 🚀 Escalabilidade

### Horizontal Scaling:

O sistema é stateless e pode escalar horizontalmente:

```
┌─────────┐
│ Load    │
│ Balancer│
└────┬────┘
     │
     ├──► [Instance 1] FastAPI + Agents
     ├──► [Instance 2] FastAPI + Agents
     └──► [Instance 3] FastAPI + Agents
```

### Async/Await:

- Todas as operações de I/O são assíncronas
- Permite alta concorrência
- Não bloqueia threads

### Background Jobs:

- Batch processing via background tasks
- Pode usar Celery para jobs pesados

---

## 🔧 Extensibilidade

### Adicionar Novo Agente:

```python
# 1. Criar agente
class NovoAgente:
    def __init__(self):
        self.llm = ChatAnthropic(...)
    
    async def processar(self, data):
        # Lógica do agente
        return resultado

# 2. Registrar no Coordinator
class AgentCoordinator:
    def __init__(self):
        self.novo_agente = NovoAgente()
    
    async def process_invoice(self, data):
        # Incluir no fluxo
        resultado_novo = await self.novo_agente.processar(data)
```

### Adicionar Nova Tool:

```python
from langchain.tools import BaseTool

class NovaTool(BaseTool):
    name = "nova_tool"
    description = "..."
    
    def _run(self, input_str: str) -> str:
        # Implementar lógica
        return resultado
    
    async def _arun(self, input_str: str) -> str:
        return self._run(input_str)
```

---

## 📚 Referências

- **LangChain:** https://python.langchain.com/
- **FastAPI:** https://fastapi.tiangolo.com/
- **Claude API:** https://docs.anthropic.com/
- **Pydantic:** https://docs.pydantic.dev/

---

**Versão:** 1.0.0  
**Última Atualização:** Outubro 2025
