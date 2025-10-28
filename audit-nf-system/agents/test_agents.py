"""
Testes dos Agentes de Auditoria
Execute: pytest test_agents.py -v
"""

import pytest
import asyncio
from datetime import datetime

# Fixtures de dados para testes
VALID_INVOICE = {
    "numero": "000123",
    "serie": "1",
    "data_emissao": "2025-10-27",
    "cnpj_emitente": "12345678000190",
    "razao_social_emitente": "Empresa Teste LTDA",
    "cnpj_destinatario": "98765432000199",
    "razao_social_destinatario": "Cliente Teste SA",
    "cfop": "5102",
    "tipo_operacao": "venda",
    "valor_produtos": 1000.00,
    "valor_total": 1180.00,
    "base_calculo_icms": 1000.00,
    "aliquota_icms": 18.0,
    "valor_icms": 180.00,
    "valor_ipi": 0.0,
    "valor_pis": 16.50,
    "valor_cofins": 76.00,
}

INVALID_INVOICE_CFOP = {
    **VALID_INVOICE,
    "numero": "000124",
    "cfop": "9999",  # CFOP inválido
}

INVALID_INVOICE_ICMS = {
    **VALID_INVOICE,
    "numero": "000125",
    "valor_icms": 150.00,  # ICMS incorreto (deveria ser 180)
}


@pytest.mark.asyncio
async def test_validation_agent():
    """
    Testa ValidationAgent
    """
    from validation_agent.agent import ValidationAgent
    
    agent = ValidationAgent()
    
    # Teste 1: Nota válida
    result = await agent.validate_invoice(VALID_INVOICE)
    assert result["valid"] == True
    assert len(result["errors"]) == 0
    print("✅ Teste 1 passou: Nota válida")
    
    # Teste 2: Nota com CFOP inválido
    result = await agent.validate_invoice(INVALID_INVOICE_CFOP)
    # Nota: ValidationAgent não valida CFOP semanticamente, apenas formato
    assert result["valid"] == True  # Formato está OK
    print("✅ Teste 2 passou: CFOP formato válido")
    
    # Teste 3: Nota com campos ausentes
    incomplete_invoice = {"numero": "123"}
    result = await agent.validate_invoice(incomplete_invoice)
    assert result["valid"] == False
    assert len(result["errors"]) > 0
    print("✅ Teste 3 passou: Campos ausentes detectados")


@pytest.mark.asyncio
async def test_audit_agent():
    """
    Testa AuditAgent
    """
    from audit_agent.agent import AuditAgent
    
    agent = AuditAgent()
    
    # Teste 1: Nota válida
    result = await agent.audit_invoice(VALID_INVOICE)
    assert result["aprovada"] == True
    assert len(result["irregularidades"]) == 0
    print("✅ Teste 1 passou: Nota aprovada")
    
    # Teste 2: Nota com CFOP inválido
    result = await agent.audit_invoice(INVALID_INVOICE_CFOP)
    assert result["aprovada"] == False
    assert any("CFOP" in irreg for irreg in result["irregularidades"])
    print("✅ Teste 2 passou: CFOP inválido detectado")
    
    # Teste 3: Nota com ICMS incorreto
    result = await agent.audit_invoice(INVALID_INVOICE_ICMS)
    assert result["aprovada"] == False or len(result["irregularidades"]) > 0
    print("✅ Teste 3 passou: ICMS incorreto detectado")


def test_rules_engine():
    """
    Testa RulesEngine
    """
    from audit_agent.rules_engine import RulesEngine
    
    engine = RulesEngine()
    
    # Teste 1: Validar CNPJ válido
    assert engine.validate_cnpj("12345678000190") == True
    print("✅ Teste 1 passou: CNPJ válido")
    
    # Teste 2: Validar CNPJ inválido
    assert engine.validate_cnpj("00000000000000") == False
    print("✅ Teste 2 passou: CNPJ inválido detectado")
    
    # Teste 3: Validar CFOP
    assert engine.check_cfop("5102", "venda") == True
    assert engine.check_cfop("9999", "venda") == False
    print("✅ Teste 3 passou: Validação de CFOP")
    
    # Teste 4: Calcular ICMS
    icms = engine.calculate_icms(1000.00, 18.0)
    assert icms["valor"] == 180.00
    print("✅ Teste 4 passou: Cálculo de ICMS")


