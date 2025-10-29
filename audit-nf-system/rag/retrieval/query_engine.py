from vector_store.chromadb.client import ChromaDBClient
from embeddings.embedding_model import EmbeddingModel

class QueryEngine:
    def __init__(self):
        self.embedding_model = EmbeddingModel()
        self.vector_store = ChromaDBClient()

    def search(self, query: str, k: int = 5, filters: dict = None):
        emb = self.embedding_model.get_embeddings([query])[0]
        results = self.vector_store.search(emb, k=k, filters=filters)
        return results["documents"], results.get("distances")

    def search_with_score(self, query: str, k: int = 5, filters: dict = None):
        docs, scores = self.search(query, k, filters)
        return list(zip(docs, scores))

# Exemplo:
# engine = QueryEngine()
# print(engine.search("Como calcular ICMS?", k=3))
