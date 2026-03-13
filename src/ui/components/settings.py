"""
Settings View component for the task scheduler application.
Provides configuration options for app appearance, notifications, and data management.
"""

import os
import sys
from datetime import datetime
from typing import Dict, Any

import customtkinter as ctk
from tkinter import messagebox, filedialog

# Imports using absolute paths (compatible with main.py's sys.path setup)
from database.manager import DatabaseManager
from ui.themes.theme_manager import get_theme_manager
from utils.config import get_config
from core.task_manager import TaskManager


class ModernSettings(ctk.CTkFrame):
    """Modern settings view with configuration options."""

    def __init__(self, parent, app_instance=None):
        super().__init__(parent)
        self.parent = parent
        self.app_instance = app_instance
        self.theme_manager = get_theme_manager()
        self.config = get_config()
        self.db = DatabaseManager()
        self.task_manager = TaskManager()

        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Create UI
        self.create_header()
        self.create_settings_content()

    def create_header(self):
        """Create the settings header."""
        header_frame = ctk.CTkFrame(self, height=80)
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        header_frame.grid_columnconfigure(1, weight=1)
        header_frame.grid_propagate(False)

        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text="⚙️ Settings",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=20, pady=20, sticky="w")

    def create_settings_content(self):
        """Create the main settings content area."""
        content_frame = ctk.CTkScrollableFrame(self)
        content_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        content_frame.grid_columnconfigure(0, weight=1)

        # Appearance settings
        self.create_appearance_section(content_frame, 0)

        # Notifications settings
        self.create_notifications_section(content_frame, 1)

        # General settings
        self.create_general_section(content_frame, 2)

        # Data management
        self.create_data_section(content_frame, 3)

        # About section
        self.create_about_section(content_frame, 4)

    def create_appearance_section(self, parent, row):
        """Create appearance settings section."""
        section = self.create_section(parent, "🎨 Appearance", row)

        # Theme toggle
        theme_frame = ctk.CTkFrame(section, fg_color="transparent")
        theme_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=10)
        theme_frame.grid_columnconfigure(1, weight=1)

        label = ctk.CTkLabel(theme_frame, text="Theme Mode:", font=ctk.CTkFont(size=13))
        label.grid(row=0, column=0, sticky="w")

        theme_btn = ctk.CTkButton(
            theme_frame,
            text="🌙 Toggle Dark/Light",
            command=self.toggle_theme,
            width=150
        )
        theme_btn.grid(row=0, column=2, padx=10, sticky="e")

    def create_notifications_section(self, parent, row):
        """Create notifications settings section."""
        section = self.create_section(parent, "🔔 Notifications", row)

        # Notification settings
        settings = [
            ("Enable Desktop Notifications", "notifications_enabled", True),
            ("Enable Sound Alerts", "sound_enabled", True),
            ("Show Notification Badges", "show_badges", True),
        ]

        for i, (text, key, default) in enumerate(settings):
            setting_frame = ctk.CTkFrame(section, fg_color="transparent")
            setting_frame.grid(row=i, column=0, sticky="ew", padx=20, pady=5)
            setting_frame.grid_columnconfigure(1, weight=1)

            label = ctk.CTkLabel(setting_frame, text=text, font=ctk.CTkFont(size=13))
            label.grid(row=0, column=0, sticky="w")

            switch = ctk.CTkSwitch(
                setting_frame,
                text="",
                command=lambda k=key: self.toggle_setting(k)
            )
            if self.config.get(key, default):
                switch.select()
            switch.grid(row=0, column=2, padx=10, sticky="e")

    def create_general_section(self, parent, row):
        """Create general settings section."""
        section = self.create_section(parent, "⚙️ General", row)

        # Minimize to tray option
        min_frame = ctk.CTkFrame(section, fg_color="transparent")
        min_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=10)
        min_frame.grid_columnconfigure(1, weight=1)

        label = ctk.CTkLabel(min_frame, text="Minimize to System Tray:", font=ctk.CTkFont(size=13))
        label.grid(row=0, column=0, sticky="w")

        switch = ctk.CTkSwitch(
            min_frame,
            text="",
            command=lambda: self.toggle_setting("minimize_to_tray")
        )
        if self.config.get("minimize_to_tray", True):
            switch.select()
        switch.grid(row=0, column=2, padx=10, sticky="e")

    def create_data_section(self, parent, row):
        """Create data management section."""
        section = self.create_section(parent, "💾 Data Management", row)

        # Backup button
        backup_btn = ctk.CTkButton(
            section,
            text="📁 Backup Database",
            command=self.backup_database,
            width=200
        )
        backup_btn.grid(row=0, column=0, padx=20, pady=5,sticky="w")

        # Restore button
        restore_btn = ctk.CTkButton(
            section,
            text="📥 Restore from Backup",
            command=self.restore_database,
            width=200
        )
        restore_btn.grid(row=1, column=0, padx=20, pady=5, sticky="w")

        # Export tasks
        export_btn = ctk.CTkButton(
            section,
            text="📤 Export All Tasks",
            command=self.export_tasks,
            width=200
        )
        export_btn.grid(row=2, column=0, padx=20, pady=5, sticky="w")

        # Clear completed tasks
        clear_btn = ctk.CTkButton(
            section,
            text="🗑️ Clear Completed Tasks",
            command=self.clear_completed,
            width=200,
            fg_color="red",
            hover_color="darkred"
        )
        clear_btn.grid(row=3, column=0, padx=20, pady=5, sticky="w")

    def create_about_section(self, parent, row):
        """Create about section."""
        section = self.create_section(parent, "ℹ️ About", row)

        info_text = """Task Scheduler Pro v1.0.0

A modern task management application
Built with Python & CustomTkinter

© 2024 Task Scheduler Pro Team"""

        info_label = ctk.CTkLabel(
            section,
            text=info_text,
            font=ctk.CTkFont(size=12),
            justify="left"
        )
        info_label.grid(row=0, column=0, padx=20, pady=15, sticky="w")

    def create_section(self, parent, title: str, row: int):
        """Create a settings section."""
        section_frame = ctk.CTkFrame(parent)
        section_frame.grid(row=row, column=0, sticky="ew", padx=10, pady=10)
        section_frame.grid_columnconfigure(0, weight=1)

        # Section header
        header_label = ctk.CTkLabel(
            section_frame,
            text=title,
            font=ctk.CTkFont(size=18, weight="bold")
        )
        header_label.grid(row=0, column=0, padx=20, pady=(15, 10), sticky="w")

        # Content container
        content_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        content_frame.grid(row=1, column=0, sticky="ew", padx=0, pady=(0, 15))
        content_frame.grid_columnconfigure(0, weight=1)

        return content_frame

    def toggle_theme(self):
        """Toggle between dark and light themes."""
        try:
            new_theme = self.theme_manager.toggle_theme()
            if self.app_instance:
                self.app_instance._apply_theme()
                self.app_instance.set_status(f"Switched to {new_theme} theme")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to toggle theme: {str(e)}")

    def toggle_setting(self, setting_key: str):
        """Toggle a boolean setting."""
        try:
            current_value = self.config.get(setting_key, False)
            self.config.set(setting_key, not current_value)
            if self.app_instance:
                self.app_instance.set_status(f"Setting updated: {setting_key}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update setting: {str(e)}")

    def backup_database(self):
        """Create a database backup."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"data/backups/backup_{timestamp}.db"
            os.makedirs("data/backups", exist_ok=True)
            
            self.db.backup_database(backup_path)
            messagebox.showinfo("Success", f"Database backed up to:\n{backup_path}")
            
            if self.app_instance:
                self.app_instance.set_status("Database backup created")
        except Exception as e:
            messagebox.showerror("Error", f"Backup failed: {str(e)}")

    def restore_database(self):
        """Restore database from backup."""
        try:
            file_path = filedialog.askopenfilename(
                title="Select Backup File",
                filetypes=[("Database files", "*.db"), ("All files", "*.*")],
                initialdir="data/backups"
            )
            
            if not file_path:
                return
            
            confirm = messagebox.askyesno(
                "Confirm Restore",
                "This will replace your current database. Continue?"
            )
            
            if confirm:
                self.db.restore_database(file_path)
                messagebox.showinfo("Success", "Database restored successfully!\nPlease restart the application.")
                
                if self.app_instance:
                    self.app_instance.set_status("Database restored")
        except Exception as e:
            messagebox.showerror("Error", f"Restore failed: {str(e)}")

    def export_tasks(self):
        """Export all tasks to file."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_name = f"tasks_export_{timestamp}.json"
            
            file_path = filedialog.asksaveasfilename(
                title="Export Tasks",
                defaultextension=".json",
                initialfile=default_name,
                filetypes=[("JSON files", "*.json"), ("CSV files", "*.csv"), ("All files", "*.*")]
            )
            
            if not file_path:
                return
            
            # Determine format
            format_type = "csv" if file_path.endswith(".csv") else "json"
            
            success, message = self.task_manager.export_tasks(file_path, format_type)
            
            if success:
                messagebox.showinfo("Success", message)
                if self.app_instance:
                    self.app_instance.set_status("Tasks exported")
            else:
                messagebox.showerror("Error", message)
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {str(e)}")

    def clear_completed(self):
        """Clear all completed tasks."""
        try:
            # Get completed tasks count
            tasks = self.db.get_all_tasks({"status": "Completed"})
            count = len(tasks)
            
            if count == 0:
                messagebox.showinfo("Info", "No completed tasks to clear")
                return
            
            confirm = messagebox.askyesno(
                "Confirm Clear",
                f"This will permanently delete {count} completed task(s). Continue?"
            )
            
            if confirm:
                for task in tasks:
                    self.db.delete_task(task.id)
                
                messagebox.showinfo("Success", f"Cleared {count} completed task(s)")
                
                if self.app_instance:
                    self.app_instance.set_status(f"Cleared {count} completed tasks")
                    self.app_instance.refresh_current_view()
        except Exception as e:
            messagebox.showerror("Error", f"Clear failed: {str(e)}")
