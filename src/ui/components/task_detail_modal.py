"""
Task Detail Modal Dialog component.
Displays comprehensive task information with editing capabilities.
"""

import os
import sys
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional

import customtkinter as ctk
from tkinter import messagebox

# Add parent directories to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ...database.manager import DatabaseManager
from ...database.models import Task, Alarm
from ..themes.theme_manager import get_theme_manager
from ...utils.helpers import format_datetime, format_relative_time
from ...core.task_manager import TaskManager


class TaskDetailModal(ctk.CTkToplevel):
    """Task detail modal dialog with comprehensive information."""

    def __init__(self, parent, task: Task, on_update: Optional[callable] = None, on_delete: Optional[callable] = None):
        super().__init__(parent)

        self.parent = parent
        self.task = task
        self.on_update = on_update
        self.on_delete = on_delete
        self.theme_manager = get_theme_manager()

        # Initialize managers
        self.task_manager = TaskManager()
        self.db = DatabaseManager()

        # Configure window
        self.setup_window()

        # Create UI components
        self.create_header()
        self.create_content()
        self.create_actions()

        # Load task data
        self.load_task_details()

    def setup_window(self):
        """Configure the modal window."""
        self.title("Task Details")
        self.geometry("600x700")
        self.resizable(False, False)

        # Center window relative to parent
        self.transient(self.parent)
        self.grab_set()

        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Apply theme colors
        theme_colors = self.theme_manager.get_theme_colors()
        self.configure(fg_color=theme_colors["background"])

        # Handle window close
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def create_header(self):
        """Create modal header."""
        header_frame = ctk.CTkFrame(self)
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        header_frame.grid_columnconfigure(1, weight=1)

        # Task title
        self.title_label = ctk.CTkLabel(
            header_frame,
            text="",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.title_label.grid(row=0, column=0, padx=20, pady=15, sticky="w")

        # Close button
        close_btn = ctk.CTkButton(
            header_frame,
            text="✕",
            width=30,
            height=30,
            command=self.on_close,
            fg_color="transparent",
            text_color=self.theme_manager.get_color("text_secondary"),
            hover_color=self.theme_manager.get_color("surface_variant")
        )
        close_btn.grid(row=0, column=2, padx=20, pady=15, sticky="e")

    def create_content(self):
        """Create main content area."""
        content_frame = ctk.CTkFrame(self)
        content_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_rowconfigure(0, weight=1)

        # Scrollable content
        self.scrollable_frame = ctk.CTkScrollableFrame(content_frame)
        self.scrollable_frame.grid(row=0, column=0, sticky="nsew")
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

        # Task Information Section
        self.create_task_info_section()

        # Description Section
        self.create_description_section()

        # Metadata Section
        self.create_metadata_section()

        # Alarms Section
        self.create_alarms_section()

        # Activity History Section
        self.create_activity_section()

    def create_task_info_section(self):
        """Create task information section."""
        info_frame = ctk.CTkFrame(self.scrollable_frame)
        info_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        info_frame.grid_columnconfigure(1, weight=1)

        # Section title
        title_label = ctk.CTkLabel(
            info_frame,
            text="📋 Task Information",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=20, pady=(15, 10), sticky="w")

        # Priority and Status
        status_frame = ctk.CTkFrame(info_frame)
        status_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=10, sticky="ew")
        status_frame.grid_columnconfigure(1, weight=1)

        # Priority
        priority_label = ctk.CTkLabel(
            status_frame,
            text="Priority:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        priority_label.grid(row=0, column=0, padx=10, pady=8, sticky="w")

        self.priority_display = ctk.CTkLabel(
            status_frame,
            text="",
            font=ctk.CTkFont(size=12)
        )
        self.priority_display.grid(row=0, column=1, padx=(10, 20), pady=8, sticky="w")

        # Status
        status_label = ctk.CTkLabel(
            status_frame,
            text="Status:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        status_label.grid(row=1, column=0, padx=10, pady=8, sticky="w")

        self.status_display = ctk.CTkLabel(
            status_frame,
            text="",
            font=ctk.CTkFont(size=12)
        )
        self.status_display.grid(row=1, column=1, padx=(10, 20), pady=8, sticky="w")

        # Category
        category_label = ctk.CTkLabel(
            status_frame,
            text="Category:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        category_label.grid(row=2, column=0, padx=10, pady=8, sticky="w")

        self.category_display = ctk.CTkLabel(
            status_frame,
            text="",
            font=ctk.CTkFont(size=12)
        )
        self.category_display.grid(row=2, column=1, padx=(10, 20), pady=8, sticky="w")

    def create_description_section(self):
        """Create description section."""
        desc_frame = ctk.CTkFrame(self.scrollable_frame)
        desc_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        desc_frame.grid_columnconfigure(0, weight=1)

        # Section title
        title_label = ctk.CTkLabel(
            desc_frame,
            text="📄 Description",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=20, pady=(15, 10), sticky="w")

        # Description text
        self.description_text = ctk.CTkTextbox(
            desc_frame,
            height=100,
            state="disabled"
        )
        self.description_text.grid(row=1, column=0, padx=20, pady=(0, 15), sticky="ew")

    def create_metadata_section(self):
        """Create metadata section."""
        meta_frame = ctk.CTkFrame(self.scrollable_frame)
        meta_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        meta_frame.grid_columnconfigure(1, weight=1)

        # Section title
        title_label = ctk.CTkLabel(
            meta_frame,
            text="📅 Dates & Times",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, padx=20, pady=(15, 10), sticky="w")

        # Created At
        created_label = ctk.CTkLabel(
            meta_frame,
            text="Created:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        created_label.grid(row=1, column=0, padx=10, pady=8, sticky="w")

        self.created_display = ctk.CTkLabel(
            meta_frame,
            text="",
            font=ctk.CTkFont(size=12)
        )
        self.created_display.grid(row=1, column=1, padx=(10, 20), pady=8, sticky="w")

        # Updated At
        updated_label = ctk.CTkLabel(
            meta_frame,
            text="Updated:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        updated_label.grid(row=2, column=0, padx=10, pady=8, sticky="w")

        self.updated_display = ctk.CTkLabel(
            meta_frame,
            text="",
            font=ctk.CTkFont(size=12)
        )
        self.updated_display.grid(row=2, column=1, padx=(10, 20), pady=8, sticky="w")

        # Due Date
        due_label = ctk.CTkLabel(
            meta_frame,
            text="Due Date:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        due_label.grid(row=3, column=0, padx=10, pady=8, sticky="w")

        self.due_display = ctk.CTkLabel(
            meta_frame,
            text="",
            font=ctk.CTkFont(size=12)
        )
        self.due_display.grid(row=3, column=1, padx=(10, 20), pady=8, sticky="w")

        # Reminder Time
        reminder_label = ctk.CTkLabel(
            meta_frame,
            text="Reminder:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        reminder_label.grid(row=4, column=0, padx=10, pady=8, sticky="w")

        self.reminder_display = ctk.CTkLabel(
            meta_frame,
            text="",
            font=ctk.CTkFont(size=12)
        )
        self.reminder_display.grid(row=4, column=1, padx=(10, 20), pady=8, sticky="w")

        # Completed At
        completed_label = ctk.CTkLabel(
            meta_frame,
            text="Completed:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        completed_label.grid(row=5, column=0, padx=10, pady=8, sticky="w")

        self.completed_display = ctk.CTkLabel(
            meta_frame,
            text="",
            font=ctk.CTkFont(size=12)
        )
        self.completed_display.grid(row=5, column=1, padx=(10, 20), pady=8, sticky="w")

        # Recurring Information
        if self.task.recurring_type and self.task.recurring_type != "None":
            recurring_label = ctk.CTkLabel(
                meta_frame,
                text="Recurring:",
                font=ctk.Font(size=12, weight="bold")
            )
            recurring_label.grid(row=6, column=0, padx=10, pady=8, sticky="w")

            recurring_text = f"{self.task.recurring_type}"
            if self.task.recurring_interval > 1:
                recurring_text += f" (every {self.task.recurring_interval})"

            self.recurring_display = ctk.CTkLabel(
                meta_frame,
                text=recurring_text,
                font=ctk.CTkFont(size=12)
            )
            self.recurring_display.grid(row=6, column=1, padx=(10, 20), pady=8, sticky="w")

    def create_alarms_section(self):
        """Create alarms section."""
        alarms_frame = ctk.CTkFrame(self.scrollable_frame)
        alarms_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=10)
        alarms_frame.grid_columnconfigure(0, weight=1)

        # Section title
        title_label = ctk.CTkLabel(
            alarms_frame,
            text="⏰ Alarms",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=20, pady=(15, 10), sticky="w")

        # Alarms container
        self.alarms_container = ctk.CTkFrame(alarms_frame)
        self.alarms_container.grid(row=1, column=0, padx=20, pady=(0, 15), sticky="ew")
        self.alarms_container.grid_columnconfigure(0, weight=1)

        # Add alarm button
        add_alarm_btn = ctk.CTkButton(
            alarms_frame,
            text="➕ Add Alarm",
            command=self.add_alarm,
            width=120
        )
        add_alarm_btn.grid(row=2, column=0, padx=20, pady=(0, 15), sticky="w")

    def create_activity_section(self):
        """Create activity history section."""
        activity_frame = ctk.CTkFrame(self.scrollable_frame)
        activity_frame.grid(row=4, column=0, sticky="ew", padx=10, pady=10)
        activity_frame.grid_columnconfigure(0, weight=1)

        # Section title
        title_label = ctk.CTkLabel(
            activity_frame,
            text="📊 Activity History",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=20, pady=(15, 10), sticky="w")

        # Activity container
        self.activity_container = ctk.CTkFrame(activity_frame)
        self.activity_container.grid(row=1, column=0, padx=20, pady=(0, 15), sticky="ew")
        self.activity_container.grid_columnconfigure(0, weight=1)

        # Load activity history
        self.load_activity_history()

    def create_actions(self):
        """Create action buttons."""
        action_frame = ctk.CTkFrame(self)
        action_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 20))
        action_frame.grid_columnconfigure(2, weight=1)

        # Status-dependent buttons
        self.action_buttons_frame = ctk.CTkFrame(action_frame)
        self.action_buttons_frame.grid(row=0, column=0, columnspan=3, sticky="ew")
        action_buttons_frame.grid_columnconfigure(0, weight=1)

        # Edit button
        self.edit_btn = ctk.CTkButton(
            action_buttons_frame,
            text="✏️ Edit Task",
            command=self.edit_task,
            width=120
        )
        self.edit_btn.grid(row=0, column=0, padx=10, pady=20)

        # Complete button (if pending)
        self.complete_btn = ctk.CTkButton(
            action_buttons_frame,
            text="✅ Complete",
            command=self.complete_task,
            width=120,
            fg_color=self.theme_manager.get_color("priority_low")
        )
        self.complete_btn.grid(row=0, column=1, padx=5, pady=20)

        # Delete button
        self.delete_btn = ctk.CTkButton(
            action_buttons_frame,
            text="🗑️ Delete",
            command=self.delete_task,
            width=120,
            fg_color=self.theme_manager.get_color("priority_high")
        )
        self.delete_btn.grid(row=0, column=2, padx=(5, 10), pady=20)

    def load_task_details(self):
        """Load task details into the modal."""
        # Update title
        self.title_label.configure(text=self.task.title)

        # Update priority and status
        self.priority_display.configure(
            text=self.task.priority,
            text_color=self.theme_manager.get_priority_color(self.task.priority)
        )

        status_color = self.theme_manager.get_status_color(self.task.status)
        self.status_display.configure(
            text=self.task.status,
            text_color=status_color
        )

        # Update category
        self.category_display.configure(text=self.task.category)

        # Update description
        if self.task.description:
            self.description_text.delete("1.0", "end")
            self.description_text.insert("1.0", self.task.description)

        # Update dates
        if self.task.created_at:
            try:
                created_dt = datetime.fromisoformat(self.task.created_at.replace('Z', '+00:00'))
                self.created_display.configure(text=format_datetime(created_dt, "display"))
            except ValueError:
                self.created_display.configure(text=self.task.created_at or "N/A")

        if self.task.updated_at:
            try:
                updated_dt = datetime.fromisoformat(self.task.updated_at.replace('Z', '+00:00'))
                self.updated_display.configure(text=format_datetime(updated_dt, "display"))
            except ValueError:
                self.updated_display.configure(text=self.task.updated_at or "N/A")

        if self.task.due_date:
            try:
                due_dt = datetime.fromisoformat(self.task.due_date.replace('Z', '+00:00'))
                due_text = format_datetime(due_dt, "display")

                # Add relative time
                relative = format_relative_time(due_dt)
                self.due_display.configure(text=f"{due_text} ({relative})")

                # Color code overdue tasks
                if self.task.is_overdue():
                    self.due_display.configure(text_color=self.theme_manager.get_color("priority_high"))
            except ValueError:
                self.due_display.configure(text=self.task.due_date or "No due date")
        else:
            self.due_display.configure(text="No due date")

        if self.task.reminder_time:
            try:
                reminder_dt = datetime.fromisoformat(self.task.reminder_time.replace('Z', '+00:00'))
                self.reminder_display.configure(text=format_datetime(reminder_dt, "display"))
            except ValueError:
                self.reminder_display.configure(text=self.task.reminder_time or "No reminder")
        else:
            self.reminder_display.configure(text="No reminder")

        if self.task.completed_at:
            try:
                completed_dt = datetime.fromisoformat(self.task.completed_at.replace('Z', '+00:00'))
                self.completed_display.configure(text=format_datetime(completed_dt, "display"))
            except ValueError:
                self.completed_display.configure(text=self.task.completed_at or "Not completed")
        else:
            self.completed_display.configure(text="Not completed")

        # Load alarms
        self.load_alarms()

        # Update action buttons based on status
        self.update_action_buttons()

    def load_alarms(self):
        """Load alarms for this task."""
        # Clear existing alarms display
        for widget in self.alarms_container.winfo_children():
            widget.destroy()

        # Get alarms from database
        alarms = self.db.get_alarms_for_task(self.task.id)

        if not alarms:
            no_alarms_label = ctk.CTkLabel(
                self.alarms_container,
                text="No alarms set for this task",
                font=ctk.CTkFont(size=12, slant="italic"),
                text_color=self.theme_manager.get_color("text_secondary")
            )
            no_alarms.grid(row=0, column=0, padx=20, pady=20)
        else:
            for i, alarm in enumerate(alarms):
                self.create_alarm_item(alarm, i)

    def create_alarm_item(self, alarm: Alarm, index: int):
        """Create a single alarm item display."""
        alarm_frame = ctk.CTkFrame(self.alarms_container)
        alarm_frame.grid(row=index, column=0, padx=10, pady=5, sticky="ew")
        alarm_frame.grid_columnconfigure(1, weight=1)

        # Alarm time
        try:
            alarm_dt = datetime.fromisoformat(alarm.alarm_time.replace('Z', '+00:00'))
            time_text = format_datetime(alarm_dt, "display")
        except ValueError:
            time_text = alarm.alarm_time or "Unknown"

        time_label = ctk.CTkLabel(
            alarm_frame,
            text=time_text,
            font=ctk.CTkFont(size=12)
        )
        time_label.grid(row=0, column=0, padx=15, pady=10, sticky="w")

        # Status
        status_text = "Active" if alarm.is_active else "Inactive"
        status_color = self.theme_manager.get_color("priority_low") if alarm.is_active else self.theme_manager.get_color("text_secondary")

        status_label = ctk.CTkLabel(
            alarm_frame,
            text=status_text,
            font=ctk.CTkFont(size=10),
            text_color=status_color
        )
        status_label.grid(row=0, column=1, padx=(5, 15), pady=10, sticky="e")

        # Snooze count
        if alarm.snooze_count > 0:
            snooze_label = ctk.CTkLabel(
                alarm_frame,
                text=f"Snoozed {alarm.snooze_count} times",
                font=ctk.CTkFont(size=10),
                text_color=self.theme_manager.get_color("text_secondary")
            )
            snooze_label.grid(row=0, column=2, padx=(5, 15), pady=10, sticky="e")

        # Delete alarm button
        delete_alarm_btn = ctk.CTkButton(
            alarm_frame,
            text="Remove",
            width=60,
            height=25,
            command=lambda a=alarm: self.delete_alarm(a),
            fg_color="transparent",
            text_color=self.theme_manager.get_color("priority_medium"),
            border_width=1,
            border_color=self.theme_manager.get_color("border")
        )
        delete_alarm_btn.grid(row=0, column=3, padx=(0, 10), pady=5)

        # Store alarm reference
        alarm_frame.alarm = alarm

    def load_activity_history(self):
        """Load activity history for the task."""
        # Clear existing activity display
        for widget in self.activity_container.winfo_children():
            widget.destroy()

        # Create activity items based on task changes
        activities = []

        # Task creation
        if self.task.created_at:
            activities.append({
                "action": "Created",
                "timestamp": self.task.created_at,
                "description": f"Task '{self.task.title}' was created"
            })

        # Task updates (simplified - would need change tracking in real implementation)
        if self.task.updated_at and self.task.updated_at != self.task.created_at:
            activities.append({
                "action": "Updated",
                "timestamp": self.task.updated_at,
                "description": f"Task '{self.task.title}' was updated"
            })

        # Task completion
        if self.task.completed_at:
            activities.append({
                "action": "Completed",
                "timestamp": self.task.completed_at,
                "description": f"Task '{self.task.title}' was completed"
            })

        # Sort activities by timestamp (most recent first)
        activities.sort(key=lambda x: x["timestamp"], reverse=True)

        if not activities:
            no_activity_label = ctk.CTkLabel(
                self.activity_container,
                text="No activity history available",
                font=ctk.CTkFont(size=12, slant="italic"),
                text_color=self.theme_manager.get_color("text_secondary")
            )
            no_activity_label.grid(row=0, column=0, padx=20, pady=20)
        else:
            for i, activity in enumerate(activities):
                self.create_activity_item(activity, i)

    def create_activity_item(self, activity: Dict[str, Any], index: int):
        """Create a single activity item display."""
        activity_frame = ctk.CTkFrame(self.activity_container)
        activity_frame.grid(row=index, column=0, padx=10, pady=3, sticky="ew")
        activity_frame.grid_columnconfigure(1, weight=1)

        # Action
        action_colors = {
            "Created": self.theme_manager.get_color("priority_low"),
            "Updated": self.theme_manager.get_color("primary"),
            "Completed": self.theme_manager.get_color("success"),
            "Deleted": self.theme_manager.get_color("priority_high")
        }

        action_color = action_colors.get(activity["action"], self.theme_manager.get_color("text_secondary"))

        action_label = ctk.CTkLabel(
            activity_frame,
            text=activity["action"],
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=action_color,
            width=60
        )
        action_label.grid(row=0, column=0, padx=15, pady=8, sticky="w")

        # Timestamp
        try:
            timestamp = datetime.fromisoformat(activity["timestamp"].replace('Z', '+00:00'))
            time_text = format_datetime(timestamp, "short")
        except ValueError:
            time_text = activity["timestamp"] or "Unknown time"

        time_label = ctk.CTkLabel(
            activity_frame,
            text=time_text,
            font=ctk.CTkFont(size=10),
            text_color=self.theme_manager.get_color("text_secondary")
        )
        time_label.grid(row=0, column=1, padx=(5, 15), pady=8, sticky="w")

        # Description
        desc_label = ctk.CTkLabel(
            activity_frame,
            text=activity["description"],
            font=ctk.CTkFont(size=10),
            text_color=self.theme_manager.get_color("text_primary"),
            anchor="w"
        )
        desc_label.grid(row=1, column=0, columnspan=2, padx=15, pady=(0, 8), sticky="ew")

    def update_action_buttons(self):
        """Update action buttons based on task status."""
        # Remove existing buttons
        for widget in self.action_buttons_frame.winfo_children():
            widget.destroy()

        # Create buttons based on status
        if self.task.status == "Pending":
            # Show complete button
            complete_btn = ctk.CTkButton(
                self.action_buttons_frame,
                text="✅ Complete",
                command=self.complete_task,
                width=120,
                fg_color=self.theme_manager.get_color("priority_low")
            )
            complete_btn.pack(side="left", padx=5, pady=20)

            # Show snooze button if due soon
            if self.task.due_date and self.task.is_due_today():
                snooze_btn = ctk.CTkButton(
                    self.action_buttons_frame,
                    text="⏰ Snooze",
                    command=self.snooze_task,
                    width=120
                )
                snooze_btn.pack(side="left", padx=5, pady=20)

        elif self.task.status == "Completed":
            # Show reopen button
            reopen_btn = ctk.CTkButton(
                self.action_buttons_frame,
                text="🔄 Reopen",
                command=self.reopen_task,
                width=120,
                fg_color=self.theme_manager.get_color("surface_variant")
            )
            reopen_btn.pack(side="left", padx=5, pady=20)

        # Always show edit button
        edit_btn = ctk.CTkButton(
            self.action_buttons_frame,
            text="✏️ Edit",
            command=self.edit_task,
            width=120
        )
        edit_btn.pack(side="left", padx=5, pady=20)

        # Always show delete button (with appropriate styling)
        if self.task.status == "Completed":
            delete_color = self.theme_manager.get_color("surface_variant")
        else:
            delete_color = self.theme_manager.get_color("priority_high")

        delete_btn = ctk.CTkButton(
            self.action_buttons_frame,
            text="🗑️ Delete",
            command=self.delete_task,
            width=120,
            fg_color=delete_color
        )
        delete_btn.pack(side="left", padx=5, pady=20)

    # Action methods
    def edit_task(self):
        """Edit the current task."""
        try:
            from .task_form import ModernTaskForm

            form = ModernTaskForm(self, self.task, on_update=self.on_task_updated)
            self.wait_window(form)

        except ImportError:
            messagebox.showerror("Error", "Task form component not available")
        except Exception as e:
            messagebox.showerror("Error", f"Error opening task form: {str(e)}")

    def complete_task(self):
        """Mark task as completed."""
        try:
            success, message = self.task_manager.update_task(self.task.id, {"status": "Completed"})

            if success:
                self.task = self.task_manager.get_task(self.task.id)
                self.load_task_details()

                if self.on_update:
                    self.on_update(self.task)

                messagebox.showinfo("Success", "Task marked as completed!")
            else:
                messagebox.showerror("Error", f"Failed to complete task: {message}")

        except Exception as e:
            messagebox.showerror("Error", f"Error completing task: {str(e)}")

    def reopen_task(self):
        """Reopen a completed task."""
        try:
            success, message = self.task_manager.update_task(self.task.id, {
                "status": "Pending",
                "completed_at": None
            })

            if success:
                self.task = self.task_manager.get_task(self.task.id)
                self.load_task_details()

                if self.on_update:
                    self.on_update(self.task)

                messagebox.showinfo("Success", "Task reopened!")
            else:
                messagebox.showerror("Error", f"Failed to reopen task: {message}")

        except Exception as e:
            messagebox.showerror("Error", f"Error reopening task: {str(e)}")

    def snooze_task(self):
        """Snooze the task (create a reminder for later)."""
        try:
            # Calculate snooze time (15 minutes from now)
            snooze_time = datetime.now() + timedelta(minutes=15)

            success, message = self.task_manager.update_task(self.task.id, {
                "reminder_time": snooze_time.isoformat()
            })

            if success:
                self.task = self.task_manager.get_task(self.task.id)
                self.load_task_details()

                if self.on_update:
                    self.on_update(self.task)

                messagebox.showinfo("Snoozed", f"Task snoozed for 15 minutes!")
            else:
                messagebox.showerror("Error", f"Failed to snooze task: {message}")

        except Exception as e:
            messagebox.showerror("Error", f"Error snoozing task: {str(e)}")

    def delete_task(self):
        """Delete the task."""
        if messagebox.askyesno("Delete Task", f"Are you sure you want to delete '{self.task.title}'? This action cannot be undone."):
            try:
                success, message = self.task_manager.delete_task(self.task.id)

                if success:
                    if self.on_delete:
                        self.on_delete(self.task)

                    self.destroy()
                    messagebox.showinfo("Deleted", "Task deleted successfully!")
                else:
                    messagebox.showerror("Error", f"Failed to delete task: {message}")

            except Exception as e:
                messagebox.showerror("Error", f"Error deleting task: {str(e)}")

    def add_alarm(self):
        """Add a new alarm for this task."""
        try:
            # Create alarm for 1 hour from now if no due date
            if self.task.due_date:
                try:
                    due_dt = datetime.fromisoformat(self.task.due_date.replace('Z', '+00:00'))
                    alarm_time = due_dt - timedelta(hours=1)
                except ValueError:
                    alarm_time = datetime.now() + timedelta(hours=1)
            else:
                alarm_time = datetime.now() + timedelta(hours=1)

            success = self.task_manager.create_alarm(self.task.id, alarm_time)

            if success:
                self.load_alarms()
                messagebox.showinfo("Success", "Alarm added successfully!")
            else:
                messagebox.showerror("Error", "Failed to add alarm")

        except Exception as e:
            messagebox.showerror("Error", f"Error adding alarm: {str(e)}")

    def delete_alarm(self, alarm: Alarm):
        """Delete an alarm."""
        if messagebox.askyesno("Remove Alarm", "Are you sure you want to remove this alarm?"):
            try:
                success = self.db.delete_alarm(alarm.id)

                if success:
                    self.load_alarms()
                    messagebox.showinfo("Success", "Alarm removed!")
                else:
                    messagebox.showerror("Error", "Failed to remove alarm")

            except Exception as e:
                messagebox.showerror("Error", f"Error removing alarm: {str(e)}")

    def on_task_updated(self, updated_task):
        """Handle task update callback."""
        self.task = updated_task
        self.load_task_details()

    def on_close(self):
        """Handle modal close."""
        self.destroy()


def show_task_detail(parent, task: Task, on_update=None, on_delete=None) -> Optional[TaskDetailModal]:
    """Show task detail modal and return the modal instance."""
    try:
        modal = TaskDetailModal(parent, task, on_update, on_delete)
        return modal
    except Exception as e:
        print(f"Error showing task detail: {e}")
        return None