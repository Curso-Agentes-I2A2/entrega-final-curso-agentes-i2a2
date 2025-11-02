import asyncio
import os
import tempfile
import pytest
from httpx import AsyncClient

# session-scoped event loop for pytest-asyncio
@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def temp_dir():
    d = tempfile.TemporaryDirectory()
    yield d.name
    d.cleanup()

@pytest.fixture
async def api_client():
    """
    Async HTTP client for integration tests.
    Set TEST_BASE_URL env var to point to running stack (default http://localhost:8000).
    """
    base = os.getenv("TEST_BASE_URL", "http://localhost:8000")
    async with AsyncClient(base_url=base, timeout=30.0) as client:
        yield client

@pytest.fixture
def valid_invoice_data():
    return {
        "numero": "123456",
        "serie": "1",
        "cnpj_emitente": "12345678000190",
        "valor_total": 10000.00,
        "data_emissao": "2025-10-23",
    }

@pytest.fixture
def invalid_invoice_data():
    return {
        "numero": "",
        "serie": "-",
        "cnpj_emitente": "123",
        "valor_total": -100.0,
    }

@pytest.fixture
def mock_rag_client(mocker):
    """
    Mock RAG client used by services.
    """
    mock = mocker.Mock()
    mock.search.return_value = [{"content": "Regulamento exemplo", "score": 0.9}]
    return mock

@pytest.fixture
def mock_llm(mocker):
    """
    Mock LLM client (e.g., for audit agent).
    """
    mock = mocker.Mock()
    mock.generate.return_value = {
        "aprovada": True,
        "irregularidades": [],
        "confianca": 0.95,
    }
    return mock

@pytest.fixture(autouse=True)
def set_test_env(monkeypatch):
    """
    Global test env. Use autouse to ensure environment is for tests.
    """
    monkeypatch.setenv("ENVIRONMENT", "test")
    # If you need to override anything else, do here.
    yield