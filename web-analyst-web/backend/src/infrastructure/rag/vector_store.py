"""
RAG (Retrieval-Augmented Generation) with source attribution support.
"""
import numpy as np
import faiss
from typing import List, Dict, Tuple, Optional
import openai
import os


class VectorStore:
    """Vector store for semantic search with FAISS"""
    
    def __init__(self, embedding_model: str = "text-embedding-3-small"):
        self.embedding_model = embedding_model
        self.index = None
        self.chunks = []  # Store full chunk objects with metadata
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
    
    def build(self, chunks: List[Dict]):
        """
        Build FAISS index from chunks with metadata.
        
        Args:
            chunks: List of dicts with 'text' and 'metadata' keys
        """
        if not chunks:
            return
        
        self.chunks = chunks
        texts = [chunk['text'] for chunk in chunks]
        
        embeddings = self.embed(texts)
        self.dimension = embeddings.shape[1]
        
        self.index = faiss.IndexFlatL2(self.dimension)
        self.index.add(embeddings)
    
    def retrieve(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Retrieve top-k most similar chunks with metadata.
        
        Args:
            query: Search query
            top_k: Number of results to return
            
        Returns:
            List of chunk dicts with 'text', 'metadata', and 'score' keys
        """
        if not self.index or self.index.ntotal == 0:
            return []
        
        query_embedding = self.embed([query])
        distances, indices = self.index.search(
            query_embedding,
            min(top_k, self.index.ntotal)
        )
        
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(self.chunks):
                chunk = self.chunks[idx].copy()
                chunk['score'] = float(dist)
                results.append(chunk)
        
        return results


def build_vector_store_from_sources(
    source_contents: List[Dict],
    kb_docs: Optional[List[Tuple[str, str]]] = None
) -> VectorStore:
    """
    Build vector store from source chunks and optional KB documents.
    
    Args:
        source_contents: List of source dicts with chunked content
        kb_docs: Optional list of (title, content) tuples for KB
        
    Returns:
        VectorStore instance
    """
    from src.domain.chunking.sentence_chunker import chunk_text
    
    store = VectorStore()
    all_chunks = []
    
    # Add source chunks (already chunked with metadata)
    for source in source_contents:
        if 'chunks' in source:
            all_chunks.extend(source['chunks'])
    
    # Add KB documents if provided
    if kb_docs:
        for title, content in kb_docs:
            kb_chunks = chunk_text(
                content,
                source_id=f"kb-{title}",
                title=f"KB: {title}",
                max_chars=1500
            )
            # Convert to dict format
            for chunk in kb_chunks:
                all_chunks.append({
                    'text': chunk.text,
                    'metadata': {
                        'source_id': chunk.metadata.source_id,
                        'chunk_index': chunk.metadata.chunk_index,
                        'title': chunk.metadata.title,
                        'url': chunk.metadata.url
                    }
                })
    
    store.build(all_chunks)
    return store
