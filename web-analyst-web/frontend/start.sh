#!/bin/bash

PORT=3000

# Kill process on port if in use
echo "Checking port $PORT..."
fuser -k $PORT/tcp 2>/dev/null && echo "Killed process on port $PORT" && sleep 2

echo "Starting on port $PORT..."
next dev -p $PORT
