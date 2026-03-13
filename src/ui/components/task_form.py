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

# Imports using absolute paths (compatible with main.py's sys.path setup)
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
        # Main container with distinct sections
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)

        # Header (Fixed at top)
        self.create_header(main_frame)

        # Scrollable Form Content
        form_scroll = ctk.CTkScrollableFrame(main_frame, fg_color="transparent")
        form_scroll.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        form_scroll.grid_columnconfigure(0, weight=1)

        # Form Sections
        self.create_title_section(form_scroll)
        self.create_details_section(form_scroll)
        self.create_schedule_section(form_scroll)
        self.create_extras_section(form_scroll)

        # Footer Actions (Fixed at bottom)
        self.create_action_buttons(main_frame)

    def create_header(self, parent):
        """Create form header."""
        header_frame = ctk.CTkFrame(parent, height=70, corner_radius=0)
        header_frame.grid(row=0, column=0, sticky="ew")
        header_frame.grid_columnconfigure(1, weight=1)
        header_frame.grid_propagate(False)

        # Icon and title
        title_text = "Edit Task" if self.is_editing else "New Task"
        icon_text = "✏️" if self.is_editing else "✨"
        
        title_label = ctk.CTkLabel(
            header_frame,
            text=f"{icon_text}  {title_text}",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=25, pady=20, sticky="w")

        # Close button
        close_btn = ctk.CTkButton(
            header_frame,
            text="✕",
            width=32,
            height=32,
            command=self.on_cancel,
            fg_color="transparent",
            text_color=self.theme_manager.get_color("text_secondary"),
            hover_color=self.theme_manager.get_color("surface_variant"),
            corner_radius=16
        )
        close_btn.grid(row=0, column=2, padx=20, pady=20, sticky="e")
        
        # Divider
        divider = ctk.CTkFrame(header_frame, height=2, fg_color=self.theme_manager.get_color("border"))
        divider.place(relx=0, rely=1, relwidth=1, anchor="sw")

    def create_title_section(self, parent):
        """Create title and basic info section."""
        section_frame = ctk.CTkFrame(parent, fg_color="transparent")
        section_frame.pack(fill="x", padx=25, pady=(25, 15))
        section_frame.grid_columnconfigure(0, weight=1)

        # Title Input (Large, like a document header)
        self.title_entry = ctk.CTkEntry(
            section_frame,
            placeholder_text="What needs to be done?",
            height=50,
            font=ctk.CTkFont(size=18, weight="bold"),
            border_width=0,
            fg_color=self.theme_manager.get_color("surface_variant") # Slight background contrast
        )
        self.title_entry.grid(row=0, column=0, sticky="ew")
        
        # Add a subtle bottom border effect manually if needed, or rely on entry style
        
        # Character count and error in one line below
        meta_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        meta_frame.grid(row=1, column=0, sticky="ew", pady=(5,0))
        meta_frame.grid_columnconfigure(0, weight=1)
        
        self.title_error_label = ctk.CTkLabel(
            meta_frame,
            text="",
            font=ctk.CTkFont(size=11),
            text_color=self.theme_manager.get_color("priority_high")
        )
        self.title_error_label.grid(row=0, column=0, sticky="w")

        self.title_counter_label = ctk.CTkLabel(
            meta_frame,
            text="0/200",
            font=ctk.CTkFont(size=11),
            text_color=self.theme_manager.get_color("text_secondary")
        )
        self.title_counter_label.grid(row=0, column=1, sticky="e")

        # Bind events
        self.title_entry.bind("<KeyRelease>", self.on_title_change)
        self.title_entry.bind("<FocusOut>", self.validate_title)

    def create_details_section(self, parent):
        """Create description, priority and category."""
        section_frame = ctk.CTkFrame(parent, fg_color="transparent")
        section_frame.pack(fill="x", padx=25, pady=10)
        section_frame.grid_columnconfigure(1, weight=1)

        # Description
        desc_label = ctk.CTkLabel(
            section_frame, 
            text="DESCRIPTION", 
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=self.theme_manager.get_color("text_secondary")
        )
        desc_label.grid(row=0, column=0, sticky="w", pady=(0, 5))

        self.description_text = ctk.CTkTextbox(
            section_frame,
            height=100,
            wrap="word",
            font=ctk.CTkFont(size=13),
            border_width=1,
            border_color=self.theme_manager.get_color("border")
        )
        self.description_text.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        self.description_text.bind("<KeyRelease>", self.on_description_change)

        # two column layout for Priority and Category
        options_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        options_frame.grid(row=2, column=0, sticky="ew")
        options_frame.grid_columnconfigure(0, weight=1)
        options_frame.grid_columnconfigure(1, weight=1)

        # Priority Column
        priority_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
        priority_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        p_label = ctk.CTkLabel(
            priority_frame, 
            text="PRIORITY", 
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=self.theme_manager.get_color("text_secondary")
        )
        p_label.pack(anchor="w", pady=(0, 8))

        self.priority_var = ctk.StringVar(value="Medium")
        self.priority_seg = ctk.CTkSegmentedButton(
            priority_frame,
            values=["Low", "Medium", "High"],
            variable=self.priority_var,
            selected_color=self.theme_manager.get_color("primary"),
            selected_hover_color=self.theme_manager.get_color("primary_variant"),
            command=self.on_priority_change
        )
        self.priority_seg.pack(fill="x")

        # Category Column
        cat_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
        cat_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        
        c_label = ctk.CTkLabel(
            cat_frame, 
            text="CATEGORY", 
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=self.theme_manager.get_color("text_secondary")
        )
        c_label.pack(anchor="w", pady=(0, 8))

        self.category_var = ctk.StringVar(value="Personal")
        self.category_combobox = ctk.CTkComboBox(
            cat_frame,
            variable=self.category_var,
            values=self.categories + ["+ Add New"]
        )
        self.category_combobox.pack(fill="x")
        
        # Quick Category Chips (Horizontal scroll or just a few items)
        chips_frame = ctk.CTkFrame(cat_frame, fg_color="transparent")
        chips_frame.pack(fill="x", pady=(10, 0))
        
        quick_cats = ["Personal", "Work", "Study"]
        for cat in quick_cats:
            btn = ctk.CTkButton(
                chips_frame,
                text=cat,
                width=60,
                height=24,
                font=ctk.CTkFont(size=11),
                fg_color="transparent",
                border_width=1,
                border_color=self.theme_manager.get_color("border"),
                text_color=self.theme_manager.get_color("text_primary"),
                command=lambda c=cat: self.category_var.set(c)
            )
            btn.pack(side="left", padx=(0, 5))

    def create_schedule_section(self, parent):
        """Create date and time section."""
        section_frame = ctk.CTkFrame(parent, fg_color="transparent")
        section_frame.pack(fill="x", padx=25, pady=20)
        section_frame.grid_columnconfigure(0, weight=1)

        header_label = ctk.CTkLabel(
            section_frame,
            text="SCHEDULE",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=self.theme_manager.get_color("text_secondary")
        )
        header_label.pack(anchor="w", pady=(0, 10))

        # Main Date Input
        input_container = ctk.CTkFrame(section_frame, fg_color="transparent")
        input_container.pack(fill="x")
        
        self.date_var = ctk.StringVar()
        self.date_entry = ctk.CTkEntry(
            input_container,
            textvariable=self.date_var,
            placeholder_text="Select date...",
            width=200,
            height=35
        )
        self.date_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        clear_btn = ctk.CTkButton(
            input_container,
            text="Clear",
            width=60,
            height=35,
            fg_color=self.theme_manager.get_color("surface_variant"),
            text_color=self.theme_manager.get_color("text_primary"),
            hover_color=self.theme_manager.get_color("error"),
            command=self.clear_due_date
        )
        clear_btn.pack(side="right")

        # Quick Actions Grid
        grid_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        grid_frame.pack(fill="x", pady=(10, 0))
        grid_frame.grid_columnconfigure((0,1,2,3), weight=1)
        
        actions = [
            ("Today", self.set_today_date),
            ("Tomorrow", self.set_tomorrow_date),
            ("Weekend", self.set_weekend_date),
            ("Next Week", self.set_next_week_date)
        ]
        
        for i, (text, cmd) in enumerate(actions):
            btn = ctk.CTkButton(
                grid_frame,
                text=text,
                height=32,
                fg_color="transparent",
                border_width=1,
                border_color=self.theme_manager.get_color("border"),
                text_color=self.theme_manager.get_color("text_primary"),
                command=cmd
            )
            btn.grid(row=0, column=i, padx=5 if i > 0 else (0, 5), sticky="ew")

        self.date_error_label = ctk.CTkLabel(
             section_frame, text="", font=ctk.CTkFont(size=11), text_color=self.theme_manager.get_color("priority_high")
        )
        self.date_error_label.pack(anchor="w", pady=(5,0))

    def create_extras_section(self, parent):
        """Create reminder and recurring options."""
        section_frame = ctk.CTkFrame(parent, fg_color="transparent")
        section_frame.pack(fill="x", padx=25, pady=(0, 25))
        
        # Reminder Toggle Row
        self.reminder_enabled_var = ctk.BooleanVar(value=False)
        self.reminder_var = ctk.StringVar()
        
        reminder_frame = ctk.CTkFrame(section_frame, fg_color=self.theme_manager.get_color("surface_variant"))
        reminder_frame.pack(fill="x", pady=(0, 10))
        
        r_chk = ctk.CTkCheckBox(
            reminder_frame,
            text="Set Reminder",
            variable=self.reminder_enabled_var,
            command=self.toggle_reminder,
            font=ctk.CTkFont(size=13)
        )
        r_chk.pack(side="left", padx=15, pady=10)
        
        self.reminder_entry = ctk.CTkEntry(
            reminder_frame,
            textvariable=self.reminder_var,
            placeholder_text="YYYY-MM-DD HH:MM",
            width=150,
            height=30,
            state="disabled"
        )
        self.reminder_entry.pack(side="right", padx=15, pady=10)

        # Recurring Toggle Row
        self.recurring_enabled_var = ctk.BooleanVar(value=False)
        self.recurring_type_var = ctk.StringVar(value="Daily")
        self.recurring_interval_var = ctk.StringVar(value="1")
        
        recur_frame = ctk.CTkFrame(section_frame, fg_color=self.theme_manager.get_color("surface_variant"))
        recur_frame.pack(fill="x")
        
        rc_chk = ctk.CTkCheckBox(
            recur_frame,
            text="Recurring",
            variable=self.recurring_enabled_var,
            command=self.toggle_recurring,
            font=ctk.CTkFont(size=13)
        )
        rc_chk.pack(side="left", padx=15, pady=10)
        
        self.recurring_type_combo = ctk.CTkComboBox(
            recur_frame,
            values=["Daily", "Weekly", "Monthly"],
            variable=self.recurring_type_var,
            width=100,
            height=30,
            state="disabled"
        )
        self.recurring_type_combo.pack(side="right", padx=(5, 15), pady=10)


    def create_action_buttons(self, parent):
        """Create fixed action buttons at bottom."""
        footer_frame = ctk.CTkFrame(parent, height=80, corner_radius=0, fg_color=self.theme_manager.get_color("background"))
        footer_frame.grid(row=2, column=0, sticky="ew")
        footer_frame.grid_columnconfigure(1, weight=1)
        footer_frame.grid_propagate(False) # Keep fixed height

        # Divider top
        div = ctk.CTkFrame(footer_frame, height=2, fg_color=self.theme_manager.get_color("border"))
        div.place(relx=0, rely=0, relwidth=1, anchor="nw")

        # Buttons
        save_text = "Save Changes" if self.is_editing else "Create Task"
        self.save_button = ctk.CTkButton(
            footer_frame,
            text=save_text,
            command=self.on_save_task,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=self.theme_manager.get_color("primary")
        )
        self.save_button.pack(side="right", padx=25, pady=17, fill="x", expand=True)

        cancel_btn = ctk.CTkButton(
            footer_frame,
            text="Cancel",
            command=self.on_cancel,
            height=45,
            width=100,
            fg_color="transparent",
            border_width=1,
            border_color=self.theme_manager.get_color("border"),
            text_color=self.theme_manager.get_color("text_primary")
        )
        cancel_btn.pack(side="right", padx=(25, 10), pady=17)

    # Added methods for new quick actions
    def set_weekend_date(self):
        """Set due date to this coming Saturday."""
        today = datetime.now()
        days_ahead = 5 - today.weekday() # Saturday is 5
        if days_ahead <= 0: # Today is Sat or Sun
            days_ahead += 7
        target = today + timedelta(days=days_ahead)
        target = target.replace(hour=12, minute=0, second=0, microsecond=0)
        self.date_var.set(target.strftime("%Y-%m-%d %H:%M"))

    def set_next_week_date(self):
        """Set due date to next Monday."""
        today = datetime.now()
        days_ahead = 0 - today.weekday() # Monday is 0
        if days_ahead <= 0:
            days_ahead += 7
        target = today + timedelta(days=days_ahead)
        target = target.replace(hour=9, minute=0, second=0, microsecond=0)
        self.date_var.set(target.strftime("%Y-%m-%d %H:%M"))

    def on_priority_change(self, value):
        """Handle priority change for visual feedback."""
        # Optional: Change segmented button color based on priority
        colors = {
            "High": self.theme_manager.get_color("priority_high"),
            "Medium": self.theme_manager.get_color("priority_medium"),
            "Low": self.theme_manager.get_color("priority_low")
        }
        self.priority_seg.configure(selected_color=colors.get(value, self.theme_manager.get_color("primary")))

    # Existing methods update...
    # Event Handlers & Helpers
    def on_title_change(self, event=None):
        """Handle title field change."""
        text = self.title_entry.get()
        length = len(text)
        if hasattr(self, 'title_counter_label'):
            self.title_counter_label.configure(text=f"{length}/200")
            
            if length > 180:
                self.title_counter_label.configure(text_color=self.theme_manager.get_color("priority_high"))
            else:
                self.title_counter_label.configure(text_color=self.theme_manager.get_color("text_secondary"))

    def on_description_change(self, event=None):
        """Handle description field change."""
        # No counter label in new design, pass for now or add logic if needed
        pass

    def validate_title(self, event=None):
        """Validate title field."""
        title = self.title_entry.get().strip()
        try:
            validate_task_title(title)
            if hasattr(self, 'title_error_label'):
                self.title_error_label.configure(text="")
            return True
        except ValidationError as e:
            if hasattr(self, 'title_error_label'):
                self.title_error_label.configure(text=str(e))
            return False

    def on_category_change(self, choice):
        """Handle category selection change."""
        if choice == "+ Add New":
            self.show_new_category_dialog()

    def show_new_category_dialog(self):
        """Show dialog to add new category."""
        # Reset selection to first item
        default = self.categories[0] if self.categories else "Personal"
        self.category_combobox.set(default)
        self.category_var.set(default)

        dialog = ctk.CTkInputDialog(
            text="Enter new category name:",
            title="Add New Category"
        )
        
        new_category = dialog.get_input()
        
        if new_category and new_category.strip():
            cat_name = new_category.strip()
            if cat_name not in self.categories:
                self.categories.append(cat_name)
                self.category_combobox.configure(values=self.categories + ["+ Add New"])
            self.category_combobox.set(cat_name)
            self.category_var.set(cat_name)

    def toggle_reminder(self):
        """Toggle reminder field state."""
        enabled = self.reminder_enabled_var.get()
        state = "normal" if enabled else "disabled"
        
        if hasattr(self, 'reminder_entry'):
            self.reminder_entry.configure(state=state)
            
        # If enabling and date is set, pre-fill
        if enabled and self.date_var.get() and not self.reminder_var.get():
             self.set_reminder_offset(15)

    def toggle_recurring(self):
        """Toggle recurring field state."""
        enabled = self.recurring_enabled_var.get()
        state = "normal" if enabled else "disabled"
        
        if hasattr(self, 'recurring_type_combo'):
            self.recurring_type_combo.configure(state=state)
    
    def set_today_date(self):
        """Set due date to today end of day."""
        now = datetime.now()
        target = now.replace(hour=23, minute=59, second=0, microsecond=0)
        self.date_var.set(target.strftime("%Y-%m-%d %H:%M"))

    def set_tomorrow_date(self):
        """Set due date to tomorrow end of day."""
        now = datetime.now() + timedelta(days=1)
        target = now.replace(hour=23, minute=59, second=0, microsecond=0)
        self.date_var.set(target.strftime("%Y-%m-%d %H:%M"))

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
                pass

    def load_task_data(self):
         # ... reuse existing logic but update for new widgets ...
        """Load existing task data for editing."""
        if not self.task:
            return

        self.title_entry.insert(0, self.task.title)
        if self.task.description:
            self.description_text.insert("1.0", self.task.description)

        self.priority_var.set(self.task.priority)
        self.on_priority_change(self.task.priority) # Update color
        
        self.category_var.set(self.task.category)

        if self.task.due_date:
            try:
                dt = datetime.fromisoformat(self.task.due_date.replace('Z', '+00:00'))
                self.date_var.set(dt.strftime("%Y-%m-%d %H:%M"))
            except ValueError:
                self.date_var.set(self.task.due_date)

        if self.task.reminder_time:
            self.reminder_enabled_var.set(True)
            self.toggle_reminder()
            try:
                dt = datetime.fromisoformat(self.task.reminder_time.replace('Z', '+00:00'))
                self.reminder_var.set(dt.strftime("%Y-%m-%d %H:%M"))
            except ValueError:
                self.reminder_var.set(self.task.reminder_time)

        if self.task.recurring_type and self.task.recurring_type != "None":
            self.recurring_enabled_var.set(True)
            self.toggle_recurring()
            self.recurring_type_var.set(self.task.recurring_type)
            # Interval not in UI currently to simplify, assuming 1 for now or add back if needed

        self.on_title_change()


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