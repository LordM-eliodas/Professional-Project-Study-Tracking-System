"""
Main Application Window
"""

import customtkinter as ctk
import tkinter.messagebox as messagebox
from tkinter import filedialog
from functools import partial
import os
import datetime
from PIL import Image, ImageTk

from ..config.constants import COLORS, UI_SETTINGS, APP_INFO, ICON_FILE, PERFORMANCE_SETTINGS
from ..config.settings import AppSettings
from ..utils.data_manager import DataManager
from ..utils.language import LanguageManager
from ..graphics.chart_manager import ChartManager

class MainWindow(ctk.CTk):
    """Main application window"""
    
    def __init__(self, settings: AppSettings, lang_manager: LanguageManager, data_manager: DataManager,
                 time_tracker, notes_manager, goal_tracker, analytics, export_manager, quote_manager):
        super().__init__()
        
        self.settings = settings
        self.lang = lang_manager
        self.data_manager = data_manager
        self.time_tracker = time_tracker
        self.notes_manager = notes_manager
        self.goal_tracker = goal_tracker
        self.analytics = analytics
        self.export_manager = export_manager
        self.quote_manager = quote_manager
        self.chart_manager = ChartManager(lang_manager)
        
        # UI State
        self.selected_subject = None
        self.subject_buttons = {}
        self.subjects_scroll = None  # Will be created in _create_sidebar
        self.progress_bar = None
        self.target_input = None
        self.topic_list_frame = None
        self.current_view = "dashboard"  # dashboard, subject, statistics, analytics
        self.active_session_id = None
        
        # Performance optimizations
        self._dashboard_widget = None  # Cache dashboard widget
        self._last_stats_hash = None  # Track stats changes
        self._update_pending = False  # Prevent multiple simultaneous updates
        
        # Setup window
        self._setup_window()
        self._create_ui()
        
        # Apply theme
        theme = self.settings.get_theme()
        ctk.set_appearance_mode(theme)
        
        # Bind key press events for quote changing - comprehensive approach
        # Use both window-level and application-level bindings
        self.bind("<Key>", self._on_key_press)
        self.bind("<KeyPress>", self._on_key_press)
        self.bind_all("<Key>", self._on_key_press)
        self.bind_all("<KeyPress>", self._on_key_press)
        
        # Make window focusable and keep it focusable
        self.focus_set()
        self.focus_force()
        
        # Bind focus events to ensure window stays focusable
        self.bind("<FocusIn>", self._on_focus_in)
        self.bind("<Button-1>", self._on_window_click)
        self.bind_all("<Button-1>", self._on_any_click)
        
        # Set window to accept keyboard input
        self.configure(takefocus=True)
        
        # Show dashboard by default
        self._show_dashboard()
    
    def _update_subject_buttons(self):
        """Update subject buttons in sidebar with filtering and performance optimization"""
        if self.subjects_scroll is None:
            return  # Sidebar not created yet
        
        if self._update_pending:
            return  # Skip if update is already pending
        
        self._update_pending = True
        
        # Clear existing buttons (optimized)
        widgets_to_destroy = list(self.subjects_scroll.winfo_children())
        for widget in widgets_to_destroy:
            widget.destroy()
        self.subject_buttons.clear()
        
        # Get all subjects (with performance limit)
        all_subjects = list(self.data_manager.data.keys())
        max_display = PERFORMANCE_SETTINGS.get("max_subjects_display", 50)
        if len(all_subjects) > max_display:
            all_subjects = all_subjects[:max_display]
        
        # Apply filters
        filtered_subjects = self._apply_filters(all_subjects) if hasattr(self, 'current_filter') else all_subjects
        
        if not filtered_subjects:
            no_subjects_label = ctk.CTkLabel(
                self.subjects_scroll,
                text=self.lang.get("subject.select", "Select a subject/project"),
                font=ctk.CTkFont(size=12),
                text_color=(COLORS.get("TEXT_SECONDARY", "#95a5a6"), "#b0b0b0")
            )
            no_subjects_label.grid(row=0, column=0, padx=10, pady=20)
            return
        
        # Create subject buttons
        for i, subject_name in enumerate(filtered_subjects):
            subject_data = self.data_manager.data.get(subject_name, {})
            priority = subject_data.get('priority', 'medium')
            status = subject_data.get('status', 'active')
            
            # Subject button frame
            subject_frame = ctk.CTkFrame(self.subjects_scroll, fg_color="transparent")
            subject_frame.grid(row=i, column=0, padx=5, pady=5, sticky="ew")
            subject_frame.grid_columnconfigure(0, weight=1)
            
            # Priority indicator color
            priority_colors = {
                "high": COLORS["ERROR"],
                "medium": COLORS["WARNING"],
                "low": COLORS["SUCCESS"]
            }
            priority_color = priority_colors.get(priority, COLORS["INFO"])
            
            # Status indicator
            status_indicators = {
                "active": "●",
                "completed": "✓",
                "on_hold": "⏸",
                "archived": "📦"
            }
            status_indicator = status_indicators.get(status, "●")
            
            # Modern subject button with priority indicator
            btn_text = f"{status_indicator} {subject_name}"
            btn = ctk.CTkButton(
                subject_frame,
                text=btn_text,
                height=50,
                corner_radius=12,
                fg_color=(COLORS.get("CARD_LIGHT", "#f8f9fa"), COLORS.get("CARD_DARK", "#2d2d2d")),
                hover_color=(COLORS["PRIMARY"], COLORS["PRIMARY_DARK"]),
                border_width=2,
                border_color=(priority_color, priority_color),
                command=partial(self._select_subject, subject_name),
                anchor="w",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=("gray20", "gray90")
            )
            btn.grid(row=0, column=0, sticky="ew", padx=(0, 8))
            self.subject_buttons[subject_name] = btn
            
            # Modern menu button
            menu_btn = ctk.CTkButton(
                subject_frame,
                text="⋮",
                width=38,
                height=52,
                fg_color=COLORS["SECONDARY"],
                hover_color="#7c3aed",
                command=partial(self._show_subject_menu, subject_name),
                font=ctk.CTkFont(size=18, weight="bold"),
                corner_radius=12
            )
            menu_btn.grid(row=0, column=1)
        
        # Reset update flag immediately after buttons are created
        self._update_pending = False
    
    def _show_subject_menu(self, subject_name):
        """Show context menu for subject"""
        menu_window = ctk.CTkToplevel(self)
        menu_window.title("")
        menu_window.geometry("200x120")
        menu_window.transient(self)
        menu_window.overrideredirect(True)
        
        # Position near mouse or button
        menu_window.geometry(f"+{self.winfo_x() + 250}+{self.winfo_y() + 200}")
        
        edit_btn = ctk.CTkButton(
            menu_window,
            text=self.lang.get("actions.edit", "Edit"),
            command=lambda: [menu_window.destroy(), self._show_edit_subject_dialog(subject_name)],
            width=180,
            fg_color=COLORS["HOVER_COLOR"]
        )
        edit_btn.pack(pady=5)
        
        delete_btn = ctk.CTkButton(
            menu_window,
            text=self.lang.get("actions.delete", "Delete"),
            command=lambda: [menu_window.destroy(), self._delete_subject(subject_name)],
            width=180,
            fg_color=COLORS["SAKURA_PINK"]
        )
        delete_btn.pack(pady=5)
        
        cancel_btn = ctk.CTkButton(
            menu_window,
            text=self.lang.get("actions.cancel", "Cancel"),
            command=menu_window.destroy,
            width=180
        )
        cancel_btn.pack(pady=5)
        
        menu_window.grab_set()
        
        def close_on_click_outside(event):
            if event.widget == menu_window:
                menu_window.destroy()
        
        menu_window.bind("<Button-1>", close_on_click_outside)
    
    def _show_add_subject_dialog(self):
        """Show add subject dialog"""
        dialog = ctk.CTkToplevel(self)
        dialog.title(self.lang.get("subject.add", "Add Subject"))
        dialog.geometry("400x200")
        dialog.transient(self)
        dialog.grab_set()
        
        ctk.CTkLabel(dialog, text=self.lang.get("subject.subject_name", "Subject Name"), 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10)
        
        name_entry = ctk.CTkEntry(dialog, width=300, placeholder_text=self.lang.get("subject.subject_name", "Subject Name"))
        name_entry.pack(pady=5)
        name_entry.focus()
        
        ctk.CTkLabel(dialog, text=self.lang.get("subject.initial_target", "Initial Target"), 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10)
        
        target_entry = ctk.CTkEntry(dialog, width=300, placeholder_text="500")
        target_entry.insert(0, "500")
        target_entry.pack(pady=5)
        
        def add_subject():
            name = name_entry.get().strip()
            try:
                target = int(target_entry.get() or "500")
                if target <= 0:
                    raise ValueError
                
                success, result = self.data_manager.add_subject(name, target)
                if success:
                    messagebox.showinfo(
                        self.lang.get("messages.success", "Success"),
                        self.lang.get("subject.subject_added", "Subject added successfully!")
                    )
                    dialog.destroy()
                    self._update_subject_buttons()
                    self._show_dashboard()
                else:
                    if result == "empty_name":
                        messagebox.showerror(
                            self.lang.get("messages.error", "Error"),
                            self.lang.get("subject.empty_subject_name", "Subject name cannot be empty!")
                        )
                    elif result == "exists":
                        messagebox.showerror(
                            self.lang.get("messages.error", "Error"),
                            self.lang.get("subject.subject_exists", "This subject already exists!")
                        )
            except ValueError:
                messagebox.showerror(
                    self.lang.get("messages.error", "Error"),
                    self.lang.get("messages.invalid_number", "Invalid number!")
                )
        
        name_entry.bind("<Return>", lambda e: add_subject())
        target_entry.bind("<Return>", lambda e: add_subject())
        
        ctk.CTkButton(dialog, text=self.lang.get("actions.add", "Add"), command=add_subject,
                     fg_color=COLORS["HOVER_COLOR"]).pack(pady=20)
        ctk.CTkButton(dialog, text=self.lang.get("actions.cancel", "Cancel"), command=dialog.destroy).pack(pady=5)
    
    def _show_edit_subject_dialog(self, subject_name):
        """Show edit subject dialog"""
        subject_data = self.data_manager.data.get(subject_name, {})
        current_target = subject_data.get('hedef_soru', 500)
        
        dialog = ctk.CTkToplevel(self)
        dialog.title(self.lang.get("subject.edit", "Edit Subject"))
        dialog.geometry("400x200")
        dialog.transient(self)
        dialog.grab_set()
        
        ctk.CTkLabel(dialog, text=self.lang.get("subject.subject_name", "Subject Name"), 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10)
        
        name_entry = ctk.CTkEntry(dialog, width=300)
        name_entry.insert(0, subject_name)
        name_entry.pack(pady=5)
        
        ctk.CTkLabel(dialog, text=self.lang.get("subject.target", "Target"), 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10)
        
        target_entry = ctk.CTkEntry(dialog, width=300)
        target_entry.insert(0, str(current_target))
        target_entry.pack(pady=5)
        
        def update_subject():
            new_name = name_entry.get().strip()
            try:
                new_target = int(target_entry.get() or str(current_target))
                if new_target <= 0:
                    raise ValueError
                
                if not new_name:
                    messagebox.showerror(
                        self.lang.get("messages.error", "Error"),
                        self.lang.get("subject.empty_subject_name", "Subject name cannot be empty!")
                    )
                    return
                
                success, result = self.data_manager.update_subject(subject_name, new_name, new_target)
                if success:
                    messagebox.showinfo(
                        self.lang.get("messages.success", "Success"),
                        self.lang.get("subject.subject_updated", "Subject updated successfully!")
                    )
                    dialog.destroy()
                    self._update_subject_buttons()
                    if self.selected_subject == subject_name:
                        self._select_subject(new_name)
                    else:
                        self._show_dashboard()
                else:
                    if result == "exists":
                        messagebox.showerror(
                            self.lang.get("messages.error", "Error"),
                            self.lang.get("subject.subject_exists", "This subject already exists!")
                        )
            except ValueError:
                messagebox.showerror(
                    self.lang.get("messages.error", "Error"),
                    self.lang.get("messages.invalid_number", "Invalid number!")
                )
        
        ctk.CTkButton(dialog, text=self.lang.get("actions.save", "Save"), command=update_subject,
                     fg_color=COLORS["HOVER_COLOR"]).pack(pady=20)
        ctk.CTkButton(dialog, text=self.lang.get("actions.cancel", "Cancel"), command=dialog.destroy).pack(pady=5)
    
    def _delete_subject(self, subject_name):
        """Delete a subject"""
        result = messagebox.askyesno(
            self.lang.get("subject.delete", "Delete Subject"),
            self.lang.get("subject.confirm_delete_subject", "Are you sure you want to delete this subject? All data will be deleted!")
        )
        if result:
            if self.data_manager.delete_subject(subject_name):
                messagebox.showinfo(
                    self.lang.get("messages.success", "Success"),
                    self.lang.get("subject.subject_deleted", "Subject deleted successfully!")
                )
                self._update_subject_buttons()
                if self.selected_subject == subject_name:
                    self.selected_subject = None
                self._show_dashboard()
        
    def _setup_window(self):
        """Setup window properties"""
        title = self.lang.get("app.title", APP_INFO["name"])
        self.title(f"{title} - {APP_INFO['team']} | {APP_INFO['developer']}")
        self.geometry(f"{UI_SETTINGS['window_width']}x{UI_SETTINGS['window_height']}")
        self.minsize(UI_SETTINGS['min_width'], UI_SETTINGS['min_height'])
        ctk.set_default_color_theme("blue")
        
        # Set window icon
        if os.path.exists(ICON_FILE):
            try:
                # For Windows
                if os.name == 'nt':
                    self.iconbitmap(ICON_FILE)
                else:
                    # For Linux/Mac
                    img = Image.open(ICON_FILE)
                    photo = ImageTk.PhotoImage(img)
                    self.iconphoto(False, photo)
            except Exception as e:
                print(f"Could not set icon: {e}")
    
    def _create_ui(self):
        """Create UI components"""
        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0)
        
        # Create header
        self._create_header()
        
        # Create sidebar
        self._create_sidebar()
        
        # Create main content area
        self._create_main_content()
    
    def _create_header(self):
        """Create modern header with enhanced styling - website-like design"""
        # Get theme mode for dynamic colors (only Dark or Light now)
        theme_mode = ctk.get_appearance_mode()
        is_dark = theme_mode == "Dark"
        
        # Theme-based colors
        if is_dark:
            # Dark mode: Black, Blue, Red, Purple (RGB colors) - NO PINK
            header_bg = COLORS.get("CARD_DARK", "#000000")  # Pure black
            button_bg_primary = "#1a1a3e"  # Dark blue-black
            button_bg_secondary = "#2d1b4e"  # Dark purple-black
            button_bg_accent = "#3d1a2a"  # Dark red-black
            button_bg_hover = "#1a2d3e"  # Dark cyan-black
            text_color = "#ffffff"
            quote_color = (COLORS.get("PRIMARY", "#6366f1"), COLORS.get("ACCENT_2", "#06b6d4"))  # Blue/Cyan for dark
        else:
            # Light mode: Pink, White
            header_bg = COLORS.get("CARD_LIGHT", "#fef2f2")  # Soft pink-white
            button_bg_primary = "#ffe4e6"  # Light pink
            button_bg_secondary = "#fce7f3"  # Rose pink
            button_bg_accent = "#fbcfe8"  # Hot pink
            button_bg_hover = "#fdf2f8"  # Soft pink
            text_color = "#1a1a1a"
            quote_color = ("#ec4899", "#f43f5e")  # Pink for light
        
        # Destroy old header if exists (for theme changes)
        if hasattr(self, 'header_frame'):
            try:
                self.header_frame.destroy()
            except:
                pass
        
        # Store header frame reference - FORCE correct background color
        self.header_frame = ctk.CTkFrame(
            self,
            fg_color=header_bg,  # Explicitly set - black for dark, pink-white for light
            corner_radius=0,
            height=150  # Increased height for quote + stats
        )
        self.header_frame.grid(row=0, column=0, columnspan=2, padx=0, pady=0, sticky="ew")
        self.header_frame.grid_columnconfigure(0, weight=1)
        self.header_frame.grid_propagate(False)
        
        # Inner frame for content
        inner_header = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        inner_header.pack(fill="both", expand=True, padx=25, pady=(10, 12))
        inner_header.grid_columnconfigure(0, weight=1)
        
        # Quote frame with beautiful styling
        quote_frame = ctk.CTkFrame(inner_header, fg_color="transparent")
        quote_frame.grid(row=0, column=0, columnspan=2, pady=(0, 8), sticky="ew")
        quote_frame.grid_columnconfigure(0, weight=1)
        
        # Quote label at the top - FORCE correct colors for dark mode
        initial_quote = self.quote_manager.get_random_quote()
        max_length = 120
        display_quote = initial_quote if len(initial_quote) <= max_length else initial_quote[:max_length-3] + "..."
        
        # Force correct colors - dark mode MUST be blue/cyan, NOT pink
        if is_dark:
            final_quote_color = (COLORS.get("PRIMARY", "#6366f1"), COLORS.get("ACCENT_2", "#06b6d4"))  # Blue/Cyan
        else:
            final_quote_color = ("#ec4899", "#f43f5e")  # Pink
        
        self.quote_label = ctk.CTkLabel(
            quote_frame,
            text=f'💬 "{display_quote}"',
            font=ctk.CTkFont(size=13, weight="normal"),
            text_color=final_quote_color,
            anchor="center",
            wraplength=900,
            justify="center"
        )
        self.quote_label.grid(row=0, column=0, sticky="ew", padx=10)
        
        # Hint text
        current_lang = self.settings.get_language()
        hint_text = "⌨️ Herhangi bir tuşa basarak sözü değiştirin" if current_lang == "tr" else "⌨️ Press any key to change quote"
        hint_label = ctk.CTkLabel(
            quote_frame,
            text=hint_text,
            font=ctk.CTkFont(size=9),
            text_color=(COLORS.get("TEXT_SECONDARY", "#94a3b8"), COLORS.get("TEXT_SECONDARY", "#64748b")),
            anchor="center"
        )
        hint_label.grid(row=1, column=0, pady=(2, 0))
        self.quote_hint_label = hint_label
        
        # Statistics row - moved from sidebar
        stats_frame = ctk.CTkFrame(inner_header, fg_color="transparent")
        stats_frame.grid(row=1, column=0, columnspan=2, pady=(0, 8), sticky="ew")
        
        # Get statistics
        stats = self.data_manager.get_statistics()
        
        # Create compact stat cards
        stat_items = [
            (f"💯 {stats['total_solved']:,}", "Çözülen" if current_lang == "tr" else "Solved"),
            (f"🎯 {stats['total_target']:,}", "Hedef" if current_lang == "tr" else "Target"),
            (f"📈 %{stats['progress']:.1f}", "İlerleme" if current_lang == "tr" else "Progress"),
            (f"✅ {stats['completed_topics']}/{stats['total_topics']}", "Konular" if current_lang == "tr" else "Topics")
        ]
        
        for idx, (value, label) in enumerate(stat_items):
            # Force correct colors - dark mode NO PINK
            if is_dark:
                stat_bg = "#1a1a3e"  # Dark blue-black
                stat_border = COLORS.get("BORDER_DARK", "#1a1a2e")
            else:
                stat_bg = "#ffe4e6"  # Light pink
                stat_border = COLORS.get("BORDER_LIGHT", "#fce7f3")
            
            stat_card = ctk.CTkFrame(
                stats_frame,
                fg_color=stat_bg,
                corner_radius=8,
                border_width=1,
                border_color=stat_border
            )
            stat_card.grid(row=0, column=idx, padx=4, sticky="ew")
            stats_frame.grid_columnconfigure(idx, weight=1)
            
            value_label = ctk.CTkLabel(
                stat_card,
                text=value,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=(text_color, text_color)
            )
            value_label.pack(pady=(4, 0))
            
            label_label = ctk.CTkLabel(
                stat_card,
                text=label,
                font=ctk.CTkFont(size=9),
                text_color=(COLORS.get("TEXT_SECONDARY", "#94a3b8"), COLORS.get("TEXT_SECONDARY", "#64748b"))
            )
            label_label.pack(pady=(0, 4))
        
        # Title and buttons row
        title_text = self.lang.get("app.title", APP_INFO["name"])
        title_label = ctk.CTkLabel(
            inner_header,
            text=title_text,
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=(COLORS["PRIMARY"] if is_dark else "#ec4899", 
                       COLORS["ACCENT_2"] if is_dark else "#f43f5e"),
            anchor="w"
        )
        title_label.grid(row=2, column=0, sticky="w")
        
        # Buttons frame with transparent style
        buttons_frame = ctk.CTkFrame(inner_header, fg_color="transparent")
        buttons_frame.grid(row=2, column=1, sticky="e", padx=(20, 0))
        
        # Transparent button style - website-like
        button_style = {
            "width": 105,
            "height": 32,
            "corner_radius": 8,
            "font": ctk.CTkFont(size=12, weight="bold"),
            "border_width": 1,
            "fg_color": button_bg_primary,
            "hover_color": COLORS["PRIMARY"] if is_dark else "#ec4899",
            "text_color": (text_color, text_color),
            "border_color": (COLORS.get("BORDER_DARK", "#1a1a2e") if is_dark else COLORS.get("BORDER_LIGHT", "#fce7f3"))
        }
        
        # Dashboard button
        ctk.CTkButton(
            buttons_frame,
            text=self.lang.get("menu.dashboard", "Dashboard"),
            command=self._show_dashboard,
            **button_style
        ).grid(row=0, column=0, padx=3)
        
        # Statistics button
        stats_btn_style = button_style.copy()
        stats_btn_style["fg_color"] = button_bg_secondary
        stats_btn_style["hover_color"] = COLORS["SECONDARY"] if is_dark else "#f43f5e"
        ctk.CTkButton(
            buttons_frame,
            text=self.lang.get("menu.statistics", "Statistics"),
            command=self._show_advanced_statistics,
            **stats_btn_style
        ).grid(row=0, column=1, padx=3)
        
        # Analytics button
        analytics_btn_style = button_style.copy()
        analytics_btn_style["fg_color"] = button_bg_accent
        analytics_btn_style["hover_color"] = COLORS["ACCENT"] if is_dark else "#f43f5e"
        ctk.CTkButton(
            buttons_frame,
            text=self.lang.get("analytics.title", "Analytics"),
            command=self._show_analytics,
            **analytics_btn_style
        ).grid(row=0, column=2, padx=3)
        
        # Export button
        export_btn_style = button_style.copy()
        export_btn_style["fg_color"] = button_bg_hover
        export_btn_style["hover_color"] = COLORS["HOVER_COLOR"] if is_dark else "#f43f5e"
        ctk.CTkButton(
            buttons_frame,
            text=self.lang.get("menu.export", "Export"),
            command=self._export_data,
            **export_btn_style
        ).grid(row=0, column=3, padx=3)
        
        # Language selector - FORCE correct colors
        lang_options_map = {
            "Türkçe": "tr",
            "Turkish": "tr",
            "English": "en",
            "İngilizce": "en"
        }
        lang_display = ["Türkçe", "English"]
        if is_dark:
            lang_fg = button_bg_primary  # "#1a1a3e"
            lang_btn = COLORS["PRIMARY"]  # "#6366f1"
            lang_hover = COLORS["PRIMARY_DARK"]  # "#4f46e5"
        else:
            lang_fg = button_bg_primary  # "#ffe4e6"
            lang_btn = "#ec4899"  # pink
            lang_hover = "#f43f5e"  # rose
        
        self.language_menu = ctk.CTkOptionMenu(
            buttons_frame,
            values=lang_display,
            width=110,
            height=32,
            corner_radius=8,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=lang_fg,
            button_color=lang_btn,
            button_hover_color=lang_hover,
            dropdown_fg_color=(header_bg, header_bg),
            text_color=(text_color, text_color),
            command=self._change_language
        )
        current_lang = self.settings.get_language()
        self.language_menu.set("Türkçe" if current_lang == "tr" else "English")
        self.language_menu.grid(row=0, column=4, padx=3)
        
        # Theme selector - only Dark and Light (System removed) - FORCE correct colors
        theme_options = ["Dark", "Light"]
        if is_dark:
            theme_fg = button_bg_secondary  # "#2d1b4e"
            theme_btn = COLORS["SECONDARY"]  # "#8b5cf6"
            theme_hover = "#7c3aed"  # darker purple
        else:
            theme_fg = button_bg_secondary  # "#fce7f3"
            theme_btn = "#f43f5e"  # rose
            theme_hover = "#f43f5e"  # rose
        
        self.theme_menu = ctk.CTkOptionMenu(
            buttons_frame,
            values=theme_options,
            width=85,
            height=32,
            corner_radius=8,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=theme_fg,
            button_color=theme_btn,
            button_hover_color=theme_hover,
            dropdown_fg_color=(header_bg, header_bg),
            text_color=(text_color, text_color),
            command=self._change_theme
        )
        current_theme = self.settings.get_theme()
        # Convert System to Light (since they're the same)
        if current_theme == "System":
            current_theme = "Light"
            self.settings.set_theme("Light")
        self.theme_menu.set(current_theme)
        self.theme_menu.grid(row=0, column=5, padx=3)
        
        # Store stats frame reference
        self.header_stats_frame = stats_frame
    
    def _is_system_dark(self):
        """Check if system is in dark mode"""
        try:
            import darkdetect
            return darkdetect.isDark()
        except:
            return False
    
    def _update_header_stats(self):
        """Update statistics in header"""
        if not self.header_stats_frame:
            return
        
        # Clear existing stats
        for widget in self.header_stats_frame.winfo_children():
            widget.destroy()
        
        # Get current stats
        stats = self.data_manager.get_statistics()
        current_lang = self.settings.get_language()
        theme_mode = ctk.get_appearance_mode()
        is_dark = theme_mode == "Dark"  # Only Dark or Light now
        text_color = "#ffffff" if is_dark else "#1a1a1a"
        
        # Recreate stat cards
        stat_items = [
            (f"💯 {stats['total_solved']:,}", "Çözülen" if current_lang == "tr" else "Solved"),
            (f"🎯 {stats['total_target']:,}", "Hedef" if current_lang == "tr" else "Target"),
            (f"📈 %{stats['progress']:.1f}", "İlerleme" if current_lang == "tr" else "Progress"),
            (f"✅ {stats['completed_topics']}/{stats['total_topics']}", "Konular" if current_lang == "tr" else "Topics")
        ]
        
        for idx, (value, label) in enumerate(stat_items):
            # Force correct colors - dark mode NO PINK
            if is_dark:
                stat_bg = "#1a1a3e"  # Dark blue-black
                stat_border = COLORS.get("BORDER_DARK", "#1a1a2e")
            else:
                stat_bg = "#ffe4e6"  # Light pink
                stat_border = COLORS.get("BORDER_LIGHT", "#fce7f3")
            
            stat_card = ctk.CTkFrame(
                self.header_stats_frame,
                fg_color=stat_bg,
                corner_radius=8,
                border_width=1,
                border_color=stat_border
            )
            stat_card.grid(row=0, column=idx, padx=4, sticky="ew")
            self.header_stats_frame.grid_columnconfigure(idx, weight=1)
            
            value_label = ctk.CTkLabel(
                stat_card,
                text=value,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=(text_color, text_color)
            )
            value_label.pack(pady=(4, 0))
            
            label_label = ctk.CTkLabel(
                stat_card,
                text=label,
                font=ctk.CTkFont(size=9),
                text_color=(COLORS.get("TEXT_SECONDARY", "#94a3b8"), COLORS.get("TEXT_SECONDARY", "#64748b"))
            )
            label_label.pack(pady=(0, 4))
    
    def _on_focus_in(self, event):
        """Handle focus in event"""
        self.focus_set()
        return True
    
    def _on_window_click(self, event):
        """Handle window click to gain focus"""
        self.focus_set()
        return True
    
    def _on_any_click(self, event):
        """Handle any click to ensure window can receive focus"""
        self.after(10, self.focus_set)
        return True
    
    def _on_key_press(self, event):
        """Handle key press events to change quote - improved version"""
        # Get the focused widget
        try:
            focused_widget = self.focus_get()
            if focused_widget:
                widget_class = focused_widget.__class__.__name__
                # If focus is on an entry or textbox, don't change quote
                if widget_class in ['CTkEntry', 'CTkTextbox']:
                    return
        except:
            pass
        
        # Ignore special keys
        ignored_keys = ['Tab', 'Shift_L', 'Shift_R', 'Control_L', 'Control_R', 
                       'Alt_L', 'Alt_R', 'Meta_L', 'Meta_R', 'Caps_Lock', 
                       'Num_Lock', 'Scroll_Lock', 'Escape', 'Return', 'Enter',
                       'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12',
                       'Up', 'Down', 'Left', 'Right', 'Home', 'End', 'Page_Up', 'Page_Down',
                       'Insert', 'Delete', 'BackSpace']
        
        if event.keysym in ignored_keys:
            return
        
        # Change quote on any regular key press
        try:
            new_quote = self.quote_manager.get_next_quote()
            if hasattr(self, 'quote_label') and self.quote_label:
                # Truncate very long quotes
                max_length = 120
                display_quote = new_quote if len(new_quote) <= max_length else new_quote[:max_length-3] + "..."
                
                # Update quote color based on theme - FORCE correct colors
                theme_mode = ctk.get_appearance_mode()
                is_dark = theme_mode == "Dark"
                if is_dark:
                    # Dark mode: Blue/Cyan - ABSOLUTELY NO PINK
                    quote_color = (COLORS.get("PRIMARY", "#6366f1"), COLORS.get("ACCENT_2", "#06b6d4"))
                else:
                    # Light mode: Pink
                    quote_color = ("#ec4899", "#f43f5e")
                
                self.quote_label.configure(text=f'💬 "{display_quote}"', text_color=quote_color)
        except Exception as e:
            print(f"Error updating quote: {e}")
            import traceback
            traceback.print_exc()
    
    def _create_sidebar(self):
        """Create modern sidebar with enhanced styling and filtering"""
        self.sidebar = ctk.CTkFrame(
            self,
            width=UI_SETTINGS["sidebar_width"],
            corner_radius=18,
            fg_color=(COLORS.get("CARD_LIGHT", "#f8fafc"), COLORS.get("CARD_DARK", "#1e293b")),
            border_width=1,
            border_color=(COLORS.get("BORDER_LIGHT", "#e2e8f0"), COLORS.get("BORDER_DARK", "#334155"))
        )
        self.sidebar.grid(row=1, column=0, rowspan=2, padx=(20, 10), pady=(10, 20), sticky="ns")
        self.sidebar.grid_columnconfigure(0, weight=1)
        
        # Sidebar title frame with modern styling
        title_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        title_frame.grid(row=0, column=0, padx=15, pady=(20, 10), sticky="ew")
        title_frame.grid_columnconfigure(0, weight=1)
        
        subjects_label = self.lang.get("subject.subjects", "Subjects/Projects")
        title_label = ctk.CTkLabel(
            title_frame,
            text=subjects_label,
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=(COLORS["PRIMARY"], COLORS["ACCENT_2"])
        )
        title_label.grid(row=0, column=0, sticky="w")
        
        # Modern add subject button
        add_subject_btn = ctk.CTkButton(
            title_frame,
            text="+",
            width=42,
            height=42,
            fg_color=COLORS["PRIMARY"],
            hover_color=COLORS["PRIMARY_DARK"],
            command=self._show_add_subject_dialog,
            font=ctk.CTkFont(size=26, weight="bold"),
            corner_radius=12
        )
        add_subject_btn.grid(row=0, column=1, padx=(10, 0))
        
        # Search and filter frame
        filter_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        filter_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")
        filter_frame.grid_columnconfigure(0, weight=1)
        
        # Search entry with debouncing for performance
        self.search_var = ctk.StringVar()
        self.search_debounce_timer = None
        self.search_var.trace("w", lambda *args: self._debounced_filter_subjects())
        search_entry = ctk.CTkEntry(
            filter_frame,
            width=200,
            height=36,
            corner_radius=10,
            placeholder_text=self.lang.get("subject.search_placeholder", "Search..."),
            textvariable=self.search_var,
            font=ctk.CTkFont(size=12),
            border_width=1,
            border_color=(COLORS.get("BORDER_LIGHT", "#e2e8f0"), COLORS.get("BORDER_DARK", "#334155"))
        )
        search_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        # Filter button
        filter_btn = ctk.CTkButton(
            filter_frame,
            text="🔍",
            width=38,
            height=36,
            fg_color=COLORS["SECONDARY"],
            hover_color="#7c3aed",
            command=self._show_filter_dialog,
            font=ctk.CTkFont(size=16),
            corner_radius=10
        )
        filter_btn.grid(row=0, column=1)
        
        # Scrollable frame for subjects (statistics moved to navbar)
        self.subjects_scroll = ctk.CTkScrollableFrame(self.sidebar, fg_color="transparent")
        self.subjects_scroll.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")
        self.subjects_scroll.grid_columnconfigure(0, weight=1)
        self.sidebar.grid_rowconfigure(2, weight=1)
        
        # Filter state
        self.current_filter = {
            "category": None,
            "priority": None,
            "status": None
        }
        
        # Current sidebar tab
        self.current_sidebar_tab = "projects"
        
        # Initialize subject buttons
        self.subject_buttons = {}
        self._update_subject_buttons()
    
    def _create_main_content(self):
        """Create modern main content area"""
        self.main_content = ctk.CTkFrame(
            self,
            corner_radius=20,
            fg_color=(COLORS.get("CARD_LIGHT", "#f8f9fa"), COLORS.get("CARD_DARK", "#2d2d2d")),
            border_width=2,
            border_color=(COLORS.get("BORDER_LIGHT", "#e0e0e0"), COLORS.get("BORDER_DARK", "#404040"))
        )
        self.main_content.grid(row=1, column=1, padx=(10, 20), pady=(10, 5), sticky="nsew")
        self.main_content.grid_columnconfigure(0, weight=1)
        self.main_content.grid_rowconfigure(0, weight=1)
    
    def _show_projects_tab(self):
        """Show projects tab in sidebar (always visible now)"""
        self.current_sidebar_tab = "projects"
        if self.subjects_scroll:
            self.subjects_scroll.grid()
    
    def _show_home_screen(self):
        """Show home screen when no subject is selected"""
        self._show_dashboard()
    
    def _show_dashboard(self):
        """Show dashboard view with caching"""
        if self._update_pending:
            return  # Skip if update is already pending
        
        self.current_view = "dashboard"
        self.selected_subject = None  # Clear selection
        
        # Reset button colors
        for btn in self.subject_buttons.values():
            btn.configure(fg_color=(COLORS.get("CARD_LIGHT", "#f8f9fa"), COLORS.get("CARD_DARK", "#2d2d2d")))
        
        for widget in self.main_content.winfo_children():
            widget.destroy()
        
        # Create scrollable dashboard
        dashboard_scroll = ctk.CTkScrollableFrame(self.main_content)
        dashboard_scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Dashboard widget
        from .components.dashboard import DashboardWidget
        dashboard_widget = DashboardWidget(
            dashboard_scroll,
            self.data_manager,
            self.time_tracker,
            self.analytics,
            self.lang
        )
        dashboard_widget.pack(fill="x", padx=10, pady=10)
        
        # Quick actions section
        self._create_quick_actions_section(dashboard_scroll)
        
        # Subjects quick view
        self._create_subjects_quick_view(dashboard_scroll)
        
        # Upcoming deadlines section
        self._create_upcoming_deadlines_section(dashboard_scroll)
        
        # Time tracking section
        self._create_time_tracking_section(dashboard_scroll)
        
        # Goals section
        self._create_goals_section(dashboard_scroll)
        
        # Recent activity
        self._create_recent_activity_section(dashboard_scroll)
        
        # Weekly summary
        self._create_weekly_summary_section(dashboard_scroll)
        
    
    def _select_subject(self, subject_name):
        """Select a subject and show its details"""
        # Update button colors
        if self.selected_subject and self.selected_subject in self.subject_buttons:
            self.subject_buttons[self.selected_subject].configure(
                fg_color=(COLORS.get("CARD_LIGHT", "#f8f9fa"), COLORS.get("CARD_DARK", "#2d2d2d"))
            )
        
        self.selected_subject = subject_name
        if subject_name in self.subject_buttons:
            self.subject_buttons[subject_name].configure(fg_color=COLORS["PRIMARY"])
        
        # Show subject details
        self._show_subject_details(subject_name)
        
    
    def _show_subject_details(self, subject_name):
        """Show detailed view for a subject/project with enhanced info"""
        try:
            # Don't skip if update is pending - just reset it
            if self._update_pending:
                self._update_pending = False
            
            # Clear with performance optimization
            widgets_to_destroy = list(self.main_content.winfo_children())
            for widget in widgets_to_destroy:
                widget.destroy()
            
            subject_data = self.data_manager.data.get(subject_name, {})
            solved = subject_data.get('cozulen_soru', 0)
            target = subject_data.get('hedef_soru', 1)
            progress = min(solved / target if target > 0 else 0, 1.0)
            
            # Scrollable frame for details - moved to top (row 0)
            scroll_frame = ctk.CTkScrollableFrame(
                self.main_content,
                label_text=f"{subject_name} - {self.lang.get('subject.progress', 'Details')}",
                label_font=ctk.CTkFont(size=20, weight="bold")
            )
            scroll_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=5)
            scroll_frame.grid_columnconfigure(0, weight=1)
            self.main_content.grid_rowconfigure(0, weight=1)
            
            # Forms frame
            forms_frame = ctk.CTkFrame(scroll_frame)
            forms_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
            forms_frame.grid_columnconfigure((0, 1, 2), weight=1)
            
            # Create forms
            self._create_question_form(forms_frame, subject_name, solved)
            self._create_target_form(forms_frame, subject_name, target, subject_data.get('son_calisma_tarihi', ''))
            self._create_topic_form(forms_frame, subject_name)
            
            # Topic list
            self.topic_list_frame = ctk.CTkFrame(scroll_frame)
            self.topic_list_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(10, 5))
            self.topic_list_frame.grid_columnconfigure(0, weight=1)
            self._update_topic_list(subject_name)
            
            # Notes section for subject
            notes_frame = ctk.CTkFrame(scroll_frame)
            notes_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(5, 10))
            notes_frame.grid_columnconfigure(0, weight=1)
            self._create_subject_notes_section(notes_frame, subject_name)
            
            # Subject comparison chart
            chart_frame = ctk.CTkFrame(scroll_frame, height=350)
            chart_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=(5, 10))
            theme_mode = ctk.get_appearance_mode()
            self.chart_manager.create_subject_comparison_chart(
                chart_frame,
                self.data_manager,
                subject_name,
                theme_mode
            )
            
            # Performance metrics
            performance_frame = ctk.CTkFrame(scroll_frame)
            performance_frame.grid(row=4, column=0, sticky="ew", padx=10, pady=(5, 10))
            self._create_performance_section(performance_frame, subject_name)
            
            # Last Position section (optional bookmark) - moved to bottom, compact design
            last_position_frame = ctk.CTkFrame(
                scroll_frame,
                corner_radius=10,
                fg_color=(COLORS.get("CARD_LIGHT", "#f8f9fa"), COLORS.get("CARD_DARK", "#2d2d2d")),
                border_width=1,
                border_color=(COLORS.get("BORDER_LIGHT", "#e0e0e0"), COLORS.get("BORDER_DARK", "#404040"))
            )
            last_position_frame.grid(row=5, column=0, sticky="ew", padx=10, pady=(5, 10))
            last_position_frame.grid_columnconfigure(0, weight=1)
            self._create_last_position_section(last_position_frame, subject_name)
        
        except Exception as e:
            # Show error message if something goes wrong
            error_label = ctk.CTkLabel(
                self.main_content,
                text=f"{self.lang.get('messages.error', 'Error')}: {str(e)}",
                font=ctk.CTkFont(size=14),
                text_color=COLORS["ERROR"]
            )
            error_label.pack(pady=50)
            import traceback
            traceback.print_exc()
    
    def _create_question_form(self, master_frame, subject_name, current_solved):
        """Create question adding form - modern design"""
        form_frame = ctk.CTkFrame(
            master_frame,
            corner_radius=15,
            fg_color=(COLORS.get("CARD_LIGHT", "#f8fafc"), COLORS.get("CARD_DARK", "#1e293b")),
            border_width=1,
            border_color=(COLORS.get("BORDER_LIGHT", "#e2e8f0"), COLORS.get("BORDER_DARK", "#334155"))
        )
        form_frame.grid(row=0, column=0, padx=8, pady=8, sticky="ew")
        form_frame.grid_columnconfigure(0, weight=1)
        
        label_text = self.lang.get("actions.add_questions", "Add Questions")
        ctk.CTkLabel(
            form_frame, 
            text=label_text, 
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=(COLORS["PRIMARY"], COLORS["PRIMARY_LIGHT"])
        ).grid(row=0, column=0, columnspan=2, pady=(12, 8))
        
        question_input = ctk.CTkEntry(
            form_frame, 
            width=100,
            height=36,
            corner_radius=10,
            placeholder_text=self.lang.get("subject.questions", "Questions"),
            font=ctk.CTkFont(size=13),
            border_width=1,
            border_color=(COLORS.get("BORDER_LIGHT", "#e2e8f0"), COLORS.get("BORDER_DARK", "#334155"))
        )
        question_input.grid(row=1, column=0, padx=8, pady=(0, 8), sticky="ew")
        
        def add_questions_and_clear():
            count_str = question_input.get()
            try:
                count = int(count_str)
                if count <= 0:
                    raise ValueError
                
                self.data_manager.add_questions(subject_name, count)
                subject_data = self.data_manager.data.get(subject_name, {})
                solved = subject_data.get('cozulen_soru', 0)
                target = subject_data.get('hedef_soru', 1)
                progress = (solved / target * 100) if target > 0 else 0
                
                messagebox.showinfo(
                    self.lang.get("messages.success", "Success"),
                    self.lang.translate("messages.question_added", count=count) + f"\n\n"
                    f"{self.lang.get('subject.solved', 'Solved')}: {solved}/{target}\n"
                    f"{self.lang.get('subject.progress', 'Progress')}: %{progress:.1f}"
                )
                
                question_input.delete(0, "end")
                self._show_subject_details(subject_name)
            except ValueError:
                messagebox.showerror(
                    self.lang.get("messages.error", "Error"),
                    self.lang.get("messages.invalid_number", "Please enter a valid number!")
                )
        
        question_input.bind("<Return>", lambda e: add_questions_and_clear())
        
        add_text = self.lang.get("actions.add", "Add")
        ctk.CTkButton(
            form_frame,
            text=add_text,
            width=90,
            height=36,
            corner_radius=10,
            fg_color=COLORS["PRIMARY"],
            hover_color=COLORS["PRIMARY_DARK"],
            command=add_questions_and_clear,
            font=ctk.CTkFont(size=13, weight="bold"),
            border_width=0
        ).grid(row=1, column=1, padx=(0, 8), pady=(0, 8))
        
        solved_text = f"{self.lang.get('subject.solved', 'Solved')}: {current_solved}"
        ctk.CTkLabel(
            form_frame, 
            text=solved_text, 
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=(COLORS.get("TEXT_SECONDARY", "#94a3b8"), "#cbd5e1")
        ).grid(row=2, column=0, columnspan=2, pady=(0, 8))
        form_frame.grid_columnconfigure(0, weight=1)
    
    def _create_target_form(self, master_frame, subject_name, current_target, last_study_date):
        """Create target setting form - modern design"""
        form_frame = ctk.CTkFrame(
            master_frame,
            corner_radius=15,
            fg_color=(COLORS.get("CARD_LIGHT", "#f8fafc"), COLORS.get("CARD_DARK", "#1e293b")),
            border_width=1,
            border_color=(COLORS.get("BORDER_LIGHT", "#e2e8f0"), COLORS.get("BORDER_DARK", "#334155"))
        )
        form_frame.grid(row=0, column=1, padx=8, pady=8, sticky="ew")
        form_frame.grid_columnconfigure(0, weight=1)
        
        label_text = self.lang.get("actions.set_target", "Set Target")
        ctk.CTkLabel(
            form_frame, 
            text=label_text, 
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=(COLORS["SECONDARY"], COLORS["ACCENT"])
        ).grid(row=0, column=0, columnspan=2, pady=(12, 8))
        
        target_input = ctk.CTkEntry(
            form_frame, 
            width=100,
            height=36,
            corner_radius=10,
            placeholder_text=self.lang.get("subject.target", "Target"),
            font=ctk.CTkFont(size=13),
            border_width=1,
            border_color=(COLORS.get("BORDER_LIGHT", "#e2e8f0"), COLORS.get("BORDER_DARK", "#334155"))
        )
        target_input.insert(0, str(current_target))
        target_input.grid(row=1, column=0, padx=8, pady=(0, 8), sticky="ew")
        
        def set_target_and_update():
            target_str = target_input.get()
            try:
                target = int(target_str)
                if target <= 0:
                    raise ValueError
                
                self.data_manager.set_target(subject_name, target)
                subject_data = self.data_manager.data.get(subject_name, {})
                solved = subject_data.get('cozulen_soru', 0)
                progress = (solved / target * 100) if target > 0 else 0
                
                messagebox.showinfo(
                    self.lang.get("messages.success", "Success"),
                    self.lang.translate("messages.target_set", target=target) + f"\n\n"
                    f"{self.lang.get('messages.current_progress', 'Current Progress')}: {solved}/{target} (%{progress:.1f})"
                )
                
                self._show_subject_details(subject_name)
            except ValueError:
                messagebox.showerror(
                    self.lang.get("messages.error", "Error"),
                    self.lang.get("messages.invalid_number", "Please enter a valid number!")
                )
        
        target_input.bind("<Return>", lambda e: set_target_and_update())
        
        set_text = self.lang.get("actions.set", "Set")
        ctk.CTkButton(
            form_frame,
            text=set_text,
            width=90,
            height=36,
            corner_radius=10,
            fg_color=COLORS["SECONDARY"],
            hover_color="#7c3aed",
            command=set_target_and_update,
            font=ctk.CTkFont(size=13, weight="bold"),
            border_width=0
        ).grid(row=1, column=1, padx=(0, 8), pady=(0, 8))
        
        last_study_text = self.lang.get("subject.last_study", "Last Study")
        if last_study_date:
            study_label = f"{last_study_text}: {last_study_date}"
        else:
            study_label = f"{last_study_text}: {self.lang.get('subject.none', 'None')}"
        ctk.CTkLabel(
            form_frame, 
            text=study_label, 
            font=ctk.CTkFont(size=12),
            text_color=(COLORS.get("TEXT_SECONDARY", "#94a3b8"), "#cbd5e1")
        ).grid(row=2, column=0, columnspan=2, pady=(0, 8))
        form_frame.grid_columnconfigure(0, weight=1)
    
    def _create_topic_form(self, master_frame, subject_name):
        """Create topic adding form - modern design"""
        form_frame = ctk.CTkFrame(
            master_frame,
            corner_radius=15,
            fg_color=(COLORS.get("CARD_LIGHT", "#f8fafc"), COLORS.get("CARD_DARK", "#1e293b")),
            border_width=1,
            border_color=(COLORS.get("BORDER_LIGHT", "#e2e8f0"), COLORS.get("BORDER_DARK", "#334155"))
        )
        form_frame.grid(row=0, column=2, padx=8, pady=8, sticky="ew")
        form_frame.grid_columnconfigure(0, weight=1)
        
        label_text = self.lang.get("actions.add_topic", "Add New Topic")
        ctk.CTkLabel(
            form_frame, 
            text=label_text, 
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=(COLORS["ACCENT_2"], COLORS["INFO"])
        ).grid(row=0, column=0, columnspan=2, pady=(12, 8))
        
        topic_input = ctk.CTkEntry(
            form_frame, 
            height=36,
            corner_radius=10,
            placeholder_text=self.lang.get("topic.name", "Topic Name"),
            font=ctk.CTkFont(size=13),
            border_width=1,
            border_color=(COLORS.get("BORDER_LIGHT", "#e2e8f0"), COLORS.get("BORDER_DARK", "#334155"))
        )
        topic_input.grid(row=1, column=0, padx=8, pady=(0, 8), sticky="ew")
        
        def add_topic_and_clear():
            topic_name = topic_input.get().strip()
            if not topic_name:
                messagebox.showerror(
                    self.lang.get("messages.error", "Error"),
                    self.lang.get("messages.empty_topic", "Topic name cannot be empty.")
                )
                return
            
            if self.data_manager.add_topic(subject_name, topic_name):
                messagebox.showinfo(
                    self.lang.get("messages.success", "Success"),
                    self.lang.get("messages.topic_added", "Topic added.")
                )
                topic_input.delete(0, "end")
                self._update_topic_list(subject_name)
            else:
                messagebox.showerror(
                    self.lang.get("messages.error", "Error"),
                    self.lang.get("messages.topic_exists", "This topic already exists.")
                )
        
        topic_input.bind("<Return>", lambda e: add_topic_and_clear())
        
        add_text = self.lang.get("actions.add", "Add")
        ctk.CTkButton(
            form_frame,
            text=add_text,
            width=90,
            height=36,
            corner_radius=10,
            fg_color=COLORS["ACCENT_2"],
            hover_color="#0891b2",
            command=add_topic_and_clear,
            font=ctk.CTkFont(size=13, weight="bold"),
            border_width=0
        ).grid(row=1, column=1, padx=(0, 8), pady=(0, 8))
        form_frame.grid_columnconfigure(0, weight=1)
    
    def _update_topic_list(self, subject_name):
        """Update topic list display"""
        for widget in self.topic_list_frame.winfo_children():
            widget.destroy()
        
        tracking_text = self.lang.get("topic.tracking", "Topic Tracking")
        ctk.CTkLabel(
            self.topic_list_frame, 
            text=tracking_text, 
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=(COLORS["PRIMARY"], COLORS["PRIMARY_LIGHT"])
        ).grid(row=0, column=0, padx=12, pady=(12, 8), sticky="w", columnspan=5)
        
        # Headers - modernized
        headers = [
            self.lang.get("topic.name", "Topic Name"),
            self.lang.get("topic.status", "Status"),
            self.lang.get("topic.start_date", "Start"),
            self.lang.get("topic.end_date", "End"),
            self.lang.get("actions.delete", "Delete")
        ]
        for col, header in enumerate(headers):
            ctk.CTkLabel(
                self.topic_list_frame, 
                text=header, 
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=(COLORS.get("TEXT_SECONDARY", "#94a3b8"), "#cbd5e1")
            ).grid(row=1, column=col, padx=8, pady=8)
        self.topic_list_frame.grid_columnconfigure(0, weight=1)
        
        topics = self.data_manager.data.get(subject_name, {}).get('konular', [])
        
        if not topics:
            no_topics_text = self.lang.get("topic.no_topics", "No topics in this subject.")
            ctk.CTkLabel(self.topic_list_frame, text=no_topics_text, 
                        font=ctk.CTkFont(size=14)).grid(row=2, column=0, columnspan=5, padx=10, pady=10)
            return
        
        status_options = [
            self.lang.get("topic.todo", "Todo"),
            self.lang.get("topic.in_progress", "In Progress"),
            self.lang.get("topic.completed", "Completed")
        ]
        
        status_map = {
            self.lang.get("topic.todo", "Todo"): "Yapılacak",
            self.lang.get("topic.in_progress", "In Progress"): "Devam Ediyor",
            self.lang.get("topic.completed", "Completed"): "Tamamlandı"
        }
        
        reverse_status_map = {v: k for k, v in status_map.items()}
        
        for i, topic in enumerate(topics):
            row_num = i + 2
            
            topic_label = ctk.CTkLabel(
                self.topic_list_frame,
                text=topic['ad'],
                anchor="w",
                font=ctk.CTkFont(weight="bold") if topic['durum'] != "Tamamlandı" else ctk.CTkFont(slant="italic", weight="bold")
            )
            topic_label.grid(row=row_num, column=0, padx=10, pady=3, sticky="w")
            
            color_map = {
                "Yapılacak": "red",
                "Devam Ediyor": "orange",
                "Tamamlandı": "green"
            }
            
            current_status_display = reverse_status_map.get(topic['durum'], status_options[0])
            
            status_menu = ctk.CTkOptionMenu(
                self.topic_list_frame,
                values=status_options,
                width=120,
                height=32,
                corner_radius=8,
                font=ctk.CTkFont(size=11),
                button_color=color_map.get(topic['durum'], COLORS["BUTTON_COLOR"]),
                fg_color=(COLORS.get("CARD_LIGHT", "#f8fafc"), COLORS.get("CARD_DARK", "#1e293b")),
                command=lambda status, sn=subject_name, tn=topic['ad']: self._update_topic_status(sn, tn, status_map.get(status, "Yapılacak"))
            )
            status_menu.set(current_status_display)
            status_menu.grid(row=row_num, column=1, padx=8, pady=6)
            
            start_date = topic.get('baslangic_tarihi', '-')
            end_date = topic.get('bitirme_tarihi', '-')
            
            ctk.CTkLabel(
                self.topic_list_frame, 
                text=start_date, 
                width=100,
                font=ctk.CTkFont(size=11),
                text_color=(COLORS.get("TEXT_SECONDARY", "#94a3b8"), "#cbd5e1")
            ).grid(row=row_num, column=2, padx=8, pady=6)
            ctk.CTkLabel(
                self.topic_list_frame, 
                text=end_date, 
                width=100,
                font=ctk.CTkFont(size=11),
                text_color=(COLORS.get("TEXT_SECONDARY", "#94a3b8"), "#cbd5e1")
            ).grid(row=row_num, column=3, padx=8, pady=6)
            
            delete_text = self.lang.get("actions.delete", "Delete")
            ctk.CTkButton(
                self.topic_list_frame, 
                text=delete_text, 
                width=70,
                height=32,
                corner_radius=8,
                fg_color=COLORS["ERROR"],
                hover_color="#dc2626",
                font=ctk.CTkFont(size=11, weight="bold"),
                command=lambda sn=subject_name, tn=topic['ad']: self._delete_topic(sn, tn)
            ).grid(row=row_num, column=4, padx=8, pady=6)
    
    def _update_topic_status(self, subject_name, topic_name, status):
        """Update topic status"""
        if self.data_manager.update_topic_status(subject_name, topic_name, status):
            self._update_topic_list(subject_name)
    
    def _delete_topic(self, subject_name, topic_name):
        """Delete a topic"""
        confirm_text = self.lang.get("messages.confirm_delete", "Are you sure?")
        if messagebox.askyesno(self.lang.get("actions.delete", "Delete"), confirm_text):
            if self.data_manager.delete_topic(subject_name, topic_name):
                messagebox.showinfo(
                    self.lang.get("messages.success", "Success"),
                    self.lang.get("messages.topic_deleted", "Topic deleted.")
                )
                self._update_topic_list(subject_name)
    
    
    def _show_statistics(self):
        """Show statistics window"""
        stats_window = ctk.CTkToplevel(self)
        stats_window.title(self.lang.get("statistics.title", "Statistics"))
        stats_window.geometry("600x500")
        stats_window.transient(self)
        stats_window.grab_set()
        
        scroll_frame = ctk.CTkScrollableFrame(stats_window)
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        stats = self.data_manager.get_statistics()
        
        # Title
        title_text = self.lang.get("statistics.general", "General Statistics")
        ctk.CTkLabel(scroll_frame, text=title_text, 
                    font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(0, 20))
        
        # Statistics cards
        stats_data = [
            (self.lang.get("statistics.total_solved", "Total Solved"), f"{stats['total_solved']:,}", "💯"),
            (self.lang.get("statistics.total_target", "Total Target"), f"{stats['total_target']:,}", "🎯"),
            (self.lang.get("statistics.progress", "Progress"), f"%{stats['progress']:.1f}", "📈"),
            (self.lang.get("statistics.total_topics", "Total Topics"), f"{stats['total_topics']}", "📝"),
            (self.lang.get("statistics.completed_topics", "Completed Topics"), f"{stats['completed_topics']}", "✅"),
            (self.lang.get("statistics.remaining", "Remaining"), f"{stats['remaining']:,}", "⏳"),
        ]
        
        for label, value, emoji in stats_data:
            card = ctk.CTkFrame(scroll_frame)
            card.pack(fill="x", pady=5, padx=10)
            ctk.CTkLabel(card, text=f"{emoji} {label}", 
                        font=ctk.CTkFont(size=14, weight="bold")).pack(side="left", padx=15, pady=10)
            ctk.CTkLabel(card, text=value, 
                        font=ctk.CTkFont(size=16, weight="bold"),
                        text_color=COLORS["HOVER_COLOR"]).pack(side="right", padx=15, pady=10)
        
        # Subject-based statistics
        by_subject_text = self.lang.get("statistics.by_subject", "Subject-based Statistics")
        ctk.CTkLabel(scroll_frame, text=f"\n{by_subject_text}", 
                    font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(20, 10))
        
        for subject_name in sorted(self.data_manager.data.keys()):
            subject_data = self.data_manager.data[subject_name]
            solved = subject_data.get('cozulen_soru', 0)
            target = subject_data.get('hedef_soru', 1)
            progress = (solved / target * 100) if target > 0 else 0
            topic_count = len(subject_data.get('konular', []))
            
            subject_card = ctk.CTkFrame(scroll_frame)
            subject_card.pack(fill="x", pady=5, padx=10)
            
            left_frame = ctk.CTkFrame(subject_card, fg_color="transparent")
            left_frame.pack(side="left", fill="both", expand=True, padx=10, pady=5)
            ctk.CTkLabel(left_frame, text=subject_name, 
                        font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w")
            questions_text = f"{solved}/{target} {self.lang.get('subject.questions', 'questions')} (%{progress:.1f})"
            ctk.CTkLabel(left_frame, text=questions_text, 
                        font=ctk.CTkFont(size=12)).pack(anchor="w")
            
            progress_bar = ctk.CTkProgressBar(subject_card, width=150, height=20)
            progress_bar.pack(side="right", padx=10, pady=5)
            progress_bar.set(min(progress / 100, 1.0))
            
            topics_text = f"📝 {topic_count} {self.lang.get('statistics.topics', 'topics')}"
            ctk.CTkLabel(subject_card, text=topics_text, 
                        font=ctk.CTkFont(size=11)).pack(side="right", padx=10, pady=5)
        
        close_text = self.lang.get("actions.close", "Close")
        ctk.CTkButton(stats_window, text=close_text, command=stats_window.destroy,
                     fg_color=COLORS["HOVER_COLOR"]).pack(pady=10)
    
    def _export_data(self):
        """Export data dialog with format selection"""
        export_dialog = ctk.CTkToplevel(self)
        export_dialog.title(self.lang.get("export.title", "Export Data"))
        export_dialog.geometry("300x250")
        export_dialog.transient(self)
        export_dialog.grab_set()
        
        ctk.CTkLabel(export_dialog, text=self.lang.get("export.select_format", "Select Export Format"), 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=20)
        
        def export_json():
            export_dialog.destroy()
            file_path = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title=self.lang.get("export.export_json", "Export to JSON")
            )
            if file_path:
                try:
                    self.export_manager.export_to_json(file_path)
                    messagebox.showinfo(
                        self.lang.get("messages.success", "Success"),
                        f"{self.lang.get('messages.export_success', 'Data exported successfully!')}\n{file_path}"
                    )
                except Exception as e:
                    messagebox.showerror(
                        self.lang.get("messages.error", "Error"),
                        f"{self.lang.get('messages.export_error', 'Export error')}: {str(e)}"
                    )
        
        def export_excel():
            export_dialog.destroy()
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                title=self.lang.get("export.export_excel", "Export to Excel")
            )
            if file_path:
                try:
                    success, message = self.export_manager.export_to_excel(file_path)
                    if success:
                        messagebox.showinfo(
                            self.lang.get("messages.success", "Success"),
                            f"{self.lang.get('messages.export_success', 'Data exported successfully!')}\n{file_path}"
                        )
                    else:
                        messagebox.showerror(
                            self.lang.get("messages.error", "Error"),
                            f"{self.lang.get('messages.export_error', 'Export error')}: {message}"
                        )
                except Exception as e:
                    messagebox.showerror(
                        self.lang.get("messages.error", "Error"),
                        f"{self.lang.get('messages.export_error', 'Export error')}: {str(e)}"
                    )
        
        def export_pdf():
            export_dialog.destroy()
            file_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
                title=self.lang.get("export.export_pdf", "Export to PDF")
            )
            if file_path:
                try:
                    success, message = self.export_manager.export_to_pdf(file_path)
                    if success:
                        messagebox.showinfo(
                            self.lang.get("messages.success", "Success"),
                            f"{self.lang.get('messages.export_success', 'Data exported successfully!')}\n{file_path}"
                        )
                    else:
                        messagebox.showerror(
                            self.lang.get("messages.error", "Error"),
                            f"{self.lang.get('messages.export_error', 'Export error')}: {message}"
                        )
                except Exception as e:
                    messagebox.showerror(
                        self.lang.get("messages.error", "Error"),
                        f"{self.lang.get('messages.export_error', 'Export error')}: {str(e)}"
                    )
        
        ctk.CTkButton(export_dialog, text=self.lang.get("export.export_json", "Export to JSON"), command=export_json, 
                     fg_color=COLORS["HOVER_COLOR"], width=200).pack(pady=5)
        ctk.CTkButton(export_dialog, text=self.lang.get("export.export_excel", "Export to Excel"), command=export_excel, 
                     fg_color=COLORS["HOVER_COLOR"], width=200).pack(pady=5)
        ctk.CTkButton(export_dialog, text=self.lang.get("export.export_pdf", "Export to PDF"), command=export_pdf, 
                     fg_color=COLORS["HOVER_COLOR"], width=200).pack(pady=5)
        ctk.CTkButton(export_dialog, text=self.lang.get("export.cancel", "Cancel"), command=export_dialog.destroy).pack(pady=10)
    
    def _change_language(self, language_label):
        """Change application language"""
        lang_map = {
            "Türkçe": "tr",
            "Turkish": "tr",
            "English": "en",
            "İngilizce": "en"
        }
        
        new_lang = lang_map.get(language_label, "tr")
        
        if new_lang != self.settings.get_language():
            self.settings.set_language(new_lang)
            self.lang.set_language(new_lang)
            
            # Update quote hint text
            if hasattr(self, 'quote_hint_label') and self.quote_hint_label:
                hint_text = "⌨️ Herhangi bir tuşa basarak sözü değiştirin" if new_lang == "tr" else "⌨️ Press any key to change quote"
                self.quote_hint_label.configure(text=hint_text)
            
            # Update window title
            title = self.lang.get("app.title", APP_INFO["name"])
            self.title(f"{title} - {APP_INFO['team']} | {APP_INFO['developer']}")
            # Refresh UI
            self._refresh_ui_for_language()
            # Show message
            messagebox.showinfo(
                self.lang.get("messages.success", "Success"),
                self.lang.get("messages.language_changed", "Language changed. Some changes may require restart.")
            )
    
    def _refresh_ui_for_language(self):
        """Refresh UI elements when language changes"""
        # Store current state
        current_subject = self.selected_subject
        current_view = self.current_view
        
        # Clear header and recreate
        for widget in self.grid_slaves(row=0):
            widget.destroy()
        self._create_header()
        
        # Clear sidebar and recreate
        if hasattr(self, 'sidebar'):
            self.sidebar.destroy()
        self._create_sidebar()
        
        # Refresh current view
        if current_view == "dashboard":
            self._show_dashboard()
        elif current_subject:
            self._select_subject(current_subject)
        
    
    def _change_theme(self, theme):
        """Change application theme"""
        # Theme is already in English format (Dark or Light)
        if theme != ctk.get_appearance_mode():
            ctk.set_appearance_mode(theme)
            self.settings.set_theme(theme)
            
            # Destroy old header and recreate with new colors
            if hasattr(self, 'header_frame'):
                self.header_frame.destroy()
            
            # Recreate header with new theme colors
            self._create_header()
            
            # Refresh current view
            if self.selected_subject:
                self._show_subject_details(self.selected_subject)
            else:
                self._show_dashboard()
    
    def _create_quick_actions_section(self, parent):
        """Create quick actions section with modern buttons"""
        actions_frame = ctk.CTkFrame(
            parent,
            corner_radius=15,
            fg_color=(COLORS.get("CARD_LIGHT", "#f8f9fa"), COLORS.get("CARD_DARK", "#2d2d2d")),
            border_width=2,
            border_color=(COLORS.get("BORDER_LIGHT", "#e0e0e0"), COLORS.get("BORDER_DARK", "#404040"))
        )
        actions_frame.pack(fill="x", padx=10, pady=10)
        
        title = ctk.CTkLabel(
            actions_frame,
            text=f"⚡ {self.lang.get('dashboard.quick_actions', 'Quick Actions')}",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=(COLORS["PRIMARY"], COLORS["ACCENT_2"])
        )
        title.pack(pady=(15, 10))
        
        buttons_frame = ctk.CTkFrame(actions_frame, fg_color="transparent")
        buttons_frame.pack(pady=(0, 15))
        
        # Quick action buttons
        quick_actions = [
            (self.lang.get("menu.statistics", "Statistics"), COLORS["SECONDARY"], self._show_advanced_statistics),
            (self.lang.get("analytics.title", "Analytics"), COLORS["ACCENT_2"], self._show_analytics),
            (self.lang.get("menu.export", "Export"), COLORS["HOVER_COLOR"], self._export_data),
        ]
        
        for i, (text, color, command) in enumerate(quick_actions):
            btn = ctk.CTkButton(
                buttons_frame,
                text=text,
                width=140,
                height=40,
                fg_color=color,
                hover_color=color,
                command=command,
                corner_radius=10,
                font=ctk.CTkFont(size=13, weight="bold")
            )
            btn.pack(side="left", padx=8)
    
    def _create_subjects_quick_view(self, parent):
        """Create quick view of all subjects with progress"""
        subjects_frame = ctk.CTkFrame(
            parent,
            corner_radius=15,
            fg_color=(COLORS.get("CARD_LIGHT", "#f8f9fa"), COLORS.get("CARD_DARK", "#2d2d2d")),
            border_width=2,
            border_color=(COLORS.get("BORDER_LIGHT", "#e0e0e0"), COLORS.get("BORDER_DARK", "#404040"))
        )
        subjects_frame.pack(fill="x", padx=10, pady=10)
        
        title_frame = ctk.CTkFrame(subjects_frame, fg_color="transparent")
        title_frame.pack(fill="x", padx=15, pady=(15, 10))
        
        title = ctk.CTkLabel(
            title_frame,
            text=f"📚 {self.lang.get('subject.subjects', 'Subjects')} - {self.lang.get('dashboard.quick_view', 'Quick View')}",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=(COLORS["PRIMARY"], COLORS["ACCENT_2"])
        )
        title.pack(side="left")
        
        subjects = list(self.data_manager.data.keys())
        if not subjects:
            no_subjects_label = ctk.CTkLabel(
                subjects_frame,
                text=self.lang.get("subject.select", "Select a subject"),
                font=ctk.CTkFont(size=12),
                text_color=(COLORS.get("TEXT_SECONDARY", "#95a5a6"), "#b0b0b0")
            )
            no_subjects_label.pack(pady=15)
            return
        
        # Create subject cards in a grid
        grid_frame = ctk.CTkFrame(subjects_frame, fg_color="transparent")
        grid_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        # Configure grid - 2 columns
        for i in range(2):
            grid_frame.grid_columnconfigure(i, weight=1, uniform="equal")
        
        for i, subject_name in enumerate(subjects[:6]):  # Show first 6 subjects
            subject_data = self.data_manager.data.get(subject_name, {})
            solved = subject_data.get('cozulen_soru', 0)
            target = subject_data.get('hedef_soru', 1)
            progress = min((solved / target * 100) if target > 0 else 0, 100)
            
            row = i // 2
            col = i % 2
            
            # Subject card
            card = ctk.CTkFrame(
                grid_frame,
                corner_radius=12,
                fg_color=(COLORS.get("CARD_LIGHT", "#f8f9fa"), COLORS.get("CARD_DARK", "#2d2d2d")),
                border_width=1,
                border_color=(COLORS.get("BORDER_LIGHT", "#e0e0e0"), COLORS.get("BORDER_DARK", "#404040"))
            )
            card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
            
            # Card content
            inner_card = ctk.CTkFrame(card, fg_color="transparent")
            inner_card.pack(fill="both", expand=True, padx=12, pady=12)
            
            # Subject name
            name_label = ctk.CTkLabel(
                inner_card,
                text=subject_name,
                font=ctk.CTkFont(size=14, weight="bold"),
                anchor="w"
            )
            name_label.pack(fill="x", pady=(0, 8))
            
            # Progress info
            progress_text = f"{solved}/{target} ({progress:.1f}%)"
            progress_label = ctk.CTkLabel(
                inner_card,
                text=progress_text,
                font=ctk.CTkFont(size=12),
                text_color=(COLORS.get("TEXT_SECONDARY", "#95a5a6"), "#b0b0b0")
            )
            progress_label.pack(fill="x", pady=(0, 5))
            
            # Progress bar
            progress_bar = ctk.CTkProgressBar(
                inner_card,
                height=8,
                fg_color=(COLORS.get("CARD_LIGHT", "#f8f9fa"), COLORS.get("CARD_DARK", "#2d2d2d")),
                progress_color=COLORS["PRIMARY"],
                corner_radius=4
            )
            progress_bar.pack(fill="x", pady=(0, 8))
            progress_bar.set(progress / 100)
            
            # Click to view button
            def make_click_handler(subj_name):
                return lambda: self._select_subject(subj_name)
            
            view_btn = ctk.CTkButton(
                inner_card,
                text=self.lang.get("actions.view", "View"),
                width=80,
                height=28,
                fg_color=COLORS["PRIMARY"],
                hover_color=COLORS["PRIMARY_DARK"],
                command=make_click_handler(subject_name),
                corner_radius=8,
                font=ctk.CTkFont(size=11, weight="bold")
            )
            view_btn.pack()
    
    def _create_time_tracking_section(self, parent):
        """Create time tracking section in dashboard"""
        time_frame = ctk.CTkFrame(
            parent,
            corner_radius=15,
            fg_color=(COLORS.get("CARD_LIGHT", "#f8f9fa"), COLORS.get("CARD_DARK", "#2d2d2d")),
            border_width=2,
            border_color=(COLORS.get("BORDER_LIGHT", "#e0e0e0"), COLORS.get("BORDER_DARK", "#404040"))
        )
        time_frame.pack(fill="x", padx=10, pady=10)
        
        title = ctk.CTkLabel(
            time_frame,
            text=self.lang.get("time.tracking", "Time Tracking"),
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title.pack(pady=(10, 10))
        
        # Today's stats
        today_stats = self.time_tracker.get_today_stats()
        stats_text = f"{self.lang.get('time.total_today', 'Total Today')}: {int(today_stats['total_time_minutes'])} min | {today_stats['total_questions']} {self.lang.get('subject.questions', 'questions')}"
        ctk.CTkLabel(time_frame, text=stats_text, font=ctk.CTkFont(size=14)).pack(pady=5)
        
        # Session controls
        controls_frame = ctk.CTkFrame(time_frame, fg_color="transparent")
        controls_frame.pack(pady=10)
        
        if self.active_session_id:
            ctk.CTkButton(
                controls_frame,
                text=self.lang.get("time.end_session", "End Session"),
                fg_color="red",
                hover_color="darkred",
                command=self._end_study_session
            ).pack(side="left", padx=5)
        else:
            # Subject selector for session
            subjects = list(self.data_manager.data.keys())
            if subjects:
                session_subject_var = ctk.StringVar(value=subjects[0])
                session_subject_menu = ctk.CTkOptionMenu(
                    controls_frame,
                    values=subjects,
                    variable=session_subject_var,
                    width=150
                )
                session_subject_menu.pack(side="left", padx=5)
                
                ctk.CTkButton(
                    controls_frame,
                    text=self.lang.get("time.start_session", "Start Session"),
                    fg_color=COLORS["HOVER_COLOR"],
                    command=lambda: self._start_study_session(session_subject_var.get())
                ).pack(side="left", padx=5)
    
    def _create_goals_section(self, parent):
        """Create goals section in dashboard"""
        goals_frame = ctk.CTkFrame(
            parent,
            corner_radius=15,
            fg_color=(COLORS.get("CARD_LIGHT", "#f8f9fa"), COLORS.get("CARD_DARK", "#2d2d2d")),
            border_width=2,
            border_color=(COLORS.get("BORDER_LIGHT", "#e0e0e0"), COLORS.get("BORDER_DARK", "#404040"))
        )
        goals_frame.pack(fill="x", padx=10, pady=10)
        
        title_frame = ctk.CTkFrame(goals_frame, fg_color="transparent")
        title_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        title = ctk.CTkLabel(
            title_frame,
            text=self.lang.get("goals.title", "Goals"),
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title.pack(side="left")
        
        ctk.CTkButton(
            title_frame,
            text=self.lang.get("goals.add_goal", "Add Goal"),
            width=100,
            height=25,
            fg_color=COLORS["HOVER_COLOR"],
            command=self._show_add_goal_dialog
        ).pack(side="right")
        
        # Active goals
        active_goals = self.goal_tracker.get_goals(include_completed=False)
        if active_goals:
            for goal in active_goals[:5]:  # Show first 5
                goal_card = ctk.CTkFrame(goals_frame, corner_radius=5)
                goal_card.pack(fill="x", padx=10, pady=5)
                
                goal_text = f"{goal['subject']} - {goal['type']}: {goal['current_value']}/{goal['target_value']}"
                ctk.CTkLabel(goal_card, text=goal_text, font=ctk.CTkFont(size=12)).pack(side="left", padx=10, pady=5)
                
                progress = min(goal['current_value'] / goal['target_value'], 1.0) if goal['target_value'] > 0 else 0
                progress_bar = ctk.CTkProgressBar(goal_card, width=200)
                progress_bar.pack(side="right", padx=10, pady=5)
                progress_bar.set(progress)
        else:
            ctk.CTkLabel(
                goals_frame,
                text=self.lang.get("goals.no_goals", "No active goals. Add one to get started!"),
                font=ctk.CTkFont(size=12),
                text_color="gray"
            ).pack(pady=10)
    
    def _create_recent_activity_section(self, parent):
        """Create recent activity section"""
        activity_frame = ctk.CTkFrame(
            parent,
            corner_radius=15,
            fg_color=(COLORS.get("CARD_LIGHT", "#f8f9fa"), COLORS.get("CARD_DARK", "#2d2d2d")),
            border_width=2,
            border_color=(COLORS.get("BORDER_LIGHT", "#e0e0e0"), COLORS.get("BORDER_DARK", "#404040"))
        )
        activity_frame.pack(fill="x", padx=10, pady=10)
        
        title = ctk.CTkLabel(
            activity_frame,
            text=self.lang.get("recent_activity.title", "Recent Activity"),
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=(COLORS["PRIMARY"], COLORS["ACCENT_2"])
        )
        title.pack(pady=(15, 10))
        
        # Get recent notes
        recent_notes = self.notes_manager.get_all_notes()[:5]
        if recent_notes:
            for note in recent_notes:
                note_text = f"{note.get('subject', 'Unknown')}: {note.get('text', '')[:50]}..."
                ctk.CTkLabel(
                    activity_frame,
                    text=note_text,
                    font=ctk.CTkFont(size=11),
                    anchor="w"
                ).pack(fill="x", padx=15, pady=2)
        else:
            ctk.CTkLabel(
                activity_frame,
                text=self.lang.get("recent_activity.no_activity", "No recent activity"),
                font=ctk.CTkFont(size=12),
                text_color=(COLORS.get("TEXT_SECONDARY", "#95a5a6"), "#b0b0b0")
            ).pack(pady=15)
    
    def _create_weekly_summary_section(self, parent):
        """Create weekly summary section"""
        weekly_frame = ctk.CTkFrame(
            parent,
            corner_radius=15,
            fg_color=(COLORS.get("CARD_LIGHT", "#f8f9fa"), COLORS.get("CARD_DARK", "#2d2d2d")),
            border_width=2,
            border_color=(COLORS.get("BORDER_LIGHT", "#e0e0e0"), COLORS.get("BORDER_DARK", "#404040"))
        )
        weekly_frame.pack(fill="x", padx=10, pady=10)
        
        title = ctk.CTkLabel(
            weekly_frame,
            text=f"📅 {self.lang.get('dashboard.weekly_summary', 'Weekly Summary')}",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=(COLORS["PRIMARY"], COLORS["ACCENT_2"])
        )
        title.pack(pady=(15, 10))
        
        week_stats = self.time_tracker.get_week_stats()
        
        # Stats grid
        stats_grid = ctk.CTkFrame(weekly_frame, fg_color="transparent")
        stats_grid.pack(fill="x", padx=15, pady=(0, 15))
        
        for i in range(3):
            stats_grid.grid_columnconfigure(i, weight=1, uniform="equal")
        
        # Total time
        time_card = ctk.CTkFrame(
            stats_grid,
            corner_radius=10,
            fg_color=(COLORS.get("CARD_LIGHT", "#f8f9fa"), COLORS.get("CARD_DARK", "#2d2d2d")),
            border_width=1
        )
        time_card.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        
        ctk.CTkLabel(
            time_card,
            text="⏱️",
            font=ctk.CTkFont(size=24)
        ).pack(pady=(10, 5))
        
        total_hours = int(week_stats['total_time_minutes'] / 60)
        total_mins = int(week_stats['total_time_minutes'] % 60)
        time_text = f"{total_hours}h {total_mins}m"
        ctk.CTkLabel(
            time_card,
            text=time_text,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["INFO"]
        ).pack(pady=(0, 5))
        
        ctk.CTkLabel(
            time_card,
            text=self.lang.get("analytics.total_time", "Total Time"),
            font=ctk.CTkFont(size=11),
            text_color=(COLORS.get("TEXT_SECONDARY", "#95a5a6"), "#b0b0b0")
        ).pack(pady=(0, 10))
        
        # Total questions
        questions_card = ctk.CTkFrame(
            stats_grid,
            corner_radius=10,
            fg_color=(COLORS.get("CARD_LIGHT", "#f8f9fa"), COLORS.get("CARD_DARK", "#2d2d2d")),
            border_width=1
        )
        questions_card.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        
        ctk.CTkLabel(
            questions_card,
            text="📚",
            font=ctk.CTkFont(size=24)
        ).pack(pady=(10, 5))
        
        ctk.CTkLabel(
            questions_card,
            text=f"{week_stats['total_questions']}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["ERROR"]
        ).pack(pady=(0, 5))
        
        ctk.CTkLabel(
            questions_card,
            text=self.lang.get("subject.questions", "Questions"),
            font=ctk.CTkFont(size=11),
            text_color=(COLORS.get("TEXT_SECONDARY", "#95a5a6"), "#b0b0b0")
        ).pack(pady=(0, 10))
        
        # Sessions
        sessions_card = ctk.CTkFrame(
            stats_grid,
            corner_radius=10,
            fg_color=(COLORS.get("CARD_LIGHT", "#f8f9fa"), COLORS.get("CARD_DARK", "#2d2d2d")),
            border_width=1
        )
        sessions_card.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")
        
        ctk.CTkLabel(
            sessions_card,
            text="🎯",
            font=ctk.CTkFont(size=24)
        ).pack(pady=(10, 5))
        
        ctk.CTkLabel(
            sessions_card,
            text=f"{week_stats['session_count']}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["SUCCESS"]
        ).pack(pady=(0, 5))
        
        ctk.CTkLabel(
            sessions_card,
            text=self.lang.get("dashboard.sessions", "Sessions"),
            font=ctk.CTkFont(size=11),
            text_color=(COLORS.get("TEXT_SECONDARY", "#95a5a6"), "#b0b0b0")
        ).pack(pady=(0, 10))
    
    def _create_upcoming_deadlines_section(self, parent):
        """Create upcoming deadlines section"""
        deadlines = self.data_manager.get_upcoming_deadlines(days=7)
        if not deadlines:
            return
        
        deadlines_frame = ctk.CTkFrame(
            parent,
            corner_radius=15,
            fg_color=(COLORS.get("CARD_LIGHT", "#f8f9fa"), COLORS.get("CARD_DARK", "#2d2d2d")),
            border_width=2,
            border_color=(COLORS.get("BORDER_LIGHT", "#e0e0e0"), COLORS.get("BORDER_DARK", "#404040"))
        )
        deadlines_frame.pack(fill="x", padx=10, pady=10)
        
        title = ctk.CTkLabel(
            deadlines_frame,
            text=f"⏰ {self.lang.get('subject.upcoming_deadlines', 'Upcoming Deadlines')}",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=(COLORS["WARNING"], COLORS["WARNING"])
        )
        title.pack(pady=(15, 10))
        
        today = datetime.date.today()
        
        for subject_name, subject_data in sorted(deadlines.items(), key=lambda x: x[1].get('deadline', '')):
            deadline_str = subject_data.get('deadline', '')
            if not deadline_str:
                continue
            
            try:
                deadline_date = datetime.date.fromisoformat(deadline_str)
                days_left = (deadline_date - today).days
                
                deadline_card = ctk.CTkFrame(deadlines_frame, corner_radius=10)
                deadline_card.pack(fill="x", padx=15, pady=5)
                
                if days_left < 0:
                    deadline_text = f"⚠️ {subject_name} - {abs(days_left)} {self.lang.get('dashboard.days', 'days')} geçti"
                    deadline_color = COLORS["ERROR"]
                elif days_left <= 3:
                    deadline_text = f"⏰ {subject_name} - {days_left} {self.lang.get('dashboard.days', 'days')} kaldı"
                    deadline_color = COLORS["WARNING"]
                else:
                    deadline_text = f"📅 {subject_name} - {days_left} {self.lang.get('dashboard.days', 'days')} kaldı"
                    deadline_color = COLORS["INFO"]
                
                ctk.CTkLabel(
                    deadline_card,
                    text=deadline_text,
                    font=ctk.CTkFont(size=13, weight="bold"),
                    text_color=deadline_color
                ).pack(side="left", padx=10, pady=8)
                
                ctk.CTkButton(
                    deadline_card,
                    text=self.lang.get("actions.view", "View"),
                    width=80,
                    height=30,
                    fg_color=COLORS["PRIMARY"],
                    hover_color=COLORS["PRIMARY_DARK"],
                    command=partial(self._select_subject, subject_name),
                    corner_radius=8,
                    font=ctk.CTkFont(size=11, weight="bold")
                ).pack(side="right", padx=10, pady=8)
            except:
                continue
    
    def _start_study_session(self, subject_name):
        """Start a study session"""
        self.active_session_id = self.time_tracker.start_session(subject_name)
        messagebox.showinfo(
            self.lang.get("messages.success", "Success"),
            self.lang.translate("messages.session_started", subject=subject_name)
        )
        self._show_dashboard()
    
    def _end_study_session(self):
        """End current study session"""
        if self.active_session_id:
            # Create dialog for ending session
            dialog = ctk.CTkToplevel(self)
            dialog.title(self.lang.get("time.end_session_title", "End Session"))
            dialog.geometry("350x250")
            dialog.transient(self)
            dialog.grab_set()
            
            ctk.CTkLabel(dialog, text=self.lang.get("time.end_session_question", "Do you want to end the study session?"), 
                        font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10)
            
            ctk.CTkLabel(dialog, text=self.lang.get("time.questions_solved", "Questions Solved")).pack(pady=5)
            questions_entry = ctk.CTkEntry(dialog, placeholder_text="0")
            questions_entry.pack(pady=5)
            questions_entry.insert(0, "0")
            
            ctk.CTkLabel(dialog, text=self.lang.get("time.session_notes", "Session Notes") + " (optional):").pack(pady=5)
            notes_entry = ctk.CTkEntry(dialog, placeholder_text=self.lang.get("time.session_notes", "Session Notes"), width=300)
            notes_entry.pack(pady=5)
            
            def end_session():
                try:
                    questions = int(questions_entry.get() or "0")
                    notes = notes_entry.get() or ""
                    session = self.time_tracker.end_session(self.active_session_id, questions, notes)
                    if session and questions > 0:
                        # Update data manager if questions were solved
                        session_subject = session.get("subject", "")
                        if session_subject:
                            self.data_manager.add_questions(session_subject, questions)
                    self.active_session_id = None
                    dialog.destroy()
                    messagebox.showinfo(
                        self.lang.get("messages.success", "Success"),
                        self.lang.get("messages.session_ended", "Session ended successfully!")
                    )
                    self._show_dashboard()
                except ValueError:
                    messagebox.showerror(
                        self.lang.get("messages.error", "Error"),
                        self.lang.get("messages.invalid_number", "Invalid number!")
                    )
            
            ctk.CTkButton(dialog, text=self.lang.get("time.end_session", "End Session"), command=end_session, fg_color="red").pack(pady=10)
            ctk.CTkButton(dialog, text=self.lang.get("actions.cancel", "Cancel"), command=dialog.destroy).pack(pady=5)
    
    def _show_add_goal_dialog(self):
        """Show add goal dialog"""
        dialog = ctk.CTkToplevel(self)
        dialog.title(self.lang.get("goals.add_goal", "Add Goal"))
        dialog.geometry("400x300")
        dialog.transient(self)
        dialog.grab_set()
        
        # Subject selection
        ctk.CTkLabel(dialog, text=self.lang.get("subject.subjects", "Subject")).pack(pady=5)
        subjects = list(self.data_manager.data.keys())
        subject_var = ctk.StringVar(value=subjects[0] if subjects else "")
        subject_menu = ctk.CTkOptionMenu(dialog, values=subjects, variable=subject_var)
        subject_menu.pack(pady=5)
        
        # Goal type
        ctk.CTkLabel(dialog, text=self.lang.get("goals.goal_type", "Goal Type")).pack(pady=5)
        goal_types = [
            self.lang.get("goals.type_questions", "Questions"),
            self.lang.get("goals.type_time", "Study Time"),
            self.lang.get("goals.type_topics", "Topics")
        ]
        type_var = ctk.StringVar(value=goal_types[0])
        type_menu = ctk.CTkOptionMenu(dialog, values=goal_types, variable=type_var)
        type_menu.pack(pady=5)
        
        # Target value
        ctk.CTkLabel(dialog, text=self.lang.get("goals.target_value", "Target Value")).pack(pady=5)
        target_input = ctk.CTkEntry(dialog, placeholder_text=self.lang.get("goals.target_value", "Target Value"))
        target_input.pack(pady=5)
        
        # Target date
        ctk.CTkLabel(dialog, text=self.lang.get("goals.date_format", "Date (YYYY-MM-DD)")).pack(pady=5)
        date_input = ctk.CTkEntry(dialog, placeholder_text="2025-12-31")
        date_input.pack(pady=5)
        
        def add_goal():
            try:
                target = int(target_input.get())
                target_date = date_input.get() or None
                goal_type_map = {
                    self.lang.get("goals.type_questions", "Questions"): "questions",
                    self.lang.get("goals.type_time", "Study Time"): "time",
                    self.lang.get("goals.type_topics", "Topics"): "topics"
                }
                goal_type = goal_type_map.get(type_var.get(), "questions")
                
                self.goal_tracker.add_goal(subject_var.get(), goal_type, target, target_date)
                messagebox.showinfo(
                    self.lang.get("messages.success", "Success"),
                    self.lang.get("goals.goal_added", "Goal added successfully!")
                )
                dialog.destroy()
                self._show_dashboard()
            except ValueError:
                messagebox.showerror(
                    self.lang.get("messages.error", "Error"),
                    self.lang.get("messages.invalid_number", "Invalid number!")
                )
        
        ctk.CTkButton(dialog, text=self.lang.get("actions.add", "Add"), command=add_goal).pack(pady=20)
    
    def _show_advanced_statistics(self):
        """Show advanced statistics window"""
        self._show_statistics()  # For now, use existing statistics
    
    def _show_analytics(self):
        """Show analytics window"""
        analytics_window = ctk.CTkToplevel(self)
        analytics_window.title(self.lang.get("analytics.title", "Analytics"))
        analytics_window.geometry("800x600")
        analytics_window.transient(self)
        
        scroll_frame = ctk.CTkScrollableFrame(analytics_window)
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Productivity score
        productivity = self.analytics.get_productivity_score()
        score_frame = ctk.CTkFrame(scroll_frame)
        score_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(score_frame, text=self.lang.get("analytics.productivity_score", "Productivity Score"), 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        ctk.CTkLabel(score_frame, text=f"{productivity}%", 
                    font=ctk.CTkFont(size=32, weight="bold"),
                    text_color=COLORS["HOVER_COLOR"]).pack(pady=10)
        
        # Study streak
        streak = self.analytics.get_study_streak()
        streak_frame = ctk.CTkFrame(scroll_frame)
        streak_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(streak_frame, text=self.lang.get("analytics.study_streak", "Study Streak"), 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        streak_text = f"{streak} {self.lang.get('dashboard.days', 'days')}"
        ctk.CTkLabel(streak_frame, text=streak_text, 
                    font=ctk.CTkFont(size=24, weight="bold")).pack(pady=10)
        
        # Weekly trend
        weekly_trend = self.analytics.get_weekly_trend()
        trend_frame = ctk.CTkFrame(scroll_frame)
        trend_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(trend_frame, text=self.lang.get("analytics.weekly_trend", "Weekly Trend"), 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        
        for week in weekly_trend:
            week_text = f"{week['week']}: {int(week['total_time'])} {self.lang.get('dashboard.minutes', 'min')}, {week['total_questions']} {self.lang.get('subject.questions', 'questions')}"
            ctk.CTkLabel(trend_frame, text=week_text, font=ctk.CTkFont(size=12)).pack(pady=2)
        
        # Recommendations
        recommendations = self.analytics.get_recommendations()
        if recommendations:
            rec_frame = ctk.CTkFrame(scroll_frame)
            rec_frame.pack(fill="x", pady=10)
            ctk.CTkLabel(rec_frame, text=self.lang.get("analytics.recommendations", "Recommendations"), 
                        font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
            
            for rec in recommendations:
                rec_text = rec.get("message", "")
                color = COLORS.get(rec.get("type", "info").upper(), COLORS["INFO"])
                ctk.CTkLabel(rec_frame, text=rec_text, font=ctk.CTkFont(size=12),
                           text_color=color).pack(pady=2, anchor="w", padx=10)
        
        ctk.CTkButton(analytics_window, text=self.lang.get("actions.close", "Close"),
                     command=analytics_window.destroy).pack(pady=10)
    
    def _create_subject_notes_section(self, parent, subject_name):
        """Create notes section for subject"""
        ctk.CTkLabel(parent, text=self.lang.get("notes.title", "Notes"), 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10, anchor="w", padx=10)
        
        # Notes list
        notes_list_frame = ctk.CTkFrame(parent)
        notes_list_frame.pack(fill="x", padx=10, pady=5)
        notes_list_frame.grid_columnconfigure(0, weight=1)
        
        notes = self.notes_manager.get_notes(subject_name)
        if notes:
            for i, note in enumerate(notes[-5:]):  # Show last 5 notes
                note_frame = ctk.CTkFrame(notes_list_frame)
                note_frame.grid(row=i, column=0, sticky="ew", padx=5, pady=2)
                note_frame.grid_columnconfigure(0, weight=1)
                
                note_text = note.get("text", "")[:100]
                note_date = note.get("date", "")[:10]
                ctk.CTkLabel(note_frame, text=f"{note_date}: {note_text}", 
                            font=ctk.CTkFont(size=11), anchor="w").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        else:
            ctk.CTkLabel(notes_list_frame, text=self.lang.get("notes.no_notes", "No notes yet"),
                        font=ctk.CTkFont(size=12), text_color="gray").grid(row=0, column=0, padx=5, pady=5)
        
        # Add note button
        def add_note_dialog():
            note_dialog = ctk.CTkToplevel(self)
            note_dialog.title(self.lang.get("notes.add_note", "Add Note"))
            note_dialog.geometry("400x200")
            note_dialog.transient(self)
            note_dialog.grab_set()
            
            ctk.CTkLabel(note_dialog, text=self.lang.get("notes.note_text", "Note Text")).pack(pady=5)
            note_text_entry = ctk.CTkTextbox(note_dialog, height=100)
            note_text_entry.pack(pady=5, padx=10, fill="both", expand=True)
            
            def save_note():
                note_text = note_text_entry.get("1.0", "end-1c").strip()
                if note_text:
                    self.notes_manager.add_note(subject_name, None, note_text)
                    note_dialog.destroy()
                    self._show_subject_details(subject_name)
            
            ctk.CTkButton(note_dialog, text=self.lang.get("notes.save", "Save"), command=save_note).pack(pady=10)
        
        ctk.CTkButton(parent, text=self.lang.get("notes.add_note", "Add Note"),
                     command=add_note_dialog, width=150).pack(pady=10)
    
    def _create_last_position_section(self, parent, subject_name):
        """Create last position/bookmark section - compact design"""
        # Compact title row
        title_row = ctk.CTkFrame(parent, fg_color="transparent")
        title_row.pack(fill="x", padx=8, pady=(6, 4))
        title_row.grid_columnconfigure(0, weight=1)
        
        title_label = ctk.CTkLabel(
            title_row,
            text=f"📍 {self.lang.get('last_position.title', 'Last Position')}",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=(COLORS["PRIMARY"], COLORS["ACCENT_2"])
        )
        title_label.grid(row=0, column=0, sticky="w")
        
        # Get last position
        last_position = self.notes_manager.get_last_position(subject_name)
        
        if last_position and last_position.get("text"):
            # Show existing position
            position_text = last_position.get("text", "")
            position_date = last_position.get("date", "")[:10]
            
            content_frame = ctk.CTkFrame(parent, fg_color="transparent")
            content_frame.pack(fill="x", padx=8, pady=(0, 6))
            content_frame.grid_columnconfigure(0, weight=1)
            
            # Position text - compact
            text_label = ctk.CTkLabel(
                content_frame,
                text=position_text,
                font=ctk.CTkFont(size=11),
                anchor="w",
                wraplength=600
            )
            text_label.grid(row=0, column=0, sticky="w", padx=(0, 8))
            
            # Date label - compact
            date_label = ctk.CTkLabel(
                content_frame,
                text=f"📅 {position_date}",
                font=ctk.CTkFont(size=9),
                text_color=(COLORS.get("TEXT_SECONDARY", "#95a5a6"), "#b0b0b0")
            )
            date_label.grid(row=1, column=0, sticky="w", pady=(3, 0))
            
            # Buttons frame - compact
            buttons_frame = ctk.CTkFrame(parent, fg_color="transparent")
            buttons_frame.pack(fill="x", padx=8, pady=(0, 6))
            
            def edit_position():
                self._show_last_position_dialog(subject_name, position_text)
            
            def delete_position():
                result = messagebox.askyesno(
                    self.lang.get("last_position.delete", "Delete"),
                    self.lang.get("messages.confirm_delete", "Are you sure you want to delete this?")
                )
                if result:
                    if self.notes_manager.delete_last_position(subject_name):
                        messagebox.showinfo(
                            self.lang.get("messages.success", "Success"),
                            self.lang.get("last_position.deleted", "Last position deleted!")
                        )
                        self._show_subject_details(subject_name)
            
            ctk.CTkButton(
                buttons_frame,
                text=self.lang.get("last_position.edit", "Edit"),
                width=80,
                height=28,
                fg_color=COLORS["PRIMARY"],
                hover_color=COLORS["PRIMARY_DARK"],
                command=edit_position,
                corner_radius=8,
                font=ctk.CTkFont(size=11, weight="bold")
            ).pack(side="left", padx=5)
            
            ctk.CTkButton(
                buttons_frame,
                text=self.lang.get("last_position.delete", "Delete"),
                width=80,
                height=28,
                fg_color=COLORS["ERROR"],
                hover_color="#c0392b",
                command=delete_position,
                corner_radius=8,
                font=ctk.CTkFont(size=11, weight="bold")
            ).pack(side="left", padx=5)
        else:
            # Show add button - compact
            no_position_label = ctk.CTkLabel(
                parent,
                text=self.lang.get("last_position.no_position", "No last position saved yet"),
                font=ctk.CTkFont(size=10),
                text_color=(COLORS.get("TEXT_SECONDARY", "#95a5a6"), "#b0b0b0")
            )
            no_position_label.pack(pady=(0, 6))
            
            def add_position():
                self._show_last_position_dialog(subject_name)
            
            ctk.CTkButton(
                parent,
                text=f"+ {self.lang.get('last_position.add', 'Save Last Position')}",
                width=180,
                height=30,
                fg_color=COLORS["PRIMARY"],
                hover_color=COLORS["PRIMARY_DARK"],
                command=add_position,
                corner_radius=8,
                font=ctk.CTkFont(size=11, weight="bold")
            ).pack(pady=(0, 6))
    
    def _show_last_position_dialog(self, subject_name, current_text=""):
        """Show dialog for adding/editing last position"""
        dialog = ctk.CTkToplevel(self)
        dialog.title(self.lang.get("last_position.title", "Last Position"))
        dialog.geometry("500x250")
        dialog.transient(self)
        dialog.grab_set()
        
        # Title
        title_label = ctk.CTkLabel(
            dialog,
            text=self.lang.get("last_position.title", "Last Position"),
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(15, 10))
        
        # Description
        desc_label = ctk.CTkLabel(
            dialog,
            text=self.lang.get("last_position.position_text", "Last position (e.g., Page 45, Topic 3.2, etc.)"),
            font=ctk.CTkFont(size=12),
            text_color=(COLORS.get("TEXT_SECONDARY", "#95a5a6"), "#b0b0b0")
        )
        desc_label.pack(pady=(0, 10))
        
        # Text entry
        text_entry = ctk.CTkTextbox(dialog, height=100, width=450)
        text_entry.pack(pady=10, padx=20, fill="both", expand=True)
        if current_text:
            text_entry.insert("1.0", current_text)
        text_entry.focus()
        
        # Buttons
        buttons_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        buttons_frame.pack(pady=15)
        
        def save_position():
            position_text = text_entry.get("1.0", "end-1c").strip()
            if not position_text:
                messagebox.showerror(
                    self.lang.get("messages.error", "Error"),
                    self.lang.get("messages.empty_field", "Field cannot be empty!")
                )
                return
            
            is_update = bool(current_text)
            self.notes_manager.set_last_position(subject_name, position_text)
            
            if is_update:
                messagebox.showinfo(
                    self.lang.get("messages.success", "Success"),
                    self.lang.get("last_position.updated", "Last position updated!")
                )
            else:
                messagebox.showinfo(
                    self.lang.get("messages.success", "Success"),
                    self.lang.get("last_position.saved", "Last position saved!")
                )
            
            dialog.destroy()
            self._show_subject_details(subject_name)
        
        ctk.CTkButton(
            buttons_frame,
            text=self.lang.get("last_position.save", "Save"),
            width=120,
            height=35,
            fg_color=COLORS["PRIMARY"],
            hover_color=COLORS["PRIMARY_DARK"],
            command=save_position,
            corner_radius=10,
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            buttons_frame,
            text=self.lang.get("last_position.cancel", "Cancel"),
            width=120,
            height=35,
            command=dialog.destroy,
            corner_radius=10,
            font=ctk.CTkFont(size=13)
        ).pack(side="left", padx=10)
        
        # Enter key binding
        text_entry.bind("<Control-Return>", lambda e: save_position())
    
    def _apply_filters(self, subjects):
        """Apply current filters to subject list"""
        filtered = subjects
        
        # Search filter
        search_text = self.search_var.get().strip().lower() if hasattr(self, 'search_var') else ""
        if search_text:
            filtered = [s for s in filtered if search_text in s.lower()]
        
        # Category filter
        if hasattr(self, 'current_filter') and self.current_filter.get("category"):
            filtered = [
                s for s in filtered
                if self.data_manager.data.get(s, {}).get('category', '') == self.current_filter["category"]
            ]
        
        # Priority filter
        if hasattr(self, 'current_filter') and self.current_filter.get("priority"):
            filtered = [
                s for s in filtered
                if self.data_manager.data.get(s, {}).get('priority', 'medium') == self.current_filter["priority"]
            ]
        
        # Status filter
        if hasattr(self, 'current_filter') and self.current_filter.get("status"):
            filtered = [
                s for s in filtered
                if self.data_manager.data.get(s, {}).get('status', 'active') == self.current_filter["status"]
            ]
        
        return filtered
    
    def _debounced_filter_subjects(self):
        """Debounced filter subjects for better performance"""
        if hasattr(self, 'search_debounce_timer') and self.search_debounce_timer:
            self.after_cancel(self.search_debounce_timer)
        self.search_debounce_timer = self.after(
            PERFORMANCE_SETTINGS.get("debounce_search_ms", 300),
            self._filter_subjects
        )
    
    def _filter_subjects(self):
        """Filter subjects based on search"""
        self._update_subject_buttons()
    
    def _show_filter_dialog(self):
        """Show filter dialog"""
        filter_dialog = ctk.CTkToplevel(self)
        filter_dialog.title(self.lang.get("subject.filter", "Filter"))
        filter_dialog.geometry("350x300")
        filter_dialog.transient(self)
        filter_dialog.grab_set()
        
        # Category filter
        ctk.CTkLabel(filter_dialog, text=self.lang.get("subject.filter_by_category", "Filter by Category"),
                    font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(15, 5))
        categories = [self.lang.get("subject.all_categories", "All Categories")] + self.data_manager.get_all_categories()
        category_var = ctk.StringVar(value=self.lang.get("subject.all_categories", "All Categories"))
        if hasattr(self, 'current_filter') and self.current_filter.get("category"):
            category_var.set(self.current_filter["category"])
        category_menu = ctk.CTkOptionMenu(filter_dialog, values=categories, variable=category_var, width=300)
        category_menu.pack(pady=5)
        
        # Priority filter
        ctk.CTkLabel(filter_dialog, text=self.lang.get("subject.filter_by_priority", "Filter by Priority"),
                    font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(15, 5))
        priorities = [
            self.lang.get("subject.all_priorities", "All Priorities"),
            self.lang.get("subject.high_priority", "High Priority"),
            self.lang.get("subject.medium_priority", "Medium Priority"),
            self.lang.get("subject.low_priority", "Low Priority")
        ]
        priority_map = {
            self.lang.get("subject.all_priorities", "All Priorities"): None,
            self.lang.get("subject.high_priority", "High Priority"): "high",
            self.lang.get("subject.medium_priority", "Medium Priority"): "medium",
            self.lang.get("subject.low_priority", "Low Priority"): "low"
        }
        priority_var = ctk.StringVar(value=self.lang.get("subject.all_priorities", "All Priorities"))
        if hasattr(self, 'current_filter') and self.current_filter.get("priority"):
            reverse_map = {v: k for k, v in priority_map.items() if v}
            priority_var.set(reverse_map.get(self.current_filter["priority"], self.lang.get("subject.all_priorities", "All Priorities")))
        priority_menu = ctk.CTkOptionMenu(filter_dialog, values=priorities, variable=priority_var, width=300)
        priority_menu.pack(pady=5)
        
        # Status filter
        ctk.CTkLabel(filter_dialog, text=self.lang.get("subject.filter_by_status", "Filter by Status"),
                    font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(15, 5))
        statuses = [
            self.lang.get("subject.all_statuses", "All Statuses"),
            self.lang.get("subject.status_active", "Active"),
            self.lang.get("subject.status_completed", "Completed"),
            self.lang.get("subject.status_on_hold", "On Hold"),
            self.lang.get("subject.status_archived", "Archived")
        ]
        status_map = {
            self.lang.get("subject.all_statuses", "All Statuses"): None,
            self.lang.get("subject.status_active", "Active"): "active",
            self.lang.get("subject.status_completed", "Completed"): "completed",
            self.lang.get("subject.status_on_hold", "On Hold"): "on_hold",
            self.lang.get("subject.status_archived", "Archived"): "archived"
        }
        status_var = ctk.StringVar(value=self.lang.get("subject.all_statuses", "All Statuses"))
        if hasattr(self, 'current_filter') and self.current_filter.get("status"):
            reverse_map = {v: k for k, v in status_map.items() if v}
            status_var.set(reverse_map.get(self.current_filter["status"], self.lang.get("subject.all_statuses", "All Statuses")))
        status_menu = ctk.CTkOptionMenu(filter_dialog, values=statuses, variable=status_var, width=300)
        status_menu.pack(pady=5)
        
        def apply_filters():
            # Update filter state
            if not hasattr(self, 'current_filter'):
                self.current_filter = {"category": None, "priority": None, "status": None}
            
            selected_category = category_var.get()
            self.current_filter["category"] = None if selected_category == self.lang.get("subject.all_categories", "All Categories") else selected_category
            
            selected_priority = priority_var.get()
            self.current_filter["priority"] = priority_map.get(selected_priority)
            
            selected_status = status_var.get()
            self.current_filter["status"] = status_map.get(selected_status)
            
            filter_dialog.destroy()
            self._update_subject_buttons()
        
        buttons_frame = ctk.CTkFrame(filter_dialog, fg_color="transparent")
        buttons_frame.pack(pady=20)
        
        ctk.CTkButton(
            buttons_frame,
            text=self.lang.get("actions.apply", "Apply"),
            command=apply_filters,
            fg_color=COLORS["PRIMARY"],
            hover_color=COLORS["PRIMARY_DARK"],
            width=120,
            height=35,
            corner_radius=10,
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            buttons_frame,
            text=self.lang.get("actions.cancel", "Cancel"),
            command=filter_dialog.destroy,
            width=120,
            height=35,
            corner_radius=10,
            font=ctk.CTkFont(size=13)
        ).pack(side="left", padx=10)
    
    def _create_performance_section(self, parent, subject_name):
        """Create performance metrics section"""
        ctk.CTkLabel(parent, text=self.lang.get("analytics.performance", "Performance Metrics"), 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10, anchor="w", padx=10)
        
        performance = self.analytics.get_subject_performance(subject_name)
        
        metrics_frame = ctk.CTkFrame(parent, fg_color="transparent")
        metrics_frame.pack(fill="x", padx=10, pady=5)
        
        metrics = [
            (self.lang.get("analytics.efficiency", "Efficiency"), f"{performance['efficiency']} {self.lang.get('analytics.questions_per_hour', 'q/h')}"),
            (self.lang.get("analytics.consistency", "Consistency"), f"{performance['consistency_score']}%"),
            (self.lang.get("analytics.total_time", "Total Time"), f"{performance['total_time_hours']} {self.lang.get('analytics.hours', 'hours')}"),
            (self.lang.get("analytics.avg_session", "Avg Session"), f"{performance['average_session_time']} {self.lang.get('dashboard.minutes', 'min')}")
        ]
        
        for i, (label, value) in enumerate(metrics):
            metric_frame = ctk.CTkFrame(metrics_frame)
            metric_frame.grid(row=i//2, column=i%2, padx=5, pady=5, sticky="ew")
            metrics_frame.grid_columnconfigure(i%2, weight=1)
            
            ctk.CTkLabel(metric_frame, text=label, font=ctk.CTkFont(size=12)).pack(pady=2)
            ctk.CTkLabel(metric_frame, text=value, font=ctk.CTkFont(size=14, weight="bold"),
                        text_color=COLORS["HOVER_COLOR"]).pack(pady=2)

