import pytest
from tests.fixtures.mock_data import VALID_INVOICE_XML, INVALID_INVOICE_XML

@pytest.mark.asyncio
async def test_xml_parser_parses_fields():
    from backend.parsers.xml_parser import XMLParser
    parser = XMLParser()
    data = await parser.parse(VALID_INVOICE_XML)
    assert data is not None
    # check expected fields (adjust names per seu parser)
    assert "infNFe" in data or "emit" in data

@pytest.mark.asyncio
async def test_xml_parser_raises_on_invalid():
    from backend.parsers.xml_parser import XMLParser
    parser = XMLParser()
    with pytest.raises(Exception):
        await parser.parse(INVALID_INVOICE_XML)
