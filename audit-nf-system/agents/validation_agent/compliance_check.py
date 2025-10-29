# agents/validation_agent/compliance_check.py

import re
import logging
from typing import Dict
logger = logging.getLogger(__name__)

class ComplianceCheck:
    """
    Realiza verificações de conformidade estrutural e de formato em uma NF-e.
    Estas são validações determinísticas que precedem a análise de conteúdo pelo LLM.
    """

    @staticmethod
    def check_schema(xml_content: str) -> Dict[str, any]:
        """
        Valida o XML contra o schema XSD oficial da NF-e (versão 4.0, por exemplo).
        
        NOTA: A implementação real requer uma biblioteca como `lxml`.
        Isto é um mock para fins de demonstração.
        """
        # TODO: Implementar a validação real com a biblioteca lxml
        # from lxml import etree
        # schema_file = "path/to/nfe_v4.00.xsd"
        # schema = etree.XMLSchema(file=schema_file)
        # try:
        #     xml_doc = etree.fromstring(xml_content.encode('utf-8'))
        #     schema.assertValid(xml_doc)
        #     return {"valid": True, "errors": []}
        # except Exception as e:
        #     return {"valid": False, "errors": [str(e)]}
        
        if not xml_content or "<NFe" not in xml_content:
            return {"valid": False, "errors": ["Conteúdo XML parece inválido ou vazio."]}
        
        return {"valid": True, "errors": []} # Mock: Sempre retorna válido

    @staticmethod
    def validate_signature(xml_content: str) -> Dict[str, any]:
        """
        Valida a assinatura digital do XML da NF-e.
        
        NOTA: Este é um processo complexo que envolve criptografia.
        Isto é um mock para fins de demonstração.
        """
        # TODO: Implementar a validação de assinatura digital com bibliotecas como `signxml`.
        
        if "<Signature" not in xml_content:
             return {"valid": False, "message": "Tag de assinatura digital não encontrada."}

        return {"valid": True, "message": "Assinatura digital formalmente válida."} # Mock

    @staticmethod
    def check_access_key(key: str) -> Dict[str, any]:
        """
        Valida o formato e o dígito verificador da chave de acesso da NF-e (44 dígitos).
        """
        # Remove caracteres não numéricos
        key = re.sub(r'\D', '', key)

        if len(key) != 44:
            return {"valid": False, "message": f"Chave de acesso possui {len(key)} dígitos, mas deveria ter 44."}

        base_key = key[:43]
        dv_informado = int(key[43])

        # Cálculo do Dígito Verificador (Módulo 11)
        soma = 0
        peso = 2
        for i in range(42, -1, -1):
            soma += int(base_key[i]) * peso
            peso += 1
            if peso > 9:
                peso = 2
        
        resto = soma % 11
        dv_calculado = 0 if resto in [0, 1] else 11 - resto

        if dv_informado == dv_calculado:
            return {"valid": True, "message": "Chave de acesso válida."}
        else:
            return {
                "valid": False, 
                "message": f"Dígito verificador inválido. Informado: {dv_informado}, Calculado: {dv_calculado}."
            }