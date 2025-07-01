"""
Config Loader - Handles configuration files with proper path resolution
Provides access to all configuration data from the correct project root
"""

import os
import json
from typing import Dict, Any

def get_project_root() -> str:
    """Returns the absolute path to the project root directory"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.abspath(os.path.join(current_dir, '..', '..'))

def get_config_path() -> str:
    """Returns the absolute path to the config directory"""
    return os.path.join(get_project_root(), 'config')

def load_config() -> Dict[str, Any]:
    """Loads main configuration file from config/ directory"""
    config_path = os.path.join(get_config_path(), 'config.json')
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found at {config_path}")
    
    with open(config_path, 'r') as f:
        return json.load(f)

def load_exchange_configs() -> Dict[str, Any]:
    """Loads exchange configurations from config/ directory"""
    config_path = os.path.join(get_config_path(), 'exchange_configs.json')
    if not os.path.exists(config_path):
        return {}
    
    with open(config_path, 'r') as f:
        return json.load(f)

def load_messages(language: str = 'hu') -> Dict[str, str]:
    """Loads language-specific messages from config/ directory"""
    config_path = os.path.join(get_config_path(), 'messages.json')
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Messages file not found at {config_path}")
    
    with open(config_path, 'r') as f:
        messages = json.load(f)
        return messages.get(language, messages['hu'])

def save_exchange_configs(configs: Dict[str, Any]) -> None:
    """Saves exchange configurations to config/ directory"""
    config_path = os.path.join(get_config_path(), 'exchange_configs.json')
    with open(config_path, 'w') as f:
        json.dump(configs, f, indent=2)