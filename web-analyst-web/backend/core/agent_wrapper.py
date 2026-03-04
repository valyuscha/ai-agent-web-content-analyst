import uuid
from typing import Dict, List, Optional
from core.schemas import SourceContent, ExtractionResult
from core.tools import ingest_source
from core.agent import WebAnalystAgent
from core.rag import build_vector_store
from core.eval import evaluate_action_items, compute_citation_coverage, compute_low_confidence_rate
from core.utils import generate_report_markdown
from core.storage import save_session, load_session, load_all_sessions, delete_session as delete_session_storage
import os
import asyncio

# Global WebSocket manager reference
ws_manager = None

def set_ws_manager(manager):
    global ws_manager
    ws_manager = manager

class Session:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.sources: List[SourceContent] = []
        self.extraction_result: Optional[ExtractionResult] = None
        self.agent_log: List[str] = []
        self.vector_store = None
        self.kb_docs: List[tuple] = []
        self.analysis_mode: str = "General summary"
        self.tone: str = "formal"
        self.language: str = "English"
        self.reflection_count: int = 0  # Track reflection reruns

class SessionStore:
    def __init__(self):
        self.sessions: Dict[str, Session] = {}
        self._lock = __import__('threading').Lock()
        self._load_sessions_from_disk()
    
    def _load_sessions_from_disk(self):
        """Load all sessions from disk on startup"""
        all_sessions = load_all_sessions()
        for session_id, data in all_sessions.items():
            session = Session(session_id)
            session.sources = [SourceContent(**s) for s in data.get('sources', [])]
            if data.get('result'):
                session.extraction_result = ExtractionResult(**data['result'])
            session.analysis_mode = data.get('metadata', {}).get('analysis_mode', 'General summary')
            session.tone = data.get('metadata', {}).get('tone', 'formal')
            session.language = data.get('metadata', {}).get('language', 'English')
            session.agent_log = data.get('metadata', {}).get('agent_log', [])
            self.sessions[session_id] = session
    
    def create_session(self) -> str:
        with self._lock:
            session_id = str(uuid.uuid4())
            self.sessions[session_id] = Session(session_id)
            return session_id
    
    def get_session(self, session_id: str) -> Optional[Session]:
        with self._lock:
            return self.sessions.get(session_id)
    
    def save_session(self, session_id: str):
        """Save session to disk"""
        with self._lock:
            session = self.sessions.get(session_id)
            if session:
                save_session(
                    session_id,
                    session.sources,
                    session.extraction_result,
                    {
                        'analysis_mode': session.analysis_mode,
                        'tone': session.tone,
                        'language': session.language,
                        'agent_log': session.agent_log
                    }
                )
    
    def delete_session(self, session_id: str):
        with self._lock:
            if session_id in self.sessions:
                del self.sessions[session_id]
                delete_session_storage(session_id)

# Global session store
session_store = SessionStore()

def load_kb_docs() -> List[tuple]:
    """Load knowledge base documents"""
    kb_docs = []
    kb_files = [
        "kb/analysis_templates.md",
        "kb/writing_style.md",
        "kb/evaluation_rubric.md"
    ]
    for kb_file in kb_files:
        if os.path.exists(kb_file):
            with open(kb_file, 'r', encoding='utf-8') as f:
                kb_docs.append((kb_file, f.read()))
    return kb_docs

def ingest_urls(
    urls: List[str],
    analysis_mode: str,
    tone: str,
    language: str,
    api_key: str = None
) -> tuple[str, List[dict]]:
    """Ingest URLs and create session"""
    # Limit number of URLs
    if len(urls) > 5:
        raise ValueError("Maximum 5 URLs allowed per request")
    
    session_id = session_store.create_session()
    session = session_store.get_session(session_id)
    
    session.analysis_mode = analysis_mode
    session.tone = tone
    session.language = language
    session.kb_docs = load_kb_docs()
    
    sources_response = []
    
    for url in urls:
        source = ingest_source(url, api_key=api_key)
        session.sources.append(source)
        
        sources_response.append({
            "url": source.url,
            "title": source.title,
            "type": source.type,
            "status": "ok" if not source.error else "error",
            "error": source.error,
            "text_preview": source.content[:500] if source.content else "",
            "text_length": source.length
        })
    
    # Save session to disk
    session_store.save_session(session_id)
    
    return session_id, sources_response

def update_source_content(session_id: str, url: str, manual_text: str) -> bool:
    """Update source with manual content"""
    session = session_store.get_session(session_id)
    if not session:
        return False
    
    for source in session.sources:
        if source.url == url:
            source.content = manual_text
            source.length = len(manual_text)
            source.error = None
            return True
    
    return False

