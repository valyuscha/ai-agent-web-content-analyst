from fastapi import APIRouter, HTTPException, Query, Request, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional, Literal
from core.agent_wrapper import (
    ingest_urls,
    run_agent,
    run_reflection,
    evaluate_results,
    update_source_content,
    session_store
)
from core.storage import list_sessions as list_sessions_storage
from core.utils import export_report
import os
import time
from collections import defaultdict

router = APIRouter(prefix="/api")

# Rate limiting (simple in-memory implementation)
rate_limit_store = defaultdict(lambda: {"count": 0, "reset_time": time.time()})

def check_rate_limit(ip: str, limit: int = 10, window: int = 60) -> bool:
    """Check if IP is within rate limit. Returns True if allowed."""
    now = time.time()
    data = rate_limit_store[ip]
    
    # Reset if window expired
    if now > data["reset_time"]:
        data["count"] = 0
        data["reset_time"] = now + window
    
    # Check limit
    if data["count"] >= limit:
        return False
    
    data["count"] += 1
    return True

def get_client_ip(request: Request) -> str:
    """Get client IP from request"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"

class IngestRequest(BaseModel):
    urls: List[str]
    analysis_mode: Literal["General summary", "Study notes", "Product/marketing analysis", "Technical tutorial extraction"] = "General summary"
    tone: Literal["formal", "friendly"] = "formal"
    language: Literal["English", "Polish", "Ukrainian", "Russian"] = "English"

class IngestResponse(BaseModel):
    sources: List[dict]
    session_id: str

class RunRequest(BaseModel):
    session_id: str

class ReflectRequest(BaseModel):
    session_id: str
    only_low_confidence: bool = True

class UpdateSourceRequest(BaseModel):
    session_id: str
    url: str
    manual_text: str

class EvaluateRequest(BaseModel):
    predicted_action_items: List[str]
    gold_action_items: Optional[List[str]] = None
    checked_correct_ids: Optional[List[int]] = None

@router.get("/health")
async def health():
    """Health check with OpenAI configuration status"""
    api_key = os.getenv("OPENAI_API_KEY")
    return {
        "status": "ok",
        "openai_configured": bool(api_key and api_key.startswith("sk-"))
    }

@router.get("/sessions")
async def list_sessions_endpoint():
    """List all saved sessions"""
    sessions = list_sessions_storage()
    return {"sessions": sessions}

@router.get("/sessions/{session_id}")
async def get_session_endpoint(session_id: str):
    """Get a specific session"""
    session = session_store.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "session_id": session.session_id,
        "sources": [s.model_dump() for s in session.sources],
        "result": session.extraction_result.model_dump() if session.extraction_result else None,
        "agent_log": session.agent_log,
        "metadata": {
            "analysis_mode": session.analysis_mode,
            "tone": session.tone,
            "language": session.language
        }
    }

@router.get("/sessions/{session_id}/log")
async def get_session_log_endpoint(session_id: str):
    """Get current agent log for a session"""
    session = session_store.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "agent_log": session.agent_log
    }

@router.delete("/sessions/{session_id}")
async def delete_session_endpoint(session_id: str):
    """Delete a session"""
    session_store.delete_session(session_id)
    return {"status": "ok"}

@router.post("/ingest", response_model=IngestResponse)
async def ingest_endpoint(request: IngestRequest):
    """Ingest URLs and extract content"""
    # Get API key from environment for Whisper
    api_key = os.getenv("OPENAI_API_KEY")
    
    try:
        session_id, sources = ingest_urls(
            urls=request.urls,
            analysis_mode=request.analysis_mode,
            tone=request.tone,
            language=request.language,
            api_key=api_key
        )
        
        return IngestResponse(
            sources=sources,
            session_id=session_id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Ingestion failed")

@router.post("/update-source")
async def update_source_endpoint(request: UpdateSourceRequest):
    """Update source with manual content"""
    success = update_source_content(
        session_id=request.session_id,
        url=request.url,
        manual_text=request.manual_text
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Session or source not found")
    
    return {"status": "ok"}

@router.post("/run")
async def run_endpoint(request: RunRequest, http_request: Request, background_tasks: BackgroundTasks):
    """Run full agent analysis"""
    # Rate limiting
    client_ip = get_client_ip(http_request)
    if not check_rate_limit(client_ip, limit=10, window=60):
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Try again in 1 minute.")
    
    # Get API key from environment
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=503, detail="OpenAI API key not configured on server")
    
    try:
        # Run agent in background but wait for completion
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        
        executor = ThreadPoolExecutor(max_workers=1)
        loop = asyncio.get_event_loop()
        
        result = await loop.run_in_executor(
            executor,
            run_agent,
            request.session_id,
            api_key
        )
        
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.post("/reflect")
async def reflect_endpoint(request: ReflectRequest, http_request: Request):
    """Force reflection and re-extraction"""
    # Rate limiting
    client_ip = get_client_ip(http_request)
    if not check_rate_limit(client_ip, limit=10, window=60):
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Try again in 1 minute.")
    
    # Get API key from environment
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=503, detail="OpenAI API key not configured on server")
    
    try:
        result = run_reflection(
            session_id=request.session_id,
            api_key=api_key,
            only_low_confidence=request.only_low_confidence
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Reflection failed")

@router.post("/evaluate")
async def evaluate_endpoint(request: EvaluateRequest):
    """Evaluate extraction results"""
    try:
        result = evaluate_results(
            predicted_items=request.predicted_action_items,
            gold_items=request.gold_action_items,
            checked_correct_ids=request.checked_correct_ids
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Evaluation failed")

@router.get("/export")
async def export_endpoint(
    session_id: str = Query(...),
    format: Literal["md", "json"] = Query("md")
):
    """Export report as file"""
    session = session_store.get_session(session_id)
    
    if not session or not session.extraction_result:
        raise HTTPException(status_code=404, detail="Session or result not found")
    
    os.makedirs("exports", exist_ok=True)
    
    if format == "md":
        filename = export_report(session.extraction_result, f"exports/report_{session_id}.md")
        return FileResponse(
            filename,
            media_type="text/markdown",
            filename="report.md"
        )
    else:  # json
        import json
        filename = f"exports/report_{session_id}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(session.extraction_result.model_dump(), f, indent=2)
        
        return FileResponse(
            filename,
            media_type="application/json",
            filename="report.json"
        )