def test_rag_tool():
    """
    Testa RAG Tool (mock)
    """
    from tools.rag_tool import RAGTool
    
    tool = RAGTool()
    
    # Teste com mock
    result = tool._mock_rag_response("alíquota ICMS São Paulo")
    assert "18%" in result or "ICMS" in result
    print("✅ Teste passou: RAG Tool mock")


def test_calculator_tool():
    """
    Testa Calculator Tool
    """
    from tools.calculator_tool import TaxCalculatorTool
    import json
    
    tool = TaxCalculatorTool()
    
    input_data = json.dumps({
        "base_value": 1000.00,
        "state": "SP",
        "tax_regime": "nao_cumulativo",
        "product_type": "normal"
    })
    
    result_str = tool._run(input_data)
    result = json.loads(result_str)
    
    assert result["icms"]["valor"] == 180.00
    assert result["base_value"] == 1000.00
    print("✅ Teste passou: Calculator Tool")


@pytest.mark.asyncio
async def test_coordinator():
    """
    Testa AgentCoordinator (fluxo completo)
    """
    from orchestrator.coordinator import AgentCoordinator
    
    coordinator = AgentCoordinator()
    
    # Teste 1: Nota válida
    result = await coordinator.process_invoice(VALID_INVOICE)
    assert result["aprovada"] == True
    print("✅ Teste 1 passou: Fluxo completo nota válida")
    
    # Teste 2: Nota inválida
    result = await coordinator.process_invoice(INVALID_INVOICE_CFOP)
    assert result["aprovada"] == False
    print("✅ Teste 2 passou: Fluxo completo nota inválida")


def test_synthetic_generator():
    """
    Testa gerador de notas sintéticas
    """
    from synthetic_agent.nf_generator import (
        generate_valid_invoice,
        generate_invalid_invoice,
        generate_cnpj
    )
    
    # Teste 1: Gerar CNPJ
    cnpj = generate_cnpj()
    assert len(cnpj) == 14
    print(f"✅ Teste 1 passou: CNPJ gerado: {cnpj}")
    
    # Teste 2: Gerar nota válida
    invoice = generate_valid_invoice()
    assert "numero" in invoice
    assert "cfop" in invoice
    assert invoice["cfop"] in ["5101", "5102", "5103"]
    print("✅ Teste 2 passou: Nota válida gerada")
    
    # Teste 3: Gerar nota inválida
    invoice = generate_invalid_invoice(error_type="cfop")
    assert invoice["cfop"] == "9999"
    print("✅ Teste 3 passou: Nota inválida gerada")


# ========================================================================
# TESTES DE INTEGRAÇÃO (requerem API rodando)
# ========================================================================

@pytest.mark.integration
@pytest.mark.asyncio
async def test_api_audit_endpoint():
    """
    Testa endpoint /api/v1/audit
    Requer API rodando em localhost:8002
    """
    import httpx
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8002/api/v1/audit",
            json={
                "invoice": VALID_INVOICE,
                "context": {}
            },
            timeout=30.0
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "aprovada" in data
        print("✅ Teste passou: Endpoint /audit")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_api_generate_endpoint():
    """
    Testa endpoint /api/v1/generate
    """
    import httpx
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8002/api/v1/generate",
            json={
                "tipo": "valida",
                "valor_max": 5000.0,
                "estado": "SP"
            },
            timeout=30.0
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "invoice" in data
        print("✅ Teste passou: Endpoint /generate")


# ========================================================================
# EXECUÇÃO DIRETA
# ========================================================================

if __name__ == "__main__":
    """
    Executa testes básicos sem pytest
    """
    print("=" * 70)
    print("🧪 EXECUTANDO TESTES DOS AGENTES")
    print("=" * 70)
    
    # Testes síncronos
    print("\n📋 Testes do RulesEngine:")
    test_rules_engine()
    
    print("\n🛠️  Testes das Tools:")
    test_rag_tool()
    test_calculator_tool()
    
    print("\n🔧 Testes do Gerador Sintético:")
    test_synthetic_generator()
    
    # Testes assíncronos
    print("\n🤖 Testes dos Agentes:")
    
    loop = asyncio.get_event_loop()
    
    print("\n  ValidationAgent:")
    loop.run_until_complete(test_validation_agent())
    
    print("\n  AuditAgent:")
    loop.run_until_complete(test_audit_agent())
    
    print("\n  Coordinator:")
    loop.run_until_complete(test_coordinator())
    
    print("\n" + "=" * 70)
    print("✅ TODOS OS TESTES PASSARAM!")
    print("=" * 70)
