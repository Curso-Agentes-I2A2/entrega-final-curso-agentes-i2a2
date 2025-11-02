"""
Processador de Notas Fiscais Eletrônicas.

Orquestra o parse, validação e transformação de dados de NF-e.
"""
from typing import Dict, Any, Optional
import logging
from decimal import Decimal

from src.invoice_processing.parser import NFeXMLParser
from schemas.invoice_schema import InvoiceCreate

logger = logging.getLogger(__name__)


class InvoiceProcessor:
    """
    Processador principal de Notas Fiscais.
    
    Responsável por:
    - Parsear XML
    - Validar dados
    - Transformar em schema Pydantic
    - Enriquecer com metadados
    
    Exemplo de uso:
        processor = InvoiceProcessor()
        invoice_data = processor.process_xml(xml_string)
    """
    
    def __init__(self):
        self.parser = NFeXMLParser()
    
    def process_xml(self, xml_content: str) -> InvoiceCreate:
        """
        Processa XML completo e retorna schema para criação.
        
        Args:
            xml_content: String com XML da NF-e
        
        Returns:
            InvoiceCreate: Schema validado pronto para salvar
        
        Raises:
            ValueError: Se XML for inválido ou dados obrigatórios faltarem
        """
        try:
            # 1. Parse do XML
            logger.info("Iniciando parse do XML...")
            parsed_data = self.parser.parse_xml(xml_content)
            
            # 2. Extrai dados essenciais
            logger.info("Extraindo dados essenciais...")
            invoice_data = self._extract_essential_data(parsed_data)
            
            # 3. Valida dados obrigatórios
            logger.info("Validando dados obrigatórios...")
            self._validate_required_fields(invoice_data)
            
            # 4. Adiciona XML original
            invoice_data['xml_content'] = xml_content
            
            # 5. Cria e valida schema Pydantic
            logger.info("Criando schema Pydantic...")
            invoice_schema = InvoiceCreate(**invoice_data)
            
            logger.info(f"Nota fiscal processada: {invoice_schema.chave_acesso}")
            return invoice_schema
            
        except Exception as e:
            logger.error(f"Erro ao processar XML: {e}")
            raise
    
    def _extract_essential_data(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extrai apenas os dados essenciais para o modelo Invoice.
        
        Args:
            parsed_data: Dados parseados do XML
        
        Returns:
            Dicionário com dados essenciais
        """
        identificacao = parsed_data.get('identificacao', {})
        emitente = parsed_data.get('emitente', {})
        destinatario = parsed_data.get('destinatario', {})
        totais = parsed_data.get('totais', {})
        
        # Usa CNPJ ou CPF (preferência para CNPJ)
        cnpj_emitente = emitente.get('cnpj') or emitente.get('cpf', '')
        cnpj_destinatario = destinatario.get('cnpj') or destinatario.get('cpf', '')
        
        # Garante que tenha 14 dígitos (preenche CPF com zeros se necessário)
        if len(cnpj_emitente) == 11:  # CPF
            cnpj_emitente = cnpj_emitente.zfill(14)
        if len(cnpj_destinatario) == 11:  # CPF
            cnpj_destinatario = cnpj_destinatario.zfill(14)
        
        return {
            'numero': identificacao.get('numero', ''),
            'serie': identificacao.get('serie', ''),
            'chave_acesso': parsed_data.get('chave_acesso', ''),
            'cnpj_emitente': cnpj_emitente,
            'razao_social_emitente': emitente.get('razao_social', ''),
            'cnpj_destinatario': cnpj_destinatario,
            'razao_social_destinatario': destinatario.get('razao_social', ''),
            'valor_total': Decimal(str(totais.get('valor_total', 0))),
            'valor_produtos': Decimal(str(totais.get('valor_produtos', 0))),
            'valor_icms': Decimal(str(totais.get('valor_icms', 0))),
            'valor_ipi': Decimal(str(totais.get('valor_ipi', 0))),
            'data_emissao': identificacao.get('data_emissao'),
            'natureza_operacao': identificacao.get('natureza_operacao'),
            'observacoes': self._build_observacoes(parsed_data)
        }
    
    def _build_observacoes(self, parsed_data: Dict[str, Any]) -> Optional[str]:
        """
        Constrói campo de observações com informações adicionais.
        
        Args:
            parsed_data: Dados parseados completos
        
        Returns:
            String com observações ou None
        """
        info_adicionais = parsed_data.get('informacoes_adicionais', {})
        info_complementar = info_adicionais.get('info_complementar', '')
        info_fisco = info_adicionais.get('info_fisco', '')
        
        observacoes_list = []
        
        if info_complementar:
            observacoes_list.append(f"Info Complementar: {info_complementar}")
        
        if info_fisco:
            observacoes_list.append(f"Info Fisco: {info_fisco}")
        
        # Adiciona ambiente (produção/homologação)
        identificacao = parsed_data.get('identificacao', {})
        ambiente = identificacao.get('ambiente', '')
        if ambiente == '2':
            observacoes_list.append("⚠️ NOTA DE HOMOLOGAÇÃO")
        
        return '\n'.join(observacoes_list) if observacoes_list else None
    
    def _validate_required_fields(self, data: Dict[str, Any]) -> None:
        """
        Valida se todos os campos obrigatórios estão presentes.
        
        Args:
            data: Dicionário com dados extraídos
        
        Raises:
            ValueError: Se algum campo obrigatório estiver faltando
        """
        required_fields = {
            'numero': 'Número da nota fiscal',
            'serie': 'Série da nota fiscal',
            'chave_acesso': 'Chave de acesso',
            'cnpj_emitente': 'CNPJ do emitente',
            'razao_social_emitente': 'Razão social do emitente',
            'cnpj_destinatario': 'CNPJ do destinatário',
            'razao_social_destinatario': 'Razão social do destinatário',
            'valor_total': 'Valor total',
            'data_emissao': 'Data de emissão'
        }
        
        missing_fields = []
        
        for field, description in required_fields.items():
            value = data.get(field)
            if value is None or (isinstance(value, str) and not value.strip()):
                missing_fields.append(description)
        
        if missing_fields:
            raise ValueError(
                f"Campos obrigatórios não encontrados: {', '.join(missing_fields)}"
            )
        
        # Validações específicas
        if len(data['chave_acesso']) != 44:
            raise ValueError(
                f"Chave de acesso inválida: deve ter 44 dígitos, "
                f"encontrado {len(data['chave_acesso'])}"
            )
        
        if not data['chave_acesso'].isdigit():
            raise ValueError("Chave de acesso deve conter apenas números")
        
        if data['valor_total'] <= 0:
            raise ValueError("Valor total deve ser maior que zero")
    
    def get_summary(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Retorna resumo dos dados da NF-e para visualização rápida.
        
        Args:
            parsed_data: Dados parseados do XML
        
        Returns:
            Dicionário com resumo
        """
        identificacao = parsed_data.get('identificacao', {})
        emitente = parsed_data.get('emitente', {})
        destinatario = parsed_data.get('destinatario', {})
        totais = parsed_data.get('totais', {})
        produtos = parsed_data.get('produtos', [])
        
        return {
            'numero': identificacao.get('numero'),
            'serie': identificacao.get('serie'),
            'chave_acesso': parsed_data.get('chave_acesso'),
            'emitente': {
                'razao_social': emitente.get('razao_social'),
                'cnpj': emitente.get('cnpj')
            },
            'destinatario': {
                'razao_social': destinatario.get('razao_social'),
                'cnpj': destinatario.get('cnpj')
            },
            'valores': {
                'produtos': totais.get('valor_produtos'),
                'icms': totais.get('valor_icms'),
                'ipi': totais.get('valor_ipi'),
                'total': totais.get('valor_total')
            },
            'quantidade_itens': len(produtos),
            'data_emissao': identificacao.get('data_emissao')
        }