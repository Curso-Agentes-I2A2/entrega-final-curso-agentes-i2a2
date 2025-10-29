"""
API Routes - Rotas da API
Endpoints para auditoria, validação e geração de NF-e
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field

from orchestrator.coordinator import AgentCoordinator
from synthetic_agent.nf_generator import generate_valid_invoice, generate_invalid_invoice

logger = logging.getLogger(__name__)

# Criar router
router = APIRouter(tags=["agents"])

# Instância global do coordenador (será injetada via dependency)
_coordinator: Optional[AgentCoordinator] = None


def get_coordinator() -> AgentCoordinator:
    """
    Dependency injection para obter coordenador
    """
    global _coordinator
    if _coordinator is None:
        _coordinator = AgentCoordinator()
    return _coordinator


# ========================================================================
# MODELOS PYDANTIC
# ========================================================================

class InvoiceData(BaseModel):
    """
    Modelo de dados da nota fiscal
    """
    numero: str = Field(..., description="Número da NF")
    serie: str = Field(default="1", description="Série da NF")
    data_emissao: str = Field(..., description="Data de emissão (YYYY-MM-DD)")
    
    cnpj_emitente: str = Field(..., description="CNPJ do emitente")
    razao_social_emitente: Optional[str] = Field(None, description="Razão social do emitente")
    
    cnpj_destinatario: str = Field(..., description="CNPJ do destinatário")
    razao_social_destinatario: Optional[str] = Field(None, description="Razão social do destinatário")
    
    cfop: str = Field(..., description="CFOP")
    tipo_operacao: str = Field(default="venda", description="Tipo de operação")
    
    valor_produtos: float = Field(..., description="Valor total dos produtos")
    valor_total: float = Field(..., description="Valor total da NF")
    
    base_calculo_icms: Optional[float] = Field(None, description="Base de cálculo ICMS")
    aliquota_icms: Optional[float] = Field(None, description="Alíquota ICMS (%)")
    valor_icms: Optional[float] = Field(None, description="Valor ICMS")
    
    valor_ipi: Optional[float] = Field(default=0.0, description="Valor IPI")
    valor_pis: Optional[float] = Field(default=0.0, description="Valor PIS")
    valor_cofins: Optional[float] = Field(default=0.0, description="Valor COFINS")
    
    chave_acesso: Optional[str] = Field(None, description="Chave de acesso")
    xml_content: Optional[str] = Field(None, description="Conteúdo XML da NF")
    
    class Config:
        json_schema_extra = {
            "example": {
                "numero": "000123",
                "serie": "1",
                "data_emissao": "2025-10-27",
                "cnpj_emitente": "12345678000190",
                "razao_social_emitente": "Empresa Exemplo LTDA",
                "cnpj_destinatario": "98765432000199",
                "razao_social_destinatario": "Cliente Teste SA",
                "cfop": "5102",
                "tipo_operacao": "venda",
                "valor_produtos": 1000.00,
                "valor_total": 1180.00,
                "base_calculo_icms": 1000.00,
                "aliquota_icms": 18.0,
                "valor_icms": 180.00,
            }
        }


class AuditRequest(BaseModel):
    """
    Request para auditoria
    """
    invoice: InvoiceData
    context: Optional[Dict[str, Any]] = Field(default=None, description="Contexto adicional")
    
    class Config:
        json_schema_extra = {
            "example": {
                "invoice": InvoiceData.Config.json_schema_extra["example"],
                "context": {
                    "historico_fornecedor": "sem_pendencias",
                    "primeira_compra": False
                }
            }
        }


class ValidationRequest(BaseModel):
    """
    Request para validação
    """
    invoice: InvoiceData
    xml_content: Optional[str] = None


class GenerateSyntheticRequest(BaseModel):
    """
    Request para geração de NF sintética
    """
    tipo: str = Field(default="valida", description="Tipo: valida, invalida, suspeita")
    valor_max: float = Field(default=10000.0, description="Valor máximo")
    estado: str = Field(default="SP", description="Estado")


class AuditResponse(BaseModel):
    """
    Response da auditoria
    """
    aprovada: bool
    irregularidades: list
    confianca: float
    justificativa: str
    detalhes: Dict[str, Any]
    timestamp: str


# ========================================================================
# ENDPOINTS
# ========================================================================

@router.post("/audit", response_model=AuditResponse, summary="Auditar Nota Fiscal")
async def audit_invoice(
    request: AuditRequest,
    coordinator: AgentCoordinator = Depends(get_coordinator)
):
    """
    Audita uma nota fiscal completa
    
    Executa:
    1. Validação estrutural
    2. Auditoria fiscal
    3. Retorna decisão final
    
    Returns:
        Resultado da auditoria com decisão de aprovação/reprovação
    """
    logger.info(f"📨 Recebida requisição de auditoria: NF {request.invoice.numero}")
    
    try:
        # Converter Pydantic model para dict
        invoice_dict = request.invoice.model_dump()
        
        # Processar
        result = await coordinator.process_invoice(
            invoice_data=invoice_dict,
            xml_content=request.invoice.xml_content,
            context=request.context
        )
        
        return result
    
    except Exception as e:
        logger.error(f"❌ Erro na auditoria: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar auditoria: {str(e)}"
        )


@router.post("/validate", summary="Validar Estrutura da NF")
async def validate_invoice(
    request: ValidationRequest,
    coordinator: AgentCoordinator = Depends(get_coordinator)
):
    """
    Valida apenas a estrutura da nota fiscal
    
    Não executa auditoria fiscal, apenas validação técnica e estrutural.
    
    Returns:
        Resultado da validação
    """
    logger.info(f"📨 Recebida requisição de validação: NF {request.invoice.numero}")
    
    try:
        invoice_dict = request.invoice.model_dump()
        
        result = await coordinator.validation_agent.validate_invoice(
            invoice_data=invoice_dict,
            xml_content=request.xml_content
        )
        
        return result
    
    except Exception as e:
        logger.error(f"❌ Erro na validação: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar validação: {str(e)}"
        )


@router.post("/generate", summary="Gerar NF Sintética")
async def generate_synthetic_invoice(request: GenerateSyntheticRequest):
    """
    Gera nota fiscal sintética para testes
    
    Tipos disponíveis:
    - valida: NF completamente válida
    - invalida: NF com erros propositais (CFOP errado, cálculos incorretos)
    - suspeita: NF válida mas com padrões suspeitos
    
    Returns:
        Dados da nota fiscal sintética
    """
    logger.info(f"📨 Gerando NF sintética: tipo={request.tipo}")
    
    try:
        if request.tipo == "invalida":
            invoice = generate_invalid_invoice(
                max_value=request.valor_max,
                state=request.estado
            )
        else:
            invoice = generate_valid_invoice(
                max_value=request.valor_max,
                state=request.estado
            )
        
        return {
            "success": True,
            "tipo": request.tipo,
            "invoice": invoice,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"❌ Erro ao gerar NF sintética: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao gerar NF: {str(e)}"
        )


@router.post("/audit/batch", summary="Auditar Múltiplas NFs")
async def audit_batch(
    invoices: list[InvoiceData],
    background_tasks: BackgroundTasks,
    coordinator: AgentCoordinator = Depends(get_coordinator)
):
    """
    Audita múltiplas notas fiscais em lote
    
    Processa as notas de forma assíncrona e retorna ID do job.
    Use endpoint /audit/batch/{job_id} para verificar status.
    """
    logger.info(f"📨 Recebida requisição de auditoria em lote: {len(invoices)} notas")
    
    # TODO: Implementar processamento assíncrono real com Celery ou similar
    # Por enquanto, processar sequencialmente
    
    results = []
    for invoice in invoices[:10]:  # Limitar a 10 por request
        try:
            invoice_dict = invoice.model_dump()
            result = await coordinator.process_invoice(invoice_data=invoice_dict)
            results.append({
                "numero": invoice.numero,
                "status": "processed",
                "result": result
            })
        except Exception as e:
            results.append({
                "numero": invoice.numero,
                "status": "error",
                "error": str(e)
            })
    
    return {
        "total": len(invoices),
        "processed": len(results),
        "results": results,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/stats", summary="Estatísticas do Sistema")
async def get_stats():
    """
    Retorna estatísticas de uso do sistema
    """
    # TODO: Implementar tracking real de estatísticas
    
    return {
        "total_auditorias": 0,
        "aprovadas": 0,
        "reprovadas": 0,
        "taxa_aprovacao": 0.0,
        "tempo_medio_processamento": 0.0,
        "uptime_seconds": 0.0,
        "timestamp": datetime.utcnow().isoformat()
    }


# ========================================================================
# HEALTH CHECK
# ========================================================================

@router.get("/agents/health", summary="Health Check dos Agentes")
async def agents_health(coordinator: AgentCoordinator = Depends(get_coordinator)):
    """
    Verifica saúde dos agentes
    """
    return {
        "status": "healthy",
        "agents": {
            "validation_agent": "operational" if coordinator.validation_agent else "disabled",
            "audit_agent": "operational" if coordinator.audit_agent else "disabled",
        },
        "timestamp": datetime.utcnow().isoformat()
    }
