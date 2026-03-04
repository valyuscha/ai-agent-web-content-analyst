from dataclasses import dataclass
from typing import Optional

@dataclass
class AppConfig:
    openai_api_key: Optional[str] = None
    model: str = "gpt-4o-mini"
    embedding_model: str = "text-embedding-3-small"
    chunk_size: int = 800
    chunk_overlap: int = 100
    retrieval_top_k: int = 5
    temperature: float = 0.3
    low_confidence_threshold: float = 0.55
    request_timeout: int = 10
    
    @classmethod
    def from_env(cls):
        import os
        from dotenv import load_dotenv
        load_dotenv()
        return cls(openai_api_key=os.getenv("OPENAI_API_KEY"))
