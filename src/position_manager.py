"""
Position Manager - Tracks open positions
Manages both regular and trailing stop positions
"""
from typing import List, Dict, Any, Optional

class PositionManager:
    def __init__(self):
        self.positions = {}  # {exchange_name: {order_id: order}}
        self.trailing_stops = {}  # {exchange_name: {order_id: trail_percent}}

    def add_position(self, exchange_name: str, order: Dict[str, Any]):
        if exchange_name not in self.positions:
            self.positions[exchange_name] = {}
        self.positions[exchange_name][order['id']] = order

    def remove_position(self, exchange_name: str, order_id: str):
        if exchange_name in self.positions and order_id in self.positions[exchange_name]:
            del self.positions[exchange_name][order_id]
        if exchange_name in self.trailing_stops and order_id in self.trailing_stops[exchange_name]:
            del self.trailing_stops[exchange_name][order_id]

    def get_positions(self, exchange_name: str = None) -> List[Dict[str, Any]]:
        if exchange_name:
            return list(self.positions.get(exchange_name, {}).values())
        return [pos for exchange in self.positions.values() for pos in exchange.values()]

    def set_trailing_stop(self, exchange_name: str, position_id: str, trailing_percent: float):
        if exchange_name not in self.trailing_stops:
            self.trailing_stops[exchange_name] = {}
        self.trailing_stops[exchange_name][position_id] = trailing_percent