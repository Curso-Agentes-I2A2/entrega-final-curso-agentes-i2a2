# 🧪 Prompt para Gerar Tests (Testes Automatizados)

**Instruções:** Copie este prompt e cole no Claude ou GPT-4 para gerar o código inicial dos testes.

---

## PROMPT:

```
Você é um especialista em testes automatizados em Python. Preciso que você crie a estrutura inicial completa de testes para um sistema de auditoria de notas fiscais.

CONTEXTO DO PROJETO:
- Sistema de auditoria com múltiplos módulos (Backend, RAG, Agents, MCP, Frontend)
- Testes unitários, integração e end-to-end
- Testes de carga com Locust
- Cobertura mínima de 80%
- CI/CD ready

REQUISITOS TÉCNICOS:
- Framework: pytest
- Async: pytest-asyncio
- Mocks: pytest-mock
- Coverage: pytest-cov
- E2E: Playwright (para Streamlit)
- Load: Locust

ESTRUTURA DE PASTAS:
```
tests/
├── unit/
│   ├── test_backend/
│   │   ├── __init__.py
│   │   ├── test_invoice_service.py
│   │   ├── test_validation.py
│   │   └── test_xml_parser.py
│   ├── test_rag/
│   │   ├── __init__.py
│   │   ├── test_embeddings.py
│   │   ├── test_retrieval.py
│   │   └── test_chunking.py
│   └── test_agents/
│       ├── __init__.py
│       ├── test_audit_agent.py
│       └── test_orchestrator.py
├── integration/
│   ├── __init__.py
│   ├── test_workflows/
│   │   ├── __init__.py
│   │   ├── test_audit_workflow.py
│   │   └── test_api_integration.py
│   └── test_mcp_integration.py
├── e2e/
│   ├── __init__.py
│   ├── test_scenarios/
│   │   ├── __init__.py
│   │   ├── test_complete_audit.py
│   │   └── test_synthetic_generation.py
│   └── test_streamlit_ui.py
├── load/
│   ├── __init__.py
│   └── locustfile.py
├── fixtures/
│   ├── __init__.py
│   ├── sample_nf.xml
│   └── mock_data.py
├── conftest.py                # Configuração global pytest
├── pytest.ini                 # Configuração pytest
└── requirements.txt
```

POR FAVOR, GERE:

1. **pytest.ini** - Configuração do pytest:
   - Markers para diferentes tipos de teste (unit, integration, e2e, slow)
   - Opções de coverage
   - Configuração de asyncio
   - Warnings filters

2. **conftest.py** - Fixtures globais:
   - Fixture de database (mock)
   - Fixture de API client
   - Fixture de invoice válida
   - Fixture de invoice inválida
   - Fixture de mock para serviços externos
   - Setup e teardown globais

3. **fixtures/mock_data.py** - Dados de teste:
   - VALID_INVOICE_XML: XML de NF-e válida
   - INVALID_INVOICE_XML: XML com erros
   - SAMPLE_AUDIT_RESULT: Resultado de auditoria
   - MOCK_RAG_RESPONSE: Resposta do RAG
   - Mock de CNPJs válidos

4. **unit/test_backend/test_invoice_service.py** - Testes do serviço de NF:
   - test_parse_xml_valid: Parse de XML válido
   - test_parse_xml_invalid: Parse de XML inválido
   - test_validate_invoice_schema: Validação de schema
   - test_save_invoice: Salvar no banco (mock)
   - test_get_invoice_by_id: Buscar por ID
   - test_list_invoices: Listar com filtros
   - Todos os testes usando pytest-asyncio

5. **unit/test_backend/test_validation.py** - Testes de validação:
   - test_validate_cnpj_valid: CNPJ válido
   - test_validate_cnpj_invalid: CNPJ inválido
   - test_validate_access_key: Chave de acesso
   - test_validate_cfop: CFOP correto
   - test_calculate_icms: Cálculo de ICMS
   - Usar pytest.mark.parametrize para múltiplos casos

6. **unit/test_rag/test_embeddings.py** - Testes de embeddings:
   - test_generate_embeddings: Gerar embeddings
   - test_embeddings_consistency: Mesmo texto = mesmo embedding
   - test_embeddings_cache: Verificar cache
   - test_fallback_to_local_model: Fallback quando API falha
   - Mock de OpenAI API

7. **unit/test_rag/test_retrieval.py** - Testes de busca:
   - test_search_basic: Busca básica
   - test_search_with_filters: Busca com filtros
   - test_search_threshold: Score threshold
   - test_search_empty_results: Query sem resultados
   - Mock do vector store

8. **unit/test_agents/test_audit_agent.py** - Testes do agente:
   - test_audit_valid_invoice: Auditar NF válida
   - test_audit_invalid_invoice: Auditar NF inválida
   - test_agent_with_rag: Agente consulta RAG
   - test_agent_with_mcp_tools: Agente usa tools MCP
   - test_agent_error_handling: Tratamento de erros
   - Mock de LLM responses

9. **integration/test_workflows/test_audit_workflow.py** - Teste de workflow:
   - test_complete_audit_flow: Fluxo completo
     1. Upload de NF
     2. Validação
     3. Auditoria
     4. Resultado
   - test_workflow_with_rejection: Fluxo com rejeição
   - test_workflow_with_manual_review: Revisão manual
   - Usa docker-compose para subir serviços

10. **integration/test_workflows/test_api_integration.py** - Integração de APIs:
    - test_backend_to_rag: Backend consulta RAG
    - test_backend_to_agents: Backend chama agents
    - test_agents_to_mcp: Agents usam MCP
    - Verificar comunicação real entre serviços

11. **e2e/test_scenarios/test_complete_audit.py** - Teste E2E completo:
    - test_user_uploads_and_audits_invoice:
      1. Usuário acessa frontend
      2. Faz upload de NF
      3. Recebe resultado
      4. Baixa relatório
    - Usar Playwright para testar Streamlit

12. **e2e/test_streamlit_ui.py** - Testes de UI Streamlit:
    - test_homepage_loads: Página inicial carrega
    - test_upload_page_accepts_file: Upload funciona
    - test_audit_page_shows_results: Resultados aparecem
    - test_navigation_between_pages: Navegação

13. **load/locustfile.py** - Testes de carga:
    - Classe AuditUser(HttpUser)
    - Tarefas:
      * upload_invoice: POST /api/invoices/upload
      * get_audit_status: GET /api/audits/{id}
      * list_invoices: GET /api/invoices
    - Simular 100 usuários concorrentes
    - Ramp up de 10 users/segundo

14. **requirements.txt**:
    - pytest
    - pytest-asyncio
    - pytest-mock
    - pytest-cov
    - httpx
    - playwright
    - locust
    - faker (para dados fake)

FIXTURES IMPORTANTES:

```python
# conftest.py
import pytest
from httpx import AsyncClient

