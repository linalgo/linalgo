"""Configuration management for linalgo."""
import os
import json
from pathlib import Path
from typing import Dict, Any, Optional

CONFIG_DIR = Path.home() / ".linalgo"
CONFIG_FILE = CONFIG_DIR / "config.json"

def ensure_config_dir():
    """Ensure the config directory exists."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

def load_config() -> Dict[str, Any]:
    """Load configuration from the config file."""
    ensure_config_dir()
    if not CONFIG_FILE.exists():
        return {}
    
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

def save_config(config: Dict[str, Any]):
    """Save configuration to the config file."""
    ensure_config_dir()
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

def get_config(key: str, default: Any = None) -> Any:
    """Get a configuration value."""
    config = load_config()
    return config.get(key, default)

def set_config(key: str, value: Any):
    """Set a configuration value."""
    config = load_config()
    config[key] = value
    save_config(config)