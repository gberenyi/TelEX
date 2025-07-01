"""
Logolás kezelése - konzol és fájlba írással
"""
import logging
import logging.handlers
import os
from pathlib import Path
from typing import Dict, Any

def setup_logging(config: Dict[str, Any]):
    """Logolás inicializálása a konfigurációnak megfelelően"""
    log_config = config.get('logging', {})
    log_level = getattr(logging, log_config.get('level', 'INFO'))
    
    # Fő logger létrehozása
    logger = logging.getLogger()
    logger.setLevel(log_level)
    
    # Formátum létrehozása
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Konzol logolás
    if log_config.get('console_log', True):
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # Fájl logolás
    if log_config.get('file_log', False):
        log_path = log_config.get('file_path', 'logs/bot.log')
        Path(os.path.dirname(log_path)).mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.handlers.RotatingFileHandler(
            filename=log_path,
            maxBytes=log_config.get('max_bytes', 1048576),  # 1MB
            backupCount=log_config.get('backup_count', 5)
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger