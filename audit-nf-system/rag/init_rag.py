
# import logging
# from indexing.indexer import DocumentIndexer
# from retrieval.query_engine import QueryEngine

import logging
from .indexing.indexer import DocumentIndexer
from .retrieval.query_engine import QueryEngine



# Configuração do logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_initialization():
    """
    Executa a indexação inicial e um teste de busca.
    """
    logging.info("--- Iniciando o processo de inicialização do RAG ---")
    
    # 1. Indexar os documentos
    logging.info("Passo 1: Indexando documentos da pasta './data/sample_docs/'...")
    try:
        indexer = DocumentIndexer()
        indexer.index_folder("./data/sample_docs/")
        logging.info("Indexação concluída com sucesso.")
    except Exception as e:
        logging.error(f"Falha na indexação: {e}", exc_info=True)
        return

    # 2. Testar a busca
    logging.info("\nPasso 2: Realizando uma busca de teste...")
    try:
        engine = QueryEngine()
        query = "Qual a alíquota do ICMS para estados do Sul?"
        logging.info(f"Query de teste: '{query}'")
        
        results = engine.search_with_score(query, k=2)
        
        if not results:
            logging.warning("A busca de teste não retornou resultados. Verifique a indexação.")
        else:
            logging.info("Resultados da busca de teste:")
            for doc, score in results:
                print("-" * 20)
                print(f"Score de Similaridade: {score:.4f}")
                print(f"Fonte: {doc.metadata.get('source')}")
                print(f"Conteúdo do Chunk: {doc.page_content[:300]}...")
                print("-" * 20)
        
    except Exception as e:
        logging.error(f"Falha na busca de teste: {e}", exc_info=True)

    logging.info("\n--- Processo de inicialização do RAG concluído ---")

if __name__ == "__main__":
    run_initialization()
