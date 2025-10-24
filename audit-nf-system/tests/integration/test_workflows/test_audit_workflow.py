import pytest
from tests.fixtures.mock_data import VALID_INVOICE_XML, INVALID_INVOICE_XML

@pytest.mark.integration
@pytest.mark.asyncio
async def test_complete_audit_flow(api_client):
    # 1) upload
    files = {"file": ("nf.xml", VALID_INVOICE_XML, "application/xml")}
    resp = await api_client.post("/api/invoices/upload", files=files)
    assert resp.status_code == 200
    invoice_id = resp.json().get("id")
    assert invoice_id

    # 2) start audit
    resp = await api_client.post(f"/api/invoices/{invoice_id}/audit")
    assert resp.status_code in (200, 202)

    # 3) get result
    resp = await api_client.get(f"/api/audits/{invoice_id}")
    assert resp.status_code == 200
    body = resp.json()
    assert "status" in body

@pytest.mark.integration
@pytest.mark.asyncio
async def test_workflow_with_rejection(api_client):
    files = {"file": ("nf.xml", INVALID_INVOICE_XML, "application/xml")}
    resp = await api_client.post("/api/invoices/upload", files=files)
    assert resp.status_code == 200
    invoice_id = resp.json().get("id")
    resp = await api_client.post(f"/api/invoices/{invoice_id}/audit")
    assert resp.status_code in (200, 202)
    resp = await api_client.get(f"/api/audits/{invoice_id}")
    assert resp.status_code == 200
    assert resp.json().get("status") in ("rejeitada", "manual_review")
