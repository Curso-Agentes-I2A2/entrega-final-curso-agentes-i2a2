"""
Regras fiscais e tributárias para validação de NF-e.

Define constantes e funções para validação de acordo com legislação brasileira.
"""
from typing import Dict, List, Tuple
from decimal import Decimal
import re


class NFeFiscalRules:
    """
    Regras fiscais para validação de Notas Fiscais Eletrônicas.
    
    Baseado na legislação brasileira e padrões da SEFAZ.
    """
    
    # Alíquotas de ICMS por estado (interestadual)
    ICMS_ALIQUOTAS_INTERESTADUAIS = {
        ('AC', 'outros'): Decimal('12'),
        ('AL', 'outros'): Decimal('12'),
        ('AM', 'outros'): Decimal('12'),
        ('AP', 'outros'): Decimal('12'),
        ('BA', 'outros'): Decimal('12'),
        ('CE', 'outros'): Decimal('12'),
        ('DF', 'outros'): Decimal('12'),
        ('ES', 'outros'): Decimal('12'),
        ('GO', 'outros'): Decimal('12'),
        ('MA', 'outros'): Decimal('12'),
        ('MG', 'sul_sudeste'): Decimal('12'),
        ('MS', 'outros'): Decimal('12'),
        ('MT', 'outros'): Decimal('12'),
        ('PA', 'outros'): Decimal('12'),
        ('PB', 'outros'): Decimal('12'),
        ('PE', 'outros'): Decimal('12'),
        ('PI', 'outros'): Decimal('12'),
        ('PR', 'sul_sudeste'): Decimal('12'),
        ('RJ', 'sul_sudeste'): Decimal('12'),
        ('RN', 'outros'): Decimal('12'),
        ('RO', 'outros'): Decimal('12'),
        ('RR', 'outros'): Decimal('12'),
        ('RS', 'sul_sudeste'): Decimal('12'),
        ('SC', 'sul_sudeste'): Decimal('12'),
        ('SE', 'outros'): Decimal('12'),
        ('SP', 'sul_sudeste'): Decimal('12'),
        ('TO', 'outros'): Decimal('12'),
    }
    
    # Alíquotas padrão de ICMS internas por estado
    ICMS_ALIQUOTAS_INTERNAS = {
        'AC': Decimal('17'),
        'AL': Decimal('18'),
        'AM': Decimal('18'),
        'AP': Decimal('18'),
        'BA': Decimal('18'),
        'CE': Decimal('18'),
        'DF': Decimal('18'),
        'ES': Decimal('17'),
        'GO': Decimal('17'),
        'MA': Decimal('18'),
        'MG': Decimal('18'),
        'MS': Decimal('17'),
        'MT': Decimal('17'),
        'PA': Decimal('17'),
        'PB': Decimal('18'),
        'PE': Decimal('18'),
        'PI': Decimal('18'),
        'PR': Decimal('18'),
        'RJ': Decimal('18'),
        'RN': Decimal('18'),
        'RO': Decimal('17.5'),
        'RR': Decimal('17'),
        'RS': Decimal('18'),
        'SC': Decimal('17'),
        'SE': Decimal('18'),
        'SP': Decimal('18'),
        'TO': Decimal('18'),
    }
    
    # Alíquotas de IPI (algumas categorias comuns)
    IPI_ALIQUOTAS = {
        'bebidas': Decimal('10'),
        'cigarros': Decimal('300'),
        'cosmeticos': Decimal('15'),
        'eletronicos': Decimal('10'),
        'automoveis': Decimal('25'),
        'isento': Decimal('0'),
    }
    
    # Alíquotas de PIS e COFINS
    PIS_ALIQUOTA = Decimal('1.65')
    COFINS_ALIQUOTA = Decimal('7.60')
    
    # Margem de tolerância para cálculos (em reais)
    MARGEM_TOLERANCIA = Decimal('0.10')
    
    @staticmethod
    def validar_chave_acesso(chave: str) -> Tuple[bool, str]:
        """
        Valida chave de acesso da NF-e.
        
        Regras:
        - 44 dígitos numéricos
        - Dígito verificador válido (módulo 11)
        
        Args:
            chave: Chave de acesso de 44 dígitos
        
        Returns:
            Tuple[bool, str]: (válido, mensagem)
        """
        # Verifica tamanho
        if len(chave) != 44:
            return False, f"Chave deve ter 44 dígitos, encontrado {len(chave)}"
        
        # Verifica se é numérico
        if not chave.isdigit():
            return False, "Chave deve conter apenas números"
        
        # Valida dígito verificador (módulo 11)
        dv_informado = int(chave[-1])
        dv_calculado = NFeFiscalRules._calcular_dv_modulo11(chave[:43])
        
        if dv_informado != dv_calculado:
            return False, f"Dígito verificador inválido. Esperado: {dv_calculado}, Informado: {dv_informado}"
        
        return True, "Chave de acesso válida"
    
    @staticmethod
    def _calcular_dv_modulo11(numero: str) -> int:
        """
        Calcula dígito verificador usando módulo 11.
        
        Args:
            numero: String numérica de 43 dígitos
        
        Returns:
            Dígito verificador (0-9)
        """
        multiplicadores = [4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        
        soma = sum(int(d) * m for d, m in zip(numero, multiplicadores))
        resto = soma % 11
        
        if resto in (0, 1):
            return 0
        else:
            return 11 - resto
    
    @staticmethod
    def validar_cnpj(cnpj: str) -> Tuple[bool, str]:
        """
        Valida CNPJ brasileiro.
        
        Args:
            cnpj: CNPJ com 14 dígitos
        
        Returns:
            Tuple[bool, str]: (válido, mensagem)
        """
        # Remove caracteres não numéricos
        cnpj = re.sub(r'\D', '', cnpj)
        
        # Verifica tamanho
        if len(cnpj) != 14:
            return False, f"CNPJ deve ter 14 dígitos, encontrado {len(cnpj)}"
        
        # Verifica se todos os dígitos são iguais
        if cnpj == cnpj[0] * 14:
            return False, "CNPJ inválido (dígitos repetidos)"
        
        # Calcula primeiro dígito verificador
        multiplicadores1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        soma1 = sum(int(d) * m for d, m in zip(cnpj[:12], multiplicadores1))
        dv1 = 0 if soma1 % 11 < 2 else 11 - (soma1 % 11)
        
        # Calcula segundo dígito verificador
        multiplicadores2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        soma2 = sum(int(d) * m for d, m in zip(cnpj[:13], multiplicadores2))
        dv2 = 0 if soma2 % 11 < 2 else 11 - (soma2 % 11)
        
        # Verifica dígitos verificadores
        if int(cnpj[12]) != dv1 or int(cnpj[13]) != dv2:
            return False, "Dígitos verificadores do CNPJ inválidos"
        
        return True, "CNPJ válido"
    
    @staticmethod
    def validar_valores_nfe(
        valor_produtos: Decimal,
        valor_icms: Decimal,
        valor_ipi: Decimal,
        valor_total: Decimal,
        valor_frete: Decimal = Decimal('0'),
        valor_seguro: Decimal = Decimal('0'),
        valor_desconto: Decimal = Decimal('0'),
        valor_outras_despesas: Decimal = Decimal('0')
    ) -> Tuple[bool, List[str]]:
        """
        Valida se os valores da NF-e estão matematicamente corretos.
        
        Fórmula: Total = Produtos + IPI + Frete + Seguro + Outras - Desconto
        
        Args:
            valor_produtos: Valor total dos produtos
            valor_icms: Valor do ICMS (informativo, não soma no total)
            valor_ipi: Valor do IPI
            valor_total: Valor total da NF-e
            valor_frete: Valor do frete
            valor_seguro: Valor do seguro
            valor_desconto: Valor do desconto
            valor_outras_despesas: Outras despesas acessórias
        
        Returns:
            Tuple[bool, List[str]]: (válido, lista de inconsistências)
        """
        inconsistencias = []
        
        # Calcula valor esperado
        total_esperado = (
            valor_produtos +
            valor_ipi +
            valor_frete +
            valor_seguro +
            valor_outras_despesas -
            valor_desconto
        )
        
        # Verifica se o total bate
        diferenca = abs(total_esperado - valor_total)
        
        if diferenca > NFeFiscalRules.MARGEM_TOLERANCIA:
            inconsistencias.append(
                f"Divergência no valor total: Esperado R$ {total_esperado:.2f}, "
                f"Informado R$ {valor_total:.2f} (Diferença: R$ {diferenca:.2f})"
            )
        
        # Verifica se valores são positivos
        if valor_produtos < 0:
            inconsistencias.append("Valor de produtos não pode ser negativo")
        
        if valor_total < 0:
            inconsistencias.append("Valor total não pode ser negativo")
        
        # Verifica se ICMS está dentro do range esperado
        if valor_icms > valor_produtos:
            inconsistencias.append(
                f"Valor de ICMS (R$ {valor_icms:.2f}) maior que valor dos produtos "
                f"(R$ {valor_produtos:.2f})"
            )
        
        return len(inconsistencias) == 0, inconsistencias
    
    @staticmethod
    def verificar_aliquota_icms(
        valor_base: Decimal,
        valor_icms: Decimal,
        uf_origem: str,
        uf_destino: str
    ) -> Tuple[bool, str, Decimal]:
        """
        Verifica se alíquota de ICMS está correta.
        
        Args:
            valor_base: Base de cálculo do ICMS
            valor_icms: Valor do ICMS calculado
            uf_origem: UF do emitente
            uf_destino: UF do destinatário
        
        Returns:
            Tuple[bool, str, Decimal]: (correto, mensagem, alíquota calculada)
        """
        if valor_base == 0:
            return True, "Base de cálculo zerada", Decimal('0')
        
        # Calcula alíquota informada
        aliquota_informada = (valor_icms / valor_base) * 100
        
        # Determina alíquota esperada
        if uf_origem == uf_destino:
            # Operação interna
            aliquota_esperada = NFeFiscalRules.ICMS_ALIQUOTAS_INTERNAS.get(
                uf_origem,
                Decimal('18')  # Padrão
            )
        else:
            # Operação interestadual (12% ou 4% para alguns casos)
            aliquota_esperada = Decimal('12')
        
        # Verifica se está dentro da margem
        diferenca = abs(aliquota_informada - aliquota_esperada)
        
        if diferenca > Decimal('0.5'):  # Margem de 0.5%
            return (
                False,
                f"Alíquota de ICMS suspeita: {aliquota_informada:.2f}% "
                f"(esperado ~{aliquota_esperada:.2f}%)",
                aliquota_informada
            )
        
        return True, "Alíquota de ICMS dentro do esperado", aliquota_informada
    
    @staticmethod
    def listar_irregularidades_comuns() -> List[Dict[str, str]]:
        """
        Retorna lista de irregularidades fiscais comuns.
        
        Returns:
            Lista de dicionários com tipo e descrição
        """
        return [
            {
                "tipo": "divergencia_valores",
                "descricao": "Soma dos valores não confere com total da NF-e",
                "gravidade": "alta"
            },
            {
                "tipo": "chave_acesso_invalida",
                "descricao": "Chave de acesso com dígito verificador incorreto",
                "gravidade": "alta"
            },
            {
                "tipo": "cnpj_invalido",
                "descricao": "CNPJ do emitente ou destinatário inválido",
                "gravidade": "alta"
            },
            {
                "tipo": "aliquota_icms_incorreta",
                "descricao": "Alíquota de ICMS fora do padrão estadual",
                "gravidade": "média"
            },
            {
                "tipo": "data_retroativa",
                "descricao": "Data de emissão muito antiga sem justificativa",
                "gravidade": "média"
            },
            {
                "tipo": "valor_zerado",
                "descricao": "Nota fiscal com valor total zerado",
                "gravidade": "alta"
            },
            {
                "tipo": "impostos_zerados",
                "descricao": "Impostos zerados sem indicação de isenção",
                "gravidade": "baixa"
            },
            {
                "tipo": "cfop_incompativel",
                "descricao": "CFOP incompatível com natureza da operação",
                "gravidade": "média"
            }
        ]