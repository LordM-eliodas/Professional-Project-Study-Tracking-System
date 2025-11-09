"""
Application Settings Manager
"""

import json
import os
from .constants import get_config_file, UI_SETTINGS, BASE_DIR

class AppSettings:
    """Manages application settings"""
    
    def __init__(self):
        # Always get fresh path in case we're running from EXE
        self.settings_file = get_config_file()
        self.default_settings = {
            "language": "tr",  # tr, en
            "theme": "Light",  # Dark, Light (System removed - same as Light)
            "window_width": UI_SETTINGS["window_width"],
            "window_height": UI_SETTINGS["window_height"],
            "auto_save": True,
            "show_notifications": True,
        }
        self.settings = self.load_settings()
    
    def load_settings(self):
        """Load settings from file"""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    settings = self.default_settings.copy()
                    settings.update(loaded)
                    return settings
            except Exception as e:
                print(f"Settings load error: {e}")
                return self.default_settings.copy()
        return self.default_settings.copy()
    
    def save_settings(self):
        """Save settings to file"""
        try:
            os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Settings save error: {e}")
            return False
    
    def get(self, key, default=None):
        """Get a setting value"""
        return self.settings.get(key, default)
    
    def set(self, key, value):
        """Set a setting value"""
        self.settings[key] = value
        self.save_settings()
    
    def get_language(self):
        """Get current language"""
        return self.settings.get("language", "tr")
    
    def set_language(self, lang):
        """Set language"""
        self.set("language", lang)
    
    def get_theme(self):
        """Get current theme"""
        return self.settings.get("theme", "System")
    
    def set_theme(self, theme):
        """Set theme"""
        self.set("theme", theme)

