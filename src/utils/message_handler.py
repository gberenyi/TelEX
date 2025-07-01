"""
Message Handler - Üzenetek kezelése és lokalizációja
"""

import logging
import json
import os
from typing import Dict, Any
from utils.config_loader import get_config_path

class MessageHandler:
    def __init__(self, language: str = 'hu'):
        self.language = language
        self.messages = self._load_messages()
        logging.info(f"Loaded messages: {list(self.messages.keys())}")
        if not self.messages:
            logging.critical("Nincsenek üzenetek betöltve!")
        else:
            logging.info(f"Üzenetek betöltve ({len(self.messages)} db) nyelv: {language}")

    def _load_messages(self) -> Dict[str, str]:
        """Üzenetek betöltése a konfigurációs fájlból"""
        try:
            """
            config_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'config',
                'messages.json'
            )
            """
            config_path = os.path.join(get_config_path(), 'messages.json')
            logging.debug(f"Üzenetek betöltése innen: {config_path}")
            
            with open(config_path, 'r', encoding='utf-8') as f:
                messages = json.load(f)
                lang_messages = messages.get(self.language, {})
                
                # Ellenőrizzük a kötelező üzeneteket
                required_keys = ['startup_notification', 'heartbeat', 'welcome']
                for key in required_keys:
                    if key not in lang_messages:
                        logging.error(f"Hiányzó kötelező üzenet: {key}")
                
                return lang_messages
                
        except FileNotFoundError:
            logging.error("Az üzenetfájl nem található!")
            return {}
        except json.JSONDecodeError:
            logging.error("Érvénytelen JSON formátum!")
            return {}
        except Exception as e:
            logging.error(f"Váratlan hiba az üzenetek betöltésekor: {str(e)}")
            return {}

    def get_message(self, key: str, **kwargs) -> str:
        """Üzenet lekérése formázással"""
        if not self.messages:
            logging.warning("Nincsenek üzenetek betöltve!")
            return key
            
        message = self.messages.get(key, key)
        try:
            return message.format(**kwargs)
        except KeyError as e:
            logging.error(f"Hiányzó paraméter az üzenetben ({key}): {str(e)}")
            return f"{message} [Hiányzó: {str(e)}]"
        except Exception as e:
            logging.error(f"Hiba az üzenet formázásakor ({key}): {str(e)}")
            return message