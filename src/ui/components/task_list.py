"""
Advanced Task List component with filtering, search, and modern UI.
Provides a comprehensive task management interface with multiple view modes.
"""

import os
import sys
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional

import customtkinter as ctk

# Add parent directories to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ...database.manager import DatabaseManager
from ...database.models import Task
from ..themes.theme_manager import get_theme_manager
from ...utils.helpers import format_datetime, format_relative_time
from ...core.task_manager import TaskManager


class ModernTaskList(ctk.CTkFrame):
    """Modern task list component with advanced filtering and search."""

    def __init__(self, parent, app_instance=None):
        super().__init__(parent)
        self.parent = parent
        self.app_instance = app_instance
        self.theme_manager = get_theme_manager()

        # Initialize managers
        self.task_manager = TaskManager()
        self.db = DatabaseManager()

        # State variables
        self.current_tasks = []
        self.filtered_tasks = []
        self.selected_task = None
        self.view_mode = "list"  # list, grid, kanban
        self.sort_by = "due_date"  # due_date, priority, created_at, title
        self.sort_order = "asc"  # asc, desc

        # Filter state
        self.search_query = ""
        self.filter_status = "All"
        self.filter_priority = "All"
        self.filter_category = "All"
        self.filter_date_range = "All"  # All, Today, Week, Month, Overdue

        # Load categories
        self.categories = self._load_categories()

        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Create UI components
        self.create_header()
        self.create_toolbar()
        self.create_filter_panel()
        self.create_task_display()
        self.create_status_bar()

        # Load initial data
        self.refresh_tasks()

    def create_header(self):
        """Create the task list header."""
        header_frame = ctk.CTkFrame(self, height=80)
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        header_frame.grid_columnconfigure(1, weight=1)
        header_frame.grid_propagate(False)

        # Title and stats
        title_frame = ctk.CTkFrame(header_frame)
        title_frame.grid(row=0, column=0, padx=20, pady=20, sticky="w")

        title_label = ctk.CTkLabel(
            title_frame,
            text="📝 Tasks",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title_label.pack(anchor="w")

        self.stats_label = ctk.CTkLabel(
            title_frame,
            text="Loading tasks...",
            font=ctk.CTkFont(size=12),
            text_color=self.theme_manager.get_color("text_secondary")
        )
        self.stats_label.pack(anchor="w", pady=(2, 0))

        # Action buttons
        actions_frame = ctk.CTkFrame(header_frame)
        actions_frame.grid(row=0, column=2, padx=20, pady=20, sticky="e")

        # View mode buttons
        view_frame = ctk.CTkFrame(actions_frame)
        view_frame.pack(side="left", padx=(0, 10))

        self.view_var = ctk.StringVar(value="list")

        views = [
            ("📋", "list", "List View"),
            ("⊞", "grid", "Grid View"),
            ("📊", "kanban", "Kanban View")
        ]

        for icon, value, tooltip in views:
            btn = ctk.CTkButton(
                view_frame,
                text=icon,
                width=35,
                height=35,
                variable=self.view_var,
                value=value,
                command=lambda v=value: self.change_view_mode(v)
            )
            btn.pack(side="left", padx=2)
            # Add tooltip (would need custom implementation)
            # self.create_tooltip(btn, tooltip)

        # Action buttons
        new_task_btn = ctk.CTkButton(
            actions_frame,
            text="➕ New Task",
            command=self.new_task,
            width=120,
            fg_color=self.theme_manager.get_color("primary")
        )
        new_task_btn.pack(side="left", padx=5)

        refresh_btn = ctk.CTkButton(
            actions_frame,
            text="🔄",
            width=35,
            height=35,
            command=self.refresh_tasks
        )
        refresh_btn.pack(side="left", padx=5)

    def create_toolbar(self):
        """Create the toolbar with search and sort options."""
        toolbar_frame = ctk.CTkFrame(self)
        toolbar_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 10))
        toolbar_frame.grid_columnconfigure(1, weight=1)

        # Search bar
        search_frame = ctk.CTkFrame(toolbar_frame)
        search_frame.grid(row=0, column=0, padx=20, pady=15, sticky="ew")
        search_frame.grid_columnconfigure(0, weight=1)

        search_icon = ctk.CTkLabel(search_frame, text="🔍")
        search_icon.grid(row=0, column=0, padx=(10, 5), pady=10)

        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search tasks...",
            height=35
        )
        self.search_entry.grid(row=0, column=1, padx=(0, 10), pady=10, sticky="ew")
        search_frame.grid_columnconfigure(1, weight=1)

        # Bind search
        self.search_entry.bind("<KeyRelease>", self.on_search_change)

        # Clear search button
        clear_search_btn = ctk.CTkButton(
            search_frame,
            text="✕",
            width=30,
            height=30,
            command=self.clear_search,
            fg_color="transparent",
            text_color=self.theme_manager.get_color("text_secondary")
        )
        clear_search_btn.grid(row=0, column=2, padx=(0, 10), pady=10)

        # Sort controls
        sort_frame = ctk.CTkFrame(toolbar_frame)
        sort_frame.grid(row=0, column=1, padx=(0, 20), pady=15, sticky="e")

        sort_label = ctk.CTkLabel(sort_frame, text="Sort by:")
        sort_label.pack(side="left", padx=(10, 5))

        self.sort_var = ctk.StringVar(value="due_date")
        sort_options = ["due_date", "priority", "created_at", "title", "status"]
        sort_labels = ["Due Date", "Priority", "Created", "Title", "Status"]

        self.sort_combo = ctk.CTkComboBox(
            sort_frame,
            variable=self.sort_var,
            values=sort_labels,
            width=120,
            command=self.on_sort_change
        )
        self.sort_combo.pack(side="left", padx=5)

        # Sort order toggle
        self.sort_order_btn = ctk.CTkButton(
            sort_frame,
            text="↑",
            width=30,
            height=30,
            command=self.toggle_sort_order
        )
        self.sort_order_btn.pack(side="left", padx=5)

    def create_filter_panel(self):
        """Create the filter panel."""
        filter_frame = ctk.CTkFrame(self)
        filter_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 10))
        filter_frame.grid_columnconfigure(4, weight=1)

        # Status filter
        status_label = ctk.CTkLabel(filter_frame, text="Status:")
        status_label.grid(row=0, column=0, padx=(20, 5), pady=10)

        self.status_var = ctk.StringVar(value="All")
        status_options = ["All", "Pending", "Completed", "Cancelled"]
        self.status_combo = ctk.CTkComboBox(
            filter_frame,
            variable=self.status_var,
            values=status_options,
            width=100,
            command=lambda _: self.apply_filters()
        )
        self.status_combo.grid(row=0, column=1, padx=(0, 15), pady=10)

        # Priority filter
        priority_label = ctk.CTkLabel(filter_frame, text="Priority:")
        priority_label.grid(row=0, column=2, padx=(0, 5), pady=10)

        self.priority_var = ctk.StringVar(value="All")
        priority_options = ["All", "High", "Medium", "Low"]
        self.priority_combo = ctk.CTkComboBox(
            filter_frame,
            variable=self.priority_var,
            values=priority_options,
            width=100,
            command=lambda _: self.apply_filters()
        )
        self.priority_combo.grid(row=0, column=3, padx=(0, 15), pady=10)

        # Category filter
        category_label = ctk.CTkLabel(filter_frame, text="Category:")
        category_label.grid(row=0, column=4, padx=(0, 5), pady=10, sticky="w")

        self.category_var = ctk.StringVar(value="All")
        category_options = ["All"] + self.categories
        self.category_combo = ctk.CTkComboBox(
            filter_frame,
            variable=self.category_var,
            values=category_options,
            width=120,
            command=lambda _: self.apply_filters()
        )
        self.category_combo.grid(row=0, column=5, padx=(0, 15), pady=10)

        # Date range filter
        date_label = ctk.CTkLabel(filter_frame, text="Date:")
        date_label.grid(row=0, column=6, padx=(0, 5), pady=10)

        self.date_var = ctk.StringVar(value="All")
        date_options = ["All", "Today", "This Week", "This Month", "Overdue", "No Due Date"]
        self.date_combo = ctk.CTkComboBox(
            filter_frame,
            variable=self.date_var,
            values=date_options,
            width=120,
            command=lambda _: self.apply_filters()
        )
        self.date_combo.grid(row=0, column=7, padx=(0, 20), pady=10)

        # Clear filters button
        clear_filters_btn = ctk.CTkButton(
            filter_frame,
            text="Clear Filters",
            command=self.clear_filters,
            width=100,
            height=30,
            fg_color="transparent",
            text_color=self.theme_manager.get_color("text_primary"),
            border_width=1,
            border_color=self.theme_manager.get_color("border")
        )
        clear_filters_btn.grid(row=0, column=8, padx=(0, 20), pady=10)

    def create_task_display(self):
        """Create the main task display area."""
        # Container for different view modes
        self.display_container = ctk.CTkFrame(self)
        self.display_container.grid(row=3, column=0, sticky="nsew", padx=20, pady=(0, 10))
        self.display_container.grid_columnconfigure(0, weight=1)
        self.display_container.grid_rowconfigure(0, weight=1)

        # List view (default)
        self.list_frame = ctk.CTkScrollableFrame(self.display_container)
        self.list_frame.grid_columnconfigure(0, weight=1)

        # Grid view
        self.grid_frame = ctk.CTkScrollableFrame(self.display_container)
        self.grid_frame.grid_columnconfigure(0, weight=1)

        # Kanban view
        self.kanban_frame = ctk.CTkFrame(self.display_container)
        self.kanban_frame.grid_columnconfigure(0, weight=1)
        self.kanban_frame.grid_columnconfigure(2, weight=1)

        # Show initial view
        self.change_view_mode("list")

    def create_status_bar(self):
        """Create status bar with task counts."""
        status_frame = ctk.CTkFrame(self, height=40)
        status_frame.grid(row=4, column=0, sticky="ew", padx=20, pady=(0, 20))
        status_frame.grid_propagate(False)

        # Task counts
        self.status_label = ctk.CTkLabel(
            status_frame,
            text="Ready",
            anchor="w"
        )
        self.status_label.pack(side="left", padx=20, pady=10)

        # Spacer
        spacer = ctk.CTkFrame(status_frame, fg_color="transparent")
        spacer.pack(side="left", expand=True, fill="x")

        # Selected task info
        self.selected_info_label = ctk.CTkLabel(
            status_frame,
            text="",
            anchor="e"
        )
        self.selected_info_label.pack(side="right", padx=20, pady=10)

    def create_task_item(self, parent, task: Task, index: int):
        """Create a task item for list view."""
        # Main task frame
        task_frame = ctk.CTkFrame(parent)
        task_frame.grid(row=index, column=0, padx=10, pady=5, sticky="ew")
        task_frame.grid_columnconfigure(2, weight=1)

        # Selection state
        is_selected = self.selected_task and self.selected_task.id == task.id
        bg_color = self.theme_manager.get_color("surface_variant") if is_selected else "transparent"

        # Checkbox
        checkbox_var = ctk.BooleanVar(value=task.status == "Completed")
        checkbox = ctk.CTkCheckBox(
            task_frame,
            text="",
            variable=checkbox_var,
            command=lambda t=task, v=checkbox_var: self.toggle_task_completion(t, v.get()),
            width=20
        )
        checkbox.grid(row=0, column=0, padx=(15, 10), pady=15)

        # Priority indicator
        priority_color = self.theme_manager.get_priority_color(task.priority)
        priority_label = ctk.CTkLabel(
            task_frame,
            text="●",
            font=ctk.CTkFont(size=12),
            text_color=priority_color
        )
        priority_label.grid(row=0, column=1, padx=(0, 10), pady=15)

        # Task content
        content_frame = ctk.CTkFrame(task_frame, fg_color="transparent")
        content_frame.grid(row=0, column=2, padx=(0, 15), pady=10, sticky="ew")
        content_frame.grid_columnconfigure(0, weight=1)

        # Title
        title_color = self.theme_manager.get_color("text_secondary") if task.status == "Completed" else self.theme_manager.get_color("text_primary")
        title_font = ctk.CTkFont(size=14, slant="italic" if task.status == "Completed" else "normal")

        title_label = ctk.CTkLabel(
            content_frame,
            text=task.title,
            font=title_font,
            text_color=title_color,
            anchor="w"
        )
        title_label.grid(row=0, column=0, sticky="ew", pady=(0, 2))

        # Meta information
        meta_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        meta_frame.grid(row=1, column=0, sticky="ew")
        meta_frame.grid_columnconfigure(2, weight=1)

        # Category badge
        if task.category:
            category_label = ctk.CTkLabel(
                meta_frame,
                text=f"📁 {task.category}",
                font=ctk.CTkFont(size=10),
                text_color=self.theme_manager.get_color("text_secondary")
            )
            category_label.grid(row=0, column=0, padx=(0, 10), sticky="w")

        # Due date
        if task.due_date:
            due_text = format_datetime(task.due_date, "short")
            due_color = self.theme_manager.get_color("priority_high") if task.is_overdue() else self.theme_manager.get_color("text_secondary")
            due_label = ctk.CTkLabel(
                meta_frame,
                text=f"📅 {due_text}",
                font=ctk.CTkFont(size=10),
                text_color=due_color
            )
            due_label.grid(row=0, column=1, padx=(0, 10), sticky="w")

        # Status
        status_color = self.theme_manager.get_status_color(task.status)
        status_label = ctk.CTkLabel(
            meta_frame,
            text=f"• {task.status}",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=status_color
        )
        status_label.grid(row=0, column=2, sticky="w")

        # Action buttons
        actions_frame = ctk.CTkFrame(task_frame, fg_color="transparent")
        actions_frame.grid(row=0, column=3, padx=(0, 15), pady=10)

        # Edit button
        edit_btn = ctk.CTkButton(
            actions_frame,
            text="✏️",
            width=30,
            height=30,
            command=lambda t=task: self.edit_task(t),
            fg_color="transparent",
            text_color=self.theme_manager.get_color("text_secondary")
        )
        edit_btn.pack(side="left", padx=2)

        # Delete button
        delete_btn = ctk.CTkButton(
            actions_frame,
            text="🗑️",
            width=30,
            height=30,
            command=lambda t=task: self.delete_task(t),
            fg_color="transparent",
            text_color=self.theme_manager.get_color("priority_high")
        )
        delete_btn.pack(side="left", padx=2)

        # Bind click events
        task_frame.bind("<Button-1>", lambda e, t=task: self.select_task(t))
        for widget in task_frame.winfo_children():
            widget.bind("<Button-1>", lambda e, t=task: self.select_task(t))

        # Store reference
        task_frame.task = task
        task_frame.checkbox = checkbox

        return task_frame

    def create_grid_task_item(self, parent, task: Task, index: int):
        """Create a task item for grid view."""
        card = ctk.CTkFrame(parent, width=250, height=150)
        card.grid(row=index // 3, column=index % 3, padx=10, pady=10, sticky="nsew")
        card.grid_propagate(False)

        # Configure grid
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(2, weight=1)

        # Priority indicator
        priority_color = self.theme_manager.get_priority_color(task.priority)
        priority_frame = ctk.CTkFrame(card, height=4, fg_color=priority_color)
        priority_frame.grid(row=0, column=0, sticky="ew")
        priority_frame.grid_propagate(False)

        # Title
        title_font = ctk.CTkFont(size=12, weight="bold")
        title_color = self.theme_manager.get_color("text_secondary") if task.status == "Completed" else self.theme_manager.get_color("text_primary")

        title_label = ctk.CTkLabel(
            card,
            text=task.title[:30] + "..." if len(task.title) > 30 else task.title,
            font=title_font,
            text_color=title_color,
            wraplength=230
        )
        title_label.grid(row=1, column=0, padx=10, pady=(10, 5), sticky="ew")

        # Content frame
        content_frame = ctk.CTkFrame(card, fg_color="transparent")
        content_frame.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="nsew")
        content_frame.grid_columnconfigure(0, weight=1)

        # Description preview
        if task.description:
            desc_label = ctk.CTkLabel(
                content_frame,
                text=task.description[:50] + "..." if len(task.description) > 50 else task.description,
                font=ctk.CTkFont(size=10),
                text_color=self.theme_manager.get_color("text_secondary"),
                wraplength=230,
                anchor="w"
            )
            desc_label.grid(row=0, column=0, sticky="ew", pady=(0, 5))

        # Meta info
        meta_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        meta_frame.grid(row=1, column=0, sticky="ew")

        # Category
        if task.category:
            cat_label = ctk.CTkLabel(
                meta_frame,
                text=f"📁 {task.category[:15]}",
                font=ctk.CTkFont(size=9),
                text_color=self.theme_manager.get_color("text_secondary")
            )
            cat_label.pack(anchor="w")

        # Due date
        if task.due_date:
            due_text = format_datetime(task.due_date, "short")
            due_label = ctk.CTkLabel(
                meta_frame,
                text=f"📅 {due_text}",
                font=ctk.CTkFont(size=9),
                text_color=self.theme_manager.get_color("text_secondary")
            )
            due_label.pack(anchor="w")

        # Store reference
        card.task = task

        # Bind click event
        card.bind("<Button-1>", lambda e, t=task: self.select_task(t))

        return card

    def create_kanban_board(self):
        """Create kanban board view."""
        # Clear existing kanban content
        for widget in self.kanban_frame.winfo_children():
            widget.destroy()

        # Kanban columns
        columns = [
            ("To Do", "Pending"),
            ("In Progress", "Pending"),  # Could add custom status
            ("Done", "Completed")
        ]

        for i, (title, status) in enumerate(columns):
            # Column frame
            column_frame = ctk.CTkFrame(self.kanban_frame)
            column_frame.grid(row=0, column=i, padx=10, pady=10, sticky="nsew")
            column_frame.grid_columnconfigure(0, weight=1)
            column_frame.grid_rowconfigure(1, weight=1)

            # Column header
            header_frame = ctk.CTkFrame(column_frame)
            header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

            header_label = ctk.CTkLabel(
                header_frame,
                text=f"{title}\n{self.get_status_count(status)} tasks",
                font=ctk.CTkFont(size=14, weight="bold"),
                anchor="center"
            )
            header_label.pack(pady=5)

            # Task container
            task_container = ctk.CTkScrollableFrame(column_frame, height=400)
            task_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
            task_container.grid_columnconfigure(0, weight=1)

            # Add tasks to column
            column_tasks = [t for t in self.filtered_tasks if t.status == status]
            for j, task in enumerate(column_tasks):
                self.create_kanban_task_item(task_container, task, j)

    def create_kanban_task_item(self, parent, task: Task, index: int):
        """Create a task item for kanban view."""
        card = ctk.CTkFrame(parent)
        card.grid(row=index, column=0, padx=5, pady=5, sticky="ew")
        card.grid_columnconfigure(0, weight=1)

        # Priority indicator
        priority_color = self.theme_manager.get_priority_color(task.priority)
        priority_label = ctk.CTkLabel(
            card,
            text="●",
            font=ctk.CTkFont(size=8),
            text_color=priority_color
        )
        priority_label.grid(row=0, column=0, padx=(10, 5), pady=(5, 0), sticky="w")

        # Title
        title_label = ctk.CTkLabel(
            card,
            text=task.title[:40] + "..." if len(task.title) > 40 else task.title,
            font=ctk.CTkFont(size=11, weight="bold"),
            wraplength=200,
            anchor="w"
        )
        title_label.grid(row=1, column=0, padx=10, pady=(0, 5), sticky="ew")

        # Category
        if task.category:
            cat_label = ctk.CTkLabel(
                card,
                text=f"📁 {task.category[:20]}",
                font=ctk.CTkFont(size=9),
                text_color=self.theme_manager.get_color("text_secondary")
            )
            cat_label.grid(row=2, column=0, padx=10, pady=(0, 5), sticky="w")

        # Due date
        if task.due_date:
            due_text = format_datetime(task.due_date, "short")
            due_label = ctk.CTkLabel(
                card,
                text=f"📅 {due_text}",
                font=ctk.CTkFont(size=9),
                text_color=self.theme_manager.get_color("text_secondary")
            )
            due_label.grid(row=3, column=0, padx=10, pady=(0, 10), sticky="w")

        # Store reference
        card.task = task

        # Bind click event
        card.bind("<Button-1>", lambda e, t=task: self.select_task(t))

        return card

    # Data management methods
    def refresh_tasks(self):
        """Refresh task list from database."""
        try:
            self.current_tasks = self.db.get_all_tasks()
            self.apply_filters()
            self.update_stats()

            if self.app_instance:
                self.app_instance.set_status("Tasks refreshed")

        except Exception as e:
            print(f"Error refreshing tasks: {e}")
            if self.app_instance:
                self.app_instance.set_status("Error loading tasks")

    def apply_filters(self):
        """Apply all filters to the task list."""
        try:
            self.filtered_tasks = self.current_tasks.copy()

            # Apply search filter
            if self.search_query.strip():
                query = self.search_query.lower()
                self.filtered_tasks = [
                    task for task in self.filtered_tasks
                    if query in task.title.lower() or
                       (task.description and query in task.description.lower())
                ]

            # Apply status filter
            if self.status_var.get() != "All":
                self.filtered_tasks = [
                    task for task in self.filtered_tasks
                    if task.status == self.status_var.get()
                ]

            # Apply priority filter
            if self.priority_var.get() != "All":
                self.filtered_tasks = [
                    task for task in self.filtered_tasks
                    if task.priority == self.priority_var.get()
                ]

            # Apply category filter
            if self.category_var.get() != "All":
                self.filtered_tasks = [
                    task for task in self.filtered_tasks
                    if task.category == self.category_var.get()
                ]

            # Apply date range filter
            self.apply_date_filter()

            # Apply sorting
            self.apply_sorting()

            # Update display
            self.update_display()

            # Update status
            self.update_status_display()

        except Exception as e:
            print(f"Error applying filters: {e}")

    def apply_date_filter(self):
        """Apply date range filter."""
        date_filter = self.date_var.get()
        today = date.today()

        if date_filter == "Today":
            self.filtered_tasks = [
                task for task in self.filtered_tasks
                if task.due_date and task.is_due_today()
            ]
        elif date_filter == "This Week":
            week_end = today + timedelta(days=6)
            self.filtered_tasks = [
                task for task in self.filtered_tasks
                if task.due_date and today <= datetime.fromisoformat(task.due_date.replace('Z', '+00:00')).date() <= week_end
            ]
        elif date_filter == "This Month":
            month_end = today.replace(day=28) + timedelta(days=4)  # Get to next month
            month_end = month_end - timedelta(days=month_end.day)  # Back to last day of current month
            self.filtered_tasks = [
                task for task in self.filtered_tasks
                if task.due_date and today <= datetime.fromisoformat(task.due_date.replace('Z', '+00:00')).date() <= month_end
            ]
        elif date_filter == "Overdue":
            self.filtered_tasks = [task for task in self.filtered_tasks if task.is_overdue()]
        elif date_filter == "No Due Date":
            self.filtered_tasks = [task for task in self.filtered_tasks if not task.due_date]

    def apply_sorting(self):
        """Apply sorting to filtered tasks."""
        sort_by = self.sort_var.get()

        # Sort tasks
        if sort_by == "due_date":
            self.filtered_tasks.sort(key=lambda t: t.due_date or "9999-12-31", reverse=self.sort_order == "desc")
        elif sort_by == "priority":
            priority_order = {"High": 0, "Medium": 1, "Low": 2}
            self.filtered_tasks.sort(key=lambda t: priority_order.get(t.priority, 3), reverse=self.sort_order == "asc")
        elif sort_by == "created_at":
            self.filtered_tasks.sort(key=lambda t: t.created_at or "", reverse=self.sort_order == "desc")
        elif sort_by == "title":
            self.filtered_tasks.sort(key=lambda t: t.title.lower(), reverse=self.sort_order == "desc")
        elif sort_by == "status":
            status_order = {"Pending": 0, "Completed": 1, "Cancelled": 2}
            self.filtered_tasks.sort(key=lambda t: status_order.get(t.status, 3), reverse=self.sort_order == "desc")

    def update_display(self):
        """Update the task display based on current view mode."""
        # Hide all views
        self.list_frame.grid_forget()
        self.grid_frame.grid_forget()
        self.kanban_frame.grid_forget()

        if self.view_mode == "list":
            self.update_list_view()
            self.list_frame.grid(row=0, column=0, sticky="nsew")
        elif self.view_mode == "grid":
            self.update_grid_view()
            self.grid_frame.grid(row=0, column=0, sticky="nsew")
        elif self.view_mode == "kanban":
            self.update_kanban_view()

    def update_list_view(self):
        """Update list view."""
        # Clear existing items
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        if not self.filtered_tasks:
            no_tasks_label = ctk.CTkLabel(
                self.list_frame,
                text="No tasks found matching your criteria",
                font=ctk.CTkFont(size=14, slant="italic"),
                text_color=self.theme_manager.get_color("text_secondary")
            )
            no_tasks_label.grid(row=0, column=0, pady=50)
            return

        # Create task items
        for i, task in enumerate(self.filtered_tasks):
            self.create_task_item(self.list_frame, task, i)

    def update_grid_view(self):
        """Update grid view."""
        # Clear existing items
        for widget in self.grid_frame.winfo_children():
            widget.destroy()

        if not self.filtered_tasks:
            no_tasks_label = ctk.CTkLabel(
                self.grid_frame,
                text="No tasks found matching your criteria",
                font=ctk.CTkFont(size=14, slant="italic"),
                text_color=self.theme_manager.get_color("text_secondary")
            )
            no_tasks_label.grid(row=0, column=0, pady=50)
            return

        # Create task items
        for i, task in enumerate(self.filtered_tasks):
            self.create_grid_task_item(self.grid_frame, task, i)

    def update_kanban_view(self):
        """Update kanban view."""
        self.create_kanban_board()
        self.kanban_frame.grid(row=0, column=0, sticky="nsew")

    # Event handlers
    def on_search_change(self, event=None):
        """Handle search input change."""
        self.search_query = self.search_entry.get()
        self.apply_filters()

    def on_sort_change(self, selection):
        """Handle sort change."""
        # Map display labels to internal values
        mapping = {
            "Due Date": "due_date",
            "Priority": "priority",
            "Created": "created_at",
            "Title": "title",
            "Status": "status"
        }
        self.sort_by = mapping.get(selection, "due_date")
        self.apply_filters()

    def toggle_sort_order(self):
        """Toggle sort order."""
        self.sort_order = "desc" if self.sort_order == "asc" else "asc"
        self.sort_order_btn.configure(text="↓" if self.sort_order == "desc" else "↑")
        self.apply_filters()

    def change_view_mode(self, mode):
        """Change view mode."""
        self.view_mode = mode
        self.update_display()

    def select_task(self, task):
        """Select a task."""
        self.selected_task = task
        self.update_display()  # Refresh to show selection
        self.update_selected_info()

    def toggle_task_completion(self, task, completed):
        """Toggle task completion status."""
        try:
            new_status = "Completed" if completed else "Pending"
            success, message = self.task_manager.update_task(task.id, {"status": new_status})

            if success:
                self.refresh_tasks()
                if self.app_instance:
                    self.app_instance.set_status(f"Task {new_status.lower()}")
            else:
                if self.app_instance:
                    self.app_instance.show_error(f"Failed to update task: {message}")

        except Exception as e:
            if self.app_instance:
                self.app_instance.show_error(f"Error updating task: {str(e)}")

    def edit_task(self, task):
        """Edit a task."""
        from .task_form import ModernTaskForm

        form = ModernTaskForm(self.parent, task, on_save=self.refresh_tasks)
        self.wait_window(form)

    def delete_task(self, task):
        """Delete a task."""
        if messagebox.askyesno("Delete Task", f"Are you sure you want to delete '{task.title}'?"):
            try:
                success, message = self.task_manager.delete_task(task.id)
                if success:
                    self.refresh_tasks()
                    if self.app_instance:
                        self.app_instance.set_status("Task deleted")
                else:
                    if self.app_instance:
                        self.app_instance.show_error(f"Failed to delete task: {message}")
            except Exception as e:
                if self.app_instance:
                    self.app_instance.show_error(f"Error deleting task: {str(e)}")

    def new_task(self):
        """Create a new task."""
        from .task_form import ModernTaskForm

        form = ModernTaskForm(self.parent, on_save=self.refresh_tasks)
        self.wait_window(form)

    def clear_search(self):
        """Clear search input."""
        self.search_entry.delete(0, "end")
        self.search_query = ""
        self.apply_filters()

    def clear_filters(self):
        """Clear all filters."""
        self.status_var.set("All")
        self.priority_var.set("All")
        self.category_var.set("All")
        self.date_var.set("All")
        self.search_entry.delete(0, "end")
        self.search_query = ""
        self.apply_filters()

    # Helper methods
    def _load_categories(self) -> List[str]:
        """Load categories from database."""
        try:
            categories = self.db.get_all_categories()
            return [cat.name for cat in categories]
        except:
            return ["Personal", "Work", "Health", "Shopping", "Study"]

    def get_status_count(self, status: str) -> int:
        """Get count of tasks with specific status."""
        return len([task for task in self.filtered_tasks if task.status == status])

    def update_stats(self):
        """Update statistics display."""
        total = len(self.current_tasks)
        completed = len([t for t in self.current_tasks if t.status == "Completed"])
        pending = len([t for t in self.current_tasks if t.status == "Pending"])
        overdue = len([t for t in self.current_tasks if t.is_overdue()])

        stats_text = f"Total: {total} | Completed: {completed} | Pending: {pending} | Overdue: {overdue}"
        self.stats_label.configure(text=stats_text)

    def update_status_display(self):
        """Update status display."""
        total_filtered = len(self.filtered_tasks)
        if self.search_query or any(v.get() != "All" for v in [self.status_var, self.priority_var, self.category_var, self.date_var]):
            status_text = f"Showing {total_filtered} of {len(self.current_tasks)} tasks (filtered)"
        else:
            status_text = f"Showing {total_filtered} tasks"

        self.status_label.configure(text=status_text)

    def update_selected_info(self):
        """Update selected task info."""
        if self.selected_task:
            info_text = f"Selected: {self.selected_task.title[:30]}{'...' if len(self.selected_task.title) > 30 else ''}"
        else:
            info_text = ""

        self.selected_info_label.configure(text=info_text)