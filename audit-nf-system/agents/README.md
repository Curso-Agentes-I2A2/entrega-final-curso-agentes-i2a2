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