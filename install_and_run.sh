#!/bin/bash
# Install dependencies and start demo

echo "=========================================="
echo "Installing Dependencies..."
echo "=========================================="

pip3 install --quiet fastapi uvicorn[standard] pydantic pydantic-settings \
  langchain langchain-openai langchain-anthropic langchain-core langgraph \
  structlog redis chromadb cryptography httpx python-dotenv ccxt \
  2>&1 | grep -E "(Successfully|ERROR)" | head -5

echo ""
echo "=========================================="
echo "Starting Backend..."
echo "=========================================="
echo ""
echo "Backend starting on http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop"
echo ""

cd /Users/brixxbeat/Desktop/AiAGENT
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

