#!/bin/bash
# Start everything for demo recording

echo "=========================================="
echo "Starting AI Trading Agent Demo"
echo "=========================================="
echo ""

# Check Redis
if ! redis-cli ping > /dev/null 2>&1; then
    echo "⚠ Redis not running. Starting Redis..."
    redis-server --daemonize yes 2>&1
    sleep 2
    if redis-cli ping > /dev/null 2>&1; then
        echo "✓ Redis started"
    else
        echo "⚠ Redis not available - continuing without it"
    fi
else
    echo "✓ Redis is running"
fi

echo ""
echo "=========================================="
echo "Starting Backend Server"
echo "=========================================="
echo ""
echo "Backend will start on: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Start backend
cd /Users/brixxbeat/Desktop/AiAGENT
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

