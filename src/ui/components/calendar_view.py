"""
Modern Calendar View component with interactive calendar and task scheduling.
Provides monthly, weekly, and daily calendar views with task visualization.
"""

import os
import sys
import calendar
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional

import customtkinter as ctk

# Add parent directories to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ...database.manager import DatabaseManager
from ...database.models import Task
from ..themes.theme_manager import get_theme_manager
from ...utils.helpers import format_datetime, get_month_dates, get_week_dates
from ...core.task_manager import TaskManager


class ModernCalendarView(ctk.CTkFrame):
    """Modern calendar view with interactive scheduling capabilities."""

    def __init__(self, parent, app_instance=None):
        super().__init__(parent)
        self.parent = parent
        self.app_instance = app_instance
        self.theme_manager = get_theme_manager()

        # Initialize managers
        self.task_manager = TaskManager()
        self.db = DatabaseManager()

        # Calendar state
        self.current_date = date.today()
        self.selected_date = date.today()
        self.view_mode = "month"  # month, week, day
        self.tasks = []
        self.selected_task = None

        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Create UI components
        self.create_header()
        self.create_view_selector()
        self.create_calendar_display()
        self.create_task_panel()

        # Load initial data
        self.refresh_calendar()

    def create_header(self):
        """Create calendar header with navigation."""
        header_frame = ctk.CTkFrame(self, height=80)
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        header_frame.grid_columnconfigure(1, weight=1)
        header_frame.grid_propagate(False)

        # Navigation controls
        nav_frame = ctk.CTkFrame(header_frame)
        nav_frame.grid(row=0, column=0, padx=20, pady=20, sticky="w")

        # Previous button
        prev_btn = ctk.CTkButton(
            nav_frame,
            text="◀",
            width=40,
            height=40,
            command=self.navigate_previous
        )
        prev_btn.pack(side="left", padx=(0, 5))

        # Current date display
        self.date_label = ctk.CTkLabel(
            nav_frame,
            text="",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.date_label.pack(side="left", padx=10)

        # Next button
        next_btn = ctk.CTkButton(
            nav_frame,
            text="▶",
            width=40,
            height=40,
            command=self.navigate_next
        )
        next_btn.pack(side="left", padx=(5, 10))

        # Today button
        today_btn = ctk.CTkButton(
            nav_frame,
            text="Today",
            command=self.go_to_today,
            width=80,
            height=40
        )
        today_btn.pack(side="left", padx=5)

        # Right side controls
        actions_frame = ctk.CTkFrame(header_frame)
        actions_frame.grid(row=0, column=2, padx=20, pady=20, sticky="e")

        # New task button
        new_task_btn = ctk.CTkButton(
            actions_frame,
            text="➕ New Task",
            command=self.new_task_for_date,
            width=120,
            fg_color=self.theme_manager.get_color("primary")
        )
        new_task_btn.pack(side="left", padx=5)

        # Refresh button
        refresh_btn = ctk.CTkButton(
            actions_frame,
            text="🔄",
            width=40,
            height=40,
            command=self.refresh_calendar
        )
        refresh_btn.pack(side="left", padx=5)

    def create_view_selector(self):
        """Create view mode selector."""
        view_frame = ctk.CTkFrame(self)
        view_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 10))
        view_frame.grid_columnconfigure(2, weight=1)

        # View mode label
        view_label = ctk.CTkLabel(
            view_frame,
            text="View:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        view_label.grid(row=0, column=0, padx=(20, 10), pady=15)

        # View mode buttons
        self.view_var = ctk.StringVar(value="month")

        views = [
            ("Month", "month"),
            ("Week", "week"),
            ("Day", "day")
        ]

        for i, (text, value) in enumerate(views, start=1):
            btn = ctk.CTkRadioButton(
                view_frame,
                text=text,
                variable=self.view_var,
                value=value,
                command=lambda v=value: self.change_view_mode(v)
            )
            btn.grid(row=0, column=i, padx=5, pady=15)

    def create_calendar_display(self):
        """Create the main calendar display area."""
        self.calendar_container = ctk.CTkFrame(self)
        self.calendar_container.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 10))
        self.calendar_container.grid_columnconfigure(0, weight=1)
        self.calendar_container.grid_rowconfigure(0, weight=1)

        # Initialize month view
        self.create_month_view()

    def create_month_view(self):
        """Create month calendar view."""
        # Clear existing content
        for widget in self.calendar_container.winfo_children():
            widget.destroy()

        self.month_frame = ctk.CTkFrame(self.calendar_container)
        self.month_frame.grid(row=0, column=0, sticky="nsew")
        self.month_frame.grid_columnconfigure(0, weight=1)
        self.month_frame.grid_rowconfigure(1, weight=1)

        # Day headers
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        weekend_days = ["Sat", "Sun"]

        for i, day in enumerate(days):
            day_label = ctk.CTkLabel(
                self.month_frame,
                text=day,
                font=ctk.CTkFont(size=12, weight="bold"),
                width=50,
                height=30
            )
            day_label.grid(row=0, column=i, padx=1, pady=1, sticky="nsew")

            # Highlight weekends
            if day in weekend_days:
                day_label.configure(text_color=self.theme_manager.get_color("calendar_weekend"))

        # Calendar grid
        self.calendar_grid = ctk.CTkFrame(self.month_frame)
        self.calendar_grid.grid(row=1, column=0, columnspan=7, sticky="nsew")

        # Configure grid for 6 weeks x 7 days
        for week in range(6):
            for day in range(7):
                self.calendar_grid.grid_rowconfigure(week, weight=1)
                self.calendar_grid.grid_columnconfigure(day, weight=1)

        self.update_month_calendar()

    def create_week_view(self):
        """Create week calendar view."""
        # Clear existing content
        for widget in self.calendar_container.winfo_children():
            widget.destroy()

        self.week_frame = ctk.CTkFrame(self.calendar_container)
        self.week_frame.grid(row=0, column=0, sticky="nsew")
        self.week_frame.grid_columnconfigure(0, weight=1)
        self.week_frame.grid_rowconfigure(1, weight=1)

        # Time column
        time_label = ctk.CTkLabel(
            self.week_frame,
            text="Time",
            font=ctk.CTkFont(size=12, weight="bold"),
            width=60,
            height=30
        )
        time_label.grid(row=0, column=0, padx=1, pady=1, sticky="nsew")

        # Day headers
        week_dates = get_week_dates(self.current_date)
        for i, (day_date, day_name) in enumerate(zip(week_dates, ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])):
            is_today = day_date == date.today()
            is_weekend = day_date.weekday() >= 5

            day_header = ctk.CTkFrame(self.week_frame)
            day_header.grid(row=0, column=i+1, padx=1, pady=1, sticky="nsew")

            # Date
            date_color = self.theme_manager.get_color("primary") if is_today else self.theme_manager.get_color("text_primary")
            if is_weekend:
                date_color = self.theme_manager.get_color("calendar_weekend")

            date_label = ctk.CTkLabel(
                day_header,
                text=f"{day_name}\n{day_date.day}",
                font=ctk.CTkFont(size=10, weight="bold" if is_today else "normal"),
                text_color=date_color
            )
            date_label.pack(pady=5)

        # Week grid
        self.week_grid = ctk.CTkFrame(self.week_frame)
        self.week_grid.grid(row=1, column=0, columnspan=8, sticky="nsew")

        # Configure grid for hours x days
        for hour in range(24):
            self.week_grid.grid_rowconfigure(hour, weight=1)
        for day in range(7):
            self.week_grid.grid_columnconfigure(day, weight=1)

        self.update_week_calendar()

    def create_day_view(self):
        """Create day calendar view."""
        # Clear existing content
        for widget in self.calendar_container.winfo_children():
            widget.destroy()

        self.day_frame = ctk.CTkFrame(self.calendar_container)
        self.day_frame.grid(row=0, column=0, sticky="nsew")
        self.day_frame.grid_columnconfigure(0, weight=1)
        self.day_frame.grid_rowconfigure(1, weight=1)

        # Day header
        day_header = ctk.CTkFrame(self.day_frame)
        day_header.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        is_today = self.current_date == date.today()
        day_name = self.current_date.strftime("%A, %B %d, %Y")

        day_title = ctk.CTkLabel(
            day_header,
            text=day_name,
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.theme_manager.get_color("primary") if is_today else self.theme_manager.get_color("text_primary")
        )
        day_title.pack(pady=10)

        # Day schedule
        self.day_schedule = ctk.CTkScrollableFrame(self.day_frame, height=400)
        self.day_schedule.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.day_schedule.grid_columnconfigure(0, weight=1)

        self.update_day_calendar()

    def create_task_panel(self):
        """Create task details panel."""
        self.task_panel = ctk.CTkFrame(self)
        self.task_panel.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 20))
        self.task_panel.grid_columnconfigure(1, weight=1)

        # Panel header
        header_frame = ctk.CTkFrame(self.task_panel)
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=10)

        header_label = ctk.CTkLabel(
            header_frame,
            text="📋 Tasks for Selected Date",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        header_label.pack(side="left", padx=10, pady=10)

        # Selected date display
        self.selected_date_label = ctk.CTkLabel(
            header_frame,
            text="",
            font=ctk.CTkFont(size=14),
            text_color=self.theme_manager.get_color("text_secondary")
        )
        self.selected_date_label.pack(side="right", padx=10, pady=10)

        # Task list
        self.task_list_frame = ctk.CTkScrollableFrame(self.task_panel, height=150)
        self.task_list_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 10))
        self.task_list_frame.grid_columnconfigure(0, weight=1)

        # Loading label
        self.task_loading_label = ctk.CTkLabel(
            self.task_list_frame,
            text="Select a date to view tasks",
            font=ctk.CTkFont(size=12, slant="italic"),
            text_color=self.theme_manager.get_color("text_secondary")
        )
        self.task_loading_label.grid(row=0, column=0, pady=20)

        self.update_task_panel()

    def update_month_calendar(self):
        """Update month calendar display."""
        if not hasattr(self, 'calendar_grid'):
            return

        # Clear existing day cells
        for widget in self.calendar_grid.winfo_children():
            widget.destroy()

        # Get calendar days
        month_days = get_month_dates(self.current_date)
        today = date.today()

        for week_idx, week in enumerate(month_days):
            for day_idx, day_date in enumerate(week):
                # Create day cell
                day_cell = self.create_day_cell(self.calendar_grid, day_date, week_idx, day_idx)

    def create_day_cell(self, parent, day_date: date, row: int, col: int):
        """Create a single day cell for month view."""
        # Handle days outside current month
        is_current_month = day_date.month == self.current_date.month
        is_today = day_date == date.today()
        is_weekend = day_date.weekday() >= 5
        is_selected = day_date == self.selected_date

        # Determine background color
        bg_color = "transparent"
        if is_selected:
            bg_color = self.theme_manager.get_color("primary")
        elif is_today:
            bg_color = self.theme_manager.get_color("surface_variant")
        elif not is_current_month:
            bg_color = self.theme_manager.get_color("calendar_other_month")

        # Create day cell frame
        day_frame = ctk.CTkFrame(parent, fg_color=bg_color)
        day_frame.grid(row=row, column=col, padx=1, pady=1, sticky="nsew")

        # Day number
        text_color = self.theme_manager.get_color("on_primary") if is_selected else self.theme_manager.get_color("text_primary")
        if not is_current_month:
            text_color = self.theme_manager.get_color("text_secondary")
        elif is_weekend:
            text_color = self.theme_manager.get_color("calendar_weekend")

        day_label = ctk.CTkLabel(
            day_frame,
            text=str(day_date.day),
            font=ctk.CTkFont(size=12, weight="bold" if is_today else "normal"),
            text_color=text_color
        )
        day_label.pack(pady=(5, 2))

        # Task indicators
        day_tasks = self.get_tasks_for_date(day_date)
        if day_tasks:
            # Priority indicators
            priority_indicators = []
            for task in day_tasks[:3]:  # Show max 3 indicators
                priority_color = self.theme_manager.get_priority_color(task.priority)
                indicator = ctk.CTkLabel(
                    day_frame,
                    text="●",
                    font=ctk.CTkFont(size=8),
                    text_color=priority_color
                )
                indicator.pack(side="left", padx=1)

            # More tasks indicator
            if len(day_tasks) > 3:
                more_label = ctk.CTkLabel(
                    day_frame,
                    text=f"+{len(day_tasks) - 3}",
                    font=ctk.CTkFont(size=8),
                    text_color=self.theme_manager.get_color("text_secondary")
                )
                more_label.pack(side="left", padx=1)

        # Bind click event
        day_frame.bind("<Button-1>", lambda e, d=day_date: self.select_date(d))
        day_label.bind("<Button-1>", lambda e, d=day_date: self.select_date(d))

        # Store reference
        day_frame.day_date = day_date

        return day_frame

    def update_week_calendar(self):
        """Update week calendar display."""
        if not hasattr(self, 'week_grid'):
            return

        # Clear existing cells
        for widget in self.week_grid.winfo_children():
            widget.destroy()

        # Create hourly slots for each day
        week_dates = get_week_dates(self.current_date)
        today = date.today()

        for hour in range(24):
            # Time label
            time_label = ctk.CTkLabel(
                self.week_grid,
                text=f"{hour:02d}:00",
                font=ctk.CTkFont(size=10),
                text_color=self.theme_manager.get_color("text_secondary")
            )
            time_label.grid(row=hour, column=0, padx=5, pady=1, sticky="e")

            # Day cells
            for day_idx, day_date in enumerate(week_dates):
                day_cell = ctk.CTkFrame(self.week_grid, fg_color="transparent")
                day_cell.grid(row=hour, column=day_idx + 1, padx=1, pady=1, sticky="nsew")

                # Highlight current day/time
                is_today = day_date == today
                is_current_hour = hour == datetime.now().hour

                if is_today and is_current_hour:
                    day_cell.configure(fg_color=self.theme_manager.get_color("surface_variant"))

                # Add tasks for this hour
                hour_tasks = self.get_tasks_for_datetime(day_date, hour)
                for task in hour_tasks[:2]:  # Show max 2 tasks
                    task_label = ctk.CTkLabel(
                        day_cell,
                        text=task.title[:15] + "..." if len(task.title) > 15 else task.title,
                        font=ctk.CTkFont(size=8),
                        anchor="w"
                    )
                    task_label.pack(pady=1, padx=2)

                # Bind click event
                day_cell.bind("<Button-1>", lambda e, d=day_date: self.select_date(d))

    def update_day_calendar(self):
        """Update day calendar display."""
        if not hasattr(self, 'day_schedule'):
            return

        # Clear existing content
        for widget in self.day_schedule.winfo_children():
            widget.destroy()

        # Get tasks for the day
        day_tasks = self.get_tasks_for_date(self.current_date)

        if not day_tasks:
            no_tasks_label = ctk.CTkLabel(
                self.day_schedule,
                text="No tasks scheduled for this day",
                font=ctk.CTkFont(size=14, slant="italic"),
                text_color=self.theme_manager.get_color("text_secondary")
            )
            no_tasks_label.pack(pady=20)
            return

        # Group tasks by time
        tasks_by_time = {}
        for task in day_tasks:
            if task.due_date:
                try:
                    dt = datetime.fromisoformat(task.due_date.replace('Z', '+00:00'))
                    time_key = dt.strftime("%H:%M")
                    if time_key not in tasks_by_time:
                        tasks_by_time[time_key] = []
                    tasks_by_time[time_key].append(task)
                except ValueError:
                    pass

        # Display tasks by time
        for time_key in sorted(tasks_by_time.keys()):
            time_frame = ctk.CTkFrame(self.day_schedule)
            time_frame.pack(fill="x", padx=10, pady=5)

            # Time label
            time_label = ctk.CTkLabel(
                time_frame,
                text=time_key,
                font=ctk.CTkFont(size=12, weight="bold"),
                width=80,
                anchor="w"
            )
            time_label.pack(side="left", padx=10, pady=10)

            # Tasks for this time
            for task in tasks_by_time[time_key]:
                task_item = self.create_day_task_item(time_frame, task)
                task_item.pack(side="left", padx=5, pady=5)

    def create_day_task_item(self, parent, task):
        """Create a task item for day view."""
        task_frame = ctk.CTkFrame(parent)
        task_frame.pack(side="left", padx=2, pady=2)

        # Priority indicator
        priority_color = self.theme_manager.get_priority_color(task.priority)
        priority_label = ctk.CTkLabel(
            task_frame,
            text="●",
            font=ctk.CTkFont(size=10),
            text_color=priority_color
        )
        priority_label.pack(side="left", padx=(5, 2))

        # Task title
        title_text = task.title[:25] + "..." if len(task.title) > 25 else task.title
        title_label = ctk.CTkLabel(
            task_frame,
            text=title_text,
            font=ctk.CTkFont(size=10),
            anchor="w"
        )
        title_label.pack(side="left", padx=2)

        # Bind click event
        task_frame.bind("<Button-1>", lambda e, t=task: self.view_task_details(t))

        return task_frame

    def update_task_panel(self):
        """Update task panel with selected date tasks."""
        # Clear existing tasks
        for widget in self.task_list_frame.winfo_children():
            widget.destroy()

        # Update selected date label
        date_text = self.selected_date.strftime("%A, %B %d, %Y")
        self.selected_date_label.configure(text=date_text)

        # Get tasks for selected date
        tasks = self.get_tasks_for_date(self.selected_date)

        if not tasks:
            no_tasks_label = ctk.CTkLabel(
                self.task_list_frame,
                text="No tasks for this date",
                font=ctk.CTkFont(size=12, slant="italic"),
                text_color=self.theme_manager.get_color("text_secondary")
            )
            no_tasks_label.grid(row=0, column=0, pady=20)
            return

        # Display tasks
        for i, task in enumerate(tasks):
            self.create_panel_task_item(task, i)

    def create_panel_task_item(self, task, index):
        """Create a task item for the panel."""
        task_frame = ctk.CTkFrame(self.task_list_frame)
        task_frame.grid(row=index, column=0, padx=5, pady=3, sticky="ew")
        task_frame.grid_columnconfigure(1, weight=1)

        # Priority indicator
        priority_color = self.theme_manager.get_priority_color(task.priority)
        priority_label = ctk.CTkLabel(
            task_frame,
            text="●",
            font=ctk.CTkFont(size=12),
            text_color=priority_color
        )
        priority_label.grid(row=0, column=0, padx=(10, 5), pady=8)

        # Task title
        title_color = self.theme_manager.get_color("text_secondary") if task.status == "Completed" else self.theme_manager.get_color("text_primary")
        title_label = ctk.CTkLabel(
            task_frame,
            text=task.title,
            font=ctk.CTkFont(size=12),
            text_color=title_color,
            anchor="w"
        )
        title_label.grid(row=0, column=1, padx=(0, 10), pady=8, sticky="w")

        # Time
        if task.due_date:
            try:
                dt = datetime.fromisoformat(task.due_date.replace('Z', '+00:00'))
                time_text = dt.strftime("%I:%M %p")
                time_label = ctk.CTkLabel(
                    task_frame,
                    text=time_text,
                    font=ctk.CTkFont(size=10),
                    text_color=self.theme_manager.get_color("text_secondary")
                )
                time_label.grid(row=0, column=2, padx=(0, 10), pady=8)
            except ValueError:
                pass

        # Bind click event
        task_frame.bind("<Button-1>", lambda e, t=task: self.view_task_details(t))

        return task_frame

    # Navigation methods
    def navigate_previous(self):
        """Navigate to previous period."""
        if self.view_mode == "month":
            # Previous month
            if self.current_date.month == 1:
                self.current_date = self.current_date.replace(year=self.current_date.year - 1, month=12)
            else:
                self.current_date = self.current_date.replace(month=self.current_date.month - 1)
        elif self.view_mode == "week":
            # Previous week
            self.current_date = self.current_date - timedelta(weeks=1)
        elif self.view_mode == "day":
            # Previous day
            self.current_date = self.current_date - timedelta(days=1)

        self.refresh_calendar()

    def navigate_next(self):
        """Navigate to next period."""
        if self.view_mode == "month":
            # Next month
            if self.current_date.month == 12:
                self.current_date = self.current_date.replace(year=self.current_date.year + 1, month=1)
            else:
                self.current_date = self.current_date.replace(month=self.current_date.month + 1)
        elif self.view_mode == "week":
            # Next week
            self.current_date = self.current_date + timedelta(weeks=1)
        elif self.view_mode == "day":
            # Next day
            self.current_date = self.current_date + timedelta(days=1)

        self.refresh_calendar()

    def go_to_today(self):
        """Navigate to today."""
        self.current_date = date.today()
        self.selected_date = date.today()
        self.refresh_calendar()

    def change_view_mode(self, mode):
        """Change calendar view mode."""
        self.view_mode = mode
        self.refresh_calendar()

    def select_date(self, selected_date: date):
        """Select a date."""
        self.selected_date = selected_date

        # Update display
        if self.view_mode == "month":
            self.update_month_calendar()
        elif self.view_mode == "week":
            self.update_week_calendar()

        # Update task panel
        self.update_task_panel()

        if self.app_instance:
            self.app_instance.set_status(f"Selected: {selected_date.strftime('%B %d, %Y')}")

    # Data methods
    def refresh_calendar(self):
        """Refresh calendar display."""
        try:
            # Load tasks
            self.tasks = self.db.get_all_tasks()

            # Update date label
            self.update_date_label()

            # Update view
            if self.view_mode == "month":
                self.update_month_calendar()
            elif self.view_mode == "week":
                self.update_week_calendar()
            elif self.view_mode == "day":
                self.update_day_calendar()

            # Update task panel
            self.update_task_panel()

            if self.app_instance:
                self.app_instance.set_status("Calendar refreshed")

        except Exception as e:
            print(f"Error refreshing calendar: {e}")
            if self.app_instance:
                self.app_instance.set_status("Error loading calendar")

    def update_date_label(self):
        """Update the date label in header."""
        if self.view_mode == "month":
            month_name = calendar.month_name[self.current_date.month]
            self.date_label.configure(text=f"{month_name} {self.current_date.year}")
        elif self.view_mode == "week":
            week_dates = get_week_dates(self.current_date)
            start_date = week_dates[0].strftime("%b %d")
            end_date = week_dates[-1].strftime("%b %d, %Y")
            self.date_label.configure(text=f"{start_date} - {end_date}")
        elif self.view_mode == "day":
            day_name = self.current_date.strftime("%A, %B %d, %Y")
            self.date_label.configure(text=day_name)

    def get_tasks_for_date(self, target_date: date) -> List[Task]:
        """Get tasks for a specific date."""
        return [task for task in self.tasks if task.due_date and task.is_due_today()]

    def get_tasks_for_datetime(self, target_date: date, hour: int) -> List[Task]:
        """Get tasks for a specific date and hour."""
        tasks_for_date = self.get_tasks_for_date(target_date)
        tasks_for_hour = []

        for task in tasks_for_date:
            if task.due_date:
                try:
                    dt = datetime.fromisoformat(task.due_date.replace('Z', '+00:00'))
                    if dt.hour == hour:
                        tasks_for_hour.append(task)
                except ValueError:
                    pass

        return tasks_for_hour

    # Action methods
    def new_task_for_date(self):
        """Create new task for selected date."""
        try:
            from .task_form import ModernTaskForm

            # Pre-fill due date
            task_data = {}
            if self.selected_date:
                # Set to end of selected date
                due_datetime = datetime.combine(self.selected_date, datetime.now().time().replace(hour=23, minute=59))
                task_data["due_date"] = due_datetime.strftime("%Y-%m-%d %H:%M")

            # Create temporary task with pre-filled data
            from ...database.models import Task
            temp_task = Task(task_data)

            form = ModernTaskForm(self.parent, temp_task, on_save=self.refresh_calendar)
            self.wait_window(form)

        except ImportError:
            if self.app_instance:
                self.app_instance.show_info("Task form component not available yet")
        except Exception as e:
            if self.app_instance:
                self.app_instance.show_error(f"Error opening task form: {str(e)}")

    def view_task_details(self, task):
        """View task details."""
        if self.app_instance:
            details = f"Task: {task.title}\n"
            details += f"Status: {task.status}\n"
            details += f"Priority: {task.priority}\n"
            if task.due_date:
                details += f"Due: {format_datetime(task.due_date, 'display')}\n"
            if task.description:
                details += f"Description: {task.description}"

            self.app_instance.show_info(details)