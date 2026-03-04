import numpy as np
import faiss
from typing import List, Tuple
import openai
import os

class VectorStore:
    def __init__(self, embedding_model: str = "text-embedding-3-small"):
        self.embedding_model = embedding_model
        self.index = None
        self.texts = []
        self.metadata = []
        self.dimension = 1536
        
    def embed(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings using OpenAI"""
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.embeddings.create(
            input=texts,
            model=self.embedding_model
        )
        embeddings = [item.embedding for item in response.data]
        return np.array(embeddings, dtype='float32')
    
    def build(self, texts: List[str], metadata: List[dict] = None):
        """Build FAISS index from texts"""
        if not texts:
            return
        
        self.texts = texts
        self.metadata = metadata or [{"source": "unknown"} for _ in texts]
        
        embeddings = self.embed(texts)
        self.dimension = embeddings.shape[1]
        
        self.index = faiss.IndexFlatL2(self.dimension)
        self.index.add(embeddings)
    
    def retrieve(self, query: str, top_k: int = 5) -> List[Tuple[str, dict, float]]:
        """Retrieve top-k most similar texts"""
        if not self.index or self.index.ntotal == 0:
            return []
        
        query_embedding = self.embed([query])
        distances, indices = self.index.search(query_embedding, min(top_k, self.index.ntotal))
        
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(self.texts):
                results.append((self.texts[idx], self.metadata[idx], float(dist)))
        
        return results

def build_vector_store(source_contents: List, kb_docs: List[Tuple[str, str]]) -> VectorStore:
    """Build vector store from source chunks and KB documents"""
    from tools import chunk_text
    
    store = VectorStore()
    all_texts = []
    all_metadata = []
    
    # Add KB documents
    for kb_name, kb_content in kb_docs:
        chunks = chunk_text(kb_content, chunk_size=600, overlap=50)
        for chunk in chunks:
            all_texts.append(chunk)
            all_metadata.append({"source": "kb", "kb_name": kb_name})
    
    # Add source content chunks
    for source in source_contents:
        if source.content:
            chunks = chunk_text(source.content, chunk_size=800, overlap=100)
            for chunk in chunks:
                all_texts.append(chunk)
                all_metadata.append({
                    "source": "content",
                    "url": source.url,
                    "title": source.title,
                    "type": source.type
                })
    
    if all_texts:
        store.build(all_texts, all_metadata)
    
    return store
