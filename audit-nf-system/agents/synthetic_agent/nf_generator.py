"""
NF Generator - Gerador de Notas Fiscais Sintéticas
Para testes e desenvolvimento
"""

import random
import string
from datetime import datetime, timedelta
from typing import Dict, Any


def generate_cnpj() -> str:
    """
    Gera CNPJ válido aleatório
    """
    # Gerar 12 primeiros dígitos
    cnpj = [random.randint(0, 9) for _ in range(12)]
    
    # Calcular primeiro dígito verificador
    peso = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma = sum(cnpj[i] * peso[i] for i in range(12))
    resto = soma % 11
    dv1 = 0 if resto < 2 else 11 - resto
    cnpj.append(dv1)
    
    # Calcular segundo dígito verificador
    peso = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma = sum(cnpj[i] * peso[i] for i in range(13))
    resto = soma % 11
    dv2 = 0 if resto < 2 else 11 - resto
    cnpj.append(dv2)
    
    return ''.join(str(d) for d in cnpj)


def generate_access_key(
    uf: str = "35",  # São Paulo
    ano_mes: str = None,
    cnpj: str = None,
    modelo: str = "55",  # NF-e
    serie: str = "001",
    numero: str = None
) -> str:
    """
    Gera chave de acesso válida
    
    Formato: UF(2) + AAMM(4) + CNPJ(14) + Modelo(2) + Serie(3) + Numero(9) + Tipo(1) + Codigo(8) + DV(1)
    """
    if ano_mes is None:
        now = datetime.now()
        ano_mes = now.strftime("%y%m")
    
    if cnpj is None:
        cnpj = generate_cnpj()
    
    if numero is None:
        numero = str(random.randint(1, 999999999)).zfill(9)
    
    tipo_emissao = "1"  # Normal
    codigo_numerico = ''.join(random.choices(string.digits, k=8))
    
    # Montar chave sem DV
    chave_sem_dv = (
        uf +
        ano_mes +
        cnpj +
        modelo +
        serie +
        numero +
        tipo_emissao +
        codigo_numerico
    )
    
    # Calcular DV
    dv = calculate_access_key_digit(chave_sem_dv)
    
    return chave_sem_dv + str(dv)


def calculate_access_key_digit(key: str) -> int:
    """
    Calcula dígito verificador da chave de acesso
    """
    peso = list(range(2, 10)) * 6
    soma = sum(int(key[i]) * peso[i % len(peso)] for i in range(len(key)))
    resto = soma % 11
    return 0 if resto in [0, 1] else 11 - resto


def generate_valid_invoice(
    max_value: float = 10000.0,
    state: str = "SP"
) -> Dict[str, Any]:
    """
    Gera nota fiscal completamente válida
    """
    # CNPJs
    cnpj_emitente = generate_cnpj()
    cnpj_destinatario = generate_cnpj()
    
    # Número e série
    numero = str(random.randint(1, 999999)).zfill(6)
    serie = "1"
    
    # Data de emissão (últimos 30 dias)
    dias_atras = random.randint(0, 30)
    data_emissao = (datetime.now() - timedelta(days=dias_atras)).strftime("%Y-%m-%d")
    
    # CFOP válido para venda
    cfops_validos = ["5101", "5102", "5103"]
    cfop = random.choice(cfops_validos)
    
    # Valores
    valor_produtos = round(random.uniform(100, max_value), 2)
    
    # ICMS (18% padrão SP)
    base_calculo_icms = valor_produtos
    aliquota_icms = 18.0
    valor_icms = round(base_calculo_icms * (aliquota_icms / 100), 2)
    
    # IPI (10%)
    aliquota_ipi = 10.0
    valor_ipi = round(valor_produtos * (aliquota_ipi / 100), 2)
    
    # PIS/COFINS (regime não cumulativo)
    valor_pis = round(valor_produtos * 0.0165, 2)
    valor_cofins = round(valor_produtos * 0.076, 2)
    
    # Valor total
    valor_total = valor_produtos + valor_ipi
    
    # Chave de acesso
    chave_acesso = generate_access_key(
        uf="35" if state == "SP" else "33",
        cnpj=cnpj_emitente,
        numero=numero
    )
    
    return {
        "numero": numero,
        "serie": serie,
        "data_emissao": data_emissao,
        "cnpj_emitente": cnpj_emitente,
        "razao_social_emitente": f"Empresa {random.randint(1000, 9999)} LTDA",
        "cnpj_destinatario": cnpj_destinatario,
        "razao_social_destinatario": f"Cliente {random.randint(1000, 9999)} SA",
        "cfop": cfop,
        "tipo_operacao": "venda",
        "valor_produtos": valor_produtos,
        "valor_total": valor_total,
        "base_calculo_icms": base_calculo_icms,
        "aliquota_icms": aliquota_icms,
        "valor_icms": valor_icms,
        "aliquota_ipi": aliquota_ipi,
        "valor_ipi": valor_ipi,
        "valor_pis": valor_pis,
        "valor_cofins": valor_cofins,
        "chave_acesso": chave_acesso,
        "estado_emitente": state,
    }


