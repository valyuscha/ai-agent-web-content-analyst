from pydantic import BaseModel, Field
from typing import List, Literal, Optional

class SourceResult(BaseModel):
    url: str
    title: str
    type: Literal["youtube", "article"]
    summary: str
    key_points: List[str] = []
    recommendations_or_decisions: List[str] = []
    open_questions: List[str] = []
    risks_or_ambiguities: List[str] = []

class CombinedResult(BaseModel):
    overall_summary: str
    cross_source_agreements: List[str] = []
    cross_source_conflicts: List[str] = []
    final_action_plan: List[str] = []
    confidence_notes: List[str] = []

class ExtractionResult(BaseModel):
    sources: List[SourceResult]
    combined: CombinedResult

class SourceContent(BaseModel):
    url: str
    title: str
    type: Literal["youtube", "article"]
    content: str
    error: Optional[str] = None
    length: int = 0
