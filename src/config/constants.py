"""
Application Constants
"""

import os

# =================================================================
# Application Information
# =================================================================
APP_INFO = {
    "name": "Crono Ders Takip Sistemi",
    "team": "TEAM AURORA",
    "developer": "Chaster",
    "version": "1.0.0",
    "description": "Professional Project & Study Tracking System",
}

# =================================================================
# Color Definitions
# =================================================================
COLORS = {
    # Modern Primary Colors - Refined
    "JAPAN_BLUE": "#1e3a5f",      # Deeper, richer blue
    "SAKURA_PINK": "#e63946",     # Softer, modern red
    "BUTTON_COLOR": "#2d3748",    # Modern dark gray-blue
    "HOVER_COLOR": "#06b6d4",     # Modern cyan (Primary Action)
    "TEXT_COLOR": "#f1f5f9",      # Softer light gray
    "TEXT_SECONDARY": "#94a3b8",  # Modern medium gray
    
    # Status Colors - Enhanced
    "SUCCESS": "#10b981",         # Modern emerald green
    "WARNING": "#f59e0b",         # Modern amber
    "ERROR": "#ef4444",           # Modern red
    "INFO": "#3b82f6",            # Modern blue
    
    # Modern Accent Colors - RGB Theme Based
    # Dark Mode: Black, Blue, Red, Purple
    "PRIMARY": "#6366f1",         # Indigo (Dark: Blue-Purple, Light: Pink)
    "PRIMARY_DARK": "#4f46e5",    # Darker Indigo (Dark: Deep Blue, Light: Deep Pink)
    "PRIMARY_LIGHT": "#818cf8",   # Lighter Indigo (Dark: Light Blue, Light: Light Pink)
    "SECONDARY": "#8b5cf6",       # Purple (Dark: Purple, Light: Rose Pink)
    "ACCENT": "#ec4899",          # Pink (Dark: Red-Pink, Light: Bright Pink)
    "ACCENT_2": "#06b6d4",        # Cyan (Dark: Blue, Light: Soft Pink)
    
    # Gradient Colors - Theme Based
    "GRADIENT_1_START": "#6366f1", # Indigo (Dark: Blue, Light: Pink)
    "GRADIENT_1_END": "#8b5cf6",   # Purple (Dark: Purple, Light: Rose)
    "GRADIENT_2_START": "#ec4899", # Pink (Dark: Red, Light: Pink)
    "GRADIENT_2_END": "#f43f5e",   # Rose (Dark: Dark Red, Light: Light Pink)
    "GRADIENT_3_START": "#06b6d4", # Cyan (Dark: Blue, Light: Soft Pink)
    "GRADIENT_3_END": "#3b82f6",   # Blue (Dark: Blue, Light: Pink)
    
    # Background Colors - Theme Based
    "BG_LIGHT": "#ffffff",        # Pure white for light mode
    "BG_DARK": "#000000",          # Pure black for dark mode (RGB black)
    "CARD_LIGHT": "#fef2f2",       # Soft pink-white for light mode
    "CARD_DARK": "#0a0a0f",        # Very dark blue-black for dark mode
    "BORDER_LIGHT": "#fce7f3",     # Light pink border for light mode
    "BORDER_DARK": "#1a1a2e",      # Dark blue-black border for dark mode
    
    # Additional Modern Colors
    "SURFACE_LIGHT": "#f1f5f9",   # Surface color light
    "SURFACE_DARK": "#1e293b",    # Surface color dark
    "OVERLAY_LIGHT": "#ffffff",   # Overlay light
    "OVERLAY_DARK": "#334155",    # Overlay dark
}

# =================================================================
# File Paths
# =================================================================
import sys

