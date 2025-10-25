"""
Parser de XML de Notas Fiscais Eletrônicas (NF-e).

Extrai dados estruturados do XML seguindo o padrão da SEFAZ.
"""
from lxml import etree
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class NFeXMLParser:
    """
    Parser especializado para XMLs de NF-e (Nota Fiscal Eletrônica).
    
    Suporta versões 3.10 e 4.00 do layout da NF-e.
    
    Exemplo de uso:
        parser = NFeXMLParser()
        data = parser.parse_xml(xml_string)
        print(data['identificacao']['numero'])
    """
    
    # Namespace padrão da NF-e
    NAMESPACE = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}
    
    def parse_xml(self, xml_content: str) -> Dict[str, Any]:
        """
        Faz parse completo do XML da NF-e.
        
        Args:
            xml_content: String contendo o XML completo
        
        Returns:
            Dicionário com dados estruturados da NF-e
        
        Raises:
            ValueError: Se XML for inválido ou não seguir padrão NF-e
        """
        try:
            root = etree.fromstring(xml_content.encode('utf-8'))
            
            # Tenta encontrar a tag infNFe (pode estar em diferentes níveis)
            inf_nfe = self._find_inf_nfe(root)
            
            if inf_nfe is None:
                raise ValueError("Tag infNFe não encontrada no XML")
            
            # Extrai cada seção do XML
            data = {
                'chave_acesso': self._extract_chave_acesso(inf_nfe),
                'identificacao': self._extract_identificacao(inf_nfe),
                'emitente': self._extract_emitente(inf_nfe),
                'destinatario': self._extract_destinatario(inf_nfe),
                'produtos': self._extract_produtos(inf_nfe),
                'totais': self._extract_totais(inf_nfe),
                'transporte': self._extract_transporte(inf_nfe),
                'pagamento': self._extract_pagamento(inf_nfe),
                'informacoes_adicionais': self._extract_info_adicionais(inf_nfe)
            }
            
            logger.info(f"XML parseado com sucesso: NF-e {data['identificacao']['numero']}")
            return data
            
        except etree.XMLSyntaxError as e:
            logger.error(f"Erro de sintaxe XML: {e}")
            raise ValueError(f"XML malformado: {str(e)}")
        except Exception as e:
            logger.error(f"Erro ao fazer parse do XML: {e}")
            raise ValueError(f"Erro ao processar XML: {str(e)}")
    
    def _find_inf_nfe(self, root: etree.Element) -> Optional[etree.Element]:
        """Encontra a tag infNFe no XML (pode estar em diferentes níveis)."""
        # Tenta caminho direto
        inf_nfe = root.find('.//nfe:infNFe', self.NAMESPACE)
        if inf_nfe is not None:
            return inf_nfe
        
        # Tenta sem namespace
        inf_nfe = root.find('.//infNFe')
        return inf_nfe
    
    def _extract_chave_acesso(self, inf_nfe: etree.Element) -> str:
        """Extrai chave de acesso do atributo Id."""
        chave = inf_nfe.get('Id', '')
        # Remove prefixo "NFe" se existir
        return chave.replace('NFe', '').strip()
    
    def _extract_identificacao(self, inf_nfe: etree.Element) -> Dict[str, Any]:
        """Extrai dados de identificação da NF-e (tag <ide>)."""
        ide = inf_nfe.find('nfe:ide', self.NAMESPACE) or inf_nfe.find('ide')
        
        if ide is None:
            raise ValueError("Tag <ide> não encontrada")
        
        return {
            'uf': self._get_text(ide, 'cUF'),
            'numero': self._get_text(ide, 'nNF'),
            'serie': self._get_text(ide, 'serie'),
            'modelo': self._get_text(ide, 'mod', '55'),
            'data_emissao': self._parse_datetime(self._get_text(ide, 'dhEmi')),
            'data_saida': self._parse_datetime(self._get_text(ide, 'dhSaiEnt')),
            'tipo_operacao': self._get_text(ide, 'tpNF'),  # 0=Entrada, 1=Saída
            'natureza_operacao': self._get_text(ide, 'natOp'),
            'tipo_emissao': self._get_text(ide, 'tpEmis'),
            'finalidade': self._get_text(ide, 'finNFe'),
            'ambiente': self._get_text(ide, 'tpAmb'),  # 1=Produção, 2=Homologação
        }
    
    def _extract_emitente(self, inf_nfe: etree.Element) -> Dict[str, Any]:
        """Extrai dados do emitente (tag <emit>)."""
        emit = inf_nfe.find('nfe:emit', self.NAMESPACE) or inf_nfe.find('emit')
        
        if emit is None:
            raise ValueError("Tag <emit> não encontrada")
        
        endereco = emit.find('nfe:enderEmit', self.NAMESPACE) or emit.find('enderEmit')
        
        return {
            'cnpj': self._get_text(emit, 'CNPJ'),
            'cpf': self._get_text(emit, 'CPF'),
            'razao_social': self._get_text(emit, 'xNome'),
            'nome_fantasia': self._get_text(emit, 'xFant'),
            'inscricao_estadual': self._get_text(emit, 'IE'),
            'regime_tributario': self._get_text(emit, 'CRT'),
            'endereco': self._extract_endereco(endereco) if endereco is not None else {}
        }
    
    def _extract_destinatario(self, inf_nfe: etree.Element) -> Dict[str, Any]:
        """Extrai dados do destinatário (tag <dest>)."""
        dest = inf_nfe.find('nfe:dest', self.NAMESPACE) or inf_nfe.find('dest')
        
        if dest is None:
            raise ValueError("Tag <dest> não encontrada")
        
        endereco = dest.find('nfe:enderDest', self.NAMESPACE) or dest.find('enderDest')
        
        return {
            'cnpj': self._get_text(dest, 'CNPJ'),
            'cpf': self._get_text(dest, 'CPF'),
            'razao_social': self._get_text(dest, 'xNome'),
            'inscricao_estadual': self._get_text(dest, 'IE'),
            'indicador_ie': self._get_text(dest, 'indIEDest'),
            'endereco': self._extract_endereco(endereco) if endereco is not None else {}
        }
    
    def _extract_endereco(self, endereco: etree.Element) -> Dict[str, str]:
        """Extrai dados de endereço."""
        return {
            'logradouro': self._get_text(endereco, 'xLgr'),
            'numero': self._get_text(endereco, 'nro'),
            'complemento': self._get_text(endereco, 'xCpl'),
            'bairro': self._get_text(endereco, 'xBairro'),
            'municipio': self._get_text(endereco, 'xMun'),
            'codigo_municipio': self._get_text(endereco, 'cMun'),
            'uf': self._get_text(endereco, 'UF'),
            'cep': self._get_text(endereco, 'CEP'),
            'telefone': self._get_text(endereco, 'fone')
        }
    
    def _extract_produtos(self, inf_nfe: etree.Element) -> List[Dict[str, Any]]:
        """Extrai dados dos produtos/itens (tags <det>)."""
        produtos = []
        
        dets = inf_nfe.findall('nfe:det', self.NAMESPACE) or inf_nfe.findall('det')
        
        for det in dets:
            prod = det.find('nfe:prod', self.NAMESPACE) or det.find('prod')
            imposto = det.find('nfe:imposto', self.NAMESPACE) or det.find('imposto')
            
            if prod is None:
                continue
            
            produto = {
                'numero_item': det.get('nItem'),
                'codigo': self._get_text(prod, 'cProd'),
                'codigo_ean': self._get_text(prod, 'cEAN'),
                'descricao': self._get_text(prod, 'xProd'),
                'ncm': self._get_text(prod, 'NCM'),
                'cfop': self._get_text(prod, 'CFOP'),
                'unidade': self._get_text(prod, 'uCom'),
                'quantidade': self._get_float(prod, 'qCom'),
                'valor_unitario': self._get_float(prod, 'vUnCom'),
                'valor_total': self._get_float(prod, 'vProd'),
                'impostos': self._extract_impostos(imposto) if imposto is not None else {}
            }
            
            produtos.append(produto)
        
        return produtos
    
    def _extract_impostos(self, imposto: etree.Element) -> Dict[str, Any]:
        """Extrai dados de impostos de um produto."""
        impostos = {}
        
        # ICMS
        icms = imposto.find('.//nfe:ICMS', self.NAMESPACE) or imposto.find('.//ICMS')
        if icms is not None:
            # Pode ter vários tipos: ICMS00, ICMS10, ICMS20, etc
            icms_tipo = icms.find('*')  # Pega primeiro filho
            if icms_tipo is not None:
                impostos['icms'] = {
                    'tipo': icms_tipo.tag.replace('{' + self.NAMESPACE['nfe'] + '}', ''),
                    'base_calculo': self._get_float(icms_tipo, 'vBC'),
                    'aliquota': self._get_float(icms_tipo, 'pICMS'),
                    'valor': self._get_float(icms_tipo, 'vICMS')
                }
        
        # IPI
        ipi = imposto.find('.//nfe:IPI', self.NAMESPACE) or imposto.find('.//IPI')
        if ipi is not None:
            ipi_trib = ipi.find('nfe:IPITrib', self.NAMESPACE) or ipi.find('IPITrib')
            if ipi_trib is not None:
                impostos['ipi'] = {
                    'base_calculo': self._get_float(ipi_trib, 'vBC'),
                    'aliquota': self._get_float(ipi_trib, 'pIPI'),
                    'valor': self._get_float(ipi_trib, 'vIPI')
                }
        
        # PIS
        pis = imposto.find('.//nfe:PIS', self.NAMESPACE) or imposto.find('.//PIS')
        if pis is not None:
            pis_aliq = pis.find('*')  # Pode ser PISAliq, PISNT, etc
            if pis_aliq is not None:
                impostos['pis'] = {
                    'base_calculo': self._get_float(pis_aliq, 'vBC'),
                    'aliquota': self._get_float(pis_aliq, 'pPIS'),
                    'valor': self._get_float(pis_aliq, 'vPIS')
                }
        
        # COFINS
        cofins = imposto.find('.//nfe:COFINS', self.NAMESPACE) or imposto.find('.//COFINS')
        if cofins is not None:
            cofins_aliq = cofins.find('*')
            if cofins_aliq is not None:
                impostos['cofins'] = {
                    'base_calculo': self._get_float(cofins_aliq, 'vBC'),
                    'aliquota': self._get_float(cofins_aliq, 'pCOFINS'),
                    'valor': self._get_float(cofins_aliq, 'vCOFINS')
                }
        
        return impostos
    
    def _extract_totais(self, inf_nfe: etree.Element) -> Dict[str, float]:
        """Extrai totais da NF-e (tag <total>)."""
        total = inf_nfe.find('.//nfe:total/nfe:ICMSTot', self.NAMESPACE) or \
                inf_nfe.find('.//total/ICMSTot')
        
        if total is None:
            raise ValueError("Tag <total> não encontrada")
        
        return {
            'base_calculo_icms': self._get_float(total, 'vBC'),
            'valor_icms': self._get_float(total, 'vICMS'),
            'valor_produtos': self._get_float(total, 'vProd'),
            'valor_frete': self._get_float(total, 'vFrete'),
            'valor_seguro': self._get_float(total, 'vSeg'),
            'valor_desconto': self._get_float(total, 'vDesc'),
            'valor_ipi': self._get_float(total, 'vIPI'),
            'valor_pis': self._get_float(total, 'vPIS'),
            'valor_cofins': self._get_float(total, 'vCOFINS'),
            'valor_total': self._get_float(total, 'vNF'),
            'valor_tributos': self._get_float(total, 'vTotTrib')
        }
    
    def _extract_transporte(self, inf_nfe: etree.Element) -> Dict[str, Any]:
        """Extrai dados de transporte (tag <transp>)."""
        transp = inf_nfe.find('nfe:transp', self.NAMESPACE) or inf_nfe.find('transp')
        
        if transp is None:
            return {}
        
        return {
            'modalidade_frete': self._get_text(transp, 'modFrete'),
            'transportadora': self._extract_transportadora(transp)
        }
    
    def _extract_transportadora(self, transp: etree.Element) -> Dict[str, str]:
        """Extrai dados da transportadora."""
        transporta = transp.find('nfe:transporta', self.NAMESPACE) or transp.find('transporta')
        
        if transporta is None:
            return {}
        
        return {
            'cnpj': self._get_text(transporta, 'CNPJ'),
            'cpf': self._get_text(transporta, 'CPF'),
            'razao_social': self._get_text(transporta, 'xNome'),
            'inscricao_estadual': self._get_text(transporta, 'IE')
        }
    
    def _extract_pagamento(self, inf_nfe: etree.Element) -> List[Dict[str, Any]]:
        """Extrai formas de pagamento (tag <pag>)."""
        pagamentos = []
        
        pag = inf_nfe.find('nfe:pag', self.NAMESPACE) or inf_nfe.find('pag')
        
        if pag is None:
            return pagamentos
        
        detpags = pag.findall('nfe:detPag', self.NAMESPACE) or pag.findall('detPag')
        
        for detpag in detpags:
            pagamentos.append({
                'forma_pagamento': self._get_text(detpag, 'tPag'),
                'valor': self._get_float(detpag, 'vPag')
            })
        
        return pagamentos
    
    def _extract_info_adicionais(self, inf_nfe: etree.Element) -> Dict[str, str]:
        """Extrai informações adicionais (tag <infAdic>)."""
        inf_adic = inf_nfe.find('nfe:infAdic', self.NAMESPACE) or inf_nfe.find('infAdic')
        
        if inf_adic is None:
            return {}
        
        return {
            'info_complementar': self._get_text(inf_adic, 'infCpl'),
            'info_fisco': self._get_text(inf_adic, 'infAdFisco')
        }
    
    def _get_text(self, element: etree.Element, tag: str, default: str = '') -> str:
        """Helper para extrair texto de uma tag com namespace."""
        # Tenta com namespace
        child = element.find(f'nfe:{tag}', self.NAMESPACE)
        if child is not None and child.text:
            return child.text.strip()
        
        # Tenta sem namespace
        child = element.find(tag)
        if child is not None and child.text:
            return child.text.strip()
        
        return default
    
    def _get_float(self, element: etree.Element, tag: str, default: float = 0.0) -> float:
        """Helper para extrair valor numérico."""
        text = self._get_text(element, tag)
        if not text:
            return default
        
        try:
            return float(text)
        except ValueError:
            return default
    
    def _parse_datetime(self, datetime_str: str) -> Optional[datetime]:
        """Converte string de data/hora para objeto datetime."""
        if not datetime_str:
            return None
        
        try:
            # Remove timezone se presente (ex: -03:00)
            datetime_str = datetime_str[:19]
            return datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S')
        except Exception:
            return None