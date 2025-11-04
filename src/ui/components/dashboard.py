"""
Modern Dashboard component for the task scheduler application.
Displays overview of tasks, statistics, and quick actions with modern UI elements.
"""

import os
import sys
from datetime import datetime, date, timedelta
from typing import List, Dict, Any

import customtkinter as ctk

# Add parent directories to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ...database.manager import DatabaseManager
from ..themes.theme_manager import get_theme_manager
from ...utils.helpers import format_datetime, calculate_task_statistics
from ...core.task_manager import TaskManager


class ModernDashboard(ctk.CTkFrame):
    """Modern dashboard component with statistics and quick actions."""

    def __init__(self, parent, app_instance=None):
        super().__init__(parent)
        self.parent = parent
        self.app_instance = app_instance
        self.theme_manager = get_theme_manager()

        # Initialize data managers
        self.task_manager = TaskManager()
        self.db = DatabaseManager()

        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Create UI components
        self.create_header()
        self.create_main_content()
        self.create_quick_actions()

        # Load initial data
        self.refresh_data()

        # Set up auto-refresh
        self.schedule_refresh()

    def create_header(self):
        """Create the dashboard header with title and theme toggle."""
        header_frame = ctk.CTkFrame(self, height=80)
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        header_frame.grid_columnconfigure(1, weight=1)
        header_frame.grid_propagate(False)

        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text="📊 Dashboard",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=20, pady=20, sticky="w")

        # Right side controls
        controls_frame = ctk.CTkFrame(header_frame)
        controls_frame.grid(row=0, column=2, padx=20, pady=20, sticky="e")

        # Refresh button
        refresh_btn = ctk.CTkButton(
            controls_frame,
            text="🔄 Refresh",
            command=self.refresh_data,
            width=100
        )
        refresh_btn.pack(side="left", padx=5)

        # New task button
        new_task_btn = ctk.CTkButton(
            controls_frame,
            text="➕ New Task",
            command=self.new_task,
            width=120,
            fg_color=self.theme_manager.get_color("primary")
        )
        new_task_btn.pack(side="left", padx=5)

    def create_main_content(self):
        """Create the main dashboard content with statistics cards."""
        content_frame = ctk.CTkFrame(self)
        content_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        content_frame.grid_columnconfigure(1, weight=1)
        content_frame.grid_rowconfigure(0, weight=1)

        # Left side - Statistics cards
        left_frame = ctk.CTkFrame(content_frame)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=10)
        left_frame.grid_columnconfigure(0, weight=1)

        # Statistics cards
        self.create_stats_cards(left_frame)

        # Right side - Recent tasks and upcoming
        right_frame = ctk.CTkFrame(content_frame)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=10)
        right_frame.grid_columnconfigure(0, weight=1)
        right_frame.grid_rowconfigure(1, weight=1)

        # Recent tasks
        self.create_recent_tasks_section(right_frame)

        # Upcoming tasks
        self.create_upcoming_tasks_section(right_frame)

    def create_stats_cards(self, parent):
        """Create statistics cards showing task overview."""
        stats_title = ctk.CTkLabel(
            parent,
            text="📈 Task Statistics",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        stats_title.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        # Create statistics cards container
        cards_container = ctk.CTkFrame(parent)
        cards_container.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        cards_container.grid_columnconfigure(1, weight=1)

        # Total Tasks Card
        total_card = self.create_stat_card(
            cards_container,
            "📋 Total Tasks",
            "0",
            self.theme_manager.get_color("primary"),
            row=0, column=0
        )
        self.total_tasks_label = total_card.children[0].children[0]  # Get the label

        # Completed Tasks Card
        completed_card = self.create_stat_card(
            cards_container,
            "✅ Completed",
            "0",
            self.theme_manager.get_color("priority_low"),
            row=0, column=2
        )
        self.completed_tasks_label = completed_card.children[0].children[0]

        # Pending Tasks Card
        pending_card = self.create_stat_card(
            cards_container,
            "⏳ Pending",
            "0",
            self.theme_manager.get_color("priority_medium"),
            row=1, column=0
        )
        self.pending_tasks_label = pending_card.children[0].children[0]

        # Overdue Tasks Card
        overdue_card = self.create_stat_card(
            cards_container,
            "⚠️ Overdue",
            "0",
            self.theme_manager.get_color("priority_high"),
            row=1, column=2
        )
        self.overdue_tasks_label = overdue_card.children[0].children[0]

        # Completion Rate Card (spans 2 columns)
        completion_card = self.create_stat_card(
            cards_container,
            "📊 Completion Rate",
            "0%",
            self.theme_manager.get_color("accent"),
            row=2, column=0, columnspan=3
        )
        self.completion_rate_label = completion_card.children[0].children[0]

    def create_stat_card(self, parent, title: str, value: str, color: str,
                        row: int, column: int, columnspan: int = 1):
        """Create a single statistics card."""
        card = ctk.CTkFrame(parent)
        card.grid(row=row, column=column, columnspan=columnspan, padx=5, pady=5, sticky="ew")
        card.grid_columnconfigure(0, weight=1)

        # Card content
        content_frame = ctk.CTkFrame(card, fg_color=color)
        content_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        content_frame.grid_columnconfigure(0, weight=1)

        # Value label
        value_label = ctk.CTkLabel(
            content_frame,
            text=value,
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="white"
        )
        value_label.grid(row=0, column=0, padx=15, pady=(10, 5))

        # Title label
        title_label = ctk.CTkLabel(
            content_frame,
            text=title,
            font=ctk.CTkFont(size=12),
            text_color="white"
        )
        title_label.grid(row=1, column=0, padx=15, pady=(0, 10))

        return card

    def create_recent_tasks_section(self, parent):
        """Create recent tasks section."""
        recent_frame = ctk.CTkFrame(parent)
        recent_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(10, 5))
        recent_frame.grid_columnconfigure(0, weight=1)

        # Header
        header_label = ctk.CTkLabel(
            recent_frame,
            text="🕐 Recent Tasks",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        header_label.grid(row=0, column=0, padx=20, pady=15, sticky="w")

        # View all button
        view_all_btn = ctk.CTkButton(
            recent_frame,
            text="View All",
            command=lambda: self.app_instance.switch_view("tasks") if self.app_instance else None,
            width=80,
            height=25
        )
        view_all_btn.grid(row=0, column=1, padx=20, pady=15, sticky="e")

        # Recent tasks scrollable frame
        self.recent_tasks_frame = ctk.CTkScrollableFrame(recent_frame, height=200)
        self.recent_tasks_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=(0, 10), sticky="ew")
        self.recent_tasks_frame.grid_columnconfigure(0, weight=1)

        # Loading label
        self.recent_loading_label = ctk.CTkLabel(
            self.recent_tasks_frame,
            text="Loading recent tasks...",
            font=ctk.CTkFont(size=12, slant="italic")
        )
        self.recent_loading_label.grid(row=0, column=0, pady=20)

    def create_upcoming_tasks_section(self, parent):
        """Create upcoming tasks section."""
        upcoming_frame = ctk.CTkFrame(parent)
        upcoming_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(5, 10))
        upcoming_frame.grid_columnconfigure(0, weight=1)
        upcoming_frame.grid_rowconfigure(1, weight=1)

        # Header
        header_label = ctk.CTkLabel(
            upcoming_frame,
            text="⏰ Upcoming Tasks",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        header_label.grid(row=0, column=0, padx=20, pady=15, sticky="w")

        # Calendar view button
        calendar_btn = ctk.CTkButton(
            upcoming_frame,
            text="📅 Calendar",
            command=lambda: self.app_instance.switch_view("calendar") if self.app_instance else None,
            width=80,
            height=25
        )
        calendar_btn.grid(row=0, column=1, padx=20, pady=15, sticky="e")

        # Upcoming tasks scrollable frame
        self.upcoming_tasks_frame = ctk.CTkScrollableFrame(upcoming_frame, height=200)
        self.upcoming_tasks_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=(0, 10), sticky="nsew")
        self.upcoming_tasks_frame.grid_columnconfigure(0, weight=1)

        # Loading label
        self.upcoming_loading_label = ctk.CTkLabel(
            self.upcoming_tasks_frame,
            text="Loading upcoming tasks...",
            font=ctk.CTkFont(size=12, slant="italic")
        )
        self.upcoming_loading_label.grid(row=0, column=0, pady=20)

    def create_quick_actions(self):
        """Create quick actions section at the bottom."""
        quick_actions_frame = ctk.CTkFrame(self)
        quick_actions_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(10, 20))
        quick_actions_frame.grid_columnconfigure(1, weight=1)

        # Title
        title_label = ctk.CTkLabel(
            quick_actions_frame,
            text="⚡ Quick Actions",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=20, pady=15, sticky="w")

        # Action buttons
        actions_container = ctk.CTkFrame(quick_actions_frame)
        actions_container.grid(row=1, column=0, columnspan=2, padx=20, pady=(0, 15), sticky="ew")

        # Quick action buttons
        buttons_data = [
            ("📝 Add Task", self.new_task, self.theme_manager.get_color("primary")),
            ("🔍 Search Tasks", self.search_tasks, self.theme_manager.get_color("accent")),
            ("📊 View Statistics", lambda: self.app_instance.switch_view("statistics") if self.app_instance else None, self.theme_manager.get_color("priority_medium")),
            ("📅 Open Calendar", lambda: self.app_instance.switch_view("calendar") if self.app_instance else None, self.theme_manager.get_color("priority_low")),
            ("⚙️ Settings", lambda: self.app_instance.switch_view("settings") if self.app_instance else None, self.theme_manager.get_color("surface"))
        ]

        for i, (text, command, color) in enumerate(buttons_data):
            btn = ctk.CTkButton(
                actions_container,
                text=text,
                command=command,
                fg_color=color,
                width=140,
                height=40
            )
            btn.grid(row=0, column=i, padx=5, pady=5)

    def create_task_item(self, parent, task, show_priority=True):
        """Create a task item widget."""
        task_frame = ctk.CTkFrame(parent)
        task_frame.grid(row=parent.grid_size()[1], column=0, padx=5, pady=5, sticky="ew")
        task_frame.grid_columnconfigure(1, weight=1)

        # Priority indicator
        if show_priority:
            priority_color = self.theme_manager.get_priority_color(task.priority)
            priority_label = ctk.CTkLabel(
                task_frame,
                text="●",
                font=ctk.CTkFont(size=16),
                text_color=priority_color
            )
            priority_label.grid(row=0, column=0, padx=(10, 5), pady=10)

        # Task title
        title_label = ctk.CTkLabel(
            task_frame,
            text=task.title[:40] + "..." if len(task.title) > 40 else task.title,
            font=ctk.CTkFont(size=12, weight="normal"),
            anchor="w"
        )
        title_label.grid(row=0, column=1, padx=5, pady=10, sticky="w")

        # Due date or status
        if task.due_date:
            due_text = format_datetime(task.due_date, "short")
            due_label = ctk.CTkLabel(
                task_frame,
                text=due_text,
                font=ctk.CTkFont(size=10),
                text_color=self.theme_manager.get_color("text_secondary")
            )
            due_label.grid(row=0, column=2, padx=5, pady=10)

        # Status indicator
        status_color = self.theme_manager.get_status_color(task.status)
        status_label = ctk.CTkLabel(
            task_frame,
            text=task.status[:3],
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=status_color
        )
        status_label.grid(row=0, column=3, padx=(5, 10), pady=10)

        # Bind click event
        task_frame.bind("<Button-1>", lambda e: self.view_task_details(task))
        for widget in task_frame.winfo_children():
            widget.bind("<Button-1>", lambda e, t=task: self.view_task_details(t))

    def refresh_data(self):
        """Refresh all dashboard data."""
        try:
            # Update statistics
            stats = self.task_manager.get_task_statistics()
            self.update_statistics(stats)

            # Update recent tasks
            self.update_recent_tasks()

            # Update upcoming tasks
            self.update_upcoming_tasks()

            if self.app_instance:
                self.app_instance.set_status("Dashboard refreshed")

        except Exception as e:
            print(f"Error refreshing dashboard data: {e}")
            if self.app_instance:
                self.app_instance.set_status("Error refreshing dashboard")

    def update_statistics(self, stats):
        """Update statistics cards."""
        self.total_tasks_label.configure(text=str(stats.get('total_created', 0)))
        self.completed_tasks_label.configure(text=str(stats.get('total_completed', 0)))
        self.pending_tasks_label.configure(text=str(stats.get('pending', 0)))
        self.overdue_tasks_label.configure(text=str(stats.get('overdue_count', 0)))
        self.completion_rate_label.configure(text=f"{stats.get('completion_rate', 0):.1f}%")

    def update_recent_tasks(self):
        """Update recent tasks section."""
        # Clear existing tasks
        for widget in self.recent_tasks_frame.winfo_children():
            widget.destroy()

        # Get recent tasks (last 10 modified)
        recent_tasks = self.db.get_all_tasks()
        recent_tasks.sort(key=lambda t: t.updated_at or t.created_at or '', reverse=True)
        recent_tasks = recent_tasks[:10]

        if recent_tasks:
            for task in recent_tasks:
                self.create_task_item(self.recent_tasks_frame, task)
        else:
            no_tasks_label = ctk.CTkLabel(
                self.recent_tasks_frame,
                text="No recent tasks found",
                font=ctk.CTkFont(size=12, slant="italic"),
                text_color=self.theme_manager.get_color("text_secondary")
            )
            no_tasks_label.grid(row=0, column=0, pady=20)

    def update_upcoming_tasks(self):
        """Update upcoming tasks section."""
        # Clear existing tasks
        for widget in self.upcoming_tasks_frame.winfo_children():
            widget.destroy()

        # Get upcoming tasks (next 7 days)
        upcoming_tasks = self.task_manager.get_upcoming_tasks(24 * 7)  # Next 7 days

        if upcoming_tasks:
            for task in upcoming_tasks:
                self.create_task_item(self.upcoming_tasks_frame, task)
        else:
            no_tasks_label = ctk.CTkLabel(
                self.upcoming_tasks_frame,
                text="No upcoming tasks",
                font=ctk.CTkFont(size=12, slant="italic"),
                text_color=self.theme_manager.get_color("text_secondary")
            )
            no_tasks_label.grid(row=0, column=0, pady=20)

    def schedule_refresh(self):
        """Schedule automatic data refresh."""
        if self.app_instance and self.app_instance.is_running:
            self.refresh_data()
            # Schedule next refresh in 30 seconds
            self.after(30000, self.schedule_refresh)

    # Action methods
    def new_task(self):
        """Open new task dialog."""
        if self.app_instance:
            self.app_instance.new_task()

    def search_tasks(self):
        """Open search dialog."""
        if self.app_instance:
            self.app_instance.search_tasks()

    def view_task_details(self, task):
        """View task details."""
        if self.app_instance:
            self.app_instance.show_info(f"Task: {task.title}\nStatus: {task.status}\nPriority: {task.priority}")