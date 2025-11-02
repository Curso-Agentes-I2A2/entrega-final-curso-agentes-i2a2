# mcp/tools/validation_tools.py

import re

def validate_cnpj_format(cnpj: str) -> bool:
    """Valida o formato de um CNPJ (14 dígitos)."""
    return bool(re.match(r'^\d{14}$', ''.join(filter(str.isdigit, cnpj))))

def validate_cnpj_digits(cnpj: str) -> bool:
    """Valida os dígitos verificadores de um CNPJ."""
    clean_cnpj = ''.join(filter(str.isdigit, cnpj))
    if len(clean_cnpj) != 14:
        return False

    def calculate_digit(digits: str, weights: list) -> int:
        s = sum(int(d) * w for d, w in zip(digits, weights))
        rest = s % 11
        return 0 if rest < 2 else 11 - rest

    # Validação do primeiro dígito
    weights1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    d1 = calculate_digit(clean_cnpj[:12], weights1)
    if d1 != int(clean_cnpj[12]):
        return False

    # Validação do segundo dígito
    weights2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    d2 = calculate_digit(clean_cnpj[:13], weights2)
    return d2 == int(clean_cnpj[13])

def validate_access_key_format(key: str) -> bool:
    """Valida o formato da chave de acesso da NF-e (44 dígitos)."""
    return bool(re.match(r'^\d{44}$', ''.join(filter(str.isdigit, key))))

def validate_access_key_digits(key: str) -> bool:
    """Valida o dígito verificador da chave de acesso da NF-e."""
    clean_key = ''.join(filter(str.isdigit, key))
    if len(clean_key) != 44:
        return False
        
    base_key = clean_key[:43]
    weights = [4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2] * 4
    s = sum(int(d) * w for d, w in zip(base_key, weights))
    rest = s % 11
    
    dv = 0 if rest in [0, 1] else 11 - rest
    return dv == int(clean_key[43])

def validate_cfop(cfop: str, operation_type: str) -> dict:
    """
    Valida um CFOP (Código Fiscal de Operações e Prestações).
    operation_type pode ser 'entrada' ou 'saida'.
    """
    cfop_str = str(cfop)
    if not re.match(r'^[1-7]\d{3}$', cfop_str):
        return {"valid": False, "reason": "Formato inválido. Deve ter 4 dígitos e começar com 1-7."}
    
    first_digit = cfop_str[0]
    is_valid = False
    
    if operation_type == 'entrada':
        if first_digit in ['1', '2', '3']:
            is_valid = True
    elif operation_type == 'saida':
        if first_digit in ['5', '6', '7']:
            is_valid = True
    else:
        return {"valid": False, "reason": f"Tipo de operação '{operation_type}' desconhecido."}

    if not is_valid:
        return {"valid": False, "reason": f"CFOP {cfop} incompatível com operação de '{operation_type}'."}

    # Lógica de validação simplificada (pode ser expandida com tabela de CFOPs)
    cfop_map = {
        '1': "Entrada / Aquisições do Estado",
        '2': "Entrada / Aquisições de Outro Estado",
        '3': "Entrada / Aquisições do Exterior",
        '5': "Saídas / Vendas para o Estado",
        '6': "Saídas / Vendas para Outro Estado",
        '7': "Saídas / Vendas para o Exterior",
    }
    
    return {
        "valid": True,
        "description": cfop_map.get(first_digit, "Descrição não encontrada"),
        "type": "Entrada" if first_digit in "123" else "Saída"
    }
	