import pytest

@pytest.mark.integration
@pytest.mark.asyncio
async def test_backend_to_rag(api_client):
    resp = await api_client.get("/api/rag/health")
    assert resp.status_code in (200, 204)

@pytest.mark.integration
@pytest.mark.asyncio
async def test_backend_to_agents(api_client):
    resp = await api_client.get("/api/agents/health")
    assert resp.status_code in (200, 204)

@pytest.mark.integration
@pytest.mark.asyncio
async def test_agents_to_mcp(api_client):
    resp = await api_client.get("/api/mcp/health")
    assert resp.status_code in (200, 204)
