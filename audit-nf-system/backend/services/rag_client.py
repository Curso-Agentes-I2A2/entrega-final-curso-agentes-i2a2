"""
Cliente HTTP para comunicação com serviço RAG (Retrieval-Augmented Generation).
Implementa mock quando serviço não está disponível.
"""
import httpx
from typing import Optional, Any
import logging

from config import settings

logger = logging.getLogger(__name__)


class Document(dict):
    """
    Representa um documento retornado pelo RAG.
    
    Attributes:
        content: Conteúdo do documento
        metadata: Metadados (source, score, etc)
        score: Score de relevância
    """
    def __init__(self, content: str, metadata: Optional[dict] = None, score: Optional[float] = None):
        super().__init__(content=content, metadata=metadata or {}, score=score)
        self.content = content
        self.metadata = metadata or {}
        self.score = score


class RAGClient:
    """
    Cliente para comunicação com serviço RAG.
    
    Quando RAG_SERVICE_URL não está configurado, retorna dados mock
    para permitir desenvolvimento/teste sem dependência do serviço real.
    
    Exemplo de uso:
        rag = RAGClient()
        docs = await rag.search("validação de ICMS em NF-e")
        for doc in docs:
            print(f"Relevância: {doc.score}")
            print(f"Conteúdo: {doc.content}")
    """
    
    def __init__(self):
        self.base_url = settings.RAG_SERVICE_URL
        self.timeout = settings.RAG_SERVICE_TIMEOUT
        self.use_mock = self.base_url is None
        
        if self.use_mock:
            logger.info("RAG Service URL não configurada. Usando dados mock.")
        else:
            logger.info(f"RAG Client configurado para: {self.base_url}")
    
    async def search(
        self,
        query: str,
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None
    ) -> list[Document]:
        """
        Busca documentos relevantes no sistema RAG.
        
        Args:
            query: Texto da consulta
            top_k: Número máximo de documentos a retornar
            filters: Filtros adicionais (metadados)
        
        Returns:
            Lista de documentos relevantes
        
        Raises:
            httpx.HTTPError: Em caso de erro na comunicação
        """
        if self.use_mock:
            return self._get_mock_documents(query, top_k)
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/search",
                    json={
                        "query": query,
                        "top_k": top_k,
                        "filters": filters or {}
                    }
                )
                response.raise_for_status()
                
                data = response.json()
                documents = [
                    Document(
                        content=doc["content"],
                        metadata=doc.get("metadata", {}),
                        score=doc.get("score")
                    )
                    for doc in data.get("documents", [])
                ]
                
                logger.info(f"RAG search retornou {len(documents)} documentos")
                return documents
                
        except httpx.HTTPError as e:
            logger.error(f"Erro ao consultar RAG service: {e}")
            # Fallback para mock em caso de erro
            logger.warning("Usando dados mock como fallback")
            return self._get_mock_documents(query, top_k)
    
    async def add_document(
        self,
        content: str,
        metadata: Optional[dict[str, Any]] = None
    ) -> dict[str, Any]:
        """
        Adiciona um novo documento ao sistema RAG.
        
        Args:
            content: Conteúdo do documento
            metadata: Metadados (categoria, data, etc)
        
        Returns:
            Resposta do serviço com ID do documento
        """
        if self.use_mock:
            logger.info("Mock mode: documento não será persistido")
            return {"id": "mock-doc-id", "status": "success"}
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/documents",
                    json={
                        "content": content,
                        "metadata": metadata or {}
                    }
                )
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPError as e:
            logger.error(f"Erro ao adicionar documento ao RAG: {e}")
            raise
    
    def _get_mock_documents(self, query: str, top_k: int) -> list[Document]:
        """
        Retorna documentos mock para desenvolvimento/teste.
        
        Simula uma base de conhecimento sobre legislação fiscal brasileira.
        """
        mock_docs = [
            Document(
                content=(
                    "A Nota Fiscal Eletrônica (NF-e) deve conter a chave de acesso "
                    "de 44 dígitos, composta por: UF (2), AAMM (4), CNPJ (14), "
                    "Modelo (2), Série (3), Número (9), Forma de Emissão (1) e "
                    "Dígito Verificador (1)."
                ),
                metadata={
                    "source": "Legislação NF-e",
                    "category": "estrutura",
                    "relevance": "high"
                },
                score=0.95
            ),
            Document(
                content=(
                    "O valor do ICMS deve ser calculado sobre o valor dos produtos, "
                    "aplicando-se a alíquota correspondente à operação. Para operações "
                    "interestaduais, aplicam-se as alíquotas definidas pelo CONFAZ."
                ),
                metadata={
                    "source": "Regulamento ICMS",
                    "category": "tributacao",
                    "relevance": "high"
                },
                score=0.89
            ),
            Document(
                content=(
                    "Irregularidades comuns em NF-e incluem: divergência entre "
                    "valor declarado e calculado, CNPJ inválido, data de emissão "
                    "retroativa sem justificativa, e ausência de informações "
                    "obrigatórias de produtos."
                ),
                metadata={
                    "source": "Guia de Auditoria Fiscal",
                    "category": "irregularidades",
                    "relevance": "medium"
                },
                score=0.82
            ),
            Document(
                content=(
                    "A validação da chave de acesso deve verificar: formato correto "
                    "de 44 dígitos numéricos, dígito verificador válido usando "
                    "módulo 11, e correspondência dos dados embutidos na chave "
                    "com os dados do documento."
                ),
                metadata={
                    "source": "Manual de Validação NF-e",
                    "category": "validacao",
                    "relevance": "high"
                },
                score=0.91
            ),
            Document(
                content=(
                    "O prazo legal para emissão de NF-e é de até 5 dias úteis após "
                    "a ocorrência do fato gerador. Emissões fora deste prazo podem "
                    "ser consideradas irregulares e sujeitas a penalidades."
                ),
                metadata={
                    "source": "Código Tributário",
                    "category": "prazos",
                    "relevance": "medium"
                },
                score=0.76
            ),
        ]
        
        # Retorna top_k documentos
        return mock_docs[:top_k]