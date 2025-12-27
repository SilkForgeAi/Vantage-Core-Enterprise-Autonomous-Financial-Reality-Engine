#!/bin/bash
# Quick demo commands for video recording

BASE="http://localhost:8000/api/agent/message"
USER="demo_user_1"

echo "=========================================="
echo "AI Trading Agent - Demo Commands"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}1. Check Balance:${NC}"
curl -s -X POST "$BASE" -H "Content-Type: application/json" \
  -d "{\"user_id\": \"$USER\", \"message\": \"check my USDT balance\"}" | python3 -m json.tool
echo ""

sleep 2

echo -e "${BLUE}2. Get Bitcoin Price:${NC}"
curl -s -X POST "$BASE" -H "Content-Type: application/json" \
  -d "{\"user_id\": \"$USER\", \"message\": \"what is the current price of Bitcoin?\"}" | python3 -m json.tool
echo ""

sleep 2

echo -e "${BLUE}3. Buy Order (Intent Consistency Test):${NC}"
echo -e "${YELLOW}Phrasing 1: 'buy 0.1 BTC'${NC}"
curl -s -X POST "$BASE" -H "Content-Type: application/json" \
  -d "{\"user_id\": \"$USER\", \"message\": \"buy 0.1 BTC\"}" | python3 -m json.tool
echo ""

sleep 2

echo -e "${YELLOW}Phrasing 2: 'I want to buy 0.1 Bitcoin'${NC}"
curl -s -X POST "$BASE" -H "Content-Type: application/json" \
  -d "{\"user_id\": \"$USER\", \"message\": \"I want to buy 0.1 Bitcoin\"}" | python3 -m json.tool
echo ""

sleep 2

echo -e "${YELLOW}Phrasing 3: 'Purchase 0.1 BTC please'${NC}"
curl -s -X POST "$BASE" -H "Content-Type: application/json" \
  -d "{\"user_id\": \"$USER\", \"message\": \"Purchase 0.1 BTC please\"}" | python3 -m json.tool
echo ""

sleep 2

echo -e "${BLUE}4. Check Positions:${NC}"
curl -s -X POST "$BASE" -H "Content-Type: application/json" \
  -d "{\"user_id\": \"$USER\", \"message\": \"what positions do I have?\"}" | python3 -m json.tool
echo ""

sleep 2

echo -e "${BLUE}5. Sell Order:${NC}"
curl -s -X POST "$BASE" -H "Content-Type: application/json" \
  -d "{\"user_id\": \"$USER\", \"message\": \"sell 0.01 BTC\"}" | python3 -m json.tool
echo ""

echo -e "${GREEN}=========================================="
echo "Demo Complete!"
echo "==========================================${NC}"