def generate_invalid_invoice(
    max_value: float = 10000.0,
    state: str = "SP",
    error_type: str = "random"
) -> Dict[str, Any]:
    """
    Gera nota fiscal com erros propositais
    
    Args:
        error_type: tipo de erro ('cfop', 'icms', 'cnpj', 'random')
    """
    # Começar com nota válida
    invoice = generate_valid_invoice(max_value, state)
    
    # Escolher tipo de erro se random
    if error_type == "random":
        error_type = random.choice(["cfop", "icms", "cnpj", "valor"])
    
    # Injetar erro específico
    if error_type == "cfop":
        # CFOP inválido
        invoice["cfop"] = "9999"
    
    elif error_type == "icms":
        # ICMS calculado errado
        invoice["valor_icms"] = round(invoice["valor_icms"] * 0.7, 2)  # 30% a menos
    
    elif error_type == "cnpj":
        # CNPJ inválido
        invoice["cnpj_destinatario"] = "00000000000000"
    
    elif error_type == "valor":
        # Valor total inconsistente
        invoice["valor_total"] = round(invoice["valor_total"] * 1.5, 2)
    
    return invoice


def generate_suspicious_invoice(
    max_value: float = 10000.0,
    state: str = "SP"
) -> Dict[str, Any]:
    """
    Gera nota fiscal válida mas com padrões suspeitos
    """
    invoice = generate_valid_invoice(max_value, state)
    
    # Escolher padrão suspeito
    pattern = random.choice(["round_value", "high_value", "old_date"])
    
    if pattern == "round_value":
        # Valores muito redondos
        invoice["valor_produtos"] = 10000.00
        invoice["valor_icms"] = 1800.00
        invoice["valor_total"] = 11000.00
    
    elif pattern == "high_value":
        # Valor muito alto
        invoice["valor_produtos"] = 999999.99
        invoice["valor_icms"] = round(invoice["valor_produtos"] * 0.18, 2)
        invoice["valor_total"] = invoice["valor_produtos"] + invoice["valor_icms"]
    
    elif pattern == "old_date":
        # Data de emissão antiga
        invoice["data_emissao"] = (datetime.now() - timedelta(days=55)).strftime("%Y-%m-%d")
    
    return invoice


# ========================================================================
# FUNÇÕES AUXILIARES
# ========================================================================

def format_cnpj(cnpj: str) -> str:
    """
    Formata CNPJ: 12.345.678/0001-90
    """
    return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:14]}"


def format_access_key(key: str) -> str:
    """
    Formata chave de acesso com espaços
    """
    return ' '.join(key[i:i+4] for i in range(0, len(key), 4))
