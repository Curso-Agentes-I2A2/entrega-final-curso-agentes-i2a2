# 🔌 Prompt para Gerar MCP (Model Context Protocol)

**Instruções:** Copie este prompt e cole no Claude ou GPT-4 para gerar o código inicial do MCP.

---

## PROMPT:

```
Você é um especialista em MCP (Model Context Protocol) da Anthropic. Preciso que você crie a estrutura inicial completa de servidores MCP para um sistema de auditoria de notas fiscais brasileiras.

CONTEXTO DO PROJETO:
- Servidores MCP que fornecem ferramentas e recursos para agentes de IA
- Integração com APIs externas brasileiras (BrasilAPI, ReceitaWS, ViaCEP)
- Acesso a dados internos de notas fiscais
- Ferramentas de validação e cálculo
- Recursos compartilhados entre agentes

REQUISITOS TÉCNICOS:
- Framework: mcp (Python SDK oficial da Anthropic)
- Protocolo: Model Context Protocol 1.0
- Comunicação: Async/await
- APIs externas: httpx
- Validações: Pydantic

ESTRUTURA DE PASTAS:
```
mcp/
├── servers/
│   ├── __init__.py
│   ├── nf_context_server.py   # Servidor de contexto de NFs
│   └── audit_server.py        # Servidor de ferramentas de auditoria
├── resources/
│   ├── __init__.py
│   ├── invoice_resource.py    # Recursos de NFs
│   └── supplier_resource.py   # Recursos de fornecedores
├── tools/
│   ├── __init__.py
│   ├── validation_tools.py    # Tools de validação
│   ├── external_api_tools.py  # Tools para APIs externas
│   └── calculation_tools.py   # Tools de cálculo
├── clients/
│   ├── __init__.py
│   ├── brasilapi_client.py    # Cliente BrasilAPI
│   ├── receitaws_client.py    # Cliente ReceitaWS
│   └── viacep_client.py       # Cliente ViaCEP
├── config.py
├── main.py
└── requirements.txt
```

POR FAVOR, GERE:

1. **main.py** - Inicializador dos servidores MCP:
   - Importa e registra todos os servidores
   - Configuração de logging
   - Entry point principal

2. **config.py** - Configurações:
   - URLs de APIs externas
   - Timeouts e retries
   - Configuração de cache
   - Database URLs (mock)

3. **servers/nf_context_server.py** - Servidor principal de NFs:
   - Usa @server.resource para expor recursos
   - Recursos:
     * nf://invoices - Lista de notas fiscais
     * nf://invoice/{id} - NF específica
     * nf://invoices/pending - NFs pendentes
   - Cada recurso retorna JSON estruturado
   - Mock de dados quando DB não disponível

4. **servers/audit_server.py** - Servidor de ferramentas de auditoria:
   - Usa @server.tool para expor tools
   - Tools principais:
     * validate_cnpj - Valida CNPJ (via BrasilAPI)
     * calculate_icms - Calcula ICMS
     * calculate_pis_cofins - Calcula PIS/COFINS
     * check_cfop - Valida CFOP
     * verify_access_key - Valida chave de acesso NF-e
     * check_supplier_history - Histórico do fornecedor
   - Cada tool tem schema de input/output bem definido

5. **tools/validation_tools.py** - Ferramentas de validação:
   - validate_cnpj_format(cnpj: str) -> bool
   - validate_cnpj_digits(cnpj: str) -> bool
   - validate_access_key_format(key: str) -> bool
   - validate_access_key_digits(key: str) -> bool
   - validate_cfop(cfop: str, operation_type: str) -> dict
   - Todas com lógica de validação real

6. **tools/calculation_tools.py** - Calculadora de impostos:
   - calculate_icms(base: float, aliquota: float, state: str) -> dict
   - calculate_ipi(base: float, ncm: str) -> dict
   - calculate_pis_cofins(base: float, regime: str) -> dict
   - apply_tax_reduction(value: float, reduction: float) -> float
   - Usar tabelas reais de alíquotas (simplificadas)

7. **clients/brasilapi_client.py** - Cliente BrasilAPI:
   - Classe BrasilAPIClient
   - async consult_cnpj(cnpj: str) -> dict
   - async get_bank_info(code: str) -> dict
   - async get_holiday(date: str) -> dict
   - Retry logic (3 tentativas)
   - Timeout de 10 segundos
   - Cache de respostas (5 minutos)

8. **clients/receitaws_client.py** - Cliente ReceitaWS:
   - Classe ReceitaWSClient (fallback para BrasilAPI)
   - async consult_cnpj(cnpj: str) -> dict
   - Rate limiting respeitado
   - Tratamento de erro 429 (too many requests)

9. **clients/viacep_client.py** - Cliente ViaCEP:
   - Classe ViaCEPClient
   - async consult_cep(cep: str) -> dict
   - Validação de endereços de NF

10. **tools/external_api_tools.py** - Tools que usam APIs externas:
    - verify_cnpj_external(cnpj: str) -> dict:
      * Tenta BrasilAPI primeiro
      * Fallback para ReceitaWS
      * Retorna: {valid, company_name, situation, opening_date}
    - verify_cep(cep: str) -> dict:
      * Consulta ViaCEP
      * Retorna endereço completo
    - check_bank(bank_code: str) -> dict:
      * Verifica código bancário

11. **resources/invoice_resource.py** - Recursos de NFs:
    - get_invoice(invoice_id: str) -> Resource
    - list_invoices(status: str = None, limit: int = 10) -> Resource
    - get_pending_audits() -> Resource
    - Estrutura de dados JSON para cada recurso

12. **Example de servidor MCP completo** incluindo:
    - Registro de resources
    - Registro de tools
    - Prompts templates
    - Error handling
    - Logging

13. **requirements.txt**:
    - mcp
    - httpx
    - pydantic
    - python-dotenv
    - cachetools

EXEMPLO DE IMPLEMENTAÇÃO DE TOOL:

```python
from mcp.server import Server
from mcp.types import Tool
import httpx

