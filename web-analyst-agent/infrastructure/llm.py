import openai
from core.interfaces import LLMProvider, EmbeddingProvider
from typing import List
import numpy as np

class OpenAILLM(LLMProvider):
    def __init__(self, api_key: str, model: str):
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
    
    def generate(self, prompt: str, temperature: float, json_mode: bool = False) -> str:
        kwargs = {"model": self.model, "messages": [{"role": "user", "content": prompt}], "temperature": temperature}
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}
        response = self.client.chat.completions.create(**kwargs)
        return response.choices[0].message.content

class OpenAIEmbedding(EmbeddingProvider):
    def __init__(self, api_key: str, model: str):
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
    
    def embed(self, texts: List[str]) -> np.ndarray:
        response = self.client.embeddings.create(input=texts, model=self.model)
        embeddings = [item.embedding for item in response.data]
        return np.array(embeddings, dtype='float32')
