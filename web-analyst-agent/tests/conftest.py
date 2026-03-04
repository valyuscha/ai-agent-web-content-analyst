import pytest
from unittest.mock import Mock
from core.interfaces import LLMProvider, EmbeddingProvider, VectorStoreInterface
import numpy as np

class MockLLM(LLMProvider):
    def generate(self, prompt: str, temperature: float, json_mode: bool) -> str:
        if json_mode:
            return '{"summary": "test", "key_points": ["p1", "p2"], "action_items": []}'
        return "Test response"

class MockEmbedding(EmbeddingProvider):
    def embed(self, texts):
        return np.random.rand(len(texts), 1536).astype('float32')

class MockVectorStore(VectorStoreInterface):
    def __init__(self):
        self.built = False
        
    def build(self, texts, metadata):
        self.built = True
        
    def retrieve(self, query, top_k):
        return [("context1", {"source": "test"}, 0.5), ("context2", {"source": "test"}, 0.6)]

@pytest.fixture
def mock_llm():
    return MockLLM()

@pytest.fixture
def mock_embedding():
    return MockEmbedding()

@pytest.fixture
def mock_vector_store():
    return MockVectorStore()