def run_agent(session_id: str, api_key: str) -> dict:
    """Run full agent analysis"""
    session = session_store.get_session(session_id)
    if not session:
        raise ValueError("Session not found")
    
    # Filter sources with content
    valid_sources = [s for s in session.sources if s.content]
    
    if not valid_sources:
        raise ValueError("No valid sources to analyze")
    
    # Create agent
    agent = WebAnalystAgent(api_key=api_key)
    
    # Create a custom log handler that updates session in real-time
    original_add = agent.log.add
    def add_with_session_update(message: str, detail: str = ""):
        original_add(message, detail)
        session.agent_log = agent.log.entries.copy()
        # Send via WebSocket if available
        if ws_manager:
            ws_manager.send_log_sync(session_id, message, detail)
    agent.log.add = add_with_session_update
    
    # Run agent
    result = agent.run(
        sources=valid_sources,
        kb_docs=session.kb_docs,
        analysis_mode=session.analysis_mode,
        tone=session.tone,
        language=session.language
    )
    
    session.extraction_result = result
    session.agent_log = agent.log.entries
    session.vector_store = agent.vector_store
    
    # Save session to disk
    session_store.save_session(session_id)
    
    # Generate outputs
    agent.log.add("Generating markdown report...")
    session.agent_log = agent.log.entries.copy()
    session_store.save_session(session_id)
    report_md = generate_report_markdown(result)
    
    agent.log.add("Generating email draft...")
    session.agent_log = agent.log.entries.copy()
    session_store.save_session(session_id)
    email_draft = agent.generate_email_draft(result, session.tone)
    
    # Compute metrics
    agent.log.add("Computing quality metrics...")
    session.agent_log = agent.log.entries.copy()
    session_store.save_session(session_id)
    
    # Calculate citation coverage: percentage of sources with key findings
    total_sources = len(result.sources)
    sources_with_content = sum(1 for s in result.sources if s.key_points or s.recommendations_or_decisions)
    citation_coverage = sources_with_content / total_sources if total_sources > 0 else 1.0
    
    # Low confidence rate: based on risks, ambiguities, and open questions
    total_findings = sum(len(s.key_points) + len(s.recommendations_or_decisions) for s in result.sources)
    risk_indicators = sum(len(s.risks_or_ambiguities) + len(s.open_questions) for s in result.sources)
    low_conf_rate = risk_indicators / max(total_findings, 1) if total_findings > 0 else 0.0
    
    metrics = {
        "citation_coverage": round(citation_coverage, 2),
        "low_conf_rate": round(min(low_conf_rate, 1.0), 2)
    }
    
    agent.log.add("✅ All tasks completed!")
    session.agent_log = agent.log.entries.copy()
    session_store.save_session(session_id)
    
    return {
        "result_json": result.model_dump(),
        "report_markdown": report_md,
        "email_draft": email_draft,
        "metrics": metrics,
        "agent_log": session.agent_log
    }

def run_reflection(session_id: str, api_key: str, only_low_confidence: bool = True) -> dict:
    """Force reflection and re-extraction"""
    session = session_store.get_session(session_id)
    if not session or not session.extraction_result:
        raise ValueError("No extraction result to reflect on")
    
    # Limit reflection reruns
    if session.reflection_count >= 2:
        raise ValueError("Maximum reflection reruns (2) reached for this session")
    
    session.reflection_count += 1
    
    agent = WebAnalystAgent(api_key=api_key)
    agent.vector_store = session.vector_store
    agent.log.entries = session.agent_log.copy()
    
    # Re-run reflection on each source
    improved_sources = []
    for i, source_result in enumerate(session.extraction_result.sources):
        source_content = session.sources[i]
        
        if only_low_confidence:
            low_conf_items = [item for item in source_result.action_items if item.confidence < 0.55]
            if not low_conf_items:
                improved_sources.append(source_result)
                continue
        
        agent.log.add(f"Re-reflecting on {source_result.title}")
        improved, was_fixed = agent.reflect_and_fix(
            source_result,
            source_content,
            session.analysis_mode
        )
        improved_sources.append(improved)
    
    # Update result
    session.extraction_result.sources = improved_sources
    
    # Re-combine
    combined = agent.combine_sources(improved_sources, session.tone, session.language)
    session.extraction_result.combined = combined
    
    session.agent_log = agent.log.entries
    
    # Generate outputs
    report_md = generate_report_markdown(session.extraction_result)
    email_draft = agent.generate_email_draft(session.extraction_result, session.tone)
    
    # Compute metrics
    all_action_items = []
    for source_result in session.extraction_result.sources:
        all_action_items.extend(source_result.action_items)
    
    metrics = {
        "citation_coverage": compute_citation_coverage(all_action_items),
        "low_conf_rate": compute_low_confidence_rate(all_action_items)
    }
    
    return {
        "result_json": session.extraction_result.model_dump(),
        "report_markdown": report_md,
        "email_draft": email_draft,
        "metrics": metrics,
        "agent_log": session.agent_log
    }

def evaluate_results(
    predicted_items: List[str],
    gold_items: Optional[List[str]] = None,
    checked_correct_ids: Optional[List[int]] = None
) -> dict:
    """Evaluate extraction results"""
    
    if checked_correct_ids is not None:
        # Checkbox-based evaluation
        correct_count = len(checked_correct_ids)
        total_count = len(predicted_items)
        precision = correct_count / total_count if total_count > 0 else 0.0
        
        return {
            "precision": precision,
            "recall": None,
            "f1": None,
            "matching_details": [],
            "method": "checkbox"
        }
    
    elif gold_items:
        # Gold list evaluation
        precision, recall, f1, matches = evaluate_action_items(predicted_items, gold_items)
        
        matching_details = [
            {
                "predicted": pred,
                "gold": gold,
                "similarity": score
            }
            for pred, gold, score in matches
        ]
        
        return {
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "matching_details": matching_details,
            "method": "gold_list"
        }
    
    else:
        raise ValueError("Either gold_items or checked_correct_ids must be provided")
