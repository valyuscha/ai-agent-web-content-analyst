import faiss
import numpy as np
from typing import List, Tuple
from core.interfaces import VectorStoreInterface, EmbeddingProvider

class FAISSVectorStore(VectorStoreInterface):
    def __init__(self, embedding_provider: EmbeddingProvider):
        self.embedding_provider = embedding_provider
        self.index = None
        self.texts = []
        self.metadata = []
        self.dimension = 1536
    
    def build(self, texts: List[str], metadata: List[dict] = None):
        if not texts:
            return
        
        self.texts = texts
        self.metadata = metadata or [{"source": "unknown"} for _ in texts]
        
        embeddings = self.embedding_provider.embed(texts)
        self.dimension = embeddings.shape[1]
        
        self.index = faiss.IndexFlatL2(self.dimension)
        self.index.add(embeddings)
    
    def retrieve(self, query: str, top_k: int = 5) -> List[Tuple[str, dict, float]]:
        if not self.index or self.index.ntotal == 0:
            return []
        
        query_embedding = self.embedding_provider.embed([query])
        distances, indices = self.index.search(query_embedding, min(top_k, self.index.ntotal))
        
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(self.texts):
                results.append((self.texts[idx], self.metadata[idx], float(dist)))
        
        return results
