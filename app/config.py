"""
Configuration manager for KitelyView.
Handles user preferences, grid settings, and application configuration.
"""

import os
import json
import logging
from pathlib import Path

class Config:
    """Configuration manager class"""
    
    DEFAULT_CONFIG = {
        "grid": {
            "name": "Kitely",
            "login_uri": "https://grid.kitely.com:8002",
            "login_page": "https://www.kitely.com/virtual-world-login",
        },
        "viewer": {
            "resolution": [1024, 768],
            "fullscreen": False,
            "render_distance": 128,
            "ui_scale": 1.0,
            "cache_size_mb": 1024,
        },
        "network": {
            "timeout": 30,
            "connection_retry": 3,
        },
        "paths": {
            "cache_dir": None,  # Will be set based on platform
            "log_dir": None,    # Will be set based on platform
        }
    }
    
    def __init__(self):
        """Initialize configuration"""
        self.logger = logging.getLogger("kitelyview.config")
        self.config_dir = self._get_config_dir()
        self.config_file = self.config_dir / "config.json"
        self.config = self._load_config()
        
    def _get_config_dir(self):
        """Get platform-specific configuration directory"""
        if os.name == "nt":  # Windows
            config_dir = Path(os.environ.get("APPDATA")) / "KitelyView"
        else:  # Linux (Fedora, Ubuntu)
            config_dir = Path(os.environ.get("HOME")) / ".config" / "kitelyview"
            
        # Create the directory if it doesn't exist
        if not config_dir.exists():
            config_dir.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"Created config directory: {config_dir}")
            
        return config_dir
        
    def _get_cache_dir(self):
        """Get platform-specific cache directory"""
        if os.name == "nt":  # Windows
            cache_dir = Path(os.environ.get("LOCALAPPDATA")) / "KitelyView" / "Cache"
        else:  # Linux (Fedora, Ubuntu)
            cache_dir = Path(os.environ.get("HOME")) / ".cache" / "kitelyview"
            
        # Create the directory if it doesn't exist
        if not cache_dir.exists():
            cache_dir.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"Created cache directory: {cache_dir}")
            
        return cache_dir
        
    def _get_log_dir(self):
        """Get platform-specific log directory"""
        if os.name == "nt":  # Windows
            log_dir = Path(os.environ.get("LOCALAPPDATA")) / "KitelyView" / "Logs"
        else:  # Linux (Fedora, Ubuntu)
            log_dir = Path(os.environ.get("HOME")) / ".local" / "share" / "kitelyview" / "logs"
            
        # Create the directory if it doesn't exist
        if not log_dir.exists():
            log_dir.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"Created log directory: {log_dir}")
            
        return log_dir
        
    def _load_config(self):
        """Load configuration from file or create default"""
        config = self.DEFAULT_CONFIG.copy()
        
        # Set platform-specific paths
        config["paths"]["cache_dir"] = str(self._get_cache_dir())
        config["paths"]["log_dir"] = str(self._get_log_dir())
        
        # Try to load from file
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    
                # Merge loaded config with default
                self._merge_configs(config, loaded_config)
                self.logger.info(f"Loaded configuration from {self.config_file}")
            except Exception as e:
                self.logger.error(f"Error loading config file: {e}")
        else:
            # Create default config file
            self.save_config(config)
            self.logger.info(f"Created default configuration file at {self.config_file}")
            
        return config
        
    def _merge_configs(self, base_config, new_config):
        """Recursively merge configuration dictionaries"""
        for key, value in new_config.items():
            if key in base_config:
                if isinstance(value, dict) and isinstance(base_config[key], dict):
                    self._merge_configs(base_config[key], value)
                else:
                    base_config[key] = value
            else:
                base_config[key] = value
                
    def get(self, section, key=None):
        """Get a configuration value"""
        if section in self.config:
            if key is None:
                return self.config[section]
            elif key in self.config[section]:
                return self.config[section][key]
        return None
        
    def set(self, section, key, value):
        """Set a configuration value"""
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
        
    def save_config(self, config=None):
        """Save configuration to file"""
        if config is None:
            config = self.config
            
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=4)
            self.logger.info(f"Saved configuration to {self.config_file}")
            return True
        except Exception as e:
            self.logger.error(f"Error saving config file: {e}")
            return False
