# 🤖 Prompt para Gerar Agentes de IA

**Instruções:** Copie este prompt e cole no Claude ou GPT-4 para gerar o código inicial dos agentes.

---

## PROMPT:

```
Você é um especialista em LangChain e Agentes de IA. Preciso que você crie a estrutura inicial completa de um sistema de agentes para auditoria de notas fiscais brasileiras.

CONTEXTO DO PROJETO:
- Sistema multi-agente para auditoria automatizada de NF-e
- Agentes especializados: Auditoria, Validação, Geração Sintética
- Orquestrador que coordena os agentes
- Integração com RAG para contexto fiscal
- Integração com MCP para ferramentas externas
- API REST para comunicação com backend

REQUISITOS TÉCNICOS:
- Framework: LangChain
- LLM: Anthropic Claude Sonnet 4 (com fallback para GPT-4)
- Padrão: ReAct (Reasoning + Acting)
- Comunicação: Async/await
- API: FastAPI
- Memory: ConversationBufferMemory

ESTRUTURA DE PASTAS:
```
agents/
├── audit_agent/
│   ├── __init__.py
│   ├── agent.py               # Agente principal de auditoria
│   ├── rules_engine.py        # Motor de regras fiscais
│   ├── anomaly_detection.py   # Detecção de anomalias
│   └── prompts.py             # Templates de prompts
├── validation_agent/
│   ├── __init__.py
│   ├── agent.py               # Agente de validação
│   ├── compliance_check.py    # Verificação de compliance
│   └── prompts.py
├── synthetic_agent/
│   ├── __init__.py
│   ├── agent.py               # Agente gerador de NFs
│   ├── nf_generator.py        # Lógica de geração
│   └── prompts.py
├── orchestrator/
│   ├── __init__.py
│   ├── coordinator.py         # Coordena agentes
│   └── workflow.py            # Define workflows
├── tools/
│   ├── __init__.py
│   ├── rag_tool.py            # Ferramenta para consultar RAG
│   ├── mcp_tools.py           # Ferramentas MCP
│   └── calculator_tool.py     # Calculadora de impostos
├── api/
│   ├── __init__.py
│   └── routes.py              # Endpoints FastAPI
├── config.py
├── main.py
└── requirements.txt
```

POR FAVOR, GERE:

1. **main.py** - Aplicação FastAPI dos agentes:
   - Endpoints para invocar agentes
   - Health check
   - Logs de execução
   - Tratamento de erros

2. **config.py** - Configurações:
   - API keys (Anthropic, OpenAI)
   - URLs de serviços (RAG, MCP, Backend)
   - Configurações dos agentes
   - Parâmetros de LLM (temperature, max_tokens)

3. **audit_agent/agent.py** - Agente de Auditoria:
   - Classe AuditAgent usando LangChain
   - Inicialização com Claude Sonnet
   - Tools disponíveis:
     * consult_rag: Consultar base de conhecimento
     * validate_cnpj: Validar CNPJ
     * calculate_taxes: Calcular impostos
     * check_history: Verificar histórico do fornecedor
   - Método audit_invoice(invoice_data: dict) -> dict
   - Retorna: {aprovada: bool, irregularidades: List, confianca: float, justificativa: str}

4. **audit_agent/prompts.py** - Prompts do agente de auditoria:
   - SYSTEM_PROMPT: Define papel do agente como auditor fiscal
   - AUDIT_TEMPLATE: Template para análise de NF
   - Incluir instruções sobre legislação brasileira
   - Formato de resposta em JSON estruturado

5. **audit_agent/rules_engine.py** - Motor de regras:
   - Classe RulesEngine
   - check_icms(invoice: dict) -> List[str]: Valida cálculo de ICMS
   - check_cfop(cfop: str, operation: str) -> bool: Valida CFOP
   - check_value_consistency(invoice: dict) -> List[str]: Verifica consistência de valores
   - Regras básicas de validação fiscal

6. **validation_agent/agent.py** - Agente de Validação:
   - Classe ValidationAgent
   - Foca em validação estrutural e compliance
   - Tools:
     * validate_xml_schema: Valida XML contra XSD
     * check_required_fields: Verifica campos obrigatórios
     * validate_access_key: Valida chave de acesso
   - Método validate_invoice(invoice_xml: str) -> dict

7. **validation_agent/compliance_check.py** - Verificações de compliance:
   - check_schema(xml: str) -> bool: Valida contra schema NF-e 4.0
   - validate_signature(xml: str) -> bool: Valida assinatura digital (mock)
   - check_access_key(key: str) -> bool: Valida formato da chave

8. **synthetic_agent/agent.py** - Agente Gerador:
   - Classe SyntheticAgent
   - Gera notas fiscais sintéticas para testes
   - Método generate_invoice(params: dict) -> dict
   - Parâmetros: tipo (válida/inválida/suspeita), valor_max, estado
   - Retorna NF-e em formato JSON

9. **synthetic_agent/nf_generator.py** - Lógica de geração:
   - generate_cnpj() -> str: CNPJ válido aleatório
   - generate_access_key() -> str: Chave de acesso válida
   - calculate_access_key_digit(key: str) -> str: Dígito verificador
   - generate_valid_invoice() -> dict: NF válida
   - generate_invalid_invoice() -> dict: NF com erros propositais

10. **orchestrator/coordinator.py** - Orquestrador:
    - Classe AgentCoordinator
    - Método process_invoice(invoice_data: dict) -> dict:
      1. Chama ValidationAgent
      2. Se válido, chama AuditAgent
      3. Consolida resultados
      4. Retorna decisão final
    - Gerencia fluxo de trabalho

11. **tools/rag_tool.py** - Tool para RAG:
    - Classe RAGTool(BaseTool) do LangChain
    - Consulta serviço RAG via HTTP
    - async _arun(query: str) -> str
    - Retorna contexto relevante como string

12. **tools/calculator_tool.py** - Calculadora de impostos:
    - Classe TaxCalculatorTool(BaseTool)
    - Calcula ICMS, IPI, PIS, COFINS
    - _run(base_value: float, tax_regime: str, ncm: str) -> dict
    - Retorna breakdown de impostos

13. **api/routes.py** - Rotas da API:
    - POST /audit - Auditar nota fiscal
    - POST /validate - Validar estrutura de NF
    - POST /generate - Gerar NF sintética
    - GET /health - Health check
    - WebSocket /stream - Stream de execução do agente

14. **requirements.txt**:
    - langchain
    - langchain-anthropic
    - langchain-openai
    - fastapi
    - uvicorn[standard]
    - httpx
    - pydantic
    - python-dotenv

FUNCIONALIDADES ADICIONAIS:

15. **Exemplo de teste** (test_agents.py):
    - Teste básico de cada agente
    - Mock de serviços externos (RAG, MCP)
    - Exemplo de invoice_data para teste

IMPORTANTE:
- Use async/await em todas as chamadas de LLM
- Implemente retry logic para chamadas de API
- Adicione logs detalhados de cada step do agente
- Crie fallback: se Claude falhar, usar GPT-4
- Estruture respostas sempre em JSON
- Adicione timeout para evitar agentes travados
- Implemente streaming de tokens quando possível
- Cache de decisões similares

EXEMPLO DE FLUXO:

```python
# Cliente envia NF para auditoria
invoice_data = {
    "numero": "123",
    "cnpj_emitente": "12345678000190",
    "valor_total": 10000.00,
    "impostos": {...},
    "xml": "..."
}

# Coordenador processa
coordinator = AgentCoordinator()
result = await coordinator.process_invoice(invoice_data)

# Resultado
{
    "aprovada": False,
    "irregularidades": [
        "ICMS calculado incorretamente",
        "CFOP incompatível com operação"
    ],
    "confianca": 0.95,
    "detalhes": {
        "validacao": "aprovada",
        "auditoria": "reprovada"
    }
}
```

FORMATO DE RESPOSTA:
Por favor, gere cada arquivo completo, com comentários. Inclua exemplos de prompts efetivos e mocks para desenvolvimento independente.
```

---

## TESTE RÁPIDO:

```bash
cd agents
pip install -r requirements.txt

# Configurar .env
echo "ANTHROPIC_API_KEY=sk-ant-..." > .env
echo "RAG_URL=http://localhost:8001" >> .env

# Iniciar API
uvicorn main:app --reload --port 8002

# Testar
curl -X POST http://localhost:8002/audit \
  -H "Content-Type: application/json" \
  -d @test_invoice.json
```