# agents/audit_agent/rules_engine.py
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

def run_financial_rules(invoice_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Executa um conjunto de regras financeiras determinísticas (Validação Tríplice).
    Esta função é chamada ANTES do agente LLM para verificar a integridade
    dos valores da nota.

    Args:
        invoice_data: O dicionário completo da nota fiscal,
                      contendo dados da nota e uma lista de itens.

    Returns:
        Um dicionário com o resultado da validação.
    """
    logger.info("Executando regras financeiras determinísticas (Validação Tríplice)...")
    
    try:
        # 1. Extrair dados da Nota (Cabeçalho)
        # Chave retirada do csv de validacao "202505_NFe_NotaFisca.csv" disponibilizado no drive do curso
        valor_total_nota = float(invoice_data.get("ValorTotalNota", 0.0))
        valor_desconto = float(invoice_data.get("ValorDesconto", 0.0))
        
        # Soma dos impostos do cabeçalho
        impostos_nota = sum([
            float(invoice_data.get("ValorICMS", 0.0)),
            float(invoice_data.get("ValorIPI", 0.0)),
            float(invoice_data.get("ValorPIS", 0.0)),
            float(invoice_data.get("ValorCOFINS", 0.0))
        ])

        # 2. Extrair dados dos Itens
        items_list = invoice_data.get("items", [])
        if not items_list:
            logger.warning("Nenhum item encontrado na nota para validação.")
            return {
                "passed": False,
                "message": "Falha na validação: A nota não contém itens."
            }

        soma_valor_total_itens = 0.0
        for item in items_list:
            # O ValorTotalItem já deve ser (Qtd * Vlr. Unitário)
            soma_valor_total_itens += float(item.get("ValorTotalItem", 0.0))

        # 3. Executar a Validação Tríplice
        # Fórmula: (Soma Itens) + (Soma Impostos) - (Desconto) == Valor Total da Nota
        # (Esta fórmula é uma simplificação comum; ajuste se a regra de negócio for outra)
        
        # Usamos uma tolerância pequena (ex: 0.01) para evitar erros de ponto flutuante
        tolerancia = 0.01 
        
        valor_calculado_nota = (soma_valor_total_itens + impostos_nota) - valor_desconto
        
        diferenca = abs(valor_total_nota - valor_calculado_nota)

        if diferenca <= tolerancia:
            logger.info("SUCESSO: Validação Tríplice aprovada.")
            return {
                "passed": True,
                "message": "Validação Tríplice aprovada.",
                "valor_calculado": round(valor_calculado_nota, 2),
                "valor_declarado": valor_total_nota,
                "diferenca": round(diferenca, 2)
            }
        else:
            logger.warning(f"FALHA: Validação Tríplice reprovada. Diferença: {diferenca}")
            return {
                "passed": False,
                "message": (
                    f"Falha na Validação Tríplice: "
                    f"O valor total da nota ({valor_total_nota}) é incompatível com "
                    f"o valor calculado ({round(valor_calculado_nota, 2)}). "
                    f"Diferença de {round(diferenca, 2)}."
                ),
                "soma_itens": round(soma_valor_total_itens, 2),
                "soma_impostos": round(impostos_nota, 2),
                "desconto": valor_desconto,
                "valor_calculado": round(valor_calculado_nota, 2),
                "valor_declarado": valor_total_nota,
            }

    except Exception as e:
        logger.error(f"Erro ao executar regras financeiras: {e}", exc_info=True)
        return {
            "passed": False,
            "message": f"Erro de sistema ao processar regras financeiras: {e}"
        }