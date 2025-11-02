# backend/api/routes/synthetic_routes.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from decimal import Decimal
from typing import Optional
import logging

# --- Importações principais do seu projeto ---
from database.connection import get_db
from schemas.invoice_schema import InvoiceResponse

# 1. Importa o seu Gerador de XML
# (Confirmamos que ele está em 'src/synthetic_nf/generator.py')
try:
    from src.synthetic_nf.generator import SyntheticNFeGenerator
except ImportError:
    logging.error("Falha ao importar SyntheticNFeGenerator. Verifique o caminho.")
    SyntheticNFeGenerator = None 

# 2. Importa o seu Serviço de Fatura
# (Confirmamos que ele está em 'services/invoice_service.py')
try:
    from services.invoice_service import InvoiceService
except ImportError:
    logging.error("Falha ao importar InvoiceService. Verifique o caminho.")
    InvoiceService = None


logger = logging.getLogger(__name__)

# --- Configuração do Router ---
router = APIRouter(
    prefix="/api/synthetic",  # <-- CORREÇÃO: Adicione o /api aqui
    tags=["Synthetic Data (Testing)"]
)

# --- Modelo Pydantic para o "corpo" da requisição ---
# Permite que você envie opções para o gerador
class GenerationOptions(BaseModel):
    """Opções para customizar a NF-e sintética gerada."""
    numero: Optional[int] = None
    serie: Optional[int] = None
    valor_total: Optional[Decimal] = None
    com_irregularidades: bool = False


# --- Definição do Endpoint ---
@router.post(
    "/generate-and-save",
    response_model=InvoiceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Gera e Salva uma NF-e Sintética"
)
async def generate_and_save_synthetic_invoice(
    options: GenerationOptions,
    db: AsyncSession = Depends(get_db)
):
    """
    Inicia o gerador de NF-e sintética, cria um XML e o salva no banco.
    
    Este endpoint simula um upload de XML, mas com dados gerados na hora.
    É perfeito para popular o banco de dados para testes.
    """
    
    logger.info(f"Recebida requisição para gerar NF-e sintética: {options}")
    
    # Verifica se os módulos foram importados corretamente
    if not SyntheticNFeGenerator or not InvoiceService:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Gerador sintético ou serviço de invoice não foi importado corretamente."
        )

    # 1. Instanciar o gerador
    generator = SyntheticNFeGenerator()
    
    # 2. Gerar o XML como string
    try:
        xml_string = generator.generate(
            numero=options.numero,
            serie=options.serie,
            valor_total=options.valor_total,
            com_irregularidades=options.com_irregularidades
        )
        
    except Exception as e:
        logger.error(f"Erro ao gerar o XML sintético: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro na geração do XML: {e}"
        )
    
    # 3. Instanciar o serviço e salvar o XML (exatamente como o /upload faz)
    service = InvoiceService(db=db)
    
    try:
        # Usando o método create_from_xml que já existe no seu serviço
        invoice = await service.create_from_xml(xml_content=xml_string)
        
        logger.info(f"NF-e sintética gerada e salva com sucesso: {invoice.id}")
        return invoice
        
    except ValueError as e:
        # Captura erros de duplicidade (baseado na nossa correção anterior)
        error_str = str(e).lower()
        if "duplicate key" in error_str or "unique constraint" in error_str:
            logger.warning(f"Tentativa de gerar NF-e sintética duplicada: {e}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Nota fiscal sintética já cadastrada (chave duplicada)"
            )
        else:
            # Captura outros erros de validação do XML
            logger.warning(f"Erro de valor ao salvar NF-e sintética: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Erro de validação: {str(e)}"
            )
    except Exception as e:
        logger.error(f"Erro inesperado ao salvar NF-e sintética: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao salvar a nota fiscal no banco: {e}"
        )