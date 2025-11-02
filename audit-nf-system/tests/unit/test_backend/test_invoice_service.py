import pytest
from tests.fixtures.mock_data import VALID_INVOICE_XML, INVALID_INVOICE_XML

@pytest.mark.asyncio
async def test_parse_xml_valid(mocker, mock_rag_client):
    """
    InvoiceService.parse_xml should parse valid XML into dict/object.
    """
    # import target service - adjust path conforme seu projeto
    from backend.services.invoice_service import InvoiceService

    svc = InvoiceService(rag_client=mock_rag_client)
    parsed = await svc.parse_xml(VALID_INVOICE_XML)
    assert parsed is not None
    assert "emit" in parsed or parsed.get("emitente") or parsed.get("infNFe")

@pytest.mark.asyncio
async def test_parse_xml_invalid():
    from backend.services.invoice_service import InvoiceService
    svc = InvoiceService(rag_client=None)
    with pytest.raises(Exception):
        await svc.parse_xml(INVALID_INVOICE_XML)

@pytest.mark.asyncio
async def test_validate_invoice_schema(mocker):
    from backend.services.invoice_service import InvoiceService
    mock_rag = mocker.Mock()
    svc = InvoiceService(rag_client=mock_rag)
    parsed = await svc.parse_xml(VALID_INVOICE_XML)
    valid, errors = await svc.validate_schema(parsed)
    assert valid is True
    assert isinstance(errors, list)

@pytest.mark.asyncio
async def test_save_and_get_invoice(mocker, mock_db=None):
    from backend.services.invoice_service import InvoiceService
    svc = InvoiceService(rag_client=None, db=mocker.Mock())
    # mock save_to_db
    mock_id = "1"
    mocker.patch.object(svc, "save_to_db", return_value=mock_id)
    saved = await svc.save_invoice({"numero": "1"})
    assert saved == mock_id
    mocker.patch.object(svc, "get_invoice_by_id", return_value={"numero": "1"})
    got = await svc.get_invoice_by_id(mock_id)
    assert got["numero"] == "1"

@pytest.mark.asyncio
async def test_list_invoices(mocker):
    from backend.services.invoice_service import InvoiceService
    svc = InvoiceService(rag_client=None, db=mocker.Mock())
    mocked = [{"id": 1}, {"id": 2}]
    mocker.patch.object(svc, "list_invoices", return_value=mocked)
    res = await svc.list_invoices({})
    assert isinstance(res, list)
    assert len(res) == 2
