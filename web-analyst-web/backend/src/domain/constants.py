"""
Domain constants and configuration values.
Centralized to avoid magic numbers throughout codebase.
"""

# API Limits
MAX_URLS_PER_REQUEST = 5
MAX_TEXT_LENGTH = 25000
MAX_REFLECTION_RERUNS = 2

# Chunking Configuration
CHUNK_SIZE = 800
CHUNK_OVERLAP = 100
KB_CHUNK_SIZE = 600
KB_CHUNK_OVERLAP = 50

# RAG Configuration
DEFAULT_EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSION = 1536
DEFAULT_TOP_K = 5

# Rate Limiting
DEFAULT_RATE_LIMIT = 10
DEFAULT_RATE_WINDOW = 60  # seconds

# Timeouts
URL_FETCH_TIMEOUT = 10  # seconds

# LLM Configuration
DEFAULT_MODEL = "gpt-4o-mini"
DEFAULT_TEMPERATURE = 0.7
REFLECTION_TEMPERATURE = 0.5

# Storage
STORAGE_DIR = "storage"
SESSIONS_FILE = "sessions.json"
EXPORTS_DIR = "exports"
