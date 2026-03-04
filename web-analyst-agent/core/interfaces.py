from abc import ABC, abstractmethod
from typing import List, Tuple
import numpy as np

class EmbeddingProvider(ABC):
    @abstractmethod
    def embed(self, texts: List[str]) -> np.ndarray:
        pass

class VectorStoreInterface(ABC):
    @abstractmethod
    def build(self, texts: List[str], metadata: List[dict]):
        pass
    
    @abstractmethod
    def retrieve(self, query: str, top_k: int) -> List[Tuple[str, dict, float]]:
        pass

class LLMProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str, temperature: float, json_mode: bool) -> str:
        pass

class ContentExtractor(ABC):
    @abstractmethod
    def extract(self, url: str) -> Tuple[str, str, Optional[str]]:
        """Returns (content, title, error)"""
        pass
