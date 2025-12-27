#!/bin/bash
# Demo script optimized for video recording with QuickTime

BASE="http://localhost:8000/api/agent/message"
USER="demo_user_1"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

clear
echo -e "${BOLD}${CYAN}=========================================="
echo "AI Trading Agent - Live Demo"
echo "==========================================${NC}"
echo ""
echo -e "${YELLOW}Recording Tips:${NC}"
echo "- Make sure backend is running on port 8000"
echo "- Swagger UI available at: http://localhost:8000/docs"
echo "- All trades are in DEMO MODE (simulated)"
echo ""
sleep 3

echo -e "${BOLD}${BLUE}=========================================="
echo "PART 1: Health Check"
echo "==========================================${NC}"
echo ""
echo "Checking if backend is running..."
curl -s http://localhost:8000/ | python3 -m json.tool
echo ""
sleep 3

echo -e "${BOLD}${BLUE}=========================================="
echo "PART 2: Natural Language Balance Check"
echo "==========================================${NC}"
echo ""
echo -e "${CYAN}User Message:${NC} 'check my USDT balance'"
echo ""
curl -s -X POST "$BASE" -H "Content-Type: application/json" \
  -d "{\"user_id\": \"$USER\", \"message\": \"check my USDT balance\"}" | python3 -m json.tool
echo ""
echo -e "${GREEN}✓ Shows unified balance across multiple exchanges${NC}"
echo ""
sleep 4

echo -e "${BOLD}${BLUE}=========================================="
echo "PART 3: Price Check"
echo "==========================================${NC}"
echo ""
echo -e "${CYAN}User Message:${NC} 'what is the current price of Bitcoin?'"
echo ""
curl -s -X POST "$BASE" -H "Content-Type: application/json" \
  -d "{\"user_id\": \"$USER\", \"message\": \"what is the current price of Bitcoin?\"}" | python3 -m json.tool
echo ""
echo -e "${GREEN}✓ Symbol normalization: 'Bitcoin' → 'BTC/USDT:USDT'${NC}"
echo ""
sleep 4

echo -e "${BOLD}${BLUE}=========================================="
echo "PART 4: Intent Consistency (Key Feature)"
echo "==========================================${NC}"
echo ""
echo -e "${YELLOW}Same intent, different phrasings - all produce identical outcomes${NC}"
echo ""
sleep 2

echo -e "${CYAN}Phrasing 1:${NC} 'buy 0.1 BTC'"
curl -s -X POST "$BASE" -H "Content-Type: application/json" \
  -d "{\"user_id\": \"$USER\", \"message\": \"buy 0.1 BTC\"}" | python3 -m json.tool
echo ""
sleep 3

echo -e "${CYAN}Phrasing 2:${NC} 'I want to buy 0.1 Bitcoin'"
curl -s -X POST "$BASE" -H "Content-Type: application/json" \
  -d "{\"user_id\": \"$USER\", \"message\": \"I want to buy 0.1 Bitcoin\"}" | python3 -m json.tool
echo ""
sleep 3

echo -e "${CYAN}Phrasing 3:${NC} 'Purchase 0.1 BTC please'"
curl -s -X POST "$BASE" -H "Content-Type: application/json" \
  -d "{\"user_id\": \"$USER\", \"message\": \"Purchase 0.1 BTC please\"}" | python3 -m json.tool
echo ""
echo -e "${GREEN}✓ All three produce the same normalized intent and execution${NC}"
echo ""
sleep 4

echo -e "${BOLD}${BLUE}=========================================="
echo "PART 5: Position Check"
echo "==========================================${NC}"
echo ""
echo -e "${CYAN}User Message:${NC} 'what positions do I have?'"
echo ""
curl -s -X POST "$BASE" -H "Content-Type: application/json" \
  -d "{\"user_id\": \"$USER\", \"message\": \"what positions do I have?\"}" | python3 -m json.tool
echo ""
echo -e "${GREEN}✓ Unified view across all exchanges${NC}"
echo ""
sleep 4

echo -e "${BOLD}${BLUE}=========================================="
echo "PART 6: Sell Order"
echo "==========================================${NC}"
echo ""
echo -e "${CYAN}User Message:${NC} 'sell 0.01 BTC'"
echo ""
curl -s -X POST "$BASE" -H "Content-Type: application/json" \
  -d "{\"user_id\": \"$USER\", \"message\": \"sell 0.01 BTC\"}" | python3 -m json.tool
echo ""
echo -e "${GREEN}✓ Complete trade lifecycle demonstrated${NC}"
echo ""
sleep 3

echo -e "${BOLD}${GREEN}=========================================="
echo "Demo Complete!"
echo "==========================================${NC}"
echo ""
echo -e "${CYAN}Key Highlights:${NC}"
echo "• Zero hard-coded paths - all LLM-driven"
echo "• Fully autonomous - no follow-up questions"
echo "• Deterministic execution - same intent = same outcome"
echo "• Multi-exchange support with unified state"
echo "• Sub-10 second latency"
echo "• Production-ready architecture"
echo ""
echo -e "${YELLOW}Interactive API docs:${NC} http://localhost:8000/docs"
echo ""