server = Server("audit-tools")

@server.tool("validate_cnpj")
async def validate_cnpj(cnpj: str) -> dict:
    """
    Valida CNPJ consultando BrasilAPI
    
    Args:
        cnpj: CNPJ com ou sem formatação (XX.XXX.XXX/XXXX-XX)
    
    Returns:
        {
            "valid": bool,
            "company_name": str,
            "situation": str,
            "opening_date": str
        }
    """
    # Limpar CNPJ
    clean_cnpj = ''.join(c for c in cnpj if c.isdigit())
    
    # Validar formato
    if len(clean_cnpj) != 14:
        return {"valid": False, "error": "CNPJ deve ter 14 dígitos"}
    
    # Validar dígitos verificadores
    if not validate_cnpj_digits(clean_cnpj):
        return {"valid": False, "error": "Dígitos verificadores inválidos"}
    
    # Consultar BrasilAPI
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://brasilapi.com.br/api/cnpj/v1/{clean_cnpj}",
                timeout=10.0
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "valid": True,
                    "company_name": data["razao_social"],
                    "situation": data["situacao_cadastral"],
                    "opening_date": data["data_inicio_atividade"]
                }
            else:
                return {"valid": False, "error": "CNPJ não encontrado"}
                
    except Exception as e:
        return {"valid": False, "error": f"Erro ao consultar: {str(e)}"}
```

EXEMPLO DE RESOURCE:

```python
@server.resource("nf://invoice/{invoice_id}")
async def get_invoice(invoice_id: str) -> Resource:
    """Retorna dados de uma nota fiscal específica"""
    
    # Mock para desenvolvimento (substituir por consulta real ao DB)
    invoice_data = {
        "id": invoice_id,
        "numero": "123456",
        "serie": "1",
        "cnpj_emitente": "12345678000190",
        "cnpj_destinatario": "98765432000110",
        "valor_total": 10000.00,
        "status": "pendente",
        "data_emissao": "2024-10-18"
    }
    
    return Resource(
        uri=f"nf://invoice/{invoice_id}",
        name=f"Nota Fiscal {invoice_id}",
        mimeType="application/json",
        text=json.dumps(invoice_data, indent=2)
    )
```

IMPORTANTE:
- Implemente retry logic em todas as chamadas externas
- Use cache para evitar consultas repetidas
- Timeout de 10s para APIs externas
- Fallback entre APIs (BrasilAPI → ReceitaWS)
- Logs detalhados de cada operação
- Tratamento robusto de erros
- Rate limiting para não sobrecarregar APIs
- Mock de dados quando APIs não disponíveis
- Validação de inputs com Pydantic
- Type hints em tudo

FORMATO DE RESPOSTA:
Gere cada arquivo completo com implementação real das ferramentas. Inclua mocks para desenvolvimento independente.
```

---

## TESTE:

```bash
cd mcp
pip install -r requirements.txt

# Criar .env
echo "BACKEND_URL=http://localhost:8000" > .env

# Testar servidor
python -m mcp.servers.audit_server

# Ou iniciar todos os servidores
python main.py
```