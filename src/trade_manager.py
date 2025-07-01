"""
Trade Manager - Handles trading operations
Executes orders and manages positions
"""
import logging
from typing import List, Dict, Any, Optional
from position_manager import PositionManager
from utils.message_handler import MessageHandler

class TradeManager:
    def __init__(self, exchange_manager):
        self.exchange_manager = exchange_manager
        self.position_manager = PositionManager()
        self.message_handler = MessageHandler()

    async def open_position(self, exchange_name: str, symbol: str, side: str, amount: float, price: float = None, params: Dict = None):
        order = await self.exchange_manager.create_order(
            exchange_name=exchange_name,
            symbol=symbol,
            side=side,
            amount=amount,
            price=price,
            params=params
        )
        self.position_manager.add_position(exchange_name, order)
        return order

    async def close_position(self, exchange_name: str, symbol: str, side: str, amount: float, price: float = None):
        order = await self.exchange_manager.create_order(
            exchange_name=exchange_name,
            symbol=symbol,
            side=side,
            amount=amount,
            price=price
        )
        self.position_manager.remove_position(exchange_name, order['id'])
        return order

    async def get_open_positions(self, exchange_name: str = None) -> List[Dict[str, Any]]:
        return self.position_manager.get_positions(exchange_name)

    async def set_trailing_stop(self, exchange_name: str, position_id: str, trailing_percent: float):
        self.position_manager.set_trailing_stop(exchange_name, position_id, trailing_percent)