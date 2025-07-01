"""
Heartbeat Manager - Periodikus életjel és indítási értesítések
"""

import time
import asyncio
import logging
from typing import TYPE_CHECKING
from version import __version__

if TYPE_CHECKING:
    from telegram_bot import TelegramBot

logger = logging.getLogger(__name__)

class HeartbeatManager:
    def __init__(self, bot: 'TelegramBot'):
        self.bot = bot
        self.last_activity = time.time()
        self.heartbeat_interval = 4 * 3600
        self.is_active = False

    async def send_startup_message(self):
        """Küld indítási értesítést minden engedélyezett felhasználónak"""
        try:
            # Részletes ellenőrzés
            if not hasattr(self.bot, 'message_handler'):
                logging.error("MessageHandler instance missing in bot")
                return
                
            if not hasattr(self.bot.message_handler, 'messages'):
                logging.error("Messages dictionary missing in MessageHandler")
                return
                
            if not isinstance(self.bot.message_handler.messages, dict):
                logging.error(f"Messages is not a dictionary: {type(self.bot.message_handler.messages)}")
                return

            # Üzenet ellenőrzése
            startup_msg = self.bot.message_handler.messages.get('startup_notification')
            if not startup_msg:
                logging.error("'startup_notification' message not found in loaded messages")
                return

            # Üzenet formázása
            start_time = time.strftime('%Y-%m-%d %H:%M:%S')
            try:
                message = startup_msg.format(
                    start_time=start_time,
                    version=__version__
                )
            except KeyError as e:
                logging.error(f"Missing key in startup message: {str(e)}")
                message = "✅ Bot szolgáltatás elindult"  # Alapértelmezett üzenet

            # Üzenet küldése
            for user_id in self.bot.allowed_users:
                try:
                    await self.bot.app.bot.send_message(
                        chat_id=user_id,
                        text=message,
                        parse_mode='Markdown'
                    )
                    logging.info(f"Startup notification successfully sent to {user_id}")
                except Exception as e:
                    logging.error(f"Failed to send to {user_id}: {str(e)}")
                    
        except Exception as e:
            logging.error(f"Unexpected error in startup notification: {str(e)}", exc_info=True)

    async def send_shutdown_notification(self):
        """Shutdown értesítés küldése minden engedélyezett felhasználónak"""
        try:
            self.logger.info("Sending shutdown notifications...")
            for user_id in self.bot.allowed_users:
                try:
                    await self.bot.app.bot.send_message(
                        chat_id=user_id,
                        text=self.bot.message_handler.get_message('shutdown_notification')
                    )
                    self.logger.debug(f"Shutdown notification sent to {user_id}")
                except Exception as e:
                    self.logger.error(f"Failed to send shutdown message to {user_id}: {str(e)}")
            return True
        except Exception as e:
            self.logger.error(f"Error sending shutdown messages: {str(e)}")
            return False

    async def start(self):
        """Elindítja az életjel figyelést"""
        self.is_active = True
        logger.info("Életjel szolgáltatás indítása")
        
        try:
            while self.is_active:
                try:
                    elapsed = time.time() - self.last_activity
                    if elapsed >= self.heartbeat_interval:
                        await self._send_heartbeat()
                        self.last_activity = time.time()
                except Exception as e:
                    logger.error(f"Életjel ellenőrzés hibája: {str(e)}", exc_info=True)
                
                await asyncio.sleep(60)  # Percenként ellenőrzés
        except asyncio.CancelledError:
            logger.info("Életjel leállítás kérésre")
        except Exception as e:
            logger.error(f"Életjel szolgáltatás hibája: {str(e)}", exc_info=True)
        finally:
            self.is_active = False
            logger.info("Életjel szolgáltatás leállt")

    async def _send_heartbeat(self):
        """Küld egy életjel üzenetet az engedélyezett felhasználóknak"""
        try:
            logger.info("Életjel üzenetek küldése")
            message = self.bot.message_handler.get_message('heartbeat').format(
                last_activity=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.last_activity)))
            
            for user_id in self.bot.allowed_users:
                try:
                    await self.bot.app.bot.send_message(
                        chat_id=user_id,
                        text=message
                    )
                    logger.debug(f"Életjel elküldve a felhasználónak: {user_id}")
                except Exception as e:
                    logger.error(f"Életjel küldés sikertelen a felhasználónak {user_id}: {str(e)}")
        except Exception as e:
            logger.error(f"Életjel küldési hiba: {str(e)}", exc_info=True)

    def update_activity(self):
        """Frissíti az utolsó tevékenység idejét"""
        self.last_activity = time.time()
        logger.debug(f"Tevékenység frissítve: {self.last_activity}")

    async def stop(self):
        """Szabályosan leállítja az életjel szolgáltatást"""
        self.is_running = False
        await self.send_shutdown_notification()
        self.logger.info("Heartbeat stopped")