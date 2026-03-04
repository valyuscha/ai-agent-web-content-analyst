from typing import List, Tuple
from schemas import SourceContent, ExtractionResult
from core.interfaces import VectorStoreInterface, LLMProvider
from core.domain import InsightExtractor, QualityReflector, SourceCombiner
from infrastructure.extractors import ContentExtractorFactory
from infrastructure.text_processing import chunk_text

class AgentLog:
    def __init__(self):
        self.entries = []
    
    def add(self, message: str):
        self.entries.append(message)
    
    def get_log(self) -> str:
        return "\n".join(self.entries)

class ContentIngestionService:
    def __init__(self, config):
        self.config = config
    
    def ingest(self, url: str, manual_text: str = None) -> SourceContent:
        if manual_text:
            return SourceContent(url=url, title=url, type="article", content=manual_text, length=len(manual_text))
        
        extractor = ContentExtractorFactory.create(url, self.config.request_timeout)
        content, title, error = extractor.extract(url)
        
        content_type = "youtube" if 'youtube.com' in url or 'youtu.be' in url else "article"
        return SourceContent(url=url, title=title, type=content_type, content=content, error=error, length=len(content))

class VectorStoreBuilder:
    def __init__(self, vector_store: VectorStoreInterface, config):
        self.vector_store = vector_store
        self.config = config
    
    def build(self, sources: List[SourceContent], kb_docs: List[Tuple[str, str]]):
        all_texts = []
        all_metadata = []
        
        for kb_name, kb_content in kb_docs:
            chunks = chunk_text(kb_content, self.config.chunk_size, self.config.chunk_overlap)
            for chunk in chunks:
                all_texts.append(chunk)
                all_metadata.append({"source": "kb", "kb_name": kb_name})
        
        for source in sources:
            if source.content:
                chunks = chunk_text(source.content, self.config.chunk_size, self.config.chunk_overlap)
                for chunk in chunks:
                    all_texts.append(chunk)
                    all_metadata.append({"source": "content", "url": source.url, "title": source.title, "type": source.type})
        
        if all_texts:
            self.vector_store.build(all_texts, all_metadata)

class AnalysisOrchestrator:
    def __init__(
        self,
        llm: LLMProvider,
        vector_store: VectorStoreInterface,
        config,
        log: AgentLog
    ):
        self.extractor = InsightExtractor(llm, config)
        self.reflector = QualityReflector(config)
        self.combiner = SourceCombiner(llm, config)
        self.vector_store = vector_store
        self.config = config
        self.log = log
    
    def analyze(
        self,
        sources: List[SourceContent],
        analysis_mode: str,
        tone: str,
        language: str
    ) -> ExtractionResult:
        self.log.add(f"=== PLAN: {analysis_mode} ===")
        self.log.add(f"Processing {len(sources)} sources")
        
        source_results = []
        
        for source in sources:
            if not source.content:
                self.log.add(f"✗ Skipping {source.url} (no content)")
                continue
            
            self.log.add(f"=== PROCESSING: {source.title} ===")
            
            query = f"{analysis_mode} analysis of {source.title}"
            contexts_raw = self.vector_store.retrieve(query, self.config.retrieval_top_k)
            contexts = [text for text, meta, dist in contexts_raw]
            self.log.add(f"Retrieved {len(contexts)} contexts")
            
            self.log.add("Extracting structured insights...")
            result = self.extractor.extract(source, contexts, analysis_mode, tone, language)
            
            self.log.add("Reflecting on extraction quality...")
            issues, passed = self.reflector.evaluate(result)
            
            if not passed:
                self.log.add(f"⚠ Issues found: {', '.join(issues)}")
                self.log.add("↻ Re-extracting with targeted contexts")
                
                queries = [
                    f"action items and next steps in {source.title}",
                    f"key takeaways from {source.title}",
                    "recommendations and decisions"
                ]
                
                contexts = []
                for q in queries:
                    results = self.vector_store.retrieve(q, top_k=3)
                    contexts.extend([text for text, meta, dist in results if meta.get("url") == source.url])
                
                result = self.extractor.extract(source, contexts, analysis_mode, tone, language)
            else:
                self.log.add("✓ Reflection passed")
            
            source_results.append(result)
        
        self.log.add("=== COMBINING SOURCES ===")
        combined = self.combiner.combine(source_results, tone, language)
        self.log.add("=== COMPLETE ===")
        
        return ExtractionResult(sources=source_results, combined=combined)

class EmailDraftService:
    def __init__(self, llm: LLMProvider, config):
        self.llm = llm
        self.config = config
    
    def generate(self, extraction: ExtractionResult, tone: str) -> str:
        summary = extraction.combined.overall_summary
        actions = extraction.combined.final_action_plan[:5]
        
        prompt = f"""Generate a professional follow-up email summarizing these findings:

Summary: {summary}

Key Actions:
{chr(10).join([f"- {a}" for a in actions])}

Tone: {tone}
Keep it concise (max 200 words)."""

        return self.llm.generate(prompt, 0.5, json_mode=False)
