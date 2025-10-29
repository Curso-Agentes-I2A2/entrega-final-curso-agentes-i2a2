"""
Motor de Regras Fiscais
Validações rápidas e determinísticas antes da análise com LLM
"""

import re
from typing import Dict, List, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class RulesEngine:
    """
    Motor de regras para validações fiscais rápidas
    
    Responsável por:
    - Validações determinísticas que não requerem LLM
    - Cálculos de impostos
    - Verificação de CFOPs
    - Consistência de valores
    """
    
    # Tabela de CFOPs válidos
    CFOPS_VALIDOS = {
        # Entradas
        "1101": "Compra para industrialização ou produção rural",
        "1102": "Compra para comercialização",
        "1103": "Compra para ativo imobilizado",
        "1201": "Devolução de venda de produção",
        "1202": "Devolução de venda de mercadoria",
        "1203": "Devolução de venda de produção do estabelecimento",
        
        # Saídas Internas (SP)
        "5101": "Venda de produção do estabelecimento",
        "5102": "Venda de mercadoria adquirida ou recebida de terceiros",
        "5103": "Venda de produção do estabelecimento efetuada fora",
        "5104": "Venda de mercadoria adquirida ou recebida de terceiros",
        "5151": "Transferência de produção do estabelecimento",
        "5152": "Transferência de mercadoria adquirida ou recebida de terceiros",
        "5201": "Devolução de compra para industrialização",
        "5202": "Devolução de compra para comercialização",
        "5401": "Venda de produção do estabelecimento em operação com produto sujeito ao regime de substituição tributária",
        "5403": "Venda de mercadoria adquirida ou recebida de terceiros em operação com produto sujeito ao regime de substituição tributária",
        
        # Saídas Interestaduais
        "6101": "Venda de produção do estabelecimento",
        "6102": "Venda de mercadoria adquirida ou recebida de terceiros",
        "6103": "Venda de produção do estabelecimento efetuada fora",
        "6151": "Transferência de produção do estabelecimento",
        "6152": "Transferência de mercadoria adquirida ou recebida de terceiros",
        "6201": "Devolução de compra para industrialização",
        "6202": "Devolução de compra para comercialização",
        
        # Exportação
        "7101": "Venda de produção do estabelecimento",
        "7102": "Venda de mercadoria adquirida ou recebida de terceiros",
    }
    
    # Alíquotas ICMS por estado
    ALIQUOTAS_ICMS = {
        "SP": {
            "padrao": 18.0,
            "reduzida_1": 12.0,
            "reduzida_2": 7.0,
        },
        "RJ": {
            "padrao": 20.0,
            "reduzida": 12.0,
        },
        "MG": {
            "padrao": 18.0,
        }
        # Adicionar outros estados conforme necessário
    }
    
    def __init__(self):
        """
        Inicializa motor de regras
        """
        logger.info("⚙️ Inicializando Motor de Regras")
    
    def check_icms(self, invoice: Dict[str, Any]) -> List[str]:
        """
        Valida cálculo de ICMS
        
        Args:
            invoice: Dados da nota fiscal
        
        Returns:
            Lista de erros encontrados (vazia se tudo OK)
        """
        errors = []
        
        try:
            # Extrair dados
            base_calculo = float(invoice.get("base_calculo_icms", 0))
            aliquota = float(invoice.get("aliquota_icms", 0))
            valor_informado = float(invoice.get("valor_icms", 0))
            estado = invoice.get("estado_emitente", "SP")
            
            # Se não houver base de cálculo, não podemos validar
            if base_calculo == 0:
                return []
            
            # Calcular valor esperado
            valor_esperado = base_calculo * (aliquota / 100)
            
            # Verificar diferença
            diferenca = abs(valor_informado - valor_esperado)
            tolerancia = 0.50  # Tolerância de R$ 0,50 para arredondamento
            
            if diferenca > tolerancia:
                percentual_erro = (diferenca / valor_esperado * 100) if valor_esperado > 0 else 0
                errors.append(
                    f"ICMS calculado incorretamente: esperado R$ {valor_esperado:.2f}, "
                    f"informado R$ {valor_informado:.2f} (diferença de R$ {diferenca:.2f} = {percentual_erro:.1f}%)"
                )
            
            # Validar alíquota
            aliquotas_validas = self.ALIQUOTAS_ICMS.get(estado, {})
            if aliquotas_validas:
                aliquotas_permitidas = list(aliquotas_validas.values())
                if aliquota not in aliquotas_permitidas and aliquota != 0:
                    errors.append(
                        f"Alíquota de ICMS {aliquota}% não é padrão para {estado}. "
                        f"Alíquotas comuns: {aliquotas_permitidas}"
                    )
        
        except (ValueError, TypeError, KeyError) as e:
            logger.warning(f"Erro ao validar ICMS: {e}")
            errors.append(f"Erro ao processar dados de ICMS: campos inválidos ou ausentes")
        
        return errors
    
    def check_cfop(self, cfop: str, operation: str) -> bool:
        """
        Valida se CFOP está correto para o tipo de operação
        
        Args:
            cfop: Código CFOP
            operation: Tipo de operação (compra, venda, transferencia, devolucao)
        
        Returns:
            True se válido, False se inválido
        """
        # Validar formato (4 dígitos)
        if not cfop or not re.match(r'^\d{4}$', cfop):
            logger.warning(f"CFOP inválido: {cfop}")
            return False
        
        # Verificar se CFOP existe na tabela
        if cfop not in self.CFOPS_VALIDOS:
            logger.warning(f"CFOP {cfop} não encontrado na tabela")
            return False
        
        # Validar compatibilidade com operação
        primeiro_digito = cfop[0]
        
        # Mapear operação para primeiro dígito esperado
        operacao_map = {
            "compra": ["1", "2"],  # Entrada
            "venda": ["5", "6", "7"],  # Saída
            "transferencia": ["5", "6"],  # Transferência
            "devolucao": ["1", "2", "5", "6"],  # Pode ser entrada ou saída
        }
        
        digitos_esperados = operacao_map.get(operation.lower(), [])
        
        if digitos_esperados and primeiro_digito not in digitos_esperados:
            logger.warning(
                f"CFOP {cfop} incompatível com operação '{operation}' "
                f"(esperado CFOP iniciando com {digitos_esperados})"
            )
            return False
        
        return True
    
    def check_value_consistency(self, invoice: Dict[str, Any]) -> List[str]:
        """
        Verifica consistência de valores
        
        Args:
            invoice: Dados da nota fiscal
        
        Returns:
            Lista de inconsistências encontradas
        """
        errors = []
        
        try:
            # Valor total dos produtos
            valor_produtos = float(invoice.get("valor_produtos", 0))
            
            # Impostos
            valor_icms = float(invoice.get("valor_icms", 0))
            valor_ipi = float(invoice.get("valor_ipi", 0))
            valor_pis = float(invoice.get("valor_pis", 0))
            valor_cofins = float(invoice.get("valor_cofins", 0))
            
            # Descontos
            valor_desconto = float(invoice.get("valor_desconto", 0))
            
            # Valor total informado
            valor_total_informado = float(invoice.get("valor_total", 0))
            
            # Calcular valor total esperado
            # Nota: ICMS geralmente já está incluído no valor dos produtos
            # IPI é adicionado
            valor_total_esperado = (
                valor_produtos +
                valor_ipi +
                # ICMS não é adicionado pois já está incluído
                0 -
                valor_desconto
            )
            
            # Verificar diferença
            diferenca = abs(valor_total_informado - valor_total_esperado)
            tolerancia = 0.10  # Tolerância de R$ 0,10
            
            if diferenca > tolerancia:
                errors.append(
                    f"Valor total inconsistente: esperado R$ {valor_total_esperado:.2f}, "
                    f"informado R$ {valor_total_informado:.2f} (diferença R$ {diferenca:.2f})"
                )
            
            # Validar valores negativos
            if valor_produtos < 0:
                errors.append("Valor de produtos não pode ser negativo")
            
            if valor_total_informado < 0:
                errors.append("Valor total não pode ser negativo")
            
            # Validar se impostos fazem sentido em relação ao valor
            if valor_icms > valor_produtos:
                errors.append(
                    f"Valor de ICMS (R$ {valor_icms:.2f}) maior que valor dos produtos "
                    f"(R$ {valor_produtos:.2f}), o que é improvável"
                )
        
        except (ValueError, TypeError, KeyError) as e:
            logger.warning(f"Erro ao validar consistência de valores: {e}")
            errors.append("Erro ao processar valores: campos inválidos ou ausentes")
        
        return errors
    
    def validate_cnpj(self, cnpj: str) -> bool:
        """
        Valida CNPJ (dígitos verificadores)
        
        Args:
            cnpj: CNPJ para validar (com ou sem formatação)
        
        Returns:
            True se válido, False se inválido
        """
        # Remover caracteres não numéricos
        cnpj = re.sub(r'[^0-9]', '', cnpj)
        
        # Verificar se tem 14 dígitos
        if len(cnpj) != 14:
            return False
        
        # Verificar se não é sequência repetida (ex: 00000000000000)
        if cnpj == cnpj[0] * 14:
            return False
        
        # Calcular primeiro dígito verificador
        soma = 0
        peso = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        
        for i in range(12):
            soma += int(cnpj[i]) * peso[i]
        
        resto = soma % 11
        digito1 = 0 if resto < 2 else 11 - resto
        
        if int(cnpj[12]) != digito1:
            return False
        
        # Calcular segundo dígito verificador
        soma = 0
        peso = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        
        for i in range(13):
            soma += int(cnpj[i]) * peso[i]
        
        resto = soma % 11
        digito2 = 0 if resto < 2 else 11 - resto
        
        if int(cnpj[13]) != digito2:
            return False
        
        return True
    
    def validate_date(self, date_str: str) -> bool:
        """
        Valida data de emissão
        
        Args:
            date_str: Data no formato YYYY-MM-DD ou DD/MM/YYYY
        
        Returns:
            True se válida, False se inválida
        """
        try:
            # Tentar formato ISO
            if '-' in date_str:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            else:
                date_obj = datetime.strptime(date_str, "%d/%m/%Y")
            
            # Verificar se data não é futura
            if date_obj > datetime.now():
                return False
            
            # Verificar se não é muito antiga (> 60 dias)
            dias_atras = (datetime.now() - date_obj).days
            if dias_atras > 60:
                logger.warning(f"Data de emissão muito antiga: {dias_atras} dias")
                # Retornar True mas com warning (não é erro crítico)
            
            return True
        
        except ValueError:
            return False
    
    def calculate_icms(
        self,
        base_calculo: float,
        aliquota: float
    ) -> Dict[str, float]:
        """
        Calcula ICMS
        
        Args:
            base_calculo: Base de cálculo
            aliquota: Alíquota em percentual (ex: 18 para 18%)
        
        Returns:
            Dict com valor e detalhes
        """
        valor = base_calculo * (aliquota / 100)
        
        return {
            "base_calculo": round(base_calculo, 2),
            "aliquota": aliquota,
            "valor": round(valor, 2),
        }
    
    def calculate_ipi(
        self,
        base_calculo: float,
        aliquota: float
    ) -> Dict[str, float]:
        """
        Calcula IPI
        """
        valor = base_calculo * (aliquota / 100)
        
        return {
            "base_calculo": round(base_calculo, 2),
            "aliquota": aliquota,
            "valor": round(valor, 2),
        }
    
    def calculate_pis_cofins(
        self,
        base_calculo: float,
        regime: str = "nao_cumulativo"
    ) -> Dict[str, Any]:
        """
        Calcula PIS e COFINS
        
        Args:
            base_calculo: Base de cálculo
            regime: "cumulativo" ou "nao_cumulativo"
        
        Returns:
            Dict com valores de PIS e COFINS
        """
        if regime == "cumulativo":
            aliquota_pis = 0.65
            aliquota_cofins = 3.0
        else:  # não cumulativo
            aliquota_pis = 1.65
            aliquota_cofins = 7.6
        
        valor_pis = base_calculo * (aliquota_pis / 100)
        valor_cofins = base_calculo * (aliquota_cofins / 100)
        
        return {
            "regime": regime,
            "pis": {
                "aliquota": aliquota_pis,
                "valor": round(valor_pis, 2)
            },
            "cofins": {
                "aliquota": aliquota_cofins,
                "valor": round(valor_cofins, 2)
            },
            "total": round(valor_pis + valor_cofins, 2)
        }
    
    def validate_invoice_structure(self, invoice: Dict) -> List[str]:
        """
        Valida estrutura básica da nota fiscal
        
        Args:
            invoice: Dados da nota fiscal
        
        Returns:
            Lista de erros estruturais
        """
        errors = []
        
        # Campos obrigatórios
        required_fields = [
            "numero",
            "cnpj_emitente",
            "cnpj_destinatario",
            "data_emissao",
            "cfop",
            "valor_total"
        ]
        
        for field in required_fields:
            if field not in invoice or not invoice[field]:
                errors.append(f"Campo obrigatório ausente: {field}")
        
        # Validar CNPJs
        if "cnpj_emitente" in invoice:
            if not self.validate_cnpj(str(invoice["cnpj_emitente"])):
                errors.append("CNPJ do emitente inválido")
        
        if "cnpj_destinatario" in invoice:
            if not self.validate_cnpj(str(invoice["cnpj_destinatario"])):
                errors.append("CNPJ do destinatário inválido")
        
        # Validar data
        if "data_emissao" in invoice:
            if not self.validate_date(str(invoice["data_emissao"])):
                errors.append("Data de emissão inválida")
        
        return errors


# ========================================================================
# EXPORT
# ========================================================================

__all__ = ["RulesEngine"]