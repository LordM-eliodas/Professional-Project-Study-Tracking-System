"""
Dashboard Widget Component - Ultra Modern Design
"""

import customtkinter as ctk
from ...config.constants import COLORS

class DashboardWidget(ctk.CTkFrame):
    """Ultra modern dashboard widget with enhanced visuals"""
    
    def __init__(self, master, data_manager, time_tracker, analytics, lang_manager, **kwargs):
        super().__init__(master, **kwargs)
        self.data_manager = data_manager
        self.time_tracker = time_tracker
        self.analytics = analytics
        self.lang = lang_manager
        
        # Modern card background colors
        self.card_bg_light = COLORS.get("CARD_LIGHT", "#f8fafc")
        self.card_bg_dark = COLORS.get("CARD_DARK", "#1e293b")
        
        self.configure(
            corner_radius=18,
            fg_color=(self.card_bg_light, self.card_bg_dark),
            border_width=0
        )
        self.create_widgets()
    
    def create_widgets(self):
        """Create ultra modern dashboard widgets"""
        # Title with gradient effect simulation
        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.pack(fill="x", padx=28, pady=(28, 18))
        
        title = ctk.CTkLabel(
            title_frame,
            text=self.lang.get("dashboard.title", "Dashboard"),
            font=ctk.CTkFont(size=30, weight="bold"),
            text_color=(COLORS["PRIMARY"], COLORS["PRIMARY_LIGHT"])
        )
        title.pack(side="left")
        
        # Stats grid with ultra modern cards
        stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        stats_frame.pack(fill="both", expand=True, padx=28, pady=18)
        
        # Configure grid - 3 columns
        for i in range(3):
            stats_frame.grid_columnconfigure(i, weight=1, uniform="equal")
        
        # Today's stats
        today_stats = self.time_tracker.get_today_stats()
        self.create_ultra_modern_card(
            stats_frame,
            self.lang.get("dashboard.today_time", "Today's Time"),
            f"{int(today_stats['total_time_minutes'])} {self.lang.get('dashboard.minutes', 'min')}",
            "⏱️",
            row=0,
            col=0,
            gradient_colors=(COLORS["GRADIENT_3_START"], COLORS["GRADIENT_3_END"]),
            accent_color=COLORS["INFO"]
        )
        
        self.create_ultra_modern_card(
            stats_frame,
            self.lang.get("dashboard.today_questions", "Today's Questions"),
            f"{today_stats['total_questions']}",
            "📚",
            row=0,
            col=1,
            gradient_colors=(COLORS["GRADIENT_2_START"], COLORS["GRADIENT_2_END"]),
            accent_color=COLORS["ERROR"]
        )
        
        # Productivity score
        productivity = self.analytics.get_productivity_score()
        self.create_ultra_modern_card(
            stats_frame,
            self.lang.get("dashboard.productivity", "Productivity"),
            f"{productivity}%",
            "📈",
            row=0,
            col=2,
            gradient_colors=(COLORS["GRADIENT_1_START"], COLORS["GRADIENT_1_END"]),
            accent_color=COLORS["HOVER_COLOR"]
        )
        
        # Study streak
        streak = self.analytics.get_study_streak()
        streak_text = f"{streak} {self.lang.get('dashboard.days', 'days')}"
        self.create_ultra_modern_card(
            stats_frame,
            self.lang.get("dashboard.streak", "Study Streak"),
            streak_text,
            "🔥",
            row=1,
            col=0,
            gradient_colors=("#ff6b6b", "#ee5a6f"),
            accent_color=COLORS["WARNING"]
        )
        
        # Overall progress
        stats = self.data_manager.get_statistics()
        progress_text = f"{stats['progress']:.1f}%"
        self.create_ultra_modern_card(
            stats_frame,
            self.lang.get("dashboard.overall_progress", "Overall Progress"),
            progress_text,
            "🎯",
            row=1,
            col=1,
            gradient_colors=("#51cf66", "#40c057"),
            accent_color=COLORS["SUCCESS"]
        )
        
        # Completed topics
        topics_text = f"{stats['completed_topics']}/{stats['total_topics']}"
        self.create_ultra_modern_card(
            stats_frame,
            self.lang.get("dashboard.completed_topics", "Completed Topics"),
            topics_text,
            "✅",
            row=1,
            col=2,
            gradient_colors=(COLORS["SECONDARY"], "#9b59b6"),
            accent_color="#9b59b6"
        )
    
    def create_ultra_modern_card(self, parent, title, value, emoji, row, col, gradient_colors, accent_color):
        """Create ultra modern statistics card with enhanced visuals and shadows"""
        # Main card frame with enhanced modern styling
        card = ctk.CTkFrame(
            parent,
            corner_radius=20,
            fg_color=(self.card_bg_light, self.card_bg_dark),
            border_width=2,
            border_color=(accent_color, accent_color)  # Colored border for emphasis
        )
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        
        # Enhanced inner padding for depth effect
        inner_padding = ctk.CTkFrame(card, fg_color="transparent")
        inner_padding.pack(fill="both", expand=True, padx=4, pady=4)
        
        # Inner frame for content with better spacing
        inner_frame = ctk.CTkFrame(inner_padding, fg_color="transparent")
        inner_frame.pack(fill="both", expand=True, padx=22, pady=22)
        
        # Top section with emoji and value - enhanced layout
        top_section = ctk.CTkFrame(inner_frame, fg_color="transparent")
        top_section.pack(fill="x", pady=(0, 18))
        
        # Enhanced emoji with background circle effect
        # Use subtle background colors (light/dark variants)
        bg_light = COLORS.get("CARD_LIGHT", "#f8f9fa")
        bg_dark = COLORS.get("CARD_DARK", "#2d2d2d")
        emoji_container = ctk.CTkFrame(
            top_section, 
            fg_color=(bg_light, bg_dark),  # Subtle background
            corner_radius=50,
            width=68,
            height=68,
            border_width=2,
            border_color=(accent_color, accent_color)
        )
        emoji_container.pack(side="left")
        emoji_container.pack_propagate(False)
        
        emoji_label = ctk.CTkLabel(
            emoji_container,
            text=emoji,
            font=ctk.CTkFont(size=40)
        )
        emoji_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Value with enhanced styling
        value_frame = ctk.CTkFrame(top_section, fg_color="transparent")
        value_frame.pack(side="right", fill="x", expand=True)
        value_label = ctk.CTkLabel(
            value_frame,
            text=value,
            font=ctk.CTkFont(size=30, weight="bold"),
            text_color=accent_color,
            anchor="e"
        )
        value_label.pack(side="right")
        
        # Enhanced divider with gradient effect simulation
        divider_container = ctk.CTkFrame(inner_frame, fg_color="transparent", height=3)
        divider_container.pack(fill="x", pady=(0, 15))
        
        divider = ctk.CTkFrame(
            divider_container,
            height=3,
            fg_color=(accent_color, accent_color),
            corner_radius=2
        )
        divider.pack(fill="x")
        
        # Enhanced title with better typography
        title_label = ctk.CTkLabel(
            inner_frame,
            text=title,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=(COLORS.get("TEXT_SECONDARY", "#94a3b8"), "#cbd5e1"),
            anchor="w"
        )
        title_label.pack(fill="x")
    
    def refresh(self):
        """Refresh dashboard data"""
        for widget in self.winfo_children():
            widget.destroy()
        self.create_widgets()
