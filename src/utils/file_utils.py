"""
File utility functions
"""

import os
import sys

def ensure_directory(directory_path):
    """Ensure a directory exists, create if it doesn't"""
    os.makedirs(directory_path, exist_ok=True)
    return directory_path

def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