def get_base_path():
    """Get base path, works for both development and PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            base_path = sys._MEIPASS
        else:
            # Running as script
            base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    except Exception:
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return base_path

def get_data_path():
    """Get data directory path, works for both development and PyInstaller"""
    try:
        if getattr(sys, 'frozen', False):
            # In PyInstaller, data is extracted to temp folder
            return os.path.join(sys._MEIPASS, "data")
        else:
            # In development, use project data folder
            return os.path.join(get_base_path(), "data")
    except Exception:
        return os.path.join(get_base_path(), "data")

def get_locales_path():
    """Get locales directory path, works for both development and PyInstaller"""
    try:
        if getattr(sys, 'frozen', False):
            # In PyInstaller, locales is extracted to temp folder
            return os.path.join(sys._MEIPASS, "locales")
        else:
            # In development, use project locales folder
            return os.path.join(get_base_path(), "locales")
    except Exception:
        return os.path.join(get_base_path(), "locales")

BASE_DIR = get_base_path()
DATA_DIR = get_data_path()
LOCALES_DIR = get_locales_path()
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
ICONS_DIR = os.path.join(ASSETS_DIR, "icons")
ICON_FILE = os.path.join(BASE_DIR, "pngegg.png")

# Ensure directories exist (only in development, not in PyInstaller)
if not getattr(sys, 'frozen', False):
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(LOCALES_DIR, exist_ok=True)
    os.makedirs(ASSETS_DIR, exist_ok=True)
    os.makedirs(ICONS_DIR, exist_ok=True)

# For data files, use actual data directory (not temp folder in PyInstaller)
# In PyInstaller, data should be saved to user's app data directory
def get_user_data_dir():
    """Get user data directory for saving files - dynamically calculated"""
    if getattr(sys, 'frozen', False):
        # In PyInstaller, save to user's AppData directory (like other installed programs)
        # This prevents creating data folder next to executable
        try:
            # Get AppData\Roaming directory (standard location for user data)
            if sys.platform == 'win32':
                appdata = os.getenv('APPDATA')
                if appdata:
                    # Create app-specific folder in AppData
                    user_data = os.path.join(appdata, 'CronoDersTakip', 'data')
                else:
                    # Fallback to user home directory
                    user_data = os.path.join(os.path.expanduser('~'), 'AppData', 'Roaming', 'CronoDersTakip', 'data')
            else:
                # Linux/Mac: use XDG config directory or home directory
                user_data = os.path.join(os.path.expanduser('~'), '.crono_ders_takip', 'data')
        except Exception as e:
            print(f"Warning: Could not get AppData directory: {e}")
            # Fallback to temp directory
            import tempfile
            user_data = os.path.join(tempfile.gettempdir(), "crono_ders_takip", "data")
    else:
        # Development: use project data folder
        user_data = os.path.join(get_base_path(), "data")
    
    # Always ensure directory exists
    try:
        os.makedirs(user_data, exist_ok=True)
    except Exception as e:
        print(f"Warning: Could not create data directory: {e}")
        # Fallback to temp directory if main directory fails
        import tempfile
        user_data = os.path.join(tempfile.gettempdir(), "crono_ders_takip", "data")
        os.makedirs(user_data, exist_ok=True)
    
    return user_data

# Functions to get paths dynamically (not constants, recalculated each time)
def get_data_dir():
    """Get data directory - recalculated each time for EXE compatibility"""
    return get_user_data_dir()

def get_data_file():
    """Get data file path - recalculated each time"""
    return os.path.join(get_data_dir(), "study_data.json")

def get_config_file():
    """Get config file path - recalculated each time"""
    return os.path.join(get_data_dir(), "app_config.json")

# For backward compatibility, provide DATA_DIR as a property-like access
# But modules should use get_data_dir() function instead
DATA_DIR = get_user_data_dir()  # Initial value, but will be recalculated
DATA_FILE = get_data_file()  # Initial value
CONFIG_FILE = get_config_file()  # Initial value

# =================================================================
# Default Settings
# =================================================================
DEFAULT_SUBJECTS = {
    "Biyoloji": {"cozulen_soru": 0, "hedef_soru": 300, "son_calisma_tarihi": "", "konular": []},
    "Matematik": {"cozulen_soru": 0, "hedef_soru": 700, "son_calisma_tarihi": "", "konular": []},
    "Fizik": {"cozulen_soru": 0, "hedef_soru": 400, "son_calisma_tarihi": "", "konular": []},
    "Kimya": {"cozulen_soru": 0, "hedef_soru": 400, "son_calisma_tarihi": "", "konular": []},
    "Japonca": {"cozulen_soru": 0, "hedef_soru": 1000, "son_calisma_tarihi": "", "konular": []},
}

# =================================================================
# UI Settings
# =================================================================
UI_SETTINGS = {
    "window_width": 950,
    "window_height": 700,
    "min_width": 850,
    "min_height": 650,
    "sidebar_width": 220,
    "theme": "System",  # System, Dark, Light
}

# =================================================================
# Graph Settings
# =================================================================
GRAPH_SETTINGS = {
    "figure_dpi": 100,  # Higher DPI for better quality
    "general_figure_size": (6, 4),  # Larger for better visibility
    "subject_figure_size": (8, 5),  # Larger for better visibility
    "font_family": "DejaVu Sans",
    "enable_animations": False,  # Disable animations for better performance
}

# =================================================================
# Performance Settings
# =================================================================
PERFORMANCE_SETTINGS = {
    "lazy_load_charts": True,  # Load charts only when needed
    "cache_charts": True,  # Cache chart data
    "max_chart_cache_size": 10,  # Maximum cached charts
    "debounce_search_ms": 300,  # Search debounce time in milliseconds
    "enable_chart_animations": False,  # Disable chart animations for better performance
    "chart_dpi": 80,  # Lower DPI for faster rendering
    "max_subjects_display": 50,  # Maximum subjects to display at once
}
