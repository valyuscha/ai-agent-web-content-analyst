# Web Content Analyst Agent

An AI-powered web content analysis system that extracts structured insights from articles using RAG (Retrieval-Augmented Generation), tool calling, and self-reflection.

## Overview

This project consists of two main components:
1. **Streamlit Agent** (`web-analyst-agent/`) - Standalone Streamlit interface for content analysis
2. **Web Application** (`web-analyst-web/`) - Full-stack application with FastAPI backend and Next.js frontend

## Architecture

See [architecture.mmd](./architecture.mmd) for detailed system architecture diagram.

## Technologies Used

### Backend
- **FastAPI** - Modern async web framework
- **OpenAI GPT-4** - LLM for content analysis and extraction
- **FAISS** - Vector database for semantic search
- **BeautifulSoup4** - Web scraping and article extraction
- **Pydantic** - Data validation

### Frontend
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first styling
- **WebSocket** - Real-time agent logs

### Agent Core
- **Clean Architecture** - Domain-driven design with layers (core, application, infrastructure)
- **RAG Pipeline** - Vector store + retrieval + LLM generation
- **Self-Reflection** - Quality assessment and iterative improvement

## Quick Start

### Prerequisites
- Node.js 18+
- Python 3.11+
- OpenAI API key

### Installation

```bash
# Install all dependencies
make install
```

### Configuration

Create environment files:

**`web-analyst-web/backend/.env`**
```
OPENAI_API_KEY=your_key_here
```

**`web-analyst-agent/.env`**
```
OPENAI_API_KEY=your_key_here
```

### Running the Application

```bash
make start
```
- Backend: http://localhost:8000
- Frontend: http://localhost:3000


## Testing the Agent
1. Navigate to http://localhost:3000
2. Enter OpenAI API key in settings
3. Add content sources (article URLs)
4. Select analysis mode (Study notes, Product analysis, Technical tutorial, General summary)
5. Click "Analyze" and watch real-time logs
6. Review extracted insights and citations

## Project Structure

```
capstone-project/
├── web-analyst-agent/          # Streamlit agent (standalone)
│   ├── core/                   # Domain models and business logic
│   ├── application/            # Use cases and orchestration
│   ├── infrastructure/         # External services (LLM, vector store)
│   ├── agent.py               # Main agent class
│   ├── app.py                 # Streamlit UI
│   └── requirements.txt
│
├── web-analyst-web/           # Full-stack web application
│   ├── backend/               # FastAPI server
│   │   ├── api/              # REST endpoints
│   │   ├── core/             # Agent wrapper
│   │   ├── src/              # Business logic
│   │   ├── main.py           # FastAPI app
│   │   └── requirements.txt
│   │
│   └── frontend/             # Next.js application
│       ├── src/
│       │   ├── components/   # React components
│       │   └── services/     # API clients
│       ├── app/              # Next.js pages
│       └── package.json
│
├── Makefile                   # Build and run commands
└── architecture.mmd           # System architecture diagram
```

## Key Features

- **Multi-source Analysis** - Process multiple web articles
- **RAG-Enhanced** - Uses vector store for context-aware extraction
- **Self-Reflection** - Agent evaluates and improves its own output
- **Structured Output** - JSON-formatted insights with citations
- **Real-time Logs** - WebSocket streaming of agent reasoning
- **Email Drafts** - Auto-generate summaries in email format
