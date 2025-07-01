"""
Fő belépési pont az alkalmazás számára
"""

import asyncio
import logging
from telegram_bot import TelegramBot
from utils.config_loader import load_config

# Alap logging konfiguráció
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('bot.log')
    ]
)

async def main():
    """Fő aszinkron függvény a bot indításához"""
    try:
        logging.info("Konfiguráció betöltése...")
        config = load_config()
        
        logging.info("Bot példányosítása...")
        bot = TelegramBot(config)
        
        logging.info("Bot indítása...")
        await bot.run()
        
    except Exception as e:
        logging.critical(f"Váratlan hiba: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Bot leállítás a felhasználó kérésére")
    except Exception as e:
        logging.error(f"Futás közbeni hiba: {str(e)}", exc_info=True)