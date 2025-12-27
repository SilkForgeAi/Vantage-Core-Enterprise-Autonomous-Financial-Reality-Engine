#!/bin/bash
# Complete demo runner for video recording

echo "=========================================="
echo "AI Trading Agent - Demo Mode"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if backend is running
check_backend() {
    if curl -s http://localhost:8000/ > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

echo -e "${BLUE}Starting demo...${NC}"
echo ""

# Wait for backend if not ready
echo "Waiting for backend to be ready..."
for i in {1..10}; do
    if check_backend; then
        echo -e "${GREEN}✓ Backend is running${NC}"
        break
    fi
    sleep 1
done

if ! check_backend; then
    echo -e "${YELLOW}⚠ Backend not ready. Make sure it's running in another terminal:${NC}"
    echo "   uvicorn backend.main:app --reload"
    exit 1
fi

echo ""
echo "=========================================="
echo "Demo 1: Health Check"
echo "=========================================="
curl -s http://localhost:8000/ | python3 -m json.tool
echo ""
sleep 2

echo "=========================================="
echo "Demo 2: Intent Processing - Balance Check"
echo "=========================================="
echo "Message: 'check my USDT balance'"
echo ""
curl -s -X POST "http://localhost:8000/api/agent/message" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "demo_user_1",
    "message": "check my USDT balance"
  }' | python3 -m json.tool
echo ""
sleep 3

echo "=========================================="
echo "Demo 3: Intent Processing - Buy Order"
echo "=========================================="
echo "Message: 'buy 0.1 BTC'"
echo ""
curl -s -X POST "http://localhost:8000/api/agent/message" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "demo_user_1",
    "message": "buy 0.1 BTC"
  }' | python3 -m json.tool
echo ""
sleep 3

echo "=========================================="
echo "Demo 4: Intent Consistency Test"
echo "=========================================="
echo "Same intent, different phrasings:"
echo ""

echo "Phrasing 1: 'buy 0.1 BTC'"
curl -s -X POST "http://localhost:8000/api/agent/message" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "demo_user_1", "message": "buy 0.1 BTC"}' \
  | python3 -c "import sys, json; d=json.load(sys.stdin); print(f\"  Execution ID: {d.get('execution_id')}\"); print(f\"  Latency: {d.get('latency_ms', 0):.1f}ms\"); print(f\"  Success: {d.get('success')}\")"
echo ""

echo "Phrasing 2: 'I want to buy 0.1 Bitcoin'"
curl -s -X POST "http://localhost:8000/api/agent/message" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "demo_user_1", "message": "I want to buy 0.1 Bitcoin"}' \
  | python3 -c "import sys, json; d=json.load(sys.stdin); print(f\"  Execution ID: {d.get('execution_id')}\"); print(f\"  Latency: {d.get('latency_ms', 0):.1f}ms\"); print(f\"  Success: {d.get('success')}\")"
echo ""

echo "Phrasing 3: 'Purchase 0.1 BTC please'"
curl -s -X POST "http://localhost:8000/api/agent/message" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "demo_user_1", "message": "Purchase 0.1 BTC please"}' \
  | python3 -c "import sys, json; d=json.load(sys.stdin); print(f\"  Execution ID: {d.get('execution_id')}\"); print(f\"  Latency: {d.get('latency_ms', 0):.1f}ms\"); print(f\"  Success: {d.get('success')}\")"
echo ""

echo "=========================================="
echo "Demo 5: Check Positions"
echo "=========================================="
echo "Message: 'what positions do I have?'"
echo ""
curl -s -X POST "http://localhost:8000/api/agent/message" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "demo_user_1",
    "message": "what positions do I have?"
  }' | python3 -m json.tool
echo ""

echo "=========================================="
echo -e "${GREEN}Demo Complete!${NC}"
echo "=========================================="
echo ""
echo "All operations were performed in DEMO MODE"
echo "No real money was used - all trades are simulated"
echo ""
echo "Interactive API docs: http://localhost:8000/docs"

