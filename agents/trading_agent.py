"""LangGraph-based trading agent with dynamic intent-to-execution."""
from typing import Dict, Any, TypedDict, Annotated, Optional
from datetime import datetime
import asyncio
import structlog
import json
import re
from langgraph.graph import StateGraph, END
from langchain.anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from config.settings import settings
from agents.tools import create_tools
from agents.intent_models import TradingIntent
from exchanges.exchange_manager import ExchangeManager
from storage.state_manager import state_manager
from storage.memory_manager import memory_manager
from audit.audit_logger import audit_logger


logger = structlog.get_logger()


class AgentState(TypedDict):
    """State maintained throughout agent execution."""
    user_id: str
    messages: Annotated[list, lambda x, y: x + y]  # Message history
    intent: str  # JSON string of TradingIntent
    reasoning: str
    action_taken: str
    execution_id: str
    start_time: float
    error: Optional[str]


class TradingAgent:
    """
    LangGraph-based trading agent.
    
    Key principle: Zero hard-coded paths. All decisions are LLM-driven.
    Natural language variations of the same intent must produce identical outcomes.
    """
    
    def __init__(self, user_id: str, exchange_manager: ExchangeManager):
        self.user_id = user_id
        self.exchange_manager = exchange_manager
        
        # Initialize LLM
        if settings.anthropic_api_key:
            self.llm = ChatAnthropic(
                model=settings.default_model if "claude" in settings.default_model else "claude-3-5-sonnet-20241022",
                temperature=0.1,  # Low temperature for deterministic decisions
                api_key=settings.anthropic_api_key
            )
        elif settings.openai_api_key:
            self.llm = ChatOpenAI(
                model=settings.default_model if "gpt" in settings.default_model else "gpt-4-turbo-preview",
                temperature=0.1,
                api_key=settings.openai_api_key
            )
        else:
            raise ValueError("No LLM API key configured")
        
        # Create tools
        self.tools = create_tools(user_id, exchange_manager)
        
        # Bind tools to LLM
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        
        # Build graph
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph execution graph."""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("extract_intent", self._extract_intent)
        workflow.add_node("reason_and_execute", self._reason_and_execute)
        workflow.add_node("audit", self._audit)
        
        # Add edges
        workflow.set_entry_point("extract_intent")
        workflow.add_edge("extract_intent", "reason_and_execute")
        workflow.add_edge("reason_and_execute", "audit")
        workflow.add_edge("audit", END)
        
        return workflow.compile()
    
    async def _extract_intent(self, state: AgentState) -> AgentState:
        """
        Extract intent from user message using structured output.
        
        This ensures deterministic parsing - same intent always produces same structure.
        """
        user_message = state["messages"][-1].content if state["messages"] else ""
        
        # Use LLM with structured output for deterministic intent extraction
        intent_prompt = f"""Extract the trading intent from this user message. Be precise and deterministic.

User message: {user_message}

Extract the intent according to these rules:
- For buy/sell: extract intent, symbol (will be auto-normalized to format like BTC/USDT:USDT), amount, and side
- For balance checks: extract intent and asset (e.g., "USDT", "BTC")
- For position checks: extract intent only
- Be deterministic: similar phrasings must produce identical structured outputs
- Symbols will be normalized automatically, so "BTC", "Bitcoin", "BTC/USDT" all become "BTC/USDT:USDT"

Examples:
- "buy 0.1 BTC" -> intent=buy, symbol=BTC, amount=0.1, side=buy (symbol will be normalized to BTC/USDT:USDT)
- "I want to buy 0.1 Bitcoin" -> intent=buy, symbol=BTC, amount=0.1, side=buy
- "check my USDT balance" -> intent=check_balance, asset=USDT
- "what positions do I have?" -> intent=check_position

CRITICAL: Be consistent. Same intent in different words must produce the same structured output."""
        
        try:
            # Use structured output if available (OpenAI and Claude support this)
            # For maximum determinism, we use with_structured_output
            if hasattr(self.llm, 'with_structured_output'):
                structured_llm = self.llm.with_structured_output(TradingIntent)
                intent_obj = await structured_llm.ainvoke([HumanMessage(content=intent_prompt)])
            else:
                # Fallback: use JSON mode or manual parsing with retry
                response = await self.llm.ainvoke([
                    HumanMessage(content=f"{intent_prompt}\n\nReturn ONLY valid JSON matching this schema: {TradingIntent.model_json_schema()}")
                ])
                
                # Parse JSON from response
                import json
                import re
                intent_str = response.content
                
                # Extract JSON more robustly
                json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', intent_str)
                if json_match:
                    intent_dict = json.loads(json_match.group())
                else:
                    # Try to find JSON between code blocks
                    json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', intent_str, re.DOTALL)
                    if json_match:
                        intent_dict = json.loads(json_match.group(1))
                    else:
                        intent_dict = {"intent": "unknown", "details": intent_str}
                
                # Validate and create TradingIntent object
                intent_obj = TradingIntent(**intent_dict)
            
            # Store as JSON string for state
            state["intent"] = intent_obj.model_dump_json()
            
        except Exception as e:
            logger.error(f"Error extracting intent", error=str(e))
            # Fallback to unknown intent
            intent_obj = TradingIntent(intent="unknown", details=f"Error: {str(e)}")
            state["intent"] = intent_obj.model_dump_json()
        
        return state
    
    async def _reason_and_execute(self, state: AgentState) -> AgentState:
        """
        Reason about the intent and execute using tools.
        
        This is fully LLM-driven with no hard-coded paths.
        """
        import json
        
        # Parse intent from state
        try:
            intent_data = json.loads(state["intent"])
            intent_obj = TradingIntent(**intent_data)
        except Exception as e:
            logger.error(f"Error parsing intent", error=str(e))
            intent_obj = TradingIntent(intent="unknown", details=f"Parse error: {str(e)}")
        
        # Get relevant memory
        user_message = state["messages"][-1].content if state["messages"] else ""
        relevant_memory = memory_manager.search_relevant_memory(self.user_id, user_message, n_results=3)
        
        # Get unified state context (the agent's "proprioception")
        unified_balances = await state_manager.get_unified_balances(self.user_id)
        unified_positions = await state_manager.get_unified_positions(self.user_id)
        
        # Get available exchanges
        available_exchanges = self.exchange_manager.get_user_exchanges(self.user_id)
        
        # Build system message with full context
        system_prompt = f"""You are an autonomous trading agent with full authority to execute trades. You have ZERO tolerance for follow-up questions - resolve everything autonomously.

User ID: {self.user_id}

Available tools:
- get_balance(asset): Get total balance of an asset across ALL connected exchanges (unified view)
- get_position(symbol): Get position details for a symbol across all exchanges
- place_order(symbol, side, amount, order_type, price, reduce_only): Place an order on an exchange (REAL execution with real money)
- get_ticker(symbol): Get current price/ticker for a symbol

Available exchanges: {', '.join(available_exchanges) if available_exchanges else 'None (must add exchanges first)'}

Current unified balances across all exchanges:
{json.dumps(unified_balances, indent=2) if unified_balances else 'No balances available'}

Current unified positions across all exchanges:
{json.dumps(unified_positions, indent=2) if unified_positions else 'No open positions'}

Extracted intent: {intent_obj.model_dump_json()}

Rules (CRITICAL):
1. NO follow-up questions. You MUST resolve the intent autonomously with available information.
2. Use unified state (balances/positions) for ALL decisions - this is your "proprioception".
3. Execute deterministically - same intent + same state MUST produce same action.
4. You are fully responsible for the decision. No hedging or passing blame.
5. For orders, choose the best exchange based on balance availability and execution quality.
6. If information is missing, make reasonable assumptions based on context. Never ask the user.

Relevant past interactions:
{relevant_memory if relevant_memory else "None"}

Now execute the intent using the appropriate tools. Be decisive, autonomous, and deterministic."""
        
        # Invoke LLM with tools
        messages = [
            SystemMessage(content=system_prompt),
            *state["messages"]
        ]
        
        try:
            response = await self.llm_with_tools.ainvoke(messages)
            
            # Execute tool calls (fully LLM-driven, no hard-coded logic)
            action_taken = "No action"
            if hasattr(response, 'tool_calls') and response.tool_calls:
                for tool_call in response.tool_calls:
                    tool_name = tool_call["name"]
                    tool_args = tool_call["args"]
                    
                    # Find and execute tool
                    for tool in self.tools:
                        if tool.name == tool_name:
                            try:
                                result = await tool._arun(**tool_args)
                                action_taken = f"{tool_name}({tool_args}) -> {result}"
                                logger.info(f"Tool executed", tool=tool_name, args=tool_args, result=result[:200])
                                
                                # Update state immediately after successful execution
                                await state_manager.set_execution_state(
                                    self.user_id,
                                    state["execution_id"],
                                    {"action": action_taken, "status": "success"}
                                )
                            except Exception as e:
                                logger.error(f"Tool execution error", tool=tool_name, error=str(e))
                                action_taken = f"Error in {tool_name}: {str(e)}"
                                state["error"] = str(e)
                            break
            
            state["reasoning"] = response.content
            state["action_taken"] = action_taken
            
        except Exception as e:
            logger.error(f"Error in reason_and_execute", error=str(e))
            state["error"] = str(e)
            state["reasoning"] = f"Error during execution: {str(e)}"
            state["action_taken"] = "Error"
        
        return state
    
    async def _audit(self, state: AgentState) -> AgentState:
        """Create audit log entry with full reasoning chain."""
        latency_ms = (datetime.utcnow().timestamp() - state["start_time"]) * 1000
        
        # Get unified state snapshot at execution time
        unified_balances = await state_manager.get_unified_balances(self.user_id)
        unified_positions = await state_manager.get_unified_positions(self.user_id)
        
        unified_state_snapshot = {
            "balances": unified_balances,
            "positions": unified_positions,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Extract fill result if action_taken contains order info
        fill_result = None
        if "Order filled" in state.get("action_taken", ""):
            # Parse fill information from action_taken string
            # In production, this would come from the actual OrderFill object
            fill_result = {
                "action": state["action_taken"],
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # Log to audit system
        audit_logger.log_execution(
            execution_id=state["execution_id"],
            user_id=self.user_id,
            intent=state["intent"],
            reasoning=state["reasoning"],
            action_taken=state["action_taken"],
            unified_state_at_execution=unified_state_snapshot,
            fill_result=fill_result,
            latency_ms=latency_ms,
            error=state.get("error")
        )
        
        # Store in memory
        memory_manager.add_interaction(
            self.user_id,
            state["messages"][-1].content if state["messages"] else "",
            state["intent"],
            state["action_taken"],
            {
                "execution_id": state["execution_id"],
                "timestamp": datetime.utcnow().isoformat(),
                "latency_ms": latency_ms
            }
        )
        
        return state
    
    async def process_message(self, message: str) -> Dict[str, Any]:
        """
        Process a user message and return response.
        
        This is the main entry point. Must complete in <10 seconds.
        """
        execution_id = f"exec_{datetime.utcnow().timestamp()}"
        start_time = datetime.utcnow().timestamp()
        
        initial_state: AgentState = {
            "user_id": self.user_id,
            "messages": [HumanMessage(content=message)],
            "intent": "",
            "reasoning": "",
            "action_taken": "",
            "execution_id": execution_id,
            "start_time": start_time,
            "error": None
        }
        
        try:
            # Execute graph
            final_state = await self.graph.ainvoke(initial_state)
            
            latency = (datetime.utcnow().timestamp() - start_time) * 1000
            
            if latency > settings.max_execution_time_seconds * 1000:
                logger.warning(f"Execution exceeded time limit", latency_ms=latency, limit_ms=settings.max_execution_time_seconds * 1000)
            
            return {
                "execution_id": execution_id,
                "response": final_state.get("reasoning", ""),
                "action_taken": final_state.get("action_taken", ""),
                "latency_ms": latency,
                "success": True
            }
        except Exception as e:
            logger.error(f"Agent execution error", error=str(e))
            return {
                "execution_id": execution_id,
                "response": f"Error: {str(e)}",
                "action_taken": "",
                "latency_ms": (datetime.utcnow().timestamp() - start_time) * 1000,
                "success": False
            }

