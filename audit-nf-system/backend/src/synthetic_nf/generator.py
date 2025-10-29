"""
Gerador de Notas Fiscais sintéticas para testes.

Cria XMLs de NF-e válidos com dados fictícios.
"""
from datetime import datetime, timedelta
from decimal import Decimal
import random
import string
from typing import Optional
from lxml import etree


class SyntheticNFeGenerator:
    """
    Gerador de Notas Fiscais Eletrônicas sintéticas.
    
    Útil para testes e desenvolvimento sem necessidade de NFs reais.
    
    Exemplo de uso:
        generator = SyntheticNFeGenerator()
        xml = generator.generate()
        print(xml)
    """
    
    # CNPJs fictícios para testes
    CNPJS_EMITENTES = [
        "12345678000190",
        "98765432000100",
        "11222333000144",
        "44555666000177",
    ]
    
    CNPJS_DESTINATARIOS = [
        "55666777000188",
        "88999000000199",
        "22333444000155",
        "66777888000166",
    ]
    
    PRODUTOS = [
        {
            "codigo": "001",
            "descricao": "PRODUTO EXEMPLO A",
            "ncm": "12345678",
            "valor_unitario": 100.00
        },
        {
            "codigo": "002",
            "descricao": "PRODUTO EXEMPLO B",
            "ncm": "87654321",
            "valor_unitario": 250.00
        },
        {
            "codigo": "003",
            "descricao": "PRODUTO EXEMPLO C",
            "ncm": "11223344",
            "valor_unitario": 75.50
        },
        {
            "codigo": "004",
            "descricao": "PRODUTO EXEMPLO D",
            "ncm": "99887766",
            "valor_unitario": 500.00
        }
    ]
    
    NATUREZAS_OPERACAO = [
        "Venda de Mercadoria",
        "Devolucao de Mercadoria",
        "Transferencia",
        "Remessa para Conserto"
    ]
    
    def __init__(self, seed: Optional[int] = None):
        """
        Inicializa gerador.
        
        Args:
            seed: Seed para random (para gerar XMLs reproduzíveis)
        """
        if seed:
            random.seed(seed)
    
    def generate(
        self,
        numero: Optional[int] = None,
        serie: Optional[int] = None,
        valor_total: Optional[Decimal] = None,
        com_irregularidades: bool = False
    ) -> str:
        """
        Gera XML completo de uma NF-e sintética.
        
        Args:
            numero: Número da nota (aleatório se None)
            serie: Série da nota (aleatório se None)
            valor_total: Valor total (aleatório se None)
            com_irregularidades: Se True, gera nota com problemas propositais
        
        Returns:
            String com XML completo da NF-e
        """
        # Dados básicos
        numero = numero or random.randint(1, 99999)
        serie = serie or random.randint(1, 10)
        data_emissao = self._gerar_data_emissao(com_irregularidades)
        
        # Emitente e destinatário
        cnpj_emitente = random.choice(self.CNPJS_EMITENTES)
        cnpj_destinatario = random.choice(self.CNPJS_DESTINATARIOS)
        
        # Produtos
        num_produtos = random.randint(1, 5)
        produtos = random.sample(self.PRODUTOS, min(num_produtos, len(self.PRODUTOS)))
        
        # Calcula valores
        valor_produtos = sum(
            Decimal(str(p["valor_unitario"])) * random.randint(1, 10) 
            for p in produtos
        )
        
        if valor_total:
            valor_produtos = valor_total
        
        valor_icms = valor_produtos * Decimal("0.18")  # 18%
        valor_ipi = valor_produtos * Decimal("0.10")   # 10%
        
        if com_irregularidades:
            # Gera inconsistências propositais
            valor_total_final = valor_produtos + valor_ipi + Decimal("100.00")  # Adiciona valor errado
        else:
            valor_total_final = valor_produtos + valor_ipi
        
        # Gera chave de acesso
        chave_acesso = self._gerar_chave_acesso(
            uf="35",  # SP
            ano_mes="2105",
            cnpj=cnpj_emitente,
            modelo="55",
            serie=str(serie).zfill(3),
            numero=str(numero).zfill(9),
            com_erro=com_irregularidades
        )
        
        # Monta XML
        xml = self._montar_xml(
            chave_acesso=chave_acesso,
            numero=numero,
            serie=serie,
            data_emissao=data_emissao,
            cnpj_emitente=cnpj_emitente,
            cnpj_destinatario=cnpj_destinatario,
            produtos=produtos,
            valor_produtos=valor_produtos,
            valor_icms=valor_icms,
            valor_ipi=valor_ipi,
            valor_total=valor_total_final,
            natureza_operacao=random.choice(self.NATUREZAS_OPERACAO)
        )
        
        return xml
    
    def generate_batch(self, quantidade: int = 10) -> list[str]:
        """
        Gera múltiplas NF-e sintéticas.
        
        Args:
            quantidade: Número de notas a gerar
        
        Returns:
            Lista de XMLs
        """
        return [self.generate(numero=i+1) for i in range(quantidade)]
    
    def _gerar_data_emissao(self, com_irregularidades: bool) -> datetime:
        """Gera data de emissão."""
        if com_irregularidades and random.random() > 0.5:
            # Data retroativa ou futura
            if random.random() > 0.5:
                # Retroativa (muito antiga)
                return datetime.now() - timedelta(days=random.randint(365, 365*3))
            else:
                # Futura
                return datetime.now() + timedelta(days=random.randint(1, 30))
        else:
            # Data recente normal
            return datetime.now() - timedelta(days=random.randint(0, 30))
    
    def _gerar_chave_acesso(
        self,
        uf: str,
        ano_mes: str,
        cnpj: str,
        modelo: str,
        serie: str,
        numero: str,
        com_erro: bool = False
    ) -> str:
        """
        Gera chave de acesso de 44 dígitos.
        
        Formato: UF + AAMM + CNPJ + MOD + SERIE + NUMERO + TIPO_EMISSAO + COD_NUMERICO + DV
        """
        # Componentes da chave
        tipo_emissao = "1"  # Normal
        cod_numerico = ''.join(random.choices(string.digits, k=8))
        
        # Monta chave sem DV
        chave_sem_dv = (
            uf + 
            ano_mes + 
            cnpj + 
            modelo + 
            serie + 
            numero + 
            tipo_emissao + 
            cod_numerico
        )
        
        # Calcula dígito verificador
        dv = self._calcular_dv_modulo11(chave_sem_dv)
        
        if com_erro:
            # Gera DV errado propositalmente
            dv = (dv + 1) % 10
        
        return chave_sem_dv + str(dv)
    
    def _calcular_dv_modulo11(self, numero: str) -> int:
        """Calcula dígito verificador módulo 11."""
        multiplicadores = [4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        
        soma = sum(int(d) * m for d, m in zip(numero, multiplicadores))
        resto = soma % 11
        
        return 0 if resto in (0, 1) else 11 - resto
    
    def _montar_xml(
        self,
        chave_acesso: str,
        numero: int,
        serie: int,
        data_emissao: datetime,
        cnpj_emitente: str,
        cnpj_destinatario: str,
        produtos: list,
        valor_produtos: Decimal,
        valor_icms: Decimal,
        valor_ipi: Decimal,
        valor_total: Decimal,
        natureza_operacao: str
    ) -> str:
        """Monta XML completo da NF-e."""
        
        # Namespace
        ns = "http://www.portalfiscal.inf.br/nfe"
        nsmap = {None: ns}
        
        # Elemento raiz
        nfe_proc = etree.Element(f"{{{ns}}}nfeProc", nsmap=nsmap, versao="4.00")
        nfe = etree.SubElement(nfe_proc, f"{{{ns}}}NFe")
        inf_nfe = etree.SubElement(nfe, f"{{{ns}}}infNFe", Id=f"NFe{chave_acesso}", versao="4.00")
        
        # IDE
        ide = etree.SubElement(inf_nfe, f"{{{ns}}}ide")
        self._add_element(ide, "cUF", "35", ns)
        self._add_element(ide, "cNF", chave_acesso[35:43], ns)
        self._add_element(ide, "natOp", natureza_operacao, ns)
        self._add_element(ide, "mod", "55", ns)
        self._add_element(ide, "serie", str(serie), ns)
        self._add_element(ide, "nNF", str(numero), ns)
        self._add_element(ide, "dhEmi", data_emissao.strftime("%Y-%m-%dT%H:%M:%S-03:00"), ns)
        self._add_element(ide, "tpNF", "1", ns)
        self._add_element(ide, "idDest", "1", ns)
        self._add_element(ide, "cMunFG", "3550308", ns)
        self._add_element(ide, "tpImp", "1", ns)
        self._add_element(ide, "tpEmis", "1", ns)
        self._add_element(ide, "cDV", chave_acesso[-1], ns)
        self._add_element(ide, "tpAmb", "2", ns)  # Homologação
        self._add_element(ide, "finNFe", "1", ns)
        self._add_element(ide, "indFinal", "0", ns)
        self._add_element(ide, "indPres", "1", ns)
        self._add_element(ide, "procEmi", "0", ns)
        self._add_element(ide, "verProc", "1.0.0", ns)
        
        # EMIT
        emit = etree.SubElement(inf_nfe, f"{{{ns}}}emit")
        self._add_element(emit, "CNPJ", cnpj_emitente, ns)
        self._add_element(emit, "xNome", "EMPRESA EMITENTE LTDA", ns)
        self._add_element(emit, "xFant", "Emitente", ns)
        
        ender_emit = etree.SubElement(emit, f"{{{ns}}}enderEmit")
        self._add_element(ender_emit, "xLgr", "Rua das Flores", ns)
        self._add_element(ender_emit, "nro", "123", ns)
        self._add_element(ender_emit, "xBairro", "Centro", ns)
        self._add_element(ender_emit, "cMun", "3550308", ns)
        self._add_element(ender_emit, "xMun", "São Paulo", ns)
        self._add_element(ender_emit, "UF", "SP", ns)
        self._add_element(ender_emit, "CEP", "01000000", ns)
        self._add_element(ender_emit, "cPais", "1058", ns)
        self._add_element(ender_emit, "xPais", "Brasil", ns)
        self._add_element(ender_emit, "fone", "1133334444", ns)
        
        self._add_element(emit, "IE", "123456789012", ns)
        self._add_element(emit, "CRT", "3", ns)
        
        # DEST
        dest = etree.SubElement(inf_nfe, f"{{{ns}}}dest")
        self._add_element(dest, "CNPJ", cnpj_destinatario, ns)
        self._add_element(dest, "xNome", "EMPRESA DESTINATARIA LTDA", ns)
        
        ender_dest = etree.SubElement(dest, f"{{{ns}}}enderDest")
        self._add_element(ender_dest, "xLgr", "Avenida Principal", ns)
        self._add_element(ender_dest, "nro", "456", ns)
        self._add_element(ender_dest, "xBairro", "Jardim", ns)
        self._add_element(ender_dest, "cMun", "3550308", ns)
        self._add_element(ender_dest, "xMun", "São Paulo", ns)
        self._add_element(ender_dest, "UF", "SP", ns)
        self._add_element(ender_dest, "CEP", "02000000", ns)
        self._add_element(ender_dest, "cPais", "1058", ns)
        self._add_element(ender_dest, "xPais", "Brasil", ns)
        
        self._add_element(dest, "indIEDest", "1", ns)
        self._add_element(dest, "IE", "987654321098", ns)
        
        # PRODUTOS
        for i, prod_info in enumerate(produtos, 1):
            det = etree.SubElement(inf_nfe, f"{{{ns}}}det", nItem=str(i))
            prod = etree.SubElement(det, f"{{{ns}}}prod")
            
            quantidade = random.randint(1, 10)
            valor_unit = Decimal(str(prod_info["valor_unitario"]))
            valor_prod = valor_unit * quantidade
            
            self._add_element(prod, "cProd", prod_info["codigo"], ns)
            self._add_element(prod, "cEAN", "SEM GTIN", ns)
            self._add_element(prod, "xProd", prod_info["descricao"], ns)
            self._add_element(prod, "NCM", prod_info["ncm"], ns)
            self._add_element(prod, "CFOP", "5102", ns)
            self._add_element(prod, "uCom", "UN", ns)
            self._add_element(prod, "qCom", f"{quantidade}.0000", ns)
            self._add_element(prod, "vUnCom", f"{valor_unit:.4f}", ns)
            self._add_element(prod, "vProd", f"{valor_prod:.2f}", ns)
            self._add_element(prod, "cEANTrib", "SEM GTIN", ns)
            self._add_element(prod, "uTrib", "UN", ns)
            self._add_element(prod, "qTrib", f"{quantidade}.0000", ns)
            self._add_element(prod, "vUnTrib", f"{valor_unit:.4f}", ns)
            self._add_element(prod, "indTot", "1", ns)
            
            # Impostos
            imposto = etree.SubElement(det, f"{{{ns}}}imposto")
            
            # ICMS
            icms = etree.SubElement(imposto, f"{{{ns}}}ICMS")
            icms00 = etree.SubElement(icms, f"{{{ns}}}ICMS00")
            self._add_element(icms00, "orig", "0", ns)
            self._add_element(icms00, "CST", "00", ns)
            self._add_element(icms00, "modBC", "3", ns)
            self._add_element(icms00, "vBC", f"{valor_prod:.2f}", ns)
            self._add_element(icms00, "pICMS", "18.00", ns)
            self._add_element(icms00, "vICMS", f"{valor_prod * Decimal('0.18'):.2f}", ns)
            
            # IPI
            ipi = etree.SubElement(imposto, f"{{{ns}}}IPI")
            ipi_trib = etree.SubElement(ipi, f"{{{ns}}}IPITrib")
            self._add_element(ipi_trib, "CST", "50", ns)
            self._add_element(ipi_trib, "vBC", f"{valor_prod:.2f}", ns)
            self._add_element(ipi_trib, "pIPI", "10.00", ns)
            self._add_element(ipi_trib, "vIPI", f"{valor_prod * Decimal('0.10'):.2f}", ns)
        
        # TOTAL
        total = etree.SubElement(inf_nfe, f"{{{ns}}}total")
        icms_tot = etree.SubElement(total, f"{{{ns}}}ICMSTot")
        self._add_element(icms_tot, "vBC", f"{valor_produtos:.2f}", ns)
        self._add_element(icms_tot, "vICMS", f"{valor_icms:.2f}", ns)
        self._add_element(icms_tot, "vICMSDeson", "0.00", ns)
        self._add_element(icms_tot, "vFCP", "0.00", ns)
        self._add_element(icms_tot, "vBCST", "0.00", ns)
        self._add_element(icms_tot, "vST", "0.00", ns)
        self._add_element(icms_tot, "vFCPST", "0.00", ns)
        self._add_element(icms_tot, "vFCPSTRet", "0.00", ns)
        self._add_element(icms_tot, "vProd", f"{valor_produtos:.2f}", ns)
        self._add_element(icms_tot, "vFrete", "0.00", ns)
        self._add_element(icms_tot, "vSeg", "0.00", ns)
        self._add_element(icms_tot, "vDesc", "0.00", ns)
        self._add_element(icms_tot, "vII", "0.00", ns)
        self._add_element(icms_tot, "vIPI", f"{valor_ipi:.2f}", ns)
        self._add_element(icms_tot, "vIPIDevol", "0.00", ns)
        self._add_element(icms_tot, "vPIS", "0.00", ns)
        self._add_element(icms_tot, "vCOFINS", "0.00", ns)
        self._add_element(icms_tot, "vOutro", "0.00", ns)
        self._add_element(icms_tot, "vNF", f"{valor_total:.2f}", ns)
        
        # TRANSP
        transp = etree.SubElement(inf_nfe, f"{{{ns}}}transp")
        self._add_element(transp, "modFrete", "9", ns)
        
        # PAG
        pag = etree.SubElement(inf_nfe, f"{{{ns}}}pag")
        det_pag = etree.SubElement(pag, f"{{{ns}}}detPag")
        self._add_element(det_pag, "tPag", "01", ns)
        self._add_element(det_pag, "vPag", f"{valor_total:.2f}", ns)
        
        # INFO ADIC
        inf_adic = etree.SubElement(inf_nfe, f"{{{ns}}}infAdic")
        self._add_element(inf_adic, "infCpl", "Nota Fiscal Sintética para Testes", ns)
        
        # Converte para string
        return etree.tostring(
            nfe_proc,
            encoding='unicode',
            pretty_print=True,
            xml_declaration=True
        )
    
    def _add_element(self, parent, tag: str, text: str, namespace: str):
        """Helper para adicionar elemento com namespace."""
        elem = etree.SubElement(parent, f"{{{namespace}}}{tag}")
        elem.text = text
        return elem