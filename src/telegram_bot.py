"""
Telegram Bot - User interface and command processor
Handles all Telegram interactions and commands
"""
import logging
import asyncio
import threading
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackContext
)
from utils.config_loader import load_config
from exchange_manager import ExchangeManager
from trade_manager import TradeManager
from utils.message_handler import MessageHandler as MsgHandler
from heartbeat_manager import HeartbeatManager

class TelegramBot:
    def __init__(self, config):
        """Inicializálja a Telegram botot"""
        # Logger beállítása minden más előtt
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info("TelegramBot inicializálása...")
        
        try:
            self.config = config
            self.message_handler = MsgHandler(config['settings']['default_language'])
            self.exchange_manager = ExchangeManager(config)
            self.trade_manager = TradeManager(self.exchange_manager)
            self.bot_token = config['telegram']['api_key']
            self.allowed_users = config['telegram']['allowed_users']
            
            self.logger.debug("Telegram alkalmazás építése...")
            self.app = Application.builder().token(self.bot_token).build()
            
            self._register_handlers()
            self.heartbeat = HeartbeatManager(self)
            self.logger.info("TelegramBot sikeresen inicializálva")
            
        except Exception as e:
            self.logger.critical(f"Hiba a TelegramBot inicializálásakor: {str(e)}", exc_info=True)
            raise

    def _register_handlers(self):
        """Register all command and message handlers"""
        handlers = [
            CommandHandler("start", self.start),
            CommandHandler("help", self.help),
            CommandHandler("buy", self.buy),
            CommandHandler("sell", self.sell),
            CommandHandler("positions", self.get_positions),
            CommandHandler("balance", self.get_balance),
            CommandHandler("add_exchange", self.add_exchange),
            CommandHandler("remove_exchange", self.remove_exchange),
            CommandHandler("list_exchanges", self.list_exchanges),
            CommandHandler("ping", self.ping),
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
        ]
        
        for handler in handlers:
            self.app.add_handler(handler)
        self.logger.debug(f"Registered {len(handlers)} handlers")

    async def help(self, update: Update, context: CallbackContext):
        """Display help message with all available commands"""
        if update.effective_user.id not in self.allowed_users:
            self.logger.warning(f"Unauthorized access attempt from user {update.effective_user.id}")
            return
            
        self.logger.debug(f"Sending help message to user {update.effective_user.id}")
        await update.message.reply_text(
            self.message_handler.get_message('help_text')
        )

    async def start(self, update: Update, context: CallbackContext):
        """Handle /start command"""
        if update.effective_user.id not in self.allowed_users:
            self.logger.warning(f"Unauthorized user tried to start bot: {update.effective_user.id}")
            return
            
        self.logger.info(f"New user started bot: {update.effective_user.id}")
        await update.message.reply_text(
            self.message_handler.get_message('welcome')
        )

    async def buy(self, update: Update, context: CallbackContext):
        """Handle buy command"""
        if update.effective_user.id not in self.allowed_users:
            return
            
        self.logger.info(f"Buy command received from {update.effective_user.id}")
        
        try:
            args = context.args
            if len(args) < 3:
                self.logger.warning(f"Insufficient arguments for buy command from {update.effective_user.id}")
                await update.message.reply_text(
                    self.message_handler.get_message('buy_usage')
                )
                return
            
            exchange_name = args[0]
            symbol = args[1]
            amount = float(args[2])
            price = float(args[3]) if len(args) > 3 else None
            
            self.logger.debug(f"Attempting to buy {amount} of {symbol} on {exchange_name} at {price or 'market'} price")
            
            order = await self.trade_manager.open_position(
                exchange_name, symbol, 'buy', amount, price
            )
            
            self.logger.info(f"Successfully opened position: {order}")
            await update.message.reply_text(
                self.message_handler.get_message('position_opened').format(
                    exchange=exchange_name,
                    symbol=symbol,
                    side='buy',
                    amount=amount,
                    price=price if price else 'market'
                )
            )
        except Exception as e:
            self.logger.error(f"Error in buy command: {str(e)}", exc_info=True)
            await update.message.reply_text(
                self.message_handler.get_message('error').format(error=str(e))
            )

    async def sell(self, update: Update, context: CallbackContext):
        """Handle sell command"""
        if update.effective_user.id not in self.allowed_users:
            return
            
        self.logger.info(f"Sell command received from {update.effective_user.id}")
        
        try:
            args = context.args
            if len(args) < 3:
                self.logger.warning(f"Insufficient arguments for sell command from {update.effective_user.id}")
                await update.message.reply_text(
                    self.message_handler.get_message('sell_usage')
                )
                return
            
            exchange_name = args[0]
            symbol = args[1]
            amount = float(args[2])
            price = float(args[3]) if len(args) > 3 else None
            
            self.logger.debug(f"Attempting to sell {amount} of {symbol} on {exchange_name} at {price or 'market'} price")
            
            order = await self.trade_manager.close_position(
                exchange_name, symbol, 'sell', amount, price
            )
            
            self.logger.info(f"Successfully closed position: {order}")
            await update.message.reply_text(
                self.message_handler.get_message('position_opened').format(
                    exchange=exchange_name,
                    symbol=symbol,
                    side='sell',
                    amount=amount,
                    price=price if price else 'market'
                )
            )
        except Exception as e:
            self.logger.error(f"Error in sell command: {str(e)}", exc_info=True)
            await update.message.reply_text(
                self.message_handler.get_message('error').format(error=str(e))
            )

    async def get_positions(self, update: Update, context: CallbackContext):
        """Get open positions"""
        if update.effective_user.id not in self.allowed_users:
            return
            
        self.logger.info(f"Positions request from {update.effective_user.id}")
        
        try:
            exchange_name = context.args[0] if context.args else None
            self.logger.debug(f"Getting positions for {exchange_name or 'all exchanges'}")
            
            positions = await self.trade_manager.get_open_positions(exchange_name)
            
            self.logger.debug(f"Found {len(positions)} positions")
            await update.message.reply_text(
                self.message_handler.get_message('positions').format(
                    exchange=exchange_name or 'all',
                    positions="\n".join([str(p) for p in positions]) if positions else "None"
                )
            )
        except Exception as e:
            self.logger.error(f"Error getting positions: {str(e)}", exc_info=True)
            await update.message.reply_text(
                self.message_handler.get_message('error').format(error=str(e))
            )

    async def get_balance(self, update: Update, context: CallbackContext):
        """Get account balance"""
        if update.effective_user.id not in self.allowed_users:
            return
            
        self.logger.info(f"Balance request from {update.effective_user.id}")
        
        try:
            exchange_name = context.args[0] if context.args else None
            if not exchange_name:
                self.logger.warning("No exchange specified for balance request")
                await update.message.reply_text(
                    self.message_handler.get_message('specify_exchange')
                )
                return
            
            self.logger.debug(f"Getting balance for {exchange_name}")
            balance = await self.exchange_manager.get_balance(exchange_name)
            
            self.logger.info(f"Balance retrieved for {exchange_name}")
            await update.message.reply_text(
                self.message_handler.get_message('balance').format(
                    exchange=exchange_name,
                    free=balance['free'],
                    currency=balance['info']['asset']
                )
            )
        except Exception as e:
            self.logger.error(f"Error getting balance: {str(e)}", exc_info=True)
            await update.message.reply_text(
                self.message_handler.get_message('error').format(error=str(e))
            )

    async def add_exchange(self, update: Update, context: CallbackContext):
        """Add new exchange"""
        if update.effective_user.id not in self.allowed_users:
            return
            
        self.logger.info(f"Add exchange request from {update.effective_user.id}")
        
        try:
            args = context.args
            if len(args) < 4:
                self.logger.warning(f"Insufficient arguments for add_exchange from {update.effective_user.id}")
                await update.message.reply_text(
                    self.message_handler.get_message('add_exchange_usage')
                )
                return

            name = args[0]
            exchange = args[1]
            api_key = args[2]
            secret_key = args[3]

            config = {
                "exchange": exchange,
                "apiKey": api_key,
                "secret": secret_key,
                "enableRateLimit": True
            }

            self.logger.debug(f"Testing connection to {exchange} as {name}")
            if not await self.exchange_manager.test_exchange_connection(config):
                self.logger.warning(f"Failed to connect to exchange {exchange}")
                await update.message.reply_text(
                    self.message_handler.get_message('exchange_connection_failed')
                )
                return

            self.logger.info(f"Adding exchange {name} ({exchange})")
            success = await self.exchange_manager.add_exchange(name, config)
            
            if success:
                self.logger.info(f"Successfully added exchange {name}")
                await update.message.reply_text(
                    self.message_handler.get_message('exchange_added').format(name=name)
                )
            else:
                self.logger.warning(f"Exchange {name} already exists")
                await update.message.reply_text(
                    self.message_handler.get_message('exchange_exists').format(name=name)
                )
        except Exception as e:
            self.logger.error(f"Error adding exchange: {str(e)}", exc_info=True)
            await update.message.reply_text(
                self.message_handler.get_message('error').format(error=str(e))
            )

    async def remove_exchange(self, update: Update, context: CallbackContext):
        """Remove exchange"""
        if update.effective_user.id not in self.allowed_users:
            return
            
        self.logger.info(f"Remove exchange request from {update.effective_user.id}")
        
        try:
            args = context.args
            if len(args) < 1:
                self.logger.warning(f"Missing exchange name for removal from {update.effective_user.id}")
                await update.message.reply_text(
                    self.message_handler.get_message('remove_exchange_usage')
                )
                return

            name = args[0]
            self.logger.info(f"Attempting to remove exchange {name}")
            
            success = await self.exchange_manager.remove_exchange(name)
            if success:
                self.logger.info(f"Successfully removed exchange {name}")
                await update.message.reply_text(
                    self.message_handler.get_message('exchange_removed').format(name=name)
                )
            else:
                self.logger.warning(f"Exchange {name} not found")
                await update.message.reply_text(
                    self.message_handler.get_message('exchange_not_found').format(name=name)
                )
        except Exception as e:
            self.logger.error(f"Error removing exchange: {str(e)}", exc_info=True)
            await update.message.reply_text(
                self.message_handler.get_message('error').format(error=str(e))
            )

    async def list_exchanges(self, update: Update, context: CallbackContext):
        """List available exchanges"""
        if update.effective_user.id not in self.allowed_users:
            return
            
        self.logger.info(f"List exchanges request from {update.effective_user.id}")
        
        try:
            exchanges = self.exchange_manager.get_available_exchanges()
            
            if not exchanges:
                self.logger.info("No exchanges configured")
                await update.message.reply_text(
                    self.message_handler.get_message('no_exchanges')
                )
                return

            message = self.message_handler.get_message('available_exchanges')
            for name, details in exchanges.items():
                message += f"\n- {name}: {details.split(' ')[0]}"

            self.logger.debug(f"Returning {len(exchanges)} exchanges")
            await update.message.reply_text(message)
        except Exception as e:
            self.logger.error(f"Error listing exchanges: {str(e)}", exc_info=True)
            await update.message.reply_text(
                self.message_handler.get_message('error').format(error=str(e))
            )

    async def handle_message(self, update: Update, context: CallbackContext):
        """Handle non-command messages"""
        if update.effective_user.id not in self.allowed_users:
            return
            
        self.logger.debug(f"Non-command message from {update.effective_user.id}: {update.message.text}")
        await update.message.reply_text(
            self.message_handler.get_message('invalid_command')
        )

    async def ping(self, update: Update, context: CallbackContext):
        """Respond with pong"""
        if update.effective_user.id not in self.allowed_users:
            return
            
        self.logger.debug(f"Ping request from {update.effective_user.id}")
        await update.message.reply_text(
            self.message_handler.get_message('ping_response')
        )

    async def _idle(self):
        """Egyszerű ébren tartó ciklus"""
        try:
            while True:
                await asyncio.sleep(3600)
        except asyncio.CancelledError:
            pass
                
    async def run(self):
        """Run the bot"""
        try:
            self.logger.info("Starting bot...")
            
            # Inicializálás és indítás
            await self.app.initialize()
            await self.app.start()
            
            # Heartbeat indítása
            await self.heartbeat.send_startup_message()
            self.heartbeat_task = asyncio.create_task(self.heartbeat.start())

            # Polling indítása külön taskként
            self.polling_task = asyncio.create_task(
                self.app.updater.start_polling(drop_pending_updates=True)
            )
            
            self.logger.info("Bot started successfully")
            
            # Végtelen ciklus a futás fenntartásához
            while True:
                await asyncio.sleep(3600)
                
        except asyncio.CancelledError:
            self.logger.info("Bot shutdown initiated")
        except Exception as e:
            self.logger.critical(f"Unexpected error: {str(e)}", exc_info=True)
        finally:
            self.logger.info("Shutting down bot...")
            await self.heartbeat.stop()
            
            # Taskok leállítása
            if hasattr(self, 'polling_task'):
                self.polling_task.cancel()
                try:
                    await self.polling_task
                except asyncio.CancelledError:
                    pass
                    
            if hasattr(self, 'heartbeat_task'):
                self.heartbeat_task.cancel()
                try:
                    await self.heartbeat_task
                except asyncio.CancelledError:
                    pass
                    
            # App leállítása
            if hasattr(self.app, 'updater') and self.app.updater.running:
                await self.app.updater.stop()
            if hasattr(self.app, 'running') and self.app.running:
                await self.app.stop()
            if hasattr(self.app, 'shutdown'):
                await self.app.shutdown()
            self.logger.info("Bot shutdown completed")