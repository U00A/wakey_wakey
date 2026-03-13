"""
Statistics View component for the task scheduler application.
Displays comprehensive task statistics, charts, and analytics.
"""

import os
import sys
from datetime import datetime, date, timedelta
from typing import List, Dict, Any

import customtkinter as ctk
from tkinter import messagebox

# Imports using absolute paths (compatible with main.py's sys.path setup)
from database.manager import DatabaseManager
from ui.themes.theme_manager import get_theme_manager
from core.task_manager import TaskManager


class ModernStatistics(ctk.CTkFrame):
    """Modern statistics and analytics view with charts and metrics."""

    def __init__(self, parent, app_instance=None):
        super().__init__(parent)
        self.parent = parent
        self.app_instance = app_instance
        self.theme_manager = get_theme_manager()

        # Initialize managers
        self.task_manager = TaskManager()
        self.db = DatabaseManager()

        # State
        self.stats_period = "30"  # Days

        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Create UI components
        self.create_header()
        self.create_main_content()

        # Load initial data
        self.refresh_statistics()

    def create_header(self):
        """Create the statistics header."""
        header_frame = ctk.CTkFrame(self, height=80)
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        header_frame.grid_columnconfigure(1, weight=1)
        header_frame.grid_propagate(False)

        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text="📈 Statistics & Analytics",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=20, pady=20, sticky="w")

        # Right side controls
        controls_frame = ctk.CTkFrame(header_frame)
        controls_frame.grid(row=0, column=2, padx=20, pady=20, sticky="e")

        # Period selector
        period_label = ctk.CTkLabel(
            controls_frame,
            text="Period:",
            font=ctk.CTkFont(size=12)
        )
        period_label.pack(side="left", padx=(0, 10))

        self.period_var = ctk.StringVar(value="30 Days")
        period_options = ["7 Days", "30 Days", "90 Days", "1 Year", "All Time"]
        period_combo = ctk.CTkComboBox(
            controls_frame,
            variable=self.period_var,
            values=period_options,
            width=120,
            command=self.on_period_change
        )
        period_combo.pack(side="left", padx=5)

        # Refresh button
        refresh_btn = ctk.CTkButton(
            controls_frame,
            text="🔄 Refresh",
            command=self.refresh_statistics,
            width=100
        )
        refresh_btn.pack(side="left", padx=5)

        # Export button
        export_btn = ctk.CTkButton(
            controls_frame,
            text="📊 Export",
            command=self.export_statistics,
            width=100
        )
        export_btn.pack(side="left", padx=5)

    def create_main_content(self):
        """Create the main statistics content area."""
        content_frame = ctk.CTkScrollableFrame(self)
        content_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=1)

        # Overview metrics
        self.create_overview_metrics(content_frame)

        # Charts section
        self.create_charts_section(content_frame)

        # Task breakdown
        self.create_breakdown_section(content_frame)

        # Productivity insights
        self.create_insights_section(content_frame)

    def create_overview_metrics(self, parent):
        """Create overview metrics cards."""
        metrics_frame = ctk.CTkFrame(parent)
        metrics_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        metrics_frame.grid_columnconfigure(0, weight=1)
        metrics_frame.grid_columnconfigure(1, weight=1)
        metrics_frame.grid_columnconfigure(2, weight=1)
        metrics_frame.grid_columnconfigure(3, weight=1)

        # Metrics header
        header_label = ctk.CTkLabel(
            metrics_frame,
            text="📊 Key Metrics",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        header_label.grid(row=0, column=0, columnspan=4, padx=20, pady=(15, 10), sticky="w")

        # Total Tasks Card
        total_card = self.create_metric_card(
            metrics_frame, "📋 Total Tasks", "0", 
            self.theme_manager.get_color("primary"), 0, 0
        )
        self.total_tasks_label = total_card  # Store the card itself

        # Completed Tasks Card
        completed_card = self.create_metric_card(
            metrics_frame, "✅ Completed", "0",
            self.theme_manager.get_color("priority_low"), 0, 1
        )
        self.completed_label = completed_card

        # Completion Rate Card
        completion_rate_card = self.create_metric_card(
            metrics_frame, "📊 Completion Rate", "0%",
            self.theme_manager.get_color("accent"), 0, 2
        )
        self.completion_rate_label = completion_rate_card

        # Average Completion Time Card
        avg_completion_time_card = self.create_metric_card(
            metrics_frame, "⏱️ Avg. Time", "0 days",
            self.theme_manager.get_color("priority_medium"), 0, 3
        )
        self.avg_completion_time_label = avg_completion_time_card

    def create_metric_card(self, parent, title: str, value: str, color: str, row: int, col: int):
        """Create a single metric card."""
        card = ctk.CTkFrame(parent)
        card.grid(row=row+1, column=col, padx=5, pady=10, sticky="ew")

        # Card content with color accent
        content_frame = ctk.CTkFrame(card, fg_color=color)
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Value
        value_label = ctk.CTkLabel(
            content_frame,
            text=value,
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color="white"
        )
        value_label.pack(pady=(15, 5))

        # Title
        title_label = ctk.CTkLabel(
            content_frame,
            text=title,
            font=ctk.CTkFont(size=12),
            text_color="white"
        )
        title_label.pack(pady=(0, 15))

        # Store reference to value label for updates
        card.value_label = value_label

        return card

    def create_charts_section(self, parent):
        """Create charts section."""
        charts_frame = ctk.CTkFrame(parent)
        charts_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        charts_frame.grid_columnconfigure(0, weight=1)
        charts_frame.grid_columnconfigure(1, weight=1)

        # Charts header
        header_label = ctk.CTkLabel(
            charts_frame,
            text="📊 Visual Analytics",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        header_label.grid(row=0, column=0, columnspan=2, padx=20, pady=(15, 10), sticky="w")

        # Productivity trend chart
        self.productivity_chart = self.create_productivity_chart(charts_frame)
        self.productivity_chart.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # Priority distribution chart
        self.priority_chart = self.create_priority_distribution_chart(charts_frame)
        self.priority_chart.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

    def create_productivity_chart(self, parent):
        """Create productivity trend chart (simple text-based representation)."""
        chart_frame = ctk.CTkFrame(parent)
        chart_frame.grid_columnconfigure(0, weight=1)

        # Chart title
        title_label = ctk.CTkLabel(
            chart_frame,
            text="📈 Productivity Trend",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=15, pady=(15, 10), sticky="w")

        # Chart container (placeholder for now - would need matplotlib or similar for real charts)
        # Chart container
        self.productivity_display = ctk.CTkFrame(chart_frame, fg_color="transparent")
        self.productivity_display.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="ew")
        self.productivity_display.grid_columnconfigure(0, weight=1)

        return chart_frame

    def create_priority_distribution_chart(self, parent):
        """Create priority distribution chart."""
        chart_frame = ctk.CTkFrame(parent)
        chart_frame.grid_columnconfigure(0, weight=1)

        # Chart title
        title_label = ctk.CTkLabel(
            chart_frame,
            text="🎯 Priority Distribution",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=15, pady=(15, 10), sticky="w")

        # Distribution display
        self.priority_display_frame = ctk.CTkFrame(chart_frame)
        self.priority_display_frame.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="ew")

        return chart_frame

    def create_breakdown_section(self, parent):
        """Create task breakdown section."""
        breakdown_frame = ctk.CTkFrame(parent)
        breakdown_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
        breakdown_frame.grid_columnconfigure(0, weight=1)

        # Section header
        header_label = ctk.CTkLabel(
            breakdown_frame,
            text="📁 Category Breakdown",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        header_label.grid(row=0, column=0, padx=20, pady=(15, 10), sticky="w")

        # Category breakdown list
        self.category_breakdown_frame = ctk.CTkScrollableFrame(breakdown_frame, height=200)
        self.category_breakdown_frame.grid(row=1, column=0, padx=20, pady=(0, 15), sticky="ew")
        self.category_breakdown_frame.grid_columnconfigure(0, weight=1)

    def create_insights_section(self, parent):
        """Create productivity insights section."""
        insights_frame = ctk.CTkFrame(parent)
        insights_frame.grid(row=2, column=1, sticky="nsew", padx=10, pady=10)
        insights_frame.grid_columnconfigure(0, weight=1)

        # Section header
        header_label = ctk.CTkLabel(
            insights_frame,
            text="💡 Productivity Insights",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        header_label.grid(row=0, column=0, padx=20, pady=(15, 10), sticky="w")

        # Insights display
        self.insights_display = ctk.CTkTextbox(insights_frame, height=200)
        self.insights_display.grid(row=1, column=0, padx=20, pady=(0, 15), sticky="ew")

    def refresh_statistics(self):
        """Refresh all statistics."""
        try:
            # Get period in days
            period_text = self.period_var.get()
            days = {
                "7 Days": 7,
                "30 Days": 30,
                "90 Days": 90,
                "1 Year": 365,
                "All Time": 10000
            }.get(period_text, 30)

            # Get statistics
            stats = self.task_manager.get_task_statistics(days=days)
            trends = self.task_manager.get_productivity_trends(days=min(days, 90))
            category_dist = self.task_manager.get_category_distribution()
            priority_dist = self.task_manager.get_priority_distribution()

            # Update metrics
            self.update_metrics(stats)

            # Update charts
            self.update_productivity_chart(trends)
            self.update_priority_chart(priority_dist)

            # Update breakdowns
            self.update_category_breakdown(category_dist)

            # Update insights
            self.update_insights(stats, trends)

            if self.app_instance:
                self.app_instance.set_status("Statistics refreshed")

        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Error refreshing statistics: {e!r}")
            if self.app_instance:
                self.app_instance.set_status("Error loading statistics")

    def update_metrics(self, stats):
        """Update metric cards."""
        self.total_tasks_label.value_label.configure(text=str(stats.get('total_created', 0)))
        self.completed_label.value_label.configure(text=str(stats.get('total_completed', 0)))
        self.completion_rate_label.value_label.configure(text=f"{stats.get('completion_rate', 0):.1f}%")
        
        # Average completion time (simplified)
        avg_time = stats.get('avg_completion_time_hours', 0)
        if avg_time >= 24:
            time_str = f"{avg_time / 24:.1f} days"
        else:
            time_str = f"{avg_time:.1f} hours"
        self.avg_completion_time_label.value_label.configure(text=time_str)


    def update_productivity_chart(self, trends):
        """Update productivity trend chart."""
        # Clear existing charts
        for widget in self.productivity_display.winfo_children():
            widget.destroy()
        
        # trends is the dictionary returned by get_productivity_trends
        daily_stats = trends.get('daily_stats', {})
        if not daily_stats:
            no_data_label = ctk.CTkLabel(
                self.productivity_display,
                text="No data available for this period",
                text_color=self.theme_manager.get_color("text_secondary")
            )
            no_data_label.place(relx=0.5, rely=0.5, anchor="center")
            return

        # Sort by date
        sorted_dates = sorted(daily_stats.keys())
        # Limit to last 7-14 data points if there are too many to fit nicely
        if len(sorted_dates) > 10:
             display_dates = sorted_dates[-10:]
        else:
             display_dates = sorted_dates

        # Find max value for scaling
        max_val = max([daily_stats[d] for d in display_dates]) if display_dates else 0
        if max_val == 0: max_val = 1
        
        # Create bars
        for i, date_str in enumerate(display_dates):
            completed = daily_stats[date_str]
            
            # Column frame
            col_frame = ctk.CTkFrame(self.productivity_display, fg_color="transparent")
            col_frame.grid(row=0, column=i, padx=5, pady=0, sticky="nsew")
            self.productivity_display.grid_columnconfigure(i, weight=1)
            self.productivity_display.grid_rowconfigure(0, weight=1)
            
            # Bar container (for bottom alignment)
            bar_container = ctk.CTkFrame(col_frame, fg_color="transparent")
            bar_container.pack(side="bottom", fill="x", expand=True)

            # Value label
            if completed > 0:
                val_label = ctk.CTkLabel(
                    bar_container,
                    text=str(completed),
                    font=ctk.CTkFont(size=10)
                )
                val_label.pack(side="top", pady=(0, 2))
            
            # Bar
            # Calculate height percentage
            height_pct = completed / max_val
            # Min height 2px to show 0 if needed (or just hide)
            
            bar_color = self.theme_manager.get_color("primary") if completed > 0 else self.theme_manager.get_color("surface_variant")
            
            bar = ctk.CTkFrame(
                bar_container, 
                height=max(4, int(100 * height_pct)), # Dynamic height logic slightly tricky with pack, better to use fixed height container and relative size or just fixed height pixels. 
                # Let's use relative height inside a fixed height container if possible, or just fixed pixels mapped to a max height of say 100px.
                fg_color=bar_color,
                corner_radius=4
            )
            # Using fixed pixel mapping for simplicity and robustness in grid
            scaled_height = int(120 * height_pct)
            if scaled_height < 4: scaled_height = 4
            
            bar.configure(height=scaled_height)
            bar.pack(side="top", fill="x")

            # Date label (short format)
            try:
                dt = datetime.fromisoformat(date_str)
                date_fmt = dt.strftime("%m/%d")
            except:
                date_fmt = date_str
            
            date_label = ctk.CTkLabel(
                col_frame, 
                text=date_fmt,
                font=ctk.CTkFont(size=10),
                text_color=self.theme_manager.get_color("text_secondary")
            )
            date_label.pack(side="bottom", pady=(5, 0))

    def update_priority_chart(self, priority_dist):
        """Update priority distribution chart."""
        # Clear existing display
        for widget in self.priority_display_frame.winfo_children():
            widget.destroy()

        total = sum(priority_dist.values()) if priority_dist else 1
        
        for i, (priority, count) in enumerate(priority_dist.items()):
            # Priority row
            row_frame = ctk.CTkFrame(self.priority_display_frame)
            row_frame.grid(row=i, column=0, padx=10, pady=5, sticky="ew")
            row_frame.grid_columnconfigure(1, weight=1)

            # Priority color indicator
            color = self.theme_manager.get_priority_color(priority)
            color_label = ctk.CTkLabel(
                row_frame,
                text="●",
                font=ctk.CTkFont(size=16),
                text_color=color
            )
            color_label.grid(row=0, column=0, padx=10, pady=5)

            # Priority name
            name_label = ctk.CTkLabel(
                row_frame,
                text=priority,
                font=ctk.CTkFont(size=12),
                anchor="w"
            )
            name_label.grid(row=0, column=1, padx=10, pady=5, sticky="w")

            # Count and percentage
            percentage = (count / total) * 100 if total > 0 else 0
            count_label = ctk.CTkLabel(
                row_frame,
                text=f"{count} ({percentage:.1f}%)",
                font=ctk.CTkFont(size=12),
                text_color=self.theme_manager.get_color("text_secondary")
            )
            count_label.grid(row=0, column=2, padx=10, pady=5)

            # Progress bar
            progress_frame = ctk.CTkFrame(row_frame, height=10, fg_color=self.theme_manager.get_color("surface"))
            progress_frame.grid(row=1, column=1, columnspan=2, padx=10, pady=(0, 5), sticky="ew")
            
            progress_bar = ctk.CTkFrame(progress_frame, height=10, fg_color=color)
            progress_bar.place(relx=0, rely=0, relwidth=percentage/100, relheight=1)

    def update_category_breakdown(self, category_dist):
        """Update category breakdown."""
        # Clear existing display
        for widget in self.category_breakdown_frame.winfo_children():
            widget.destroy()

        if not category_dist:
            no_data_label = ctk.CTkLabel(
                self.category_breakdown_frame,
                text="No category data available",
                font=ctk.CTkFont(size=12, slant="italic"),
                text_color=self.theme_manager.get_color("text_secondary")
            )
            no_data_label.grid(row=0, column=0, pady=20)
            return

        for i, (category, count) in enumerate(category_dist.items()):
            cat_frame = ctk.CTkFrame(self.category_breakdown_frame)
            cat_frame.grid(row=i, column=0, padx=5, pady=3, sticky="ew")
            cat_frame.grid_columnconfigure(1, weight=1)

            # Category icon
            icon_label = ctk.CTkLabel(
                cat_frame,
                text="📁",
                font=ctk.CTkFont(size=14)
            )
            icon_label.grid(row=0, column=0, padx=10, pady=8)

            # Category name
            name_label = ctk.CTkLabel(
                cat_frame,
                text=category or "Uncategorized",
                font=ctk.CTkFont(size=12),
                anchor="w"
            )
            name_label.grid(row=0, column=1, padx=10, pady=8, sticky="w")

            # Count badge
            count_badge = ctk.CTkLabel(
                cat_frame,
                text=str(count),
                font=ctk.CTkFont(size=12, weight="bold"),
                fg_color=self.theme_manager.get_color("surface_variant"),
                width=40,
                height=25,
                corner_radius=12
            )
            count_badge.grid(row=0, column=2, padx=10, pady=8)

    def update_insights(self, stats, trends):
        """Update productivity insights."""
        self.insights_display.delete("1.0", "end")
        
        insights_text = "Productivity Insights:\n\n"
        
        # Completion rate insight
        completion_rate = stats.get('completion_rate', 0)
        if completion_rate >= 80:
            insights_text += "✅ Excellent! You're completing most of your tasks.\n\n"
        elif completion_rate >= 50:
            insights_text += "👍 Good progress! Try to improve your completion rate.\n\n"
        else:
            insights_text += "💪 Keep going! Focus on completing your pending tasks.\n\n"
        
        # Overdue tasks insight
        overdue = stats.get('overdue_count', 0)
        if overdue > 0:
            insights_text += f"⚠️ You have {overdue} overdue task(s). Consider reviewing them.\n\n"
        else:
            insights_text += "🎉 Great! No overdue tasks.\n\n"
        
        # Pending tasks insight
        pending = stats.get('pending', 0)
        if pending > 10:
            insights_text += f"📋 You have {pending} pending tasks. Consider prioritizing.\n\n"
        elif pending > 0:
            insights_text += f"📋 {pending} pending task(s) to complete.\n\n"
        
        # Trend insight
        # Trend insight
        weekly_avgs = trends.get('weekly_averages', [])
        if weekly_avgs and len(weekly_avgs) >= 2:
            recent_avg = weekly_avgs[-1]
            previous_avg = weekly_avgs[-2]
            
            if recent_avg > previous_avg:
                insights_text += "📈 Your productivity is trending upward!\n\n"
            elif recent_avg < previous_avg:
                insights_text += "📉 Your productivity has slowed. Stay focused!\n\n"
            else:
                insights_text += "➡️ Your productivity is steady.\n\n"
        
        # Most productive day
        try:
            most_productive = self.task_manager.get_most_productive_day()
            if most_productive:
                insights_text += f"🌟 Your most productive day: {most_productive}\n"
        except:
            pass
        
        self.insights_display.insert("1.0", insights_text)
        self.insights_display.configure(state="disabled")

    def on_period_change(self, choice):
        """Handle period selection change."""
        self.refresh_statistics()

    def export_statistics(self):
        """Export statistics to file."""
        try:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"statistics_export_{timestamp}.txt"
            
            # Get current statistics
            period_text = self.period_var.get()
            days = {
                "7 Days": 7,
                "30 Days": 30,
                "90 Days": 90,
                "1 Year": 365,
                "All Time": 10000
            }.get(period_text, 30)
            
            stats = self.task_manager.get_task_statistics(days=days)
            category_dist = self.task_manager.get_category_distribution()
            priority_dist = self.task_manager.get_priority_distribution()
            
            # Create export content
            content = f"""Task Scheduler Pro - Statistics Export
Period: {period_text}
Export Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

=== OVERVIEW METRICS ===
Total Tasks: {stats.get('total_created', 0)}
Completed Tasks: {stats.get('total_completed', 0)}
Pending Tasks: {stats.get('pending', 0)}
Cancelled Tasks: {stats.get('cancelled', 0)}
Overdue Tasks: {stats.get('overdue_count', 0)}
Completion Rate: {stats.get('completion_rate', 0):.2f}%

=== PRIORITY DISTRIBUTION ===
"""
            for priority, count in priority_dist.items():
                content += f"{priority}: {count}\n"
            
            content += "\n=== CATEGORY BREAKDOWN ===\n"
            for category, count in category_dist.items():
                content += f"{category or 'Uncategorized'}: {count}\n"
            
            # Write to file
            export_path = f"data/exports/{filename}"
            os.makedirs("data/exports", exist_ok=True)
            
            with open(export_path, 'w') as f:
                f.write(content)
            
            if self.app_instance:
                self.app_instance.show_info(f"Statistics exported to:\n{export_path}")
        
        except Exception as e:
            if self.app_instance:
                self.app_instance.show_error(f"Error exporting statistics: {str(e)}")