@pytest.fixture
def valid_invoice_data():
    """Dados de NF válida"""
    return {
        "numero": "123456",
        "serie": "1",
        "cnpj_emitente": "12345678000190",
        "valor_total": 10000.00,
        # ... mais campos
    }

@pytest.fixture
def mock_rag_client(mocker):
    """Mock do cliente RAG"""
    mock = mocker.Mock()
    mock.search.return_value = [
        {"content": "Regulamento...", "score": 0.9}
    ]
    return mock

@pytest.fixture
async def api_client():
    """Cliente HTTP para testes de integração"""
    async with AsyncClient(base_url="http://localhost:8000") as client:
        yield client

@pytest.fixture
def mock_llm_response(mocker):
    """Mock de resposta do LLM"""
    return {
        "aprovada": True,
        "irregularidades": [],
        "confianca": 0.95
    }
```

EXEMPLO DE TESTE UNITÁRIO:

```python
# test_invoice_service.py
import pytest
from backend.services.invoice_service import InvoiceService

@pytest.mark.asyncio
async def test_validate_invoice_valid(valid_invoice_data, mock_rag_client):
    """Testa validação de NF válida"""
    service = InvoiceService(rag_client=mock_rag_client)
    
    result = await service.validate_invoice(valid_invoice_data)
    
    assert result["valid"] is True
    assert len(result["errors"]) == 0
    mock_rag_client.search.assert_called_once()

@pytest.mark.parametrize("cnpj,expected", [
    ("12345678000190", True),
    ("12345678000191", False),  # Dígito errado
    ("123", False),              # Muito curto
])
def test_validate_cnpj(cnpj, expected):
    """Testa validação de CNPJ"""
    from backend.validation.validator import validate_cnpj
    
    result = validate_cnpj(cnpj)
    assert result == expected
```

EXEMPLO DE TESTE DE INTEGRAÇÃO:

```python
# test_audit_workflow.py
import pytest

@pytest.mark.integration
@pytest.mark.asyncio
async def test_complete_audit_flow(api_client, valid_invoice_xml):
    """Testa fluxo completo de auditoria"""
    
    # 1. Upload
    response = await api_client.post(
        "/api/invoices/upload",
        files={"file": ("nf.xml", valid_invoice_xml)}
    )
    assert response.status_code == 200
    invoice_id = response.json()["id"]
    
    # 2. Iniciar auditoria
    response = await api_client.post(f"/api/invoices/{invoice_id}/audit")
    assert response.status_code == 200
    
    # 3. Verificar resultado
    response = await api_client.get(f"/api/audits/{invoice_id}")
    assert response.status_code == 200
    result = response.json()
    assert "status" in result
    assert result["status"] in ["aprovada", "rejeitada"]
```

EXEMPLO DE TESTE DE CARGA:

```python
# locustfile.py
from locust import HttpUser, task, between

class AuditUser(HttpUser):
    wait_time = between(1, 3)
    
    @task(3)
    def upload_invoice(self):
        """Upload de nota fiscal"""
        with open("fixtures/sample_nf.xml", "rb") as f:
            self.client.post(
                "/api/invoices/upload",
                files={"file": f}
            )
    
    @task(1)
    def list_invoices(self):
        """Listar notas fiscais"""
        self.client.get("/api/invoices")
```

COMANDOS ÚTEIS:

```bash
# Rodar todos os testes
pytest

# Testes unitários apenas
pytest tests/unit -v

# Com coverage
pytest --cov=backend --cov-report=html

# Testes específicos
pytest -k "test_validate_cnpj"

# Testes lentos
pytest -m slow

# Testes de integração (requer serviços rodando)
pytest tests/integration -v

# Testes de carga
locust -f tests/load/locustfile.py
```

IMPORTANTE:
- Use fixtures para evitar duplicação
- Separe testes rápidos de lentos
- Mock serviços externos sempre
- Teste casos de erro
- Use parametrize para múltiplos inputs
- Documente o que cada teste faz
- Organize por módulo testado
- Mantenha testes independentes
- Use markers do pytest
- Implemente setup/teardown quando necessário

FORMATO DE RESPOSTA:
Gere arquivos completos de teste, prontos para executar. Inclua mocks, fixtures e casos de teste relevantes.
```

---

## EXECUTAR:

```bash
cd tests
pip install -r requirements.txt

# Rodar testes
pytest -v

# Com coverage
pytest --cov --cov-report=html

# Abrir relatório
open htmlcov/index.html
```