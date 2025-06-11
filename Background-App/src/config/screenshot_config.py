import os
import sys
from typing import List, Optional, Dict, Any

class ScreenshotConfig:
    """Configuration class for screenshot capture settings."""
    
    def __init__(self, config_dict: Optional[Dict[str, Any]] = None):
        """Initialize screenshot configuration."""
        # Default values
        self.interval = 300  # 5 minutes
        self.quality = 80
        self.compression_quality = 60
        self.max_width = 1920
        self.max_height = 1080
        self.max_size_mb = 10
        self.max_storage_gb = 5
        self.retention_days = 30
        self.enabled = True
        self.capture_active_only = True
        self.blur_sensitive = False
        self.exclude_minimized = True
        self.excluded_apps = [
            'password manager',
            'bitwarden',
            '1password',
            'lastpass',
            'keychain',
            'private',
            'incognito',
            'banking'
        ]
        self.excluded_windows = [
            'login',
            'password',
            'sign in',
            'authentication',
            'two-factor',
            '2fa'
        ]
        
        # Override with provided config
        if config_dict:
            self.update_from_dict(config_dict)
    
    def update_from_dict(self, config_dict: Dict[str, Any]):
        """Update configuration from dictionary."""
        for key, value in config_dict.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'interval': self.interval,
            'quality': self.quality,
            'compression_quality': self.compression_quality,
            'max_width': self.max_width,
            'max_height': self.max_height,
            'max_size_mb': self.max_size_mb,
            'max_storage_gb': self.max_storage_gb,
            'retention_days': self.retention_days,
            'enabled': self.enabled,
            'capture_active_only': self.capture_active_only,
            'blur_sensitive': self.blur_sensitive,
            'exclude_minimized': self.exclude_minimized,
            'excluded_apps': self.excluded_apps,
            'excluded_windows': self.excluded_windows
        }
    
    def validate(self) -> List[str]:
        """Validate configuration and return list of errors."""
        errors = []
        
        if self.interval < 60:
            errors.append("Screenshot interval must be at least 60 seconds")
        if not 0 <= self.quality <= 100:
            errors.append("Quality must be between 0 and 100")
        if self.max_size_mb < 1:
            errors.append("Maximum size must be at least 1MB")
        if self.max_storage_gb < 1:
            errors.append("Maximum storage must be at least 1GB")
        if self.retention_days < 1:
            errors.append("Retention period must be at least 1 day")
            
        return errors
    
    def is_app_excluded(self, app_name: str) -> bool:
        """Check if an app should be excluded from capture."""
        app_name_lower = app_name.lower()
        return any(excluded.lower() in app_name_lower 
                  for excluded in self.excluded_apps)

    def is_window_excluded(self, window_title: str) -> bool:
        """Check if a window should be excluded from capture."""
        window_title_lower = window_title.lower()
        return any(excluded.lower() in window_title_lower
                  for excluded in self.excluded_windows)