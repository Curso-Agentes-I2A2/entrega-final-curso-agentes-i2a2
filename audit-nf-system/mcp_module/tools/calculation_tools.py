# mcp/tools/calculation_tools.py

from typing import Dict, Union

# Tabelas simplificadas de alíquotas (exemplo)
ICMS_RATES = {
    "SP": 0.18, "RJ": 0.20, "MG": 0.18, "RS": 0.17,
    "SC": 0.17, "PR": 0.19, "BA": 0.19, "PE": 0.18,
    "DEFAULT": 0.17,
}

PIS_COFINS_RATES = {
    "cumulativo": {"pis": 0.0065, "cofins": 0.03},
    "nao_cumulativo": {"pis": 0.0165, "cofins": 0.076},
}

def calculate_icms(base_value: float, state_uf: str) -> Dict[str, Union[float, str]]:
    """Calcula o ICMS com base no valor e estado."""
    aliquota = ICMS_RATES.get(state_uf.upper(), ICMS_RATES["DEFAULT"])
    icms_value = base_value * aliquota
    return {
        "base_value": base_value,
        "state": state_uf.upper(),
        "aliquota": aliquota,
        "icms_value": round(icms_value, 2)
    }

def calculate_ipi(base_value: float, ncm: str) -> Dict[str, Union[float, str]]:
    """
    Calcula o IPI (Imposto sobre Produtos Industrializados).
    A lógica real depende de uma tabela TIPI complexa. Aqui, usamos um mock.
    """
    # Mock: alíquotas de IPI baseadas no NCM (exemplo simplificado)
    ipi_aliquota = 0.0
    if ncm.startswith("8703"): # Automóveis
        ipi_aliquota = 0.25
    elif ncm.startswith("2204"): # Vinhos
        ipi_aliquota = 0.10
    
    ipi_value = base_value * ipi_aliquota
    return {
        "base_value": base_value,
        "ncm": ncm,
        "aliquota": ipi_aliquota,
        "ipi_value": round(ipi_value, 2)
    }

def calculate_pis_cofins(base_value: float, regime: str) -> Dict[str, Union[float, str]]:
    """
    Calcula PIS e COFINS com base no regime tributário.
    Regime pode ser 'cumulativo' ou 'nao_cumulativo'.
    """
    regime_lower = regime.lower()
    if regime_lower not in PIS_COFINS_RATES:
        raise ValueError("Regime tributário inválido. Use 'cumulativo' ou 'nao_cumulativo'.")
        
    rates = PIS_COFINS_RATES[regime_lower]
    pis_value = base_value * rates["pis"]
    cofins_value = base_value * rates["cofins"]
    
    return {
        "base_value": base_value,
        "regime": regime,
        "pis_aliquota": rates["pis"],
        "cofins_aliquota": rates["cofins"],
        "pis_value": round(pis_value, 2),
        "cofins_value": round(cofins_value, 2),
        "total_pis_cofins": round(pis_value + cofins_value, 2)
    }

def apply_tax_reduction(value: float, reduction_percent: float) -> float:
    """Aplica uma redução percentual a um valor."""
    if not 0 <= reduction_percent <= 100:
        raise ValueError("A porcentagem de redução deve estar entre 0 e 100.")
    
    final_value = value * (1 - (reduction_percent / 100))
    return round(final_value, 2)
