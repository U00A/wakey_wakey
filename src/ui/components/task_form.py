"""
Enhanced Task Form component with modern UI and validation.
Provides a comprehensive form for creating and editing tasks.
"""

import os
import sys
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional, Callable

import customtkinter as ctk
from tkinter import messagebox

# Add parent directories to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database.manager import DatabaseManager
from database.models import Task
from ui.themes.theme_manager import get_theme_manager
from utils.validators import ValidationError, validate_task_data, validate_task_title
from core.task_manager import TaskManager


class ModernTaskForm(ctk.CTkToplevel):
    """Modern task form dialog with validation and enhanced UI."""

    def __init__(self, parent, task: Optional[Task] = None, on_save: Optional[Callable] = None):
        super().__init__(parent)

        self.parent = parent
        self.task = task  # None for new task, Task object for editing
        self.on_save = on_save  # Callback function when task is saved
        self.theme_manager = get_theme_manager()

        # Initialize managers
        self.task_manager = TaskManager()
        self.db = DatabaseManager()

        # Form state
        self.is_editing = task is not None
        self.categories = self._load_categories()

        # Configure window
        self.setup_window()

        # Create form components
        self.create_form()

        # Load task data if editing
        if self.is_editing:
            self.load_task_data()

        # Focus on title field
        self.title_entry.focus()

    def setup_window(self):
        """Configure the dialog window."""
        title = "Edit Task" if self.is_editing else "Create New Task"
        self.title(title)

        # Set window size and position
        self.geometry("600x750")
        self.resizable(False, False)

        # Center window relative to parent
        self.transient(self.parent)
        self.grab_set()

        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Apply theme colors
        theme_colors = self.theme_manager.get_theme_colors()
        self.configure(fg_color=theme_colors["background"])

        # Handle window close
        self.protocol("WM_DELETE_WINDOW", self.on_cancel)

    def create_form(self):
        """Create the form content."""
        # Main container
        main_frame = ctk.CTkFrame(self)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        main_frame.grid_columnconfigure(0, weight=1)

        # Header
        self.create_header(main_frame)

        # Form content
        form_frame = ctk.CTkFrame(main_frame)
        form_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 20))
        form_frame.grid_columnconfigure(1, weight=1)

        # Form fields
        self.create_title_field(form_frame)
        self.create_description_field(form_frame)
        self.create_priority_field(form_frame)
        self.create_category_field(form_frame)
        self.create_due_date_field(form_frame)
        self.create_reminder_field(form_frame)
        self.create_recurring_field(form_frame)

        # Action buttons
        self.create_action_buttons(main_frame)

    def create_header(self, parent):
        """Create form header."""
        header_frame = ctk.CTkFrame(parent)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        header_frame.grid_columnconfigure(1, weight=1)

        # Icon and title
        title_text = "✏️ Edit Task" if self.is_editing else "➕ Create New Task"
        title_label = ctk.CTkLabel(
            header_frame,
            text=title_text,
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=20, pady=20, sticky="w")

        # Close button
        close_btn = ctk.CTkButton(
            header_frame,
            text="✕",
            width=30,
            height=30,
            command=self.on_cancel,
            fg_color="transparent",
            text_color=self.theme_manager.get_color("text_secondary"),
            hover_color=self.theme_manager.get_color("surface_variant")
        )
        close_btn.grid(row=0, column=2, padx=20, pady=20, sticky="e")

    def create_title_field(self, parent):
        """Create title input field."""
        # Label
        label = ctk.CTkLabel(
            parent,
            text="Task Title *",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        label.grid(row=0, column=0, padx=20, pady=(15, 5), sticky="w")

        # Input field
        self.title_entry = ctk.CTkEntry(
            parent,
            placeholder_text="Enter task title...",
            height=40
        )
        self.title_entry.grid(row=0, column=1, padx=(0, 20), pady=(15, 5), sticky="ew")

        # Character counter
        counter_frame = ctk.CTkFrame(parent, fg_color="transparent")
        counter_frame.grid(row=1, column=1, padx=(0, 20), pady=(0, 10), sticky="e")

        self.title_counter_label = ctk.CTkLabel(
            counter_frame,
            text="0/200",
            font=ctk.CTkFont(size=10),
            text_color=self.theme_manager.get_color("text_secondary")
        )
        self.title_counter_label.pack(side="right")

        # Bind events
        self.title_entry.bind("<KeyRelease>", self.on_title_change)
        self.title_entry.bind("<FocusOut>", self.validate_title)

        # Error label
        self.title_error_label = ctk.CTkLabel(
            parent,
            text="",
            font=ctk.CTkFont(size=10),
            text_color=self.theme_manager.get_color("priority_high")
        )
        self.title_error_label.grid(row=2, column=1, padx=(0, 20), pady=(0, 10), sticky="w")

    def create_description_field(self, parent):
        """Create description text area."""
        # Label
        label = ctk.CTkLabel(
            parent,
            text="Description",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        label.grid(row=3, column=0, padx=20, pady=(5, 5), sticky="nw")

        # Text area
        self.description_text = ctk.CTkTextbox(
            parent,
            height=100,
            placeholder_text="Add task description (optional)..."
        )
        self.description_text.grid(row=3, column=1, padx=(0, 20), pady=(5, 5), sticky="ew")

        # Character counter
        counter_frame = ctk.CTkFrame(parent, fg_color="transparent")
        counter_frame.grid(row=4, column=1, padx=(0, 20), pady=(0, 10), sticky="e")

        self.desc_counter_label = ctk.CTkLabel(
            counter_frame,
            text="0/2000",
            font=ctk.CTkFont(size=10),
            text_color=self.theme_manager.get_color("text_secondary")
        )
        self.desc_counter_label.pack(side="right")

        # Bind events
        self.description_text.bind("<KeyRelease>", self.on_description_change)

    def create_priority_field(self, parent):
        """Create priority selection field."""
        # Label
        label = ctk.CTkLabel(
            parent,
            text="Priority",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        label.grid(row=5, column=0, padx=20, pady=(5, 5), sticky="w")

        # Priority buttons
        priority_frame = ctk.CTkFrame(parent)
        priority_frame.grid(row=5, column=1, padx=(0, 20), pady=(5, 5), sticky="ew")

        self.priority_var = ctk.StringVar(value="Medium")

        priorities = [
            ("High", self.theme_manager.get_color("priority_high")),
            ("Medium", self.theme_manager.get_color("priority_medium")),
            ("Low", self.theme_manager.get_color("priority_low"))
        ]

        for i, (priority, color) in enumerate(priorities):
            btn = ctk.CTkRadioButton(
                priority_frame,
                text=f"● {priority}",
                variable=self.priority_var,
                value=priority,
                text_color=color,
                font=ctk.CTkFont(size=12, weight="bold")
            )
            btn.grid(row=0, column=i, padx=10, pady=10)

    def create_category_field(self, parent):
        """Create category selection field."""
        # Label
        label = ctk.CTkLabel(
            parent,
            text="Category",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        label.grid(row=6, column=0, padx=20, pady=(5, 5), sticky="w")

        # Category container
        category_frame = ctk.CTkFrame(parent)
        category_frame.grid(row=6, column=1, padx=(0, 20), pady=(5, 5), sticky="ew")
        category_frame.grid_columnconfigure(0, weight=1)

        # Category combobox
        self.category_var = ctk.StringVar(value="Personal")
        category_options = self.categories + ["+ Add New Category"]

        self.category_combobox = ctk.CTkComboBox(
            category_frame,
            variable=self.category_var,
            values=category_options,
            command=self.on_category_change
        )
        self.category_combobox.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        # New category entry (hidden by default)
        self.new_category_entry = ctk.CTkEntry(
            category_frame,
            placeholder_text="Enter new category name...",
            height=30
        )

    def create_due_date_field(self, parent):
        """Create due date field."""
        # Label
        label = ctk.CTkLabel(
            parent,
            text="Due Date & Time",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        label.grid(row=7, column=0, padx=20, pady=(5, 5), sticky="w")

        # Date container
        date_frame = ctk.CTkFrame(parent)
        date_frame.grid(row=7, column=1, padx=(0, 20), pady=(5, 5), sticky="ew")
        date_frame.grid_columnconfigure(1, weight=1)

        # Date picker
        self.date_var = ctk.StringVar()
        self.date_entry = ctk.CTkEntry(
            date_frame,
            textvariable=self.date_var,
            placeholder_text="YYYY-MM-DD HH:MM",
            height=35
        )
        self.date_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        # Quick date buttons
        today_btn = ctk.CTkButton(
            date_frame,
            text="Today",
            command=self.set_today_date,
            width=70,
            height=35
        )
        today_btn.grid(row=0, column=0, padx=(10, 5), pady=10)

        tomorrow_btn = ctk.CTkButton(
            date_frame,
            text="Tomorrow",
            command=self.set_tomorrow_date,
            width=80,
            height=35
        )
        tomorrow_btn.grid(row=0, column=2, padx=(5, 10), pady=10)

        # Clear button
        clear_btn = ctk.CTkButton(
            date_frame,
            text="Clear",
            command=self.clear_due_date,
            width=60,
            height=35,
            fg_color="transparent",
            text_color=self.theme_manager.get_color("text_secondary")
        )
        clear_btn.grid(row=0, column=3, padx=(0, 10), pady=10)

        # Error label
        self.date_error_label = ctk.CTkLabel(
            parent,
            text="",
            font=ctk.CTkFont(size=10),
            text_color=self.theme_manager.get_color("priority_high")
        )
        self.date_error_label.grid(row=8, column=1, padx=(0, 20), pady=(0, 10), sticky="w")

    def create_reminder_field(self, parent):
        """Create reminder field."""
        # Label
        label = ctk.CTkLabel(
            parent,
            text="Reminder",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        label.grid(row=9, column=0, padx=20, pady=(5, 5), sticky="w")

        # Reminder container
        reminder_frame = ctk.CTkFrame(parent)
        reminder_frame.grid(row=9, column=1, padx=(0, 20), pady=(5, 5), sticky="ew")
        reminder_frame.grid_columnconfigure(1, weight=1)

        # Enable reminder checkbox
        self.reminder_enabled_var = ctk.BooleanVar(value=False)
        reminder_checkbox = ctk.CTkCheckBox(
            reminder_frame,
            text="Enable reminder",
            variable=self.reminder_enabled_var,
            command=self.toggle_reminder
        )
        reminder_checkbox.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="w")

        # Reminder time entry (disabled by default)
        self.reminder_var = ctk.StringVar()
        self.reminder_entry = ctk.CTkEntry(
            reminder_frame,
            textvariable=self.reminder_var,
            placeholder_text="YYYY-MM-DD HH:MM",
            height=35,
            state="disabled"
        )
        self.reminder_entry.grid(row=1, column=1, padx=10, pady=(0, 10), sticky="ew")

        # Quick reminder buttons
        self.reminder_15min_btn = ctk.CTkButton(
            reminder_frame,
            text="15 min before",
            command=lambda: self.set_reminder_offset(15),
            width=100,
            height=30,
            state="disabled"
        )
        self.reminder_15min_btn.grid(row=1, column=0, padx=(10, 5), pady=(0, 10))

    def create_recurring_field(self, parent):
        """Create recurring task field."""
        # Label
        label = ctk.CTkLabel(
            parent,
            text="Recurring Task",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        label.grid(row=10, column=0, padx=20, pady=(5, 5), sticky="w")

        # Recurring container
        recurring_frame = ctk.CTkFrame(parent)
        recurring_frame.grid(row=10, column=1, padx=(0, 20), pady=(5, 5), sticky="ew")
        recurring_frame.grid_columnconfigure(1, weight=1)

        # Enable recurring checkbox
        self.recurring_enabled_var = ctk.BooleanVar(value=False)
        recurring_checkbox = ctk.CTkCheckBox(
            recurring_frame,
            text="Make this task recurring",
            variable=self.recurring_enabled_var,
            command=self.toggle_recurring
        )
        recurring_checkbox.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="w")

        # Recurring type
        self.recurring_type_var = ctk.StringVar(value="Daily")
        self.recurring_type_combo = ctk.CTkComboBox(
            recurring_frame,
            variable=self.recurring_type_var,
            values=["Daily", "Weekly", "Monthly", "Custom"],
            state="disabled",
            width=120
        )
        self.recurring_type_combo.grid(row=1, column=0, padx=(10, 5), pady=(0, 10))

        # Interval
        interval_frame = ctk.CTkFrame(recurring_frame, fg_color="transparent")
        interval_frame.grid(row=1, column=1, padx=(5, 10), pady=(0, 10), sticky="ew")

        self.recurring_interval_var = ctk.StringVar(value="1")
        self.recurring_interval_entry = ctk.CTkEntry(
            interval_frame,
            textvariable=self.recurring_interval_var,
            placeholder_text="Interval",
            width=60,
            height=30,
            state="disabled"
        )
        self.recurring_interval_entry.pack(side="left")

        interval_label = ctk.CTkLabel(interval_frame, text="times")
        interval_label.pack(side="left", padx=(5, 0))

    def create_action_buttons(self, parent):
        """Create action buttons."""
        button_frame = ctk.CTkFrame(parent)
        button_frame.grid(row=2, column=0, sticky="ew")
        button_frame.grid_columnconfigure(1, weight=1)

        # Cancel button
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.on_cancel,
            width=120,
            height=40,
            fg_color="transparent",
            text_color=self.theme_manager.get_color("text_primary"),
            border_width=1,
            border_color=self.theme_manager.get_color("border")
        )
        cancel_btn.grid(row=0, column=0, padx=10, pady=20)

        # Save button
        save_text = "Update Task" if self.is_editing else "Create Task"
        self.save_button = ctk.CTkButton(
            button_frame,
            text=save_text,
            command=self.on_save_task,
            width=120,
            height=40,
            fg_color=self.theme_manager.get_color("primary")
        )
        self.save_button.grid(row=0, column=2, padx=10, pady=20)

    # Event handlers
    def on_title_change(self, event=None):
        """Handle title field change."""
        text = self.title_entry.get()
        length = len(text)
        self.title_counter_label.configure(text=f"{length}/200")

        # Change color based on length
        if length > 180:
            self.title_counter_label.configure(text_color=self.theme_manager.get_color("priority_high"))
        elif length > 150:
            self.title_counter_label.configure(text_color=self.theme_manager.get_color("priority_medium"))
        else:
            self.title_counter_label.configure(text_color=self.theme_manager.get_color("text_secondary"))

    def on_description_change(self, event=None):
        """Handle description field change."""
        text = self.description_text.get("1.0", "end-1c")
        length = len(text)
        self.desc_counter_label.configure(text=f"{length}/2000")

        # Change color based on length
        if length > 1900:
            self.desc_counter_label.configure(text_color=self.theme_manager.get_color("priority_high"))
        elif length > 1800:
            self.desc_counter_label.configure(text_color=self.theme_manager.get_color("priority_medium"))
        else:
            self.desc_counter_label.configure(text_color=self.theme_manager.get_color("text_secondary"))

    def validate_title(self, event=None):
        """Validate title field."""
        title = self.title_entry.get().strip()
        try:
            validate_task_title(title)
            self.title_error_label.configure(text="")
            self.title_entry.configure(border_color=self.theme_manager.get_color("border"))
            return True
        except ValidationError as e:
            self.title_error_label.configure(text=str(e))
            self.title_entry.configure(border_color=self.theme_manager.get_color("priority_high"))
            return False

    def on_category_change(self, choice):
        """Handle category selection change."""
        if choice == "+ Add New Category":
            self.show_new_category_dialog()

    def show_new_category_dialog(self):
        """Show dialog to add new category."""
        # Reset selection
        self.category_combobox.set(self.categories[0] if self.categories else "Personal")

        # Create simple dialog
        dialog = ctk.CTkInputDialog(
            text="Enter new category name:",
            title="Add New Category"
        )

        new_category = dialog.get_input()
        if new_category and new_category.strip():
            # Add new category to list
            self.categories.append(new_category.strip())
            self.category_combobox.configure(values=self.categories + ["+ Add New Category"])
            self.category_combobox.set(new_category.strip())

    def toggle_reminder(self):
        """Toggle reminder field state."""
        enabled = self.reminder_enabled_var.get()
        state = "normal" if enabled else "disabled"

        self.reminder_entry.configure(state=state)
        self.reminder_15min_btn.configure(state=state)

        # Auto-set reminder time if enabled and due date is set
        if enabled and self.date_var.get():
            self.set_reminder_offset(15)  # Default 15 minutes before

    def toggle_recurring(self):
        """Toggle recurring field state."""
        enabled = self.recurring_enabled_var.get()
        state = "normal" if enabled else "disabled"

        self.recurring_type_combo.configure(state=state)
        self.recurring_interval_entry.configure(state=state)

    def set_today_date(self):
        """Set due date to today."""
        now = datetime.now()
        # Set to end of current day
        today_end = now.replace(hour=23, minute=59, second=0, microsecond=0)
        self.date_var.set(today_end.strftime("%Y-%m-%d %H:%M"))

    def set_tomorrow_date(self):
        """Set due date to tomorrow."""
        tomorrow = datetime.now() + timedelta(days=1)
        tomorrow_end = tomorrow.replace(hour=23, minute=59, second=0, microsecond=0)
        self.date_var.set(tomorrow_end.strftime("%Y-%m-%d %H:%M"))

    def clear_due_date(self):
        """Clear due date."""
        self.date_var.set("")
        self.reminder_var.set("")
        self.reminder_enabled_var.set(False)
        self.toggle_reminder()

    def set_reminder_offset(self, minutes_before):
        """Set reminder time based on due date offset."""
        if self.date_var.get():
            try:
                due_date = datetime.strptime(self.date_var.get(), "%Y-%m-%d %H:%M")
                reminder_time = due_date - timedelta(minutes=minutes_before)
                self.reminder_var.set(reminder_time.strftime("%Y-%m-%d %H:%M"))
            except ValueError:
                pass  # Invalid date format

    def load_task_data(self):
        """Load existing task data for editing."""
        if not self.task:
            return

        # Load basic fields
        self.title_entry.insert(0, self.task.title)
        if self.task.description:
            self.description_text.insert("1.0", self.task.description)

        self.priority_var.set(self.task.priority)
        self.category_var.set(self.task.category)

        if self.task.due_date:
            # Format datetime for display
            try:
                dt = datetime.fromisoformat(self.task.due_date.replace('Z', '+00:00'))
                self.date_var.set(dt.strftime("%Y-%m-%d %H:%M"))
            except ValueError:
                self.date_var.set(self.task.due_date)

        if self.task.reminder_time:
            try:
                dt = datetime.fromisoformat(self.task.reminder_time.replace('Z', '+00:00'))
                self.reminder_var.set(dt.strftime("%Y-%m-%d %H:%M"))
                self.reminder_enabled_var.set(True)
                self.toggle_reminder()
            except ValueError:
                self.reminder_var.set(self.task.reminder_time)
                self.reminder_enabled_var.set(True)
                self.toggle_reminder()

        if self.task.recurring_type and self.task.recurring_type != "None":
            self.recurring_enabled_var.set(True)
            self.recurring_type_var.set(self.task.recurring_type)
            self.recurring_interval_var.set(str(self.task.recurring_interval))
            self.toggle_recurring()

        # Update counters
        self.on_title_change()
        self.on_description_change()

    def _load_categories(self) -> List[str]:
        """Load categories from database."""
        try:
            categories = self.db.get_all_categories()
            return [cat.name for cat in categories]
        except:
            return ["Personal", "Work", "Health", "Shopping", "Study"]

    def validate_form(self) -> bool:
        """Validate all form fields."""
        is_valid = True

        # Validate title
        if not self.validate_title():
            is_valid = False

        # Validate due date if provided
        if self.date_var.get():
            try:
                datetime.strptime(self.date_var.get(), "%Y-%m-%d %H:%M")
                self.date_error_label.configure(text="")
            except ValueError:
                self.date_error_label.configure(text="Invalid date format. Use YYYY-MM-DD HH:MM")
                is_valid = False

        # Validate reminder if enabled
        if self.reminder_enabled_var.get() and self.reminder_var.get():
            try:
                reminder_dt = datetime.strptime(self.reminder_var.get(), "%Y-%m-%d %H:%M")
                if self.date_var.get():
                    due_dt = datetime.strptime(self.date_var.get(), "%Y-%m-%d %H:%M")
                    if reminder_dt >= due_dt:
                        self.date_error_label.configure(text="Reminder must be before due date")
                        is_valid = False
            except ValueError:
                self.date_error_label.configure(text="Invalid reminder date format")
                is_valid = False

        return is_valid

    def get_task_data(self) -> Dict[str, Any]:
        """Get task data from form."""
        return {
            "title": self.title_entry.get().strip(),
            "description": self.description_text.get("1.0", "end-1c").strip(),
            "priority": self.priority_var.get(),
            "category": self.category_var.get(),
            "due_date": self.date_var.get() if self.date_var.get() else None,
            "reminder_time": self.reminder_var.get() if self.reminder_enabled_var.get() else None,
            "recurring_type": self.recurring_type_var.get() if self.recurring_enabled_var.get() else "None",
            "recurring_interval": int(self.recurring_interval_var.get()) if self.recurring_enabled_var.get() else 1
        }

    def on_save_task(self):
        """Handle save task button click."""
        if not self.validate_form():
            messagebox.showerror("Validation Error", "Please fix the errors before saving.")
            return

        try:
            task_data = self.get_task_data()

            if self.is_editing:
                # Update existing task
                success, message = self.task_manager.update_task(self.task.id, task_data)
                if success:
                    messagebox.showinfo("Success", "Task updated successfully!")
                    if self.on_save:
                        self.on_save()
                    self.destroy()
                else:
                    messagebox.showerror("Error", f"Failed to update task: {message}")
            else:
                # Create new task
                success, task_id, message = self.task_manager.create_task(task_data)
                if success:
                    messagebox.showinfo("Success", "Task created successfully!")
                    if self.on_save:
                        self.on_save()
                    self.destroy()
                else:
                    messagebox.showerror("Error", f"Failed to create task: {message}")

        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")

    def on_cancel(self):
        """Handle cancel button click."""
        if messagebox.askyesno("Cancel", "Are you sure you want to discard your changes?"):
            self.destroy()