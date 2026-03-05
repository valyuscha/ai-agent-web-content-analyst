from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router
from core.agent_wrapper import set_ws_manager
from dotenv import load_dotenv
import logging
import os
import sys
from pathlib import Path
from typing import Dict, List
import asyncio
from queue import Queue

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.message_queues: Dict[str, Queue] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        if session_id not in self.active_connections:
            self.active_connections[session_id] = []
            self.message_queues[session_id] = Queue()
        self.active_connections[session_id].append(websocket)
    
    def disconnect(self, websocket: WebSocket, session_id: str):
        if session_id in self.active_connections:
            self.active_connections[session_id].remove(websocket)
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]
                if session_id in self.message_queues:
                    del self.message_queues[session_id]
    
    def send_log_sync(self, session_id: str, message: str, detail: str = ""):
        """Synchronous method to queue messages"""
        if session_id in self.message_queues:
            self.message_queues[session_id].put({"message": message, "detail": detail})
            print(f"Queued log for {session_id}: {message[:50]}...")
    
    async def send_log(self, session_id: str, message: str, detail: str = ""):
        """Async method to send messages"""
        if session_id in self.active_connections:
            for connection in self.active_connections[session_id]:
                try:
                    await connection.send_json({"type": "log", "message": message, "detail": detail})
                except:
                    pass

manager = ConnectionManager()
set_ws_manager(manager)

# Load environment variables from multiple locations
# Try backend/.env first, then project root .env
backend_env = Path(__file__).parent / ".env"
root_env = Path(__file__).parent.parent / ".env"

if backend_env.exists():
    load_dotenv(backend_env)
    print(f"✓ Loaded environment from: {backend_env}")
elif root_env.exists():
    load_dotenv(root_env)
    print(f"✓ Loaded environment from: {root_env}")
else:
    load_dotenv()  # Try default locations
    print("⚠ No .env file found, using system environment variables")

# Check OpenAI API key
openai_key = os.getenv("OPENAI_API_KEY")
if openai_key and openai_key.startswith("sk-"):
    print(f"✓ OPENAI_API_KEY LOADED: yes (starts with 'sk-', length: {len(openai_key)})")
else:
    print("✗ OPENAI_API_KEY LOADED: no")
    print("\n" + "="*60)
    print("ERROR: OPENAI_API_KEY not configured!")
    print("="*60)
    print("\nPlease create a .env file in one of these locations:")
    print(f"  1. {backend_env.absolute()}")
    print(f"  2. {root_env.absolute()}")
    print("\nWith the following content:")
    print("  OPENAI_API_KEY=sk-your-actual-key-here")
    print("\nThen restart the server.")
    print("="*60 + "\n")
    # Don't exit - allow server to start but API calls will fail gracefully

# Configure logging to not expose secrets
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Filter out sensitive headers
class SensitiveDataFilter(logging.Filter):
    def filter(self, record):
        if hasattr(record, 'msg'):
            msg = str(record.msg)
            # Redact API keys
            if openai_key and openai_key in msg:
                record.msg = msg.replace(openai_key, '[REDACTED]')
        return True

logging.getLogger().addFilter(SensitiveDataFilter())

app = FastAPI(
    title="Web Analyst API",
    description="API for analyzing web content with AI agent",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://web-analyst-frontend.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router)

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await manager.connect(websocket, session_id)
    print(f"WebSocket connected for session: {session_id}")
    try:
        while True:
            # Check for queued messages and send them
            if session_id in manager.message_queues:
                while not manager.message_queues[session_id].empty():
                    log_entry = manager.message_queues[session_id].get()
                    if isinstance(log_entry, dict):
                        message = log_entry.get("message", "")
                        detail = log_entry.get("detail", "")
                    else:
                        message = log_entry
                        detail = ""
                    print(f"Sending message: {message[:50]}...")
                    try:
                        await websocket.send_json({"type": "log", "message": message, "detail": detail})
                    except Exception as e:
                        print(f"Error sending message: {e}")
            await asyncio.sleep(0.1)
    except WebSocketDisconnect:
        manager.disconnect(websocket, session_id)
        print(f"WebSocket disconnected for session: {session_id}")
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket, session_id)

@app.get("/")
async def root():
    return {
        "message": "Web Analyst API",
        "version": "1.0.0",
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
