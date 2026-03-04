# Legacy compatibility wrapper - use infrastructure/extractors.py for new code
from infrastructure.extractors import ContentExtractorFactory
from infrastructure.text_processing import chunk_text as _chunk_text
from schemas import SourceContent

def ingest_source(url: str, manual_text: str = None) -> SourceContent:
    from application.services import ContentIngestionService
    from config import AppConfig
    service = ContentIngestionService(AppConfig())
    return service.ingest(url, manual_text)

def chunk_text(text: str, chunk_size: int = 800, overlap: int = 100):
    return _chunk_text(text, chunk_size, overlap)
