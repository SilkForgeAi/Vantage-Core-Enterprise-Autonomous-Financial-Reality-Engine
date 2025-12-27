#!/bin/bash
# Demo script for AI Trading Agent REST API

echo "=========================================="
echo "AI Trading Agent - REST API Demo"
echo "=========================================="
echo ""

BASE_URL="http://localhost:8000"

echo "1. Health Check"
echo "GET $BASE_URL/"
curl -s "$BASE_URL/" | python3 -m json.tool
echo ""
echo ""

echo "2. Add Exchange for User (example - you'll need real encrypted keys)"
echo "POST $BASE_URL/api/user/add_exchange"
echo "Note: This requires encrypted API keys. Use scripts/add_user_exchange.py instead"
echo ""
echo ""

echo "3. Get User Status"
echo "GET $BASE_URL/api/user/test_user_1/status"
curl -s "$BASE_URL/api/user/test_user_1/status" | python3 -m json.tool
echo ""
echo ""

echo "4. Process Message (Intent Processing)"
echo "POST $BASE_URL/api/agent/message"
echo "Request: {\"user_id\": \"test_user_1\", \"message\": \"check my USDT balance\"}"
curl -s -X POST "$BASE_URL/api/agent/message" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_1",
    "message": "check my USDT balance"
  }' | python3 -m json.tool
echo ""
echo ""

echo "5. Another Intent Example"
echo "POST $BASE_URL/api/agent/message"
echo "Request: {\"user_id\": \"test_user_1\", \"message\": \"what positions do I have?\"}"
curl -s -X POST "$BASE_URL/api/agent/message" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_1",
    "message": "what positions do I have?"
  }' | python3 -m json.tool
echo ""
echo ""

echo "=========================================="
echo "Demo Complete!"
echo "=========================================="

