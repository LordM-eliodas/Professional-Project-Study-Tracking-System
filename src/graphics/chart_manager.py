"""
Chart and Graph Management Module
"""

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for better performance
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import warnings
import customtkinter as ctk
from ..config.constants import COLORS, GRAPH_SETTINGS, PERFORMANCE_SETTINGS

# Filter matplotlib warnings
warnings.filterwarnings('ignore', category=UserWarning, module='matplotlib')
plt.rcParams['font.family'] = GRAPH_SETTINGS['font_family']
plt.rcParams['axes.unicode_minus'] = False

class ChartManager:
    """Manages chart creation and display with caching for performance"""
    
    def __init__(self, language_manager):
        self.lang = language_manager
        self.colors = COLORS
        self._chart_cache = {}  # Cache for charts
        self._cache_max_size = PERFORMANCE_SETTINGS.get("max_chart_cache_size", 10)
    
    def create_general_progress_chart(self, master_frame, data_manager, theme_mode='dark'):
        """Create general progress pie chart with caching"""
        # Clear existing widgets
        for widget in master_frame.winfo_children():
            widget.destroy()
        
        stats = data_manager.get_statistics()
        total_solved = stats['total_solved']
        total_target = stats['total_target']
        
        # Check cache
        cache_key = f"general_{total_solved}_{total_target}_{theme_mode}"
        if PERFORMANCE_SETTINGS.get("cache_charts", True) and cache_key in self._chart_cache:
            # Use cached chart
            cached_fig = self._chart_cache[cache_key]
            canvas = FigureCanvasTkAgg(cached_fig, master=master_frame)
            canvas_widget = canvas.get_tk_widget()
            canvas_widget.pack(fill='both', expand=True, padx=5, pady=5)
            canvas.draw()
            return
        
        if total_target <= 0:
            label = ctk.CTkLabel(master_frame, 
                                text=self.lang.get("graph.general_progress", "No data"),
                                font=ctk.CTkFont(size=14))
            label.place(relx=0.5, rely=0.5, anchor="center")
            return
        
        remaining = max(0, total_target - total_solved)
        ratios = [total_solved, remaining]
        
        # Determine text color based on theme
        text_color = 'black' if theme_mode == 'light' else 'white'
        bg_color = '#ffffff' if theme_mode == 'light' else '#1e1e1e'
        
        # Enhanced figure with better styling
        fig = plt.Figure(figsize=(6.5, 4.5), 
                        dpi=GRAPH_SETTINGS.get('figure_dpi', 100))
        ax = fig.add_subplot(111)
        
        # Modern title with better spacing
        title = self.lang.get("graph.general_progress", "General Progress")
        ax.set_title(title, color=text_color, fontsize=17, weight='bold', pad=22)
        
        solved_label = self.lang.get("graph.solved", "Solved")
        remaining_label = self.lang.get("graph.remaining", "Remaining")
        
        # Enhanced pie chart with better colors and styling
        colors_list = [self.colors['HOVER_COLOR'], self.colors['JAPAN_BLUE']]
        explode = (0.05, 0)  # Slight explode for emphasis
        
        wedges, texts, autotexts = ax.pie(
            ratios,
            labels=[solved_label, remaining_label],
            autopct=lambda p: f'{p:.1f}%\n({int(p * total_target / 100):,})',
            startangle=90,
            colors=colors_list,
            explode=explode,
            shadow=True,
            textprops={'color': text_color, 'fontsize': 11, 'weight': 'bold'},
            wedgeprops={'edgecolor': bg_color, 'linewidth': 2}
        )
        
        # Enhanced donut chart effect with better proportions
        centre_circle = plt.Circle((0, 0), 0.65, fc=bg_color, ec=bg_color, linewidth=0)
        fig.gca().add_artist(centre_circle)
        
        # Center text with progress percentage
        progress_pct = (total_solved / total_target * 100) if total_target > 0 else 0
        ax.text(0, 0, f'{progress_pct:.1f}%', 
               ha='center', va='center', 
               fontsize=26, weight='bold', color=text_color)
        
        # Enhanced autotext styling
        for text in autotexts:
            text.set_color(text_color)
            text.set_fontsize(10)
            text.set_weight('bold')
        
        # Modern legend with better positioning
        legend_labels = [
            f'{solved_label}: {total_solved:,}',
            f'{remaining_label}: {remaining:,}'
        ]
        ax.legend(wedges, legend_labels, loc="center left", 
                 bbox_to_anchor=(1.1, 0.5),
                 facecolor='none', 
                 edgecolor=text_color, 
                 labelcolor=text_color,
                 fontsize=11,
                 framealpha=0.8)
        
        fig.patch.set_facecolor(bg_color)
        ax.set_facecolor(bg_color)
        fig.tight_layout()
        
        # Cache the figure (without canvas) for performance
        if PERFORMANCE_SETTINGS.get("cache_charts", True):
            if len(self._chart_cache) >= self._cache_max_size:
                # Remove oldest entry
                oldest_key = next(iter(self._chart_cache))
                del self._chart_cache[oldest_key]
            self._chart_cache[cache_key] = fig
        
        canvas = FigureCanvasTkAgg(fig, master=master_frame)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill='both', expand=True, padx=5, pady=5)
        canvas.draw()
    
    def create_subject_comparison_chart(self, master_frame, data_manager, current_subject, theme_mode='dark'):
        """Create subject comparison bar chart"""
        for widget in master_frame.winfo_children():
            widget.destroy()
        
        theme_mode_lower = theme_mode.lower()
        axis_color = 'black' if theme_mode_lower == 'light' or (theme_mode_lower == 'system') else 'white'
        
        # Modern style with better colors (fallback to default if seaborn not available)
        try:
            plt.style.use('seaborn-v0_8-darkgrid' if theme_mode == 'dark' else 'seaborn-v0_8-whitegrid')
        except:
            plt.style.use('default')
        plt.rcParams['axes.facecolor'] = 'none'
        plt.rcParams['figure.facecolor'] = 'none'
        
        # Enhanced figure size
        fig = plt.Figure(figsize=(8.5, 5.5),
                        dpi=GRAPH_SETTINGS.get('figure_dpi', 100))
        ax = fig.add_subplot(111)
        
        subjects = list(data_manager.data.keys())
        solved_questions = [data_manager.data[s].get('cozulen_soru', 0) for s in subjects]
        target_questions = [data_manager.data[s].get('hedef_soru', 1) for s in subjects]
        
        bar_width = 0.4
        indices = range(len(subjects))
        
        # Enhanced bars with gradient effect simulation and shadows
        bars1 = ax.bar([i - bar_width/2 for i in indices], solved_questions, bar_width,
               label=self.lang.get("graph.solved_questions", "Solved Questions"),
               color=self.colors['HOVER_COLOR'],
               edgecolor=axis_color,
               linewidth=1.5,
               alpha=0.9)
        
        bars2 = ax.bar([i + bar_width/2 for i in indices], target_questions, bar_width,
               label=self.lang.get("graph.target_questions", "Target Questions"),
               color=self.colors['PRIMARY'],
               edgecolor=axis_color,
               linewidth=1.5,
               alpha=0.7)
        
        # Highlight current subject with different color
        try:
            current_index = subjects.index(current_subject)
            bars1[current_index].set_color(self.colors['ACCENT_2'])
            bars1[current_index].set_alpha(1.0)
            bars1[current_index].set_edgecolor(self.colors['PRIMARY'])
            bars1[current_index].set_linewidth(2.5)
        except ValueError:
            pass
        
        # Enhanced axis settings
        ax.set_xticks(indices)
        ax.set_xticklabels(subjects, rotation=45, ha="right", color=axis_color, fontsize=10, weight='bold')
        
        # Modern title
        title = self.lang.translate("graph.subject_comparison", subject=current_subject)
        ax.set_title(title, color=axis_color, fontsize=17, weight='bold', pad=18)
        ax.set_ylabel(self.lang.get("subject.questions", "Questions"), color=axis_color, fontsize=13, weight='bold')
        
        # Grid for better readability
        ax.grid(True, alpha=0.3, linestyle='--', color=axis_color)
        ax.set_axisbelow(True)
        
        # Enhanced tick parameters
        ax.tick_params(axis='y', colors=axis_color, labelsize=10)
        ax.tick_params(axis='x', colors=axis_color, labelsize=9)
        
        # Modern legend
        ax.legend(facecolor='none', 
                 edgecolor=axis_color, 
                 labelcolor=axis_color, 
                 fontsize=11,
                 framealpha=0.9,
                 loc='upper left')
        
        # Enhanced spines
        for spine in ax.spines.values():
            spine.set_color(axis_color)
            spine.set_linewidth(1.5)
        
        # Add value labels on bars
        for i, (bar1, bar2) in enumerate(zip(bars1, bars2)):
            height1 = bar1.get_height()
            height2 = bar2.get_height()
            if height1 > 0:
                ax.text(bar1.get_x() + bar1.get_width()/2., height1,
                       f'{int(height1)}',
                       ha='center', va='bottom', 
                       color=axis_color, fontsize=8, weight='bold')
            if height2 > 0:
                ax.text(bar2.get_x() + bar2.get_width()/2., height2,
                       f'{int(height2)}',
                       ha='center', va='bottom', 
                       color=axis_color, fontsize=8, weight='bold')
        
        fig.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, master=master_frame)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill='both', expand=True, padx=5, pady=5)
        canvas.draw()

