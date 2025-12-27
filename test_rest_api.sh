#!/bin/bash
# Interactive REST API Test Script

BASE_URL="http://localhost:8000"
USER_ID="demo_user_1"

echo "=========================================="
echo "AI Trading Agent - REST API Test"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: Health Check
echo -e "${BLUE}Test 1: Health Check${NC}"
echo "GET $BASE_URL/"
response=$(curl -s "$BASE_URL/")
echo "$response" | python3 -m json.tool
echo ""

# Test 2: Check Balance
echo -e "${BLUE}Test 2: Check USDT Balance${NC}"
echo "POST $BASE_URL/api/agent/message"
echo "Body: {\"user_id\": \"$USER_ID\", \"message\": \"check my USDT balance\"}"
response=$(curl -s -X POST "$BASE_URL/api/agent/message" \
  -H "Content-Type: application/json" \
  -d "{\"user_id\": \"$USER_ID\", \"message\": \"check my USDT balance\"}")
echo "$response" | python3 -m json.tool
echo ""

# Test 3: Buy Order
echo -e "${BLUE}Test 3: Buy 0.05 ETH${NC}"
echo "POST $BASE_URL/api/agent/message"
echo "Body: {\"user_id\": \"$USER_ID\", \"message\": \"buy 0.05 ETH\"}"
response=$(curl -s -X POST "$BASE_URL/api/agent/message" \
  -H "Content-Type: application/json" \
  -d "{\"user_id\": \"$USER_ID\", \"message\": \"buy 0.05 ETH\"}")
echo "$response" | python3 -m json.tool
echo ""

# Test 4: Check Positions
echo -e "${BLUE}Test 4: Check Positions${NC}"
echo "POST $BASE_URL/api/agent/message"
echo "Body: {\"user_id\": \"$USER_ID\", \"message\": \"what positions do I have?\"}"
response=$(curl -s -X POST "$BASE_URL/api/agent/message" \
  -H "Content-Type: application/json" \
  -d "{\"user_id\": \"$USER_ID\", \"message\": \"what positions do I have?\"}")
echo "$response" | python3 -m json.tool
echo ""

# Test 5: Get Price
echo -e "${BLUE}Test 5: Get Bitcoin Price${NC}"
echo "POST $BASE_URL/api/agent/message"
echo "Body: {\"user_id\": \"$USER_ID\", \"message\": \"what is the current price of Bitcoin?\"}"
response=$(curl -s -X POST "$BASE_URL/api/agent/message" \
  -H "Content-Type: application/json" \
  -d "{\"user_id\": \"$USER_ID\", \"message\": \"what is the current price of Bitcoin?\"}")
echo "$response" | python3 -m json.tool
echo ""

# Test 6: Sell Order
echo -e "${BLUE}Test 6: Sell 0.01 BTC${NC}"
echo "POST $BASE_URL/api/agent/message"
echo "Body: {\"user_id\": \"$USER_ID\", \"message\": \"sell 0.01 BTC\"}"
response=$(curl -s -X POST "$BASE_URL/api/agent/message" \
  -H "Content-Type: application/json" \
  -d "{\"user_id\": \"$USER_ID\", \"message\": \"sell 0.01 BTC\"}")
echo "$response" | python3 -m json.tool
echo ""

echo -e "${GREEN}=========================================="
echo "REST API Tests Complete!"
echo "==========================================${NC}"
echo ""
echo "Interactive API docs: $BASE_URL/docs"
echo "Try your own commands via the Swagger UI!"

