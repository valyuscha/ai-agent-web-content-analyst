#!/bin/bash

echo "🚀 Starting Web Analyst Backend"
echo ""

cd "$(dirname "$0")"

PORT=8000

# Kill process on port if in use
echo "Checking port $PORT..."
fuser -k $PORT/tcp 2>/dev/null && echo "Killed process on port $PORT" && sleep 2

# Test configuration first
echo "Testing configuration..."
python test_env.py

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Configuration test failed. Please fix the issues above."
    exit 1
fi

echo ""
echo "Starting server..."
uvicorn main:app --reload --port $PORT
