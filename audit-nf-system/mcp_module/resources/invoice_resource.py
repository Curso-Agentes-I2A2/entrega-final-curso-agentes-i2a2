import json
from typing import Optional


MOCK_INVOICES_DB = {
    "1001": {
        "id": "1001",
        "numero": "123456",
        "serie": "1",
        "chave_acesso": "41241012345678000190550010001234561000000017",
        "cnpj_emitente": "12345678000190",
        "razao_social_emitente": "Empresa ABC Ltda",
        "cnpj_destinatario": "98765432000110",
        "razao_social_destinatario": "Empresa XYZ S.A.",
        "valor_total": 10000.00,
        "valor_icms": 1700.00,
        "status": "pendente_auditoria",
        "data_emissao": "2024-10-18",
        "uf_emitente": "RS",
        "produtos": [
            {
                "descricao": "Produto A",
                "ncm": "87032310",
                "quantidade": 2,
                "valor_unitario": 5000.00,
                "valor_total": 10000.00
            }
        ]
    },
    "1002": {
        "id": "1002",
        "numero": "789012",
        "serie": "1",
        "chave_acesso": "35241098765432000110550010007890121000000025",
        "cnpj_emitente": "98765432000110",
        "razao_social_emitente": "Empresa XYZ S.A.",
        "cnpj_destinatario": "12345678000190",
        "razao_social_destinatario": "Empresa ABC Ltda",
        "valor_total": 2500.50,
        "valor_icms": 425.09,
        "status": "auditada_ok",
        "data_emissao": "2024-10-19",
        "uf_emitente": "SP",
        "produtos": [
            {
                "descricao": "Produto B",
                "ncm": "22042100",
                "quantidade": 5,
                "valor_unitario": 500.10,
                "valor_total": 2500.50
            }
        ]
    },
    "1003": {
        "id": "1003",
        "numero": "345678",
        "serie": "2",
        "chave_acesso": "52241011223344000155550020003456781000000033",
        "cnpj_emitente": "11223344000155",
        "razao_social_emitente": "Fornecedor Tech Corp",
        "cnpj_destinatario": "12345678000190",
        "razao_social_destinatario": "Empresa ABC Ltda",
        "valor_total": 500.00,
        "valor_icms": 85.00,
        "status": "pendente_auditoria",
        "data_emissao": "2024-10-20",
        "uf_emitente": "MG",
        "produtos": [
            {
                "descricao": "Serviço de TI",
                "ncm": "00000000",
                "quantidade": 1,
                "valor_unitario": 500.00,
                "valor_total": 500.00
            }
        ]
    },
}


async def get_invoice(invoice_id: str) -> Optional[str]:
    """
    Busca uma NF pelo ID e retorna como string JSON.
    
    Args:
        invoice_id: ID da nota fiscal
        
    Returns:
        String JSON com dados da NF ou None se não encontrada
    """
    invoice_data = MOCK_INVOICES_DB.get(invoice_id)
    
    if not invoice_data:
        return None
    
    # Retorna diretamente a string JSON
    return json.dumps(invoice_data, ensure_ascii=False, indent=2)

async def list_invoices(status: Optional[str] = None, limit: int = 10) -> str:
    """
    Lista NFs com filtro opcional por status.
    
    Args:
        status: Filtro por status ('pendente_auditoria', 'auditada_ok', etc)
        limit: Número máximo de resultados
        
    Returns:
        String JSON com lista de NFs
    """
    # Aplica filtro se fornecido
    if status:
        filtered_invoices = [
            inv for inv in MOCK_INVOICES_DB.values() 
            if inv["status"] == status
        ]
    else:
        filtered_invoices = list(MOCK_INVOICES_DB.values())
    
    # Limita resultados
    result = filtered_invoices[:limit]
    
    # Estatísticas
    total = len(filtered_invoices)
    returned = len(result)
    
    summary = {
        "total": total,
        "returned": returned,
        "status_filter": status,
        "invoices": result
    }
    
    # Retorna string JSON
    return json.dumps(summary, ensure_ascii=False, indent=2)

async def get_pending_audits() -> str:
    """
    Retorna string JSON com todas as NFs pendentes de auditoria.
    
    Returns:
        String JSON com NFs pendentes
    """
    return await list_invoices(status="pendente_auditoria")

async def get_invoice_summary() -> str:
    """
    Retorna resumo estatístico das notas fiscais.
    
    Returns:
        String JSON com estatísticas
    """
    total = len(MOCK_INVOICES_DB)
    
    # Conta por status
    status_count = {}
    total_value = 0
    total_icms = 0
    
    for inv in MOCK_INVOICES_DB.values():
        status = inv["status"]
        status_count[status] = status_count.get(status, 0) + 1
        total_value += inv["valor_total"]
        total_icms += inv["valor_icms"]
    
    summary = {
        "total_invoices": total,
        "by_status": status_count,
        "total_value": round(total_value, 2),
        "total_icms": round(total_icms, 2),
        "average_value": round(total_value / total if total > 0 else 0, 2)
    }
    
    return json.dumps(summary, ensure_ascii=False, indent=2)

def add_invoice_to_mock_db(invoice_data: dict) -> str:
    """
    Adiciona uma nova NF ao mock DB (útil para testes).
    
    Args:
        invoice_data: Dicionário com dados da NF
        
    Returns:
        ID da NF criada
    """
    # Gera novo ID
    new_id = str(max(int(k) for k in MOCK_INVOICES_DB.keys()) + 1)
    invoice_data["id"] = new_id
    
    # Adiciona ao DB
    MOCK_INVOICES_DB[new_id] = invoice_data
    
    return new_id

def get_all_invoice_ids() -> list[str]:
    """
    Retorna lista com todos os IDs de NFs disponíveis.
    
    Returns:
        Lista de IDs
    """
    return list(MOCK_INVOICES_DB.keys())