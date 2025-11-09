"""
Crono Ders Takip Sistemi
TEAM AURORA
Developer: Chaster

Main application entry point
"""

import sys
import os
import tkinter as tk
import tkinter.messagebox as messagebox

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.ui.main_window import MainWindow
from src.config.settings import AppSettings
from src.utils.data_manager import DataManager
from src.utils.language import LanguageManager
from src.utils.time_tracker import TimeTracker
from src.utils.notes_manager import NotesManager
from src.utils.goal_tracker import GoalTracker
from src.utils.analytics import Analytics
from src.utils.export_manager import ExportManager
from src.utils.quote_manager import QuoteManager

def main():
    """Main application entry point"""
    try:
        # Initialize settings
        settings = AppSettings()
        
        # Initialize language manager
        lang_manager = LanguageManager(settings.get_language())
        
        # Initialize data manager
        data_manager = DataManager()
        
        # Initialize time tracker
        time_tracker = TimeTracker()
        
        # Initialize notes manager
        notes_manager = NotesManager()
        
        # Initialize goal tracker
        goal_tracker = GoalTracker()
        
        # Initialize analytics
        analytics = Analytics(data_manager, time_tracker, goal_tracker)
        
        # Initialize export manager
        export_manager = ExportManager(data_manager, time_tracker, notes_manager, goal_tracker)
        
        # Initialize quote manager
        quote_manager = QuoteManager()
        
        # Create and run application
        app = MainWindow(settings, lang_manager, data_manager, time_tracker, notes_manager, goal_tracker, analytics, export_manager, quote_manager)
        app.mainloop()
        
    except Exception as e:
        # Show error dialog
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Critical Error",
            f"An error occurred while starting the application:\n{str(e)}\n\n"
            "Please check the data file or delete it and restart."
        )
        print(f"Critical error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

