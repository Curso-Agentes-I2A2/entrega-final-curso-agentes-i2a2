import pytest

@pytest.mark.integration
@pytest.mark.asyncio
async def test_mcp_health(api_client):
    resp = await api_client.get("/api/mcp/health")
    assert resp.status_code in (200, 204)
