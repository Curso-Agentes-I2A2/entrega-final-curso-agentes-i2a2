VALID_INVOICE_XML = """<?xml version="1.0" encoding="UTF-8"?>
<nfeProc versao="4.00">
  <NFe>
    <infNFe Id="NFe12345678901234567890" versao="4.00">
      <ide><nNF>123456</nNF></ide>
      <emit><CNPJ>12345678000190</CNPJ><xNome>Emitente Teste</xNome></emit>
      <total><ICMSTot><vBC>10000.00</vBC><vICMS>1800.00</vICMS><vNF>10000.00</vNF></ICMSTot></total>
    </infNFe>
  </NFe>
</nfeProc>
"""

INVALID_INVOICE_XML = """<?xml version="1.0"?>
<nfeProc>
  <NFe>
    <infNFe>
      <ide>
        <cUF>XX</cUF>
        <nNF>abc</nNF>
      </ide>
      <emit><CNPJ>123</CNPJ></emit>
    </infNFe>
  </NFe>
</nfeProc>
"""

SAMPLE_AUDIT_RESULT = {
    "id": "INV-1",
    "status": "aprovada",
    "irregularidades": [],
    "score": 0.95,
}

MOCK_RAG_RESPONSE = [
    {"content": "Lei X - art. 1", "score": 0.99},
    {"content": "Portaria Y - item 3", "score": 0.85},
]

VALID_CNPJS = ["12345678000190", "11111111000191"]
