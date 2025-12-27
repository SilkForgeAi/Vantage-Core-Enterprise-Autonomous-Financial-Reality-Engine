"""Background task for syncing exchange state to Redis."""
import asyncio
from typing import Dict
import structlog
from exchanges.exchange_manager import ExchangeManager
from storage.state_manager import state_manager
from config.settings import settings


logger = structlog.get_logger()


class StateSyncService:
    """Background service to sync exchange state to Redis periodically."""
    
    def __init__(self, user_exchange_managers: Dict[str, ExchangeManager]):
        """
        Initialize state sync service.
        
        Args:
            user_exchange_managers: Dict mapping user_id to ExchangeManager
        """
        self.user_exchange_managers = user_exchange_managers
        self.running = False
        self.sync_task = None
    
    async def start(self):
        """Start the background sync task."""
        if self.running:
            return
        
        self.running = True
        self.sync_task = asyncio.create_task(self._sync_loop())
        logger.info("State sync service started")
    
    async def stop(self):
        """Stop the background sync task."""
        self.running = False
        if self.sync_task:
            self.sync_task.cancel()
            try:
                await self.sync_task
            except asyncio.CancelledError:
                pass
        logger.info("State sync service stopped")
    
    async def _sync_loop(self):
        """Main sync loop."""
        while self.running:
            try:
                await self._sync_all_users()
                await asyncio.sleep(settings.state_sync_interval_seconds)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in state sync loop", error=str(e))
                await asyncio.sleep(1)
    
    async def _sync_all_users(self):
        """Sync state for all users."""
        for user_id, exchange_manager in self.user_exchange_managers.items():
            try:
                await self._sync_user_state(user_id, exchange_manager)
            except Exception as e:
                logger.error(f"Error syncing state for user {user_id}", error=str(e))
    
    async def _sync_user_state(self, user_id: str, exchange_manager: ExchangeManager):
        """Sync state for a single user."""
        # Sync balances
        unified_balances = await exchange_manager.get_unified_balances(user_id)
        for exchange_name, balances in unified_balances.items():
            balance_dict = {}
            for asset, balance_obj in balances.items():
                balance_dict[asset] = balance_obj.total
            await state_manager.set_balance(user_id, exchange_name, balance_dict)
        
        # Sync positions
        unified_positions = await exchange_manager.get_unified_positions(user_id)
        for exchange_name, positions in unified_positions.items():
            for symbol, position in positions.items():
                await state_manager.set_position(
                    user_id,
                    exchange_name,
                    symbol,
                    {
                        "size": position.size,
                        "side": position.side,
                        "entry_price": position.entry_price,
                        "unrealized_pnl": position.unrealized_pnl,
                        "leverage": position.leverage
                    }
                )

