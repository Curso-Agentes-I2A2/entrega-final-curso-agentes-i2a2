"""
Validador de Notas Fiscais usando regras fiscais.
"""
from typing import Dict, List, Any
from datetime import datetime, timedelta
from decimal import Decimal
import logging

from models.invoice import Invoice
from src.validation.rules import NFeFiscalRules

logger = logging.getLogger(__name__)


class InvoiceValidator:
    """
    Validador de Notas Fiscais Eletrônicas.
    
    Aplica regras fiscais e valida integridade dos dados.
    
    Exemplo de uso:
        validator = InvoiceValidator()
        resultado = validator.validate(invoice)
        if not resultado['valido']:
            print(resultado['irregularidades'])
    """
    
    def __init__(self):
        self.rules = NFeFiscalRules()
    
    def validate(self, invoice: Invoice) -> Dict[str, Any]:
        """
        Executa validação completa de uma nota fiscal.
        
        Args:
            invoice: Modelo Invoice do banco de dados
        
        Returns:
            Dicionário com resultado da validação:
            {
                'valido': bool,
                'irregularidades': List[str],
                'avisos': List[str],
                'score': float  # 0.0 a 1.0
            }
        """
        irregularidades = []
        avisos = []
        
        logger.info(f"Validando NF-e: {invoice.chave_acesso}")
        
        # 1. Validar chave de acesso
        valido_chave, msg_chave = self.rules.validar_chave_acesso(invoice.chave_acesso)
        if not valido_chave:
            irregularidades.append(f"Chave de acesso: {msg_chave}")
        
        # 2. Validar CNPJs
        valido_cnpj_emit, msg_emit = self.rules.validar_cnpj(invoice.cnpj_emitente)
        if not valido_cnpj_emit:
            irregularidades.append(f"CNPJ Emitente: {msg_emit}")
        
        valido_cnpj_dest, msg_dest = self.rules.validar_cnpj(invoice.cnpj_destinatario)
        if not valido_cnpj_dest:
            irregularidades.append(f"CNPJ Destinatário: {msg_dest}")
        
        # 3. Validar valores
        valido_valores, msgs_valores = self.rules.validar_valores_nfe(
            valor_produtos=invoice.valor_produtos or invoice.valor_total,
            valor_icms=invoice.valor_icms or Decimal('0'),
            valor_ipi=invoice.valor_ipi or Decimal('0'),
            valor_total=invoice.valor_total
        )
        if not valido_valores:
            irregularidades.extend(msgs_valores)
        
        # 4. Validar data de emissão
        avisos_data = self._validar_data_emissao(invoice.data_emissao)
        avisos.extend(avisos_data)
        
        # 5. Validar alíquota de ICMS (se possível extrair UF da chave)
        uf_origem = self._extrair_uf_da_chave(invoice.chave_acesso)
        if uf_origem and invoice.valor_icms and invoice.valor_produtos:
            valido_icms, msg_icms, aliquota = self.rules.verificar_aliquota_icms(
                valor_base=invoice.valor_produtos,
                valor_icms=invoice.valor_icms,
                uf_origem=uf_origem,
                uf_destino=uf_origem  # Assumindo operação interna por padrão
            )
            if not valido_icms:
                avisos.append(msg_icms)
        
        # 6. Validações de negócio
        avisos_negocio = self._validar_regras_negocio(invoice)
        avisos.extend(avisos_negocio)
        
        # Calcula score de confiança
        score = self._calcular_score(irregularidades, avisos)
        
        resultado = {
            'valido': len(irregularidades) == 0,
            'irregularidades': irregularidades,
            'avisos': avisos,
            'score': score,
            'total_problemas': len(irregularidades) + len(avisos)
        }
        
        logger.info(
            f"Validação concluída: {invoice.chave_acesso} - "
            f"Score: {score:.2f} - "
            f"Irregularidades: {len(irregularidades)} - "
            f"Avisos: {len(avisos)}"
        )
        
        return resultado
    
    def _validar_data_emissao(self, data_emissao: datetime) -> List[str]:
        """Valida data de emissão da NF-e."""
        avisos = []
        agora = datetime.now()
        
        # Data futura
        if data_emissao > agora:
            avisos.append(
                f"Data de emissão futura: {data_emissao.strftime('%d/%m/%Y')}"
            )
        
        # Data muito antiga (> 5 anos)
        limite_antigo = agora - timedelta(days=365 * 5)
        if data_emissao < limite_antigo:
            avisos.append(
                f"Data de emissão muito antiga: {data_emissao.strftime('%d/%m/%Y')} "
                f"(mais de 5 anos)"
            )
        
        # Data retroativa (> 5 dias)
        limite_retroativo = agora - timedelta(days=5)
        if data_emissao < limite_retroativo:
            dias_atras = (agora - data_emissao).days
            avisos.append(
                f"Emissão retroativa: {dias_atras} dias atrás. "
                f"Verifique se há justificativa"
            )
        
        return avisos
    
    def _validar_regras_negocio(self, invoice: Invoice) -> List[str]:
        """Valida regras específicas de negócio."""
        avisos = []
        
        # Valor total muito baixo
        if invoice.valor_total < Decimal('1.00'):
            avisos.append(
                f"Valor total muito baixo: R$ {invoice.valor_total:.2f}"
            )
        
        # Valor total muito alto (> R$ 1 milhão) - pode ser suspeito
        if invoice.valor_total > Decimal('1000000.00'):
            avisos.append(
                f"Valor total alto: R$ {invoice.valor_total:,.2f}. "
                f"Verifique se está correto"
            )
        
        # Impostos zerados
        if (invoice.valor_icms or Decimal('0')) == 0 and \
           (invoice.valor_ipi or Decimal('0')) == 0:
            avisos.append(
                "ICMS e IPI zerados. Verifique se é operação com isenção"
            )
        
        # Valor de produtos maior que total (inconsistência)
        if invoice.valor_produtos and invoice.valor_produtos > invoice.valor_total:
            avisos.append(
                f"Valor de produtos (R$ {invoice.valor_produtos:.2f}) maior que "
                f"valor total (R$ {invoice.valor_total:.2f})"
            )
        
        return avisos
    
    def _extrair_uf_da_chave(self, chave_acesso: str) -> str:
        """
        Extrai código da UF da chave de acesso.
        
        Os 2 primeiros dígitos da chave representam o código da UF.
        """
        if len(chave_acesso) < 2:
            return ''
        
        codigo_uf = chave_acesso[:2]
        
        # Mapa de códigos IBGE para UF
        mapa_uf = {
            '11': 'RO', '12': 'AC', '13': 'AM', '14': 'RR', '15': 'PA',
            '16': 'AP', '17': 'TO', '21': 'MA', '22': 'PI', '23': 'CE',
            '24': 'RN', '25': 'PB', '26': 'PE', '27': 'AL', '28': 'SE',
            '29': 'BA', '31': 'MG', '32': 'ES', '33': 'RJ', '35': 'SP',
            '41': 'PR', '42': 'SC', '43': 'RS', '50': 'MS', '51': 'MT',
            '52': 'GO', '53': 'DF'
        }
        
        return mapa_uf.get(codigo_uf, '')
    
    def _calcular_score(self, irregularidades: List[str], avisos: List[str]) -> float:
        """
        Calcula score de confiança da validação.
        
        Score: 1.0 = Perfeito
               0.0 = Muitos problemas
        
        Args:
            irregularidades: Lista de irregularidades graves
            avisos: Lista de avisos/alertas
        
        Returns:
            Float entre 0.0 e 1.0
        """
        # Começa com score perfeito
        score = 1.0
        
        # Cada irregularidade grave reduz 0.2
        score -= len(irregularidades) * 0.2
        
        # Cada aviso reduz 0.05
        score -= len(avisos) * 0.05
        
        # Garante que fique entre 0 e 1
        return max(0.0, min(1.0, score))
    
    def validate_batch(self, invoices: List[Invoice]) -> Dict[str, Any]:
        """
        Valida múltiplas notas fiscais em lote.
        
        Args:
            invoices: Lista de notas fiscais
        
        Returns:
            Estatísticas da validação em lote
        """
        resultados = []
        
        for invoice in invoices:
            resultado = self.validate(invoice)
            resultado['invoice_id'] = invoice.id
            resultado['chave_acesso'] = invoice.chave_acesso
            resultados.append(resultado)
        
        # Calcula estatísticas
        total = len(resultados)
        validos = sum(1 for r in resultados if r['valido'])
        score_medio = sum(r['score'] for r in resultados) / total if total > 0 else 0
        
        return {
            'total_validadas': total,
            'total_validas': validos,
            'total_invalidas': total - validos,
            'score_medio': score_medio,
            'resultados': resultados
        }