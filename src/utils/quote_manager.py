"""
Quote Manager Module
Manages inspirational quotes from sözler.json
"""

import json
import os
import random
import sys
from ..config.constants import BASE_DIR

class QuoteManager:
    """Manages inspirational quotes"""
    
    def __init__(self):
        # Get quotes file path - works for both development and PyInstaller
        if getattr(sys, 'frozen', False):
            # In PyInstaller, file is in the same directory as executable
            exe_dir = os.path.dirname(sys.executable)
            self.quotes_file = os.path.join(exe_dir, "sözler.json")
            # If not found, try in _MEIPASS (temp folder)
            if not os.path.exists(self.quotes_file):
                self.quotes_file = os.path.join(sys._MEIPASS, "sözler.json")
        else:
            # In development, use project root
            self.quotes_file = os.path.join(BASE_DIR, "sözler.json")
        
        self.quotes = self.load_quotes()
        self.current_index = 0
    
    def load_quotes(self):
        """Load quotes from JSON file"""
        if os.path.exists(self.quotes_file):
            try:
                with open(self.quotes_file, 'r', encoding='utf-8') as f:
                    quotes = json.load(f)
                    if isinstance(quotes, list) and len(quotes) > 0:
                        return quotes
            except Exception as e:
                print(f"Quote load error: {e}")
        
        # Default fallback quotes
        return [
            "Başarı, küçük çabaların tekrarıdır.",
            "Her gün yeni bir başlangıçtır.",
            "Hayallerinizi takip edin."
        ]
    
    def get_random_quote(self):
        """Get a random quote"""
        if not self.quotes:
            return "Başarı, küçük çabaların tekrarıdır."
        return random.choice(self.quotes)
    
    def get_next_quote(self):
        """Get next quote in sequence"""
        if not self.quotes:
            return "Başarı, küçük çabaların tekrarıdır."
        
        self.current_index = (self.current_index + 1) % len(self.quotes)
        return self.quotes[self.current_index]
    
    def get_current_quote(self):
        """Get current quote"""
        if not self.quotes:
            return "Başarı, küçük çabaların tekrarıdır."
        return self.quotes[self.current_index]

