"""
Exchange Manager - Handles all exchange connections
Manages dynamic addition/removal of exchanges
"""
import ccxt
import json
import logging
import os
from typing import Dict, Any, Optional
from utils.config_loader import get_config_path
from utils.message_handler import MessageHandler

class ExchangeManager:
    def __init__(self, config):
        self.config = config
        self.exchanges: Dict[str, Any] = {}
        self.message_handler = MessageHandler(config['settings']['default_language'])
        self.exchange_config_path = os.path.join(get_config_path(), 'exchange_configs.json')
        self.load_exchanges()

    def load_exchanges(self):
        try:
            with open(self.exchange_config_path, 'r') as f:
                exchange_configs = json.load(f)
                for name, config in exchange_configs.items():
                    self._initialize_exchange(name, config)
        except (FileNotFoundError, json.JSONDecodeError):
            logging.info("No exchange configs found, starting with empty config")

    def _initialize_exchange(self, name: str, config: Dict[str, Any]):
        try:
            exchange_class = getattr(ccxt, config['exchange'])
            self.exchanges[name] = exchange_class({
                'apiKey': config['apiKey'],
                'secret': config['secret'],
                'enableRateLimit': config.get('enableRateLimit', True),
                'options': config.get('options', {})
            })
            logging.info(f"Exchange connection created: {name}")
            return True
        except Exception as e:
            logging.error(f"Error initializing exchange {name}: {str(e)}")
            return False

    async def add_exchange(self, name: str, config: Dict[str, Any]) -> bool:
        if name in self.exchanges:
            return False
            
        # Validate the exchange connection before saving
        test_exchange = None
        try:
            exchange_class = getattr(ccxt, config['exchange'])
            test_exchange = exchange_class({
                'apiKey': config['apiKey'],
                'secret': config['secret'],
                'enableRateLimit': config.get('enableRateLimit', True)
            })
            await test_exchange.fetch_balance()  # Test connection
        except Exception as e:
            logging.error(f"Exchange validation failed: {str(e)}")
            return False
        finally:
            if test_exchange:
                await test_exchange.close()

        # Save to config
        exchange_configs = {}
        if os.path.exists(self.exchange_config_path):
            with open(self.exchange_config_path, 'r') as f:
                exchange_configs = json.load(f)
        
        exchange_configs[name] = config
        with open(self.exchange_config_path, 'w') as f:
            json.dump(exchange_configs, f, indent=2)

        # Initialize the exchange
        return self._initialize_exchange(name, config)

    async def remove_exchange(self, name: str) -> bool:
        if name not in self.exchanges:
            return False

        # Remove from active connections
        await self.exchanges[name].close()
        del self.exchanges[name]

        # Update config file
        exchange_configs = {}
        if os.path.exists(self.exchange_config_path):
            with open(self.exchange_config_path, 'r') as f:
                exchange_configs = json.load(f)
        
        if name in exchange_configs:
            del exchange_configs[name]
            with open(self.exchange_config_path, 'w') as f:
                json.dump(exchange_configs, f, indent=2)
        
        return True

    def get_exchange(self, name: str) -> Optional[Any]:
        return self.exchanges.get(name)

    def get_available_exchanges(self) -> Dict[str, str]:
        return {name: str(exchange) for name, exchange in self.exchanges.items()}

    async def test_exchange_connection(self, config: Dict[str, Any]) -> bool:
        try:
            exchange_class = getattr(ccxt, config['exchange'])
            exchange = exchange_class({
                'apiKey': config['apiKey'],
                'secret': config['secret'],
                'enableRateLimit': config.get('enableRateLimit', True)
            })
            await exchange.fetch_balance()
            await exchange.close()
            return True
        except Exception as e:
            logging.error(f"Connection test failed: {str(e)}")
            return False

    async def create_order(self, exchange_name: str, symbol: str, side: str, amount: float, price: float = None, params: Dict = None):
        exchange = self.get_exchange(exchange_name)
        if not exchange:
            raise ValueError(self.message_handler.get_message('exchange_not_found', name=exchange_name))
        
        order_type = 'limit' if price else 'market'
        
        try:
            return await exchange.create_order(
                symbol=symbol,
                type=order_type,
                side=side,
                amount=amount,
                price=price,
                params=params or {}
            )
        except Exception as e:
            logging.error(f"Order error: {str(e)}")
            raise

    async def get_balance(self, exchange_name: str):
        exchange = self.get_exchange(exchange_name)
        if not exchange:
            raise ValueError(self.message_handler.get_message('exchange_not_found', name=exchange_name))
        
        balance = await exchange.fetch_balance()
        return balance