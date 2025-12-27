"""Telegram bot interface for the trading agent."""
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import structlog
import httpx

from config.settings import settings


logger = structlog.get_logger()

# Backend API URL
API_BASE_URL = "http://localhost:8000"


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    user_id = str(update.effective_user.id)
    
    await update.message.reply_text(
        f"Welcome to the AI Trading Agent!\n\n"
        f"Your User ID: {user_id}\n\n"
        f"To get started:\n"
        f"1. Add exchanges via /add_exchange\n"
        f"2. Start trading with natural language commands\n\n"
        f"Examples:\n"
        f"- 'buy 0.1 BTC'\n"
        f"- 'check my USDT balance'\n"
        f"- 'what positions do I have?'"
    )


async def add_exchange_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /add_exchange command."""
    user_id = str(update.effective_user.id)
    
    # In production, you'd have a secure way to input API keys
    # For now, show instructions
    await update.message.reply_text(
        f"To add an exchange, use the API endpoint:\n"
        f"POST {API_BASE_URL}/api/user/add_exchange\n\n"
        f"Or set up exchanges via the web interface.\n\n"
        f"Note: API keys must be encrypted before sending."
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle user messages and route to agent."""
    user_id = str(update.effective_user.id)
    message_text = update.message.text
    
    logger.info(f"Received message", user_id=user_id, message=message_text[:100])
    
    # Send typing indicator
    await update.message.chat.send_action(action="typing")
    
    try:
        # Call backend API
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                f"{API_BASE_URL}/api/agent/message",
                json={
                    "user_id": user_id,
                    "message": message_text
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                reply = result.get("response", "No response")
                action_taken = result.get("action_taken", "")
                
                full_reply = reply
                if action_taken and action_taken != "No action":
                    full_reply += f"\n\nAction: {action_taken}"
                
                latency = result.get("latency_ms", 0)
                full_reply += f"\n\n⏱ Latency: {latency:.1f}ms"
                
                await update.message.reply_text(full_reply)
            else:
                error = response.json().get("detail", "Unknown error")
                await update.message.reply_text(f"Error: {error}")
    
    except asyncio.TimeoutError:
        await update.message.reply_text("⏱ Request timed out (>10s). Please try again.")
    except Exception as e:
        logger.error(f"Error handling message", user_id=user_id, error=str(e))
        await update.message.reply_text(f"Error: {str(e)}")


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status command."""
    user_id = str(update.effective_user.id)
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_BASE_URL}/api/user/{user_id}/status")
            
            if response.status_code == 200:
                data = response.json()
                exchanges = data.get("exchanges", [])
                status = data.get("status", "unknown")
                
                await update.message.reply_text(
                    f"Status: {status}\n"
                    f"Connected Exchanges: {', '.join(exchanges) if exchanges else 'None'}\n"
                    f"User ID: {user_id}"
                )
            else:
                await update.message.reply_text("Unable to fetch status")
    
    except Exception as e:
        logger.error(f"Error fetching status", error=str(e))
        await update.message.reply_text(f"Error: {str(e)}")


def main():
    """Start the Telegram bot."""
    if not settings.telegram_bot_token:
        logger.error("TELEGRAM_BOT_TOKEN not set in environment")
        return
    
    application = Application.builder().token(settings.telegram_bot_token).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("add_exchange", add_exchange_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("Starting Telegram bot")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

