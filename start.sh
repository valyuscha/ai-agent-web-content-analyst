#!/bin/bash

trap 'kill 0' EXIT

cd "$(dirname "$0")"

echo "🚀 Starting Web Analyst Application..."

# Kill processes on ports if in use
fuser -k 3000/tcp 8000/tcp 2>/dev/null && sleep 1

# Start backend
cd web-analyst-web/backend
source venv/bin/activate 2>/dev/null || true
uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Start frontend
cd ../frontend
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ Application started!"
echo "   Backend:  http://localhost:8000"
echo "   Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all services"

wait
