"""
Agente de Validação de NF-e
Responsável por validar estrutura, schema XML e conformidade técnica
"""

import logging
import re
from typing import Dict, List, Any, Optional
from datetime import datetime

from langchain_anthropic import ChatAnthropic
from langchain.schema import HumanMessage, SystemMessage

from config import settings, VALIDATION_AGENT_CONFIG

logger = logging.getLogger(__name__)


class ValidationAgent:
    """
    Agente especializado em validação estrutural e técnica de NF-e
    
    Responsabilidades:
    - Validar estrutura do XML
    - Verificar campos obrigatórios
    - Validar chave de acesso
    - Verificar assinatura digital (mock)
    - Validar contra schema XSD (mock)
    """
    
    def __init__(self):
        """
        Inicializa agente de validação
        """
        logger.info("✓ Inicializando Agente de Validação...")
        
        # LLM para análises que requerem raciocínio
        self.llm = ChatAnthropic(
            model=VALIDATION_AGENT_CONFIG["model"],
            temperature=VALIDATION_AGENT_CONFIG["temperature"],
            max_tokens=VALIDATION_AGENT_CONFIG["max_tokens"],
            anthropic_api_key=settings.ANTHROPIC_API_KEY,
        )
        
        logger.info("✅ Agente de Validação inicializado")
    
    async def validate_invoice(
        self,
        invoice_data: Dict[str, Any],
        xml_content: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Valida nota fiscal
        
        Args:
            invoice_data: Dados da nota fiscal
            xml_content: Conteúdo XML (opcional)
        
        Returns:
            Dict com resultado da validação
        """
        logger.info(f"✓ Validando NF {invoice_data.get('numero', 'N/A')}")
        
        start_time = datetime.utcnow()
        errors = []
        warnings = []
        
        # 1. Validar campos obrigatórios
        field_errors = self._check_required_fields(invoice_data)
        errors.extend(field_errors)
        
        # 2. Validar formatos
        format_errors = self._validate_formats(invoice_data)
        errors.extend(format_errors)
        
        # 3. Validar chave de acesso
        if "chave_acesso" in invoice_data:
            access_key_result = self._validate_access_key(invoice_data["chave_acesso"])
            if not access_key_result["valid"]:
                errors.append(access_key_result["error"])
        else:
            warnings.append("Chave de acesso não fornecida")
        
        # 4. Validar XML (se fornecido)
        if xml_content:
            xml_errors = self._validate_xml_schema(xml_content)
            errors.extend(xml_errors)
            
            signature_result = self._validate_signature(xml_content)
            if not signature_result["valid"]:
                errors.append(signature_result["error"])
        
        # 5. Validações customizadas com LLM (se necessário)
        if len(errors) == 0 and settings.DEBUG:
            llm_validation = await self._deep_validation_with_llm(invoice_data)
            warnings.extend(llm_validation.get("warnings", []))
        
        # Resultado
        is_valid = len(errors) == 0
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        result = {
            "valid": is_valid,
            "errors": errors,
            "warnings": warnings,
            "details": {
                "numero_nf": invoice_data.get("numero"),
                "total_errors": len(errors),
                "total_warnings": len(warnings),
                "processing_time_seconds": round(processing_time, 2),
                "checks_performed": [
                    "campos_obrigatorios",
                    "formatos",
                    "chave_acesso",
                ]
            },
            "timestamp": datetime.utcnow().isoformat(),
            "agent": "ValidationAgent",
            "version": "1.0.0"
        }
        
        status = "✅ VÁLIDA" if is_valid else "❌ INVÁLIDA"
        logger.info(
            f"{status} - NF {invoice_data.get('numero')} - "
            f"Erros: {len(errors)} - Avisos: {len(warnings)}"
        )
        
        return result
    
    def _check_required_fields(self, invoice: Dict) -> List[str]:
        """
        Verifica campos obrigatórios
        """
        errors = []
        
        required_fields = {
            "numero": "Número da NF",
            "serie": "Série",
            "data_emissao": "Data de emissão",
            "cnpj_emitente": "CNPJ do emitente",
            "cnpj_destinatario": "CNPJ do destinatário",
            "cfop": "CFOP",
            "valor_total": "Valor total",
        }
        
        for field, label in required_fields.items():
            if field not in invoice or invoice[field] in [None, "", []]:
                errors.append(f"Campo obrigatório ausente ou vazio: {label} ({field})")
        
        return errors
    
    def _validate_formats(self, invoice: Dict) -> List[str]:
        """
        Valida formato dos campos
        """
        errors = []
        
        # CNPJ (14 dígitos)
        for field in ["cnpj_emitente", "cnpj_destinatario"]:
            if field in invoice:
                cnpj = str(invoice[field]).replace(".", "").replace("/", "").replace("-", "")
                if not re.match(r'^\d{14}$', cnpj):
                    errors.append(f"{field}: deve ter 14 dígitos")
        
        # Data (YYYY-MM-DD ou DD/MM/YYYY)
        if "data_emissao" in invoice:
            date_str = str(invoice["data_emissao"])
            if not (re.match(r'^\d{4}-\d{2}-\d{2}$', date_str) or 
                    re.match(r'^\d{2}/\d{2}/\d{4}$', date_str)):
                errors.append("data_emissao: formato inválido (use YYYY-MM-DD ou DD/MM/YYYY)")
        
        # CFOP (4 dígitos)
        if "cfop" in invoice:
            cfop = str(invoice["cfop"])
            if not re.match(r'^\d{4}$', cfop):
                errors.append("cfop: deve ter 4 dígitos")
        
        # Valores numéricos
        numeric_fields = ["valor_total", "valor_produtos", "valor_icms"]
        for field in numeric_fields:
            if field in invoice:
                try:
                    value = float(invoice[field])
                    if value < 0:
                        errors.append(f"{field}: não pode ser negativo")
                except (ValueError, TypeError):
                    errors.append(f"{field}: deve ser numérico")
        
        return errors
    
    # def _validate_access_key(self, key: str) -> Dict[str, Any]:
    #     """
    #     Valida chave de acesso da NF-e
        
    #     Formato: 44 dígitos
    #     Estrutura: UF(2) + AAMM(4) + CNPJ(14) + Modelo(2) + Serie(3) + Numero(9) + Tipo(1) + Codigo(8) + DV(1)
    #     """
    #     # Remover espaços e caracteres não numéricos
    #     clean_key = re.sub(r'[^0-9]', '', key)
        
    #     # Verificar tamanho
    #     if len(clean_key) != 44:
    #         return {
    #             "valid": False,
    #             "error": f"Chave de acesso deve ter 44 dígitos (fornecido: {len(clean_key)})"
    #         }
        
    #     # Validar dígito verificador
    #     # Simplificado - em produção, usar cálculo real do módulo 11
    #     dv_fornecido = int(clean_key[-1])
    #     dv_calculado = self._calculate_access_key_dv(clean_key[:-1])
        
    #     if dv_fornecido != dv_calculado:
    #         return {
    #             "valid": False,
    #             "error": f"Dígito verificador inválido (esperado {dv_calculado}, fornecido {dv_fornecido})"
    #         }
        
    #     return {"valid": True}
    # (Opcional, mas recomendado: mude o 'key: str' para 'key: str | None')
    def _validate_access_key(self, key: str | None) -> Dict[str, Any]:
        """
        Valida chave de acesso da NF-e
        ...
        """
        
        # -----------------------------------------------------------------
        # CORREÇÃO: Adicione esta "guarda" no início da função
        # -----------------------------------------------------------------
        # Isso verifica se a 'key' é None ou uma string vazia
        if not key:
            return {
                "valid": False,
                "error": "Chave de acesso não fornecida (valor nulo ou vazio)"
            }
        # -----------------------------------------------------------------

        # Remover espaços e caracteres não numéricos
        # Se o código chegou aqui, 'key' é uma string e re.sub é seguro
        clean_key = re.sub(r'[^0-9]', '', key)
        
        # Verificar tamanho
        if len(clean_key) != 44:
            return {
                "valid": False,
                "error": f"Chave de acesso deve ter 44 dígitos (fornecido: {len(clean_key)})"
            }
        
        # Validar dígito verificador
        # Simplificado - em produção, usar cálculo real do módulo 11
        dv_fornecido = int(clean_key[-1])
        dv_calculado = self._calculate_access_key_dv(clean_key[:-1])
        
        if dv_fornecido != dv_calculado:
            return {
                "valid": False,
                "error": f"Dígito verificador inválido (esperado {dv_calculado}, fornecido {dv_fornecido})"
            }
        
        return {"valid": True}
    
    def _calculate_access_key_dv(self, key_without_dv: str) -> int:
        """
        Calcula dígito verificador da chave de acesso
        Algoritmo: Módulo 11
        """
        # Pesos de 2 a 9 repetidos
        peso = [2, 3, 4, 5, 6, 7, 8, 9] * 6  # Ajustar conforme necessário
        
        soma = 0
        for i, digit in enumerate(reversed(key_without_dv)):
            soma += int(digit) * peso[i % len(peso)]
        
        resto = soma % 11
        
        # Se resto for 0 ou 1, DV = 0, senão DV = 11 - resto
        if resto in [0, 1]:
            return 0
        else:
            return 11 - resto
    
    def _validate_xml_schema(self, xml_content: str) -> List[str]:
        """
        Valida XML contra schema XSD da NF-e
        
        MOCK: Em produção, usar biblioteca lxml para validação real
        """
        errors = []
        
        # Mock validation
        if not xml_content or len(xml_content) < 100:
            errors.append("XML muito curto ou vazio")
        
        if "<NFe" not in xml_content and "<nfe" not in xml_content.lower():
            errors.append("XML não parece ser uma NF-e válida (tag NFe não encontrada)")
        
        # Verificar tags essenciais
        essential_tags = ["<ide>", "<emit>", "<dest>", "<det>", "<total>"]
        for tag in essential_tags:
            if tag.lower() not in xml_content.lower():
                errors.append(f"Tag essencial ausente no XML: {tag}")
        
        return errors
    
    def _validate_signature(self, xml_content: str) -> Dict[str, Any]:
        """
        Valida assinatura digital do XML
        
        MOCK: Em produção, usar biblioteca de validação de certificado digital
        """
        # Mock validation
        if "<Signature" not in xml_content and "<signature" not in xml_content.lower():
            return {
                "valid": False,
                "error": "Assinatura digital não encontrada no XML"
            }
        
        # Simular validação bem-sucedida
        return {"valid": True}
    
    async def _deep_validation_with_llm(self, invoice: Dict) -> Dict:
        """
        Validação profunda usando LLM
        Para casos complexos ou ambíguos
        """
        prompt = f"""
        Analise esta nota fiscal e identifique possíveis problemas estruturais ou inconsistências:
        
        {invoice}
        
        Retorne em JSON:
        {{
            "warnings": ["aviso 1", "aviso 2"],
            "suggestions": ["sugestão 1", "sugestão 2"]
        }}
        """
        
        messages = [
            SystemMessage(content="Você é um validador de notas fiscais."),
            HumanMessage(content=prompt)
        ]
        
        try:
            response = await self.llm.ainvoke(messages)
            
            import json
            result = json.loads(response.content)
            return result
        except Exception as e:
            logger.warning(f"Erro na validação com LLM: {e}")
            return {"warnings": [], "suggestions": []}
