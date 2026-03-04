import json
import os
from datetime import datetime
from typing import Optional, List, Dict
from core.schemas import ExtractionResult, SourceContent

STORAGE_DIR = "storage"
SESSIONS_FILE = os.path.join(STORAGE_DIR, "sessions.json")

def ensure_storage_dir():
    """Create storage directory if it doesn't exist"""
    os.makedirs(STORAGE_DIR, exist_ok=True)

def save_session(session_id: str, sources: List[SourceContent], result: Optional[ExtractionResult] = None, metadata: Optional[Dict] = None):
    """Save session data to disk"""
    ensure_storage_dir()
    
    # Load existing sessions
    sessions = load_all_sessions()
    
    # Update or create session
    sessions[session_id] = {
        "session_id": session_id,
        "created_at": sessions.get(session_id, {}).get("created_at", datetime.now().isoformat()),
        "updated_at": datetime.now().isoformat(),
        "sources": [s.model_dump() for s in sources],
        "result": result.model_dump() if result else None,
        "metadata": metadata or {}
    }
    
    # Save to disk
    with open(SESSIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump(sessions, f, indent=2, ensure_ascii=False)
        f.flush()
        os.fsync(f.fileno())

def load_session(session_id: str) -> Optional[Dict]:
    """Load session data from disk"""
    sessions = load_all_sessions()
    return sessions.get(session_id)

def load_all_sessions() -> Dict:
    """Load all sessions from disk"""
    ensure_storage_dir()
    
    if not os.path.exists(SESSIONS_FILE):
        return {}
    
    try:
        with open(SESSIONS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def delete_session(session_id: str) -> bool:
    """Delete a session"""
    sessions = load_all_sessions()
    
    if session_id in sessions:
        del sessions[session_id]
        with open(SESSIONS_FILE, 'w', encoding='utf-8') as f:
            json.dump(sessions, f, indent=2, ensure_ascii=False)
        return True
    
    return False

def list_sessions() -> List[Dict]:
    """List all sessions with metadata"""
    sessions = load_all_sessions()
    
    # Return sorted by updated_at (most recent first)
    session_list = list(sessions.values())
    session_list.sort(key=lambda x: x.get('updated_at', ''), reverse=True)
    
    return session_list
