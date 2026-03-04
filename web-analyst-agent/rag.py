# Legacy compatibility wrapper - use infrastructure/vector_store.py for new code
from infrastructure.vector_store import FAISSVectorStore
from infrastructure.llm import OpenAIEmbedding
from infrastructure.text_processing import chunk_text
import os

# Maintain backward compatibility
VectorStore = FAISSVectorStore

def build_vector_store(source_contents, kb_docs):
    from config import AppConfig
    config = AppConfig.from_env()
    
    embedding = OpenAIEmbedding(config.openai_api_key, config.embedding_model)
    store = FAISSVectorStore(embedding)
    
    all_texts = []
    all_metadata = []
    
    for kb_name, kb_content in kb_docs:
        chunks = chunk_text(kb_content, chunk_size=600, overlap=50)
        for chunk in chunks:
            all_texts.append(chunk)
            all_metadata.append({"source": "kb", "kb_name": kb_name})
    
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
