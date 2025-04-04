"""
Configuration manager for KitelyView.
Handles user preferences, grid settings, and application configuration.
"""

import os
import json
import logging
import platform
import appdirs

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
        self.logger = logging.getLogger("kitelyview")
        self.app_name = "KitelyView"
        self.config_file = "config.json"
        
        # Set platform-specific paths
        self.config_dir = self._get_config_dir()
        self.DEFAULT_CONFIG["paths"]["cache_dir"] = self._get_cache_dir()
        self.DEFAULT_CONFIG["paths"]["log_dir"] = self._get_log_dir()
        
        # Load configuration
        self.config = self._load_config()
        
    def _get_config_dir(self):
        """Get platform-specific configuration directory"""
        try:
            config_dir = appdirs.user_config_dir(self.app_name)
        except ImportError:
            # Fallback if appdirs is not available
            if platform.system() == "Windows":
                config_dir = os.path.join(os.environ.get("APPDATA", ""), self.app_name)
            elif platform.system() == "Darwin":  # macOS
                config_dir = os.path.expanduser(f"~/Library/Preferences/{self.app_name}")
            else:  # Linux/Unix
                config_dir = os.path.expanduser(f"~/.config/{self.app_name}")
        
        # For Replit environment, use local config
        if os.environ.get("REPL_ID"):
            config_dir = ".config"
            
        os.makedirs(config_dir, exist_ok=True)
        return config_dir
    
    def _get_cache_dir(self):
        """Get platform-specific cache directory"""
        try:
            cache_dir = appdirs.user_cache_dir(self.app_name)
        except ImportError:
            # Fallback if appdirs is not available
            if platform.system() == "Windows":
                cache_dir = os.path.join(os.environ.get("LOCALAPPDATA", ""), self.app_name, "Cache")
            elif platform.system() == "Darwin":  # macOS
                cache_dir = os.path.expanduser(f"~/Library/Caches/{self.app_name}")
            else:  # Linux/Unix
                cache_dir = os.path.expanduser(f"~/.cache/{self.app_name}")
        
        # For Replit environment, use local cache
        if os.environ.get("REPL_ID"):
            cache_dir = ".cache"
            
        os.makedirs(cache_dir, exist_ok=True)
        return cache_dir
    
    def _get_log_dir(self):
        """Get platform-specific log directory"""
        try:
            log_dir = appdirs.user_log_dir(self.app_name)
        except ImportError:
            # Fallback if appdirs is not available
            if platform.system() == "Windows":
                log_dir = os.path.join(os.environ.get("LOCALAPPDATA", ""), self.app_name, "Logs")
            elif platform.system() == "Darwin":  # macOS
                log_dir = os.path.expanduser(f"~/Library/Logs/{self.app_name}")
            else:  # Linux/Unix
                log_dir = os.path.expanduser(f"~/.local/share/{self.app_name}/logs")
        
        # For Replit environment, use local logs
        if os.environ.get("REPL_ID"):
            log_dir = "logs"
            
        os.makedirs(log_dir, exist_ok=True)
        return log_dir
    
    def _load_config(self):
        """Load configuration from file or create default"""
        config_path = os.path.join(self.config_dir, self.config_file)
        
        # Check if config file exists
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    loaded_config = json.load(f)
                
                # Merge with default config to ensure all keys exist
                merged_config = self._merge_configs(self.DEFAULT_CONFIG, loaded_config)
                self.logger.info("Configuration loaded from file")
                return merged_config
            
            except (json.JSONDecodeError, IOError) as e:
                self.logger.error(f"Error loading configuration: {e}")
                self.logger.info("Using default configuration")
                return self.DEFAULT_CONFIG.copy()
        else:
            # Create default config file
            try:
                os.makedirs(os.path.dirname(config_path), exist_ok=True)
                with open(config_path, 'w') as f:
                    json.dump(self.DEFAULT_CONFIG, f, indent=4)
                self.logger.info("Default configuration created")
            except IOError as e:
                self.logger.error(f"Error creating default configuration file: {e}")
            
            return self.DEFAULT_CONFIG.copy()
    
    def _merge_configs(self, base_config, new_config):
        """Recursively merge configuration dictionaries"""
        merged = base_config.copy()
        
        for key, value in new_config.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = self._merge_configs(merged[key], value)
            else:
                merged[key] = value
                
        return merged
    
    def get(self, section, key=None):
        """Get a configuration value"""
        if section not in self.config:
            return None
        
        if key is None:
            return self.config[section]
        
        if key not in self.config[section]:
            return None
            
        return self.config[section][key]
    
    def set(self, section, key, value):
        """Set a configuration value"""
        if section not in self.config:
            self.config[section] = {}
            
        self.config[section][key] = value
        self.save_config()
        
    def save_config(self, config=None):
        """Save configuration to file"""
        if config is None:
            config = self.config
            
        config_path = os.path.join(self.config_dir, self.config_file)
        
        try:
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=4)
            self.logger.info("Configuration saved to file")
            return True
        except IOError as e:
            self.logger.error(f"Error saving configuration: {e}")
            return False