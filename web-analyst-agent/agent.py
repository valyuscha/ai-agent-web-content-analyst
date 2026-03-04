# Legacy compatibility wrapper - use application/services.py for new code
from config import AppConfig
from infrastructure.llm import OpenAILLM, OpenAIEmbedding
from infrastructure.vector_store import FAISSVectorStore
from application.services import AgentLog, AnalysisOrchestrator, VectorStoreBuilder, EmailDraftService
from typing import List, Tuple
from schemas import ExtractionResult, SourceContent

class WebAnalystAgent:
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.config = AppConfig(openai_api_key=api_key, model=model)
        self.log = AgentLog()
        
        self.llm = OpenAILLM(api_key, model)
        embedding = OpenAIEmbedding(api_key, self.config.embedding_model)
        self.vector_store = FAISSVectorStore(embedding)
        
        self.orchestrator = AnalysisOrchestrator(self.llm, self.vector_store, self.config, self.log)
        self.email_service = EmailDraftService(self.llm, self.config)
    
    def run(
        self,
        sources: List[SourceContent],
        kb_docs: List[Tuple[str, str]],
        analysis_mode: str,
        tone: str,
        language: str
    ) -> ExtractionResult:
        self.log.add("=== BUILDING VECTOR STORE ===")
        builder = VectorStoreBuilder(self.vector_store, self.config)
        builder.build(sources, kb_docs)
        self.log.add(f"Indexed {self.vector_store.index.ntotal if self.vector_store.index else 0} chunks")
        
        return self.orchestrator.analyze(sources, analysis_mode, tone, language)
    
    def generate_email_draft(self, extraction: ExtractionResult, tone: str) -> str:
        return self.email_service.generate(extraction, tone)
