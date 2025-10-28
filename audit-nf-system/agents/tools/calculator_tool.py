"""
Tax Calculator Tool - Calculadora de Impostos
Realiza cálculos de ICMS, IPI, PIS e COFINS
"""

import logging
from typing import Dict, Any
from langchain.tools import BaseTool
from pydantic import Field

logger = logging.getLogger(__name__)


class TaxCalculatorTool(BaseTool):
    """
    Tool para calcular impostos brasileiros
    
    Calcula:
    - ICMS (Imposto sobre Circulação de Mercadorias e Serviços)
    - IPI (Imposto sobre Produtos Industrializados)
    - PIS (Programa de Integração Social)
    - COFINS (Contribuição para Financiamento da Seguridade Social)
    """
    
    name: str = "calculate_taxes"
    description: str = (
        "Calcula impostos brasileiros (ICMS, IPI, PIS, COFINS). "
        "Use para validar cálculos de impostos informados na nota fiscal.\n\n"
        "Entrada (JSON string): "
        "{\n"
        '  "base_value": 1000.00,\n'
        '  "state": "SP",\n'
        '  "tax_regime": "nao_cumulativo",\n'
        '  "product_type": "normal"\n'
        "}\n\n"
        "Saída: Breakdown detalhado de todos os impostos."
    )
    
    def _run(self, input_str: str) -> str:
        """
        Calcula impostos
        
        Args:
            input_str: JSON string com parâmetros
        
        Returns:
            String com breakdown de impostos
        """
        import json
        
        try:
            # Parsear input
            params = json.loads(input_str)
            
            base_value = float(params.get("base_value", 0))
            state = params.get("state", "SP")
            tax_regime = params.get("tax_regime", "nao_cumulativo")
            product_type = params.get("product_type", "normal")
            
            # Calcular impostos
            result = self._calculate_all_taxes(
                base_value=base_value,
                state=state,
                tax_regime=tax_regime,
                product_type=product_type
            )
            
            return json.dumps(result, indent=2, ensure_ascii=False)
        
        except Exception as e:
            logger.error(f"Erro ao calcular impostos: {e}")
            return json.dumps({"error": str(e)})
    
    async def _arun(self, input_str: str) -> str:
        """
        Versão assíncrona (apenas chama a síncrona)
        """
        return self._run(input_str)
    
    def _calculate_all_taxes(
        self,
        base_value: float,
        state: str,
        tax_regime: str,
        product_type: str
    ) -> Dict[str, Any]:
        """
        Calcula todos os impostos
        """
        logger.info(f"💰 Calculando impostos: Base R$ {base_value} - Estado {state}")
        
        # Calcular ICMS
        icms = self._calculate_icms(base_value, state, product_type)
        
        # Calcular IPI
        ipi = self._calculate_ipi(base_value, product_type)
        
        # Calcular PIS/COFINS
        pis_cofins = self._calculate_pis_cofins(base_value, tax_regime)
        
        # Total de impostos
        total_taxes = (
            icms["valor"] +
            ipi["valor"] +
            pis_cofins["pis"]["valor"] +
            pis_cofins["cofins"]["valor"]
        )
        
        # Valor final
        final_value = base_value + ipi["valor"]  # IPI é "por fora"
        
        return {
            "base_value": round(base_value, 2),
            "state": state,
            "tax_regime": tax_regime,
            "product_type": product_type,
            "icms": icms,
            "ipi": ipi,
            "pis": pis_cofins["pis"],
            "cofins": pis_cofins["cofins"],
            "total_taxes": round(total_taxes, 2),
            "final_value": round(final_value, 2),
            "effective_rate": round((total_taxes / base_value * 100), 2) if base_value > 0 else 0,
            "breakdown_summary": (
                f"Base: R$ {base_value:.2f} | "
                f"ICMS: R$ {icms['valor']:.2f} | "
                f"IPI: R$ {ipi['valor']:.2f} | "
                f"PIS: R$ {pis_cofins['pis']['valor']:.2f} | "
                f"COFINS: R$ {pis_cofins['cofins']['valor']:.2f} | "
                f"Total Impostos: R$ {total_taxes:.2f}"
            )
        }
    
    def _calculate_icms(
        self,
        base_value: float,
        state: str,
        product_type: str
    ) -> Dict[str, Any]:
        """
        Calcula ICMS
        """
        # Alíquotas por estado
        aliquotas = {
            "SP": {
                "normal": 18.0,
                "cesta_basica": 7.0,
                "reduzida": 12.0,
                "isento": 0.0
            },
            "RJ": {
                "normal": 20.0,
                "reduzida": 12.0,
                "isento": 0.0
            },
            "MG": {
                "normal": 18.0,
                "isento": 0.0
            }
        }
        
        # Obter alíquota
        state_rates = aliquotas.get(state, {"normal": 18.0})
        aliquota = state_rates.get(product_type, state_rates.get("normal", 18.0))
        
        # Calcular
        valor = base_value * (aliquota / 100)
        
        return {
            "aliquota": aliquota,
            "base_calculo": round(base_value, 2),
            "valor": round(valor, 2),
            "formula": f"{base_value:.2f} × {aliquota}% = {valor:.2f}"
        }
    
    def _calculate_ipi(
        self,
        base_value: float,
        product_type: str
    ) -> Dict[str, Any]:
        """
        Calcula IPI
        
        Nota: Alíquota real depende do NCM, aqui usamos valores típicos
        """
        # Alíquotas típicas por tipo de produto (simplificado)
        aliquotas = {
            "normal": 10.0,
            "isento": 0.0,
            "reduzida": 5.0,
            "cesta_basica": 0.0
        }
        
        aliquota = aliquotas.get(product_type, 10.0)
        valor = base_value * (aliquota / 100)
        
        return {
            "aliquota": aliquota,
            "base_calculo": round(base_value, 2),
            "valor": round(valor, 2),
            "formula": f"{base_value:.2f} × {aliquota}% = {valor:.2f}",
            "nota": "IPI é calculado 'por fora' (soma-se ao valor do produto)"
        }
    
    def _calculate_pis_cofins(
        self,
        base_value: float,
        tax_regime: str
    ) -> Dict[str, Any]:
        """
        Calcula PIS e COFINS
        """
        if tax_regime == "cumulativo":
            aliquota_pis = 0.65
            aliquota_cofins = 3.0
        else:  # não cumulativo
            aliquota_pis = 1.65
            aliquota_cofins = 7.6
        
        valor_pis = base_value * (aliquota_pis / 100)
        valor_cofins = base_value * (aliquota_cofins / 100)
        
        return {
            "regime": tax_regime,
            "pis": {
                "aliquota": aliquota_pis,
                "base_calculo": round(base_value, 2),
                "valor": round(valor_pis, 2),
                "formula": f"{base_value:.2f} × {aliquota_pis}% = {valor_pis:.2f}"
            },
            "cofins": {
                "aliquota": aliquota_cofins,
                "base_calculo": round(base_value, 2),
                "valor": round(valor_cofins, 2),
                "formula": f"{base_value:.2f} × {aliquota_cofins}% = {valor_cofins:.2f}"
            }
        }


# Criar instância global para uso fácil
tax_calculator = TaxCalculatorTool()
