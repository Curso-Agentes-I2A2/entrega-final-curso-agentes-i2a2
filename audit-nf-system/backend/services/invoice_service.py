"""
Service de lógica de negócio para Notas Fiscais.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from uuid import UUID
from datetime import datetime
from decimal import Decimal
import logging
from lxml import etree

from models.invoice import Invoice, InvoiceStatus
from schemas.invoice_schema import InvoiceCreate, InvoiceUpdate, InvoiceList, InvoiceListItem
from services.rag_client import RAGClient

logger = logging.getLogger(__name__)


class InvoiceService:
    """
    Service para gerenciar operações de Notas Fiscais.
    
    Responsável por:
    - Processar e validar XMLs de NF-e
    - Criar e atualizar registros no banco
    - Integrar com serviço RAG para enriquecimento
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.rag_client = RAGClient()
    
    async def create_from_xml(self, xml_content: str) -> Invoice:
        """
        Cria uma nota fiscal a partir do conteúdo XML.
        
        Extrai informações do XML da NF-e e cria registro no banco.
        
        Args:
            xml_content: Conteúdo completo do XML da NF-e
        
        Returns:
            Invoice: Nota fiscal criada
        
        Raises:
            ValueError: Se XML for inválido ou dados obrigatórios estiverem faltando
        """
        try:
            # Parse do XML
            nfe_data = self._parse_nfe_xml(xml_content)
            
            # Cria objeto Invoice
            invoice = Invoice(
                numero=nfe_data["numero"],
                serie=nfe_data["serie"],
                chave_acesso=nfe_data["chave_acesso"],
                cnpj_emitente=nfe_data["cnpj_emitente"],
                razao_social_emitente=nfe_data["razao_social_emitente"],
                cnpj_destinatario=nfe_data["cnpj_destinatario"],
                razao_social_destinatario=nfe_data["razao_social_destinatario"],
                valor_total=Decimal(str(nfe_data["valor_total"])),
                valor_produtos=Decimal(str(nfe_data.get("valor_produtos", 0))),
                valor_icms=Decimal(str(nfe_data.get("valor_icms", 0))),
                valor_ipi=Decimal(str(nfe_data.get("valor_ipi", 0))),
                data_emissao=nfe_data["data_emissao"],
                natureza_operacao=nfe_data.get("natureza_operacao"),
                xml_content=xml_content,
                status=InvoiceStatus.PENDENTE
            )
            
            # Salva no banco
            self.db.add(invoice)
            await self.db.commit()
            await self.db.refresh(invoice)
            
            logger.info(f"Nota fiscal criada: {invoice.chave_acesso}")
            
            # Indexa no RAG para futuras consultas (async, não bloqueia)
            try:
                await self._index_invoice_in_rag(invoice)
            except Exception as e:
                logger.warning(f"Erro ao indexar NF no RAG: {e}")
            
            return invoice
            
        except Exception as e:
            logger.error(f"Erro ao criar nota fiscal: {e}")
            raise ValueError(f"Erro ao processar XML da NF-e: {str(e)}")
    
    async def get_by_id(self, invoice_id: UUID) -> Optional[Invoice]:
        """Busca nota fiscal por ID."""
        result = await self.db.execute(
            select(Invoice).where(Invoice.id == invoice_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_chave_acesso(self, chave_acesso: str) -> Optional[Invoice]:
        """Busca nota fiscal por chave de acesso."""
        result = await self.db.execute(
            select(Invoice).where(Invoice.chave_acesso == chave_acesso)
        )
        return result.scalar_one_or_none()
    
    async def list_invoices(
        self,
        page: int = 1,
        page_size: int = 20,
        status: Optional[InvoiceStatus] = None,
        cnpj_emitente: Optional[str] = None,
        data_inicio: Optional[datetime] = None,
        data_fim: Optional[datetime] = None
    ) -> InvoiceList:
        """
        Lista notas fiscais com paginação e filtros.
        
        Args:
            page: Número da página (1-indexed)
            page_size: Tamanho da página
            status: Filtro por status
            cnpj_emitente: Filtro por CNPJ do emitente
            data_inicio: Filtro por data inicial
            data_fim: Filtro por data final
        
        Returns:
            InvoiceList com total e itens paginados
        """
        # Query base
        query = select(Invoice)
        
        # Aplica filtros
        if status:
            query = query.where(Invoice.status == status)
        if cnpj_emitente:
            query = query.where(Invoice.cnpj_emitente == cnpj_emitente)
        if data_inicio:
            query = query.where(Invoice.data_emissao >= data_inicio)
        if data_fim:
            query = query.where(Invoice.data_emissao <= data_fim)
        
        # Conta total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Aplica paginação e ordenação
        query = query.order_by(Invoice.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        # Executa query
        result = await self.db.execute(query)
        invoices = result.scalars().all()
        
        # Converte para schema
        items = [InvoiceListItem.model_validate(inv) for inv in invoices]
        
        return InvoiceList(
            total=total,
            page=page,
            page_size=page_size,
            items=items
        )
    
    async def update(self, invoice_id: UUID, update_data: InvoiceUpdate) -> Optional[Invoice]:
        """
        Atualiza dados de uma nota fiscal.
        
        Args:
            invoice_id: ID da nota fiscal
            update_data: Dados para atualização
        
        Returns:
            Invoice atualizada ou None se não encontrada
        """
        invoice = await self.get_by_id(invoice_id)
        if not invoice:
            return None
        
        # Atualiza apenas campos fornecidos
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(invoice, field, value)
        
        await self.db.commit()
        await self.db.refresh(invoice)
        
        logger.info(f"Nota fiscal atualizada: {invoice_id}")
        return invoice
    
    def _parse_nfe_xml(self, xml_content: str) -> dict:
        """
        Extrai dados principais do XML da NF-e.
        
        Args:
            xml_content: String com conteúdo XML
        
        Returns:
            Dicionário com dados extraídos
        
        Raises:
            ValueError: Se XML for inválido
        """
        try:
            root = etree.fromstring(xml_content.encode('utf-8'))
            
            # Define namespaces NFe
            ns = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}
            
            # Extrai dados da tag <infNFe>
            inf_nfe = root.find('.//nfe:infNFe', ns)
            ide = inf_nfe.find('nfe:ide', ns)
            emit = inf_nfe.find('nfe:emit', ns)
            dest = inf_nfe.find('nfe:dest', ns)
            total = inf_nfe.find('.//nfe:total/nfe:ICMSTot', ns)
            
            # Extrai chave de acesso do atributo Id
            chave_acesso = inf_nfe.get('Id', '').replace('NFe', '')
            
            # Monta dicionário de dados
            return {
                "numero": ide.find('nfe:nNF', ns).text,
                "serie": ide.find('nfe:serie', ns).text,
                "chave_acesso": chave_acesso,
                "cnpj_emitente": emit.find('nfe:CNPJ', ns).text,
                "razao_social_emitente": emit.find('nfe:xNome', ns).text,
                "cnpj_destinatario": dest.find('nfe:CNPJ', ns).text,
                "razao_social_destinatario": dest.find('nfe:xNome', ns).text,
                "valor_total": float(total.find('nfe:vNF', ns).text),
                "valor_produtos": float(total.find('nfe:vProd', ns).text),
                "valor_icms": float(total.find('nfe:vICMS', ns).text or 0),
                "valor_ipi": float(total.find('nfe:vIPI', ns).text or 0),
                "data_emissao": datetime.strptime(
                    ide.find('nfe:dhEmi', ns).text[:19],
                    '%Y-%m-%dT%H:%M:%S'
                ),
                "natureza_operacao": ide.find('nfe:natOp', ns).text,
            }
            
        except Exception as e:
            logger.error(f"Erro ao fazer parse do XML: {e}")
            raise ValueError(f"XML inválido ou formato não suportado: {str(e)}")
    
    async def _index_invoice_in_rag(self, invoice: Invoice) -> None:
        """
        Indexa nota fiscal no sistema RAG para busca futura.
        
        Cria um documento textual com informações da NF para alimentar
        o sistema de busca vetorial.
        """
        content = f"""
        Nota Fiscal {invoice.numero}/{invoice.serie}
        Chave: {invoice.chave_acesso}
        Emitente: {invoice.razao_social_emitente} (CNPJ: {invoice.cnpj_emitente})
        Destinatário: {invoice.razao_social_destinatario} (CNPJ: {invoice.cnpj_destinatario})
        Valor Total: R$ {invoice.valor_total}
        Data de Emissão: {invoice.data_emissao.strftime('%d/%m/%Y')}
        Natureza: {invoice.natureza_operacao}
        """
        
        metadata = {
            "invoice_id": str(invoice.id),
            "chave_acesso": invoice.chave_acesso,
            "cnpj_emitente": invoice.cnpj_emitente,
            "data_emissao": invoice.data_emissao.isoformat(),
            "tipo": "nota_fiscal"
        }
        
        await self.rag_client.add_document(content, metadata)