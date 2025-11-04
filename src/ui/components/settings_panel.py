"""
Comprehensive Settings Panel component with modern UI.
Provides settings management for appearance, notifications, alarms, and data management.
"""

import os
import sys
from typing import List, Dict, Any, Optional

import customtkinter as ctk
from tkinter import messagebox, filedialog

# Add parent directories to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ...utils.config import get_config
from ..themes.theme_manager import get_theme_manager
from ...core.task_manager import TaskManager


class ModernSettingsPanel(ctk.CTkFrame):
    """Modern settings panel with comprehensive configuration options."""

    def __init__(self, parent, app_instance=None):
        super().__init__(parent)
        self.parent = parent
        self.app_instance = app_instance
        self.theme_manager = get_theme_manager()
        self.config = get_config()

        # Initialize managers
        self.task_manager = TaskManager()

        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Create UI components
        self.create_header()
        self.create_settings_content()
        self.create_action_buttons()

    def create_header(self):
        """Create settings header."""
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

        # Save status
        self.save_status_label = ctk.CTkLabel(
            header_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=self.theme_manager.get_color("text_secondary")
        )
        self.save_status_label.grid(row=0, column=2, padx=20, pady=20, sticky="e")

    def create_settings_content(self):
        """Create main settings content with tabs."""
        # Settings container
        settings_container = ctk.CTkFrame(self)
        settings_container.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        settings_container.grid_columnconfigure(1, weight=1)

        # Tab navigation
        self.create_tab_navigation(settings_container)

        # Settings panels
        self.create_appearance_settings(settings_container)
        self.create_notification_settings(settings_container)
        self.create_alarm_settings(settings_container)
        self.create_data_settings(settings_container)
        self.create_advanced_settings(settings_container)

        # Show default tab
        self.switch_tab("appearance")

    def create_tab_navigation(self, parent):
        """Create tab navigation."""
        nav_frame = ctk.CTkFrame(parent)
        nav_frame.grid(row=0, column=0, sticky="ns", padx=(20, 10), pady=20)
        nav_frame.grid_rowconfigure(5, weight=1)

        # Tab buttons
        tabs = [
            ("🎨", "Appearance", "appearance"),
            ("🔔", "Notifications", "notifications"),
            ("⏰", "Alarms", "alarms"),
            ("💾", "Data", "data"),
            ("🔧", "Advanced", "advanced")
        ]

        self.tab_var = ctk.StringVar(value="appearance")

        for i, (icon, text, value) in enumerate(tabs):
            btn = ctk.CTkButton(
                nav_frame,
                text=f"{icon}\n{text}",
                variable=self.tab_var,
                value=value,
                command=lambda v=value: self.switch_tab(v),
                width=120,
                height=60,
                anchor="center"
            )
            btn.grid(row=i, column=0, padx=5, pady=5, sticky="ew")

        # Configure tab buttons for hover effects
        for widget in nav_frame.winfo_children():
            if isinstance(widget, ctk.CTkButton):
                widget.configure(
                    hover_color=self.theme_manager.get_color("surface_variant"),
                    border_width=1,
                    border_color=self.theme_manager.get_color("border")
                )

    def create_appearance_settings(self, parent):
        """Create appearance settings panel."""
        self.appearance_frame = ctk.CTkFrame(parent)
        self.appearance_frame.grid(row=0, column=1, sticky="nsew", padx=(0, 20), pady=20)
        self.appearance_frame.grid_columnconfigure(0, weight=1)

        # Section title
        title_label = ctk.CTkLabel(
            self.appearance_frame,
            text="🎨 Appearance Settings",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        # Theme selection
        theme_frame = ctk.CTkFrame(self.appearance_frame)
        theme_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        theme_frame.grid_columnconfigure(1, weight=1)

        theme_label = ctk.CTkLabel(
            theme_frame,
            text="Theme:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        theme_label.grid(row=0, column=0, padx=20, pady=15, sticky="w")

        self.theme_var = ctk.StringVar(value=self.config.get("theme", "dark"))
        theme_options = ["dark", "light"]
        self.theme_combo = ctk.CTkComboBox(
            theme_frame,
            variable=self.theme_var,
            values=theme_options,
            width=150
        )
        self.theme_combo.grid(row=0, column=1, padx=(10, 20), pady=15, sticky="w")

        # Theme preview
        preview_frame = ctk.CTkFrame(self.appearance_frame)
        preview_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        preview_label = ctk.CTkLabel(
            preview_frame,
            text="Theme Preview",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        preview_label.grid(row=0, column=0, padx=20, pady=(15, 10), sticky="w")

        # Preview buttons
        preview_btns_frame = ctk.CTkFrame(preview_frame)
        preview_btns_frame.grid(row=1, column=0, padx=20, pady=(0, 15), sticky="ew")

        btn1 = ctk.CTkButton(preview_btns_frame, text="Primary Button", width=120)
        btn1.pack(side="left", padx=10, pady=10)

        btn2 = ctk.CTkButton(preview_btns_frame, text="Secondary Button", width=120, fg_color="transparent")
        btn2.pack(side="left", padx=10, pady=10)

        # Font size
        font_frame = ctk.CTkFrame(self.appearance_frame)
        font_frame.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        font_frame.grid_columnconfigure(1, weight=1)

        font_label = ctk.CTkLabel(
            font_frame,
            text="Font Size:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        font_label.grid(row=0, column=0, padx=20, pady=15, sticky="w")

        self.font_var = ctk.StringVar(value=self.config.get("font_size", "medium"))
        font_options = ["small", "medium", "large"]
        self.font_combo = ctk.CTkComboBox(
            font_frame,
            variable=self.font_var,
            values=font_options,
            width=150
        )
        self.font_combo.grid(row=0, column=1, padx=(10, 20), pady=15, sticky="w")

        # Window settings
        window_frame = ctk.CTkFrame(self.appearance_frame)
        window_frame.grid(row=4, column=0, padx=20, pady=10, sticky="ew")
        window_frame.grid_columnconfigure(0, weight=1)

        window_label = ctk.CTkLabel(
            window_frame,
            text="Window Settings",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        window_label.grid(row=0, column=0, padx=20, pady=(15, 10), sticky="w")

        # Start maximized
        self.start_maximized_var = ctk.BooleanVar(value=self.config.get("start_maximized", False))
        start_maximized_cb = ctk.CTkCheckBox(
            window_frame,
            text="Start maximized",
            variable=self.start_maximized_var
        )
        start_maximized_cb.grid(row=1, column=0, padx=20, pady=5, sticky="w")

        # Minimize to tray
        self.minimize_tray_var = ctk.BooleanVar(value=self.config.get("minimize_to_tray", True))
        minimize_tray_cb = ctk.CTkCheckBox(
            window_frame,
            text="Minimize to system tray",
            variable=self.minimize_tray_var
        )
        minimize_tray_cb.grid(row=2, column=0, padx=20, pady=5, sticky="w")

    def create_notification_settings(self, parent):
        """Create notification settings panel."""
        self.notifications_frame = ctk.CTkFrame(parent)
        self.notifications_frame.grid(row=0, column=1, sticky="nsew", padx=(0, 20), pady=20)
        self.notifications_frame.grid_columnconfigure(0, weight=1)

        # Section title
        title_label = ctk.CTkLabel(
            self.notifications_frame,
            text="🔔 Notification Settings",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        # Enable notifications
        enable_frame = ctk.CTkFrame(self.notifications_frame)
        enable_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        enable_frame.grid_columnconfigure(1, weight=1)

        self.enable_notifications_var = ctk.BooleanVar(value=self.config.get("enable_notifications", True))
        enable_cb = ctk.CTkCheckBox(
            enable_frame,
            text="Enable desktop notifications",
            variable=self.enable_notifications_var,
            command=self.toggle_notification_settings
        )
        enable_cb.grid(row=0, column=0, padx=20, pady=15, sticky="w")

        # Notification sound
        self.sound_var = ctk.BooleanVar(value=self.config.get("notification_sound", True))
        sound_cb = ctk.CTkCheckBox(
            enable_frame,
            text="Play sound for notifications",
            variable=self.sound_var
        )
        sound_cb.grid(row=1, column=0, padx=20, pady=5, sticky="w")

        # Volume control
        volume_frame = ctk.CTkFrame(self.notifications_frame)
        volume_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        volume_frame.grid_columnconfigure(1, weight=1)

        volume_label = ctk.CTkLabel(
            volume_frame,
            text="Notification Volume:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        volume_label.grid(row=0, column=0, padx=20, pady=15, sticky="w")

        self.volume_var = ctk.DoubleVar(value=self.config.get("notification_volume", 0.7))
        self.volume_slider = ctk.CTkSlider(
            volume_frame,
            from_=0.0,
            to=1.0,
            variable=self.volume_var,
            width=200
        )
        self.volume_slider.grid(row=0, column=1, padx=(10, 20), pady=15, sticky="w")

        self.volume_label = ctk.CTkLabel(
            volume_frame,
            text=f"{self.volume_var.get():.0%}",
            font=ctk.CTkFont(size=12)
        )
        self.volume_label.grid(row=0, column=2, padx=(0, 20), pady=15)

        self.volume_slider.configure(command=self.update_volume_label)

        # Default reminder time
        reminder_frame = ctk.CTkFrame(self.notifications_frame)
        reminder_frame.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        reminder_frame.grid_columnconfigure(1, weight=1)

        reminder_label = ctk.CTkLabel(
            reminder_frame,
            text="Default Reminder:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        reminder_label.grid(row=0, column=0, padx=20, pady=15, sticky="w")

        self.reminder_var = ctk.IntVar(value=self.config.get("default_reminder_minutes", 15))
        reminder_options = [5, 10, 15, 30, 60, 120]
        self.reminder_combo = ctk.CTkComboBox(
            reminder_frame,
            variable=self.reminder_var,
            values=[f"{m} min" for m in reminder_options],
            width=150
        )
        self.reminder_combo.grid(row=0, column=1, padx=(10, 20), pady=15, sticky="w")

        # Snooze duration
        snooze_frame = ctk.CTkFrame(self.notifications_frame)
        snooze_frame.grid(row=4, column=0, padx=20, pady=10, sticky="ew")
        snooze_frame.grid_columnconfigure(1, weight=1)

        snooze_label = ctk.CTkLabel(
            snooze_frame,
            text="Snooze Duration:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        snooze_label.grid(row=0, column=0, padx=20, pady=15, sticky="w")

        self.snooze_var = ctk.IntVar(value=self.config.get("snooze_duration_minutes", 5))
        snooze_options = [5, 10, 15, 30]
        self.snooze_combo = ctk.CTkComboBox(
            snooze_frame,
            variable=self.snooze_var,
            values=[f"{m} min" for m in snooze_options],
            width=150
        )
        self.snooze_combo.grid(row=0, column=1, padx=(10, 20), pady=15, sticky="w")

        # Max snooze count
        max_snooze_frame = ctk.CTkFrame(self.notifications_frame)
        max_snooze_frame.grid(row=5, column=0, padx=20, pady=10, sticky="ew")
        max_snooze_frame.grid_columnconfigure(1, weight=1)

        max_snooze_label = ctk.CTkLabel(
            max_snooze_frame,
            text="Max Snooze Count:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        max_snooze_label.grid(row=0, column=0, padx=20, pady=15, sticky="w")

        self.max_snooze_var = ctk.IntVar(value=self.config.get("max_snooze_count", 3))
        max_snooze_options = [1, 3, 5, 10]
        self.max_snooze_combo = ctk.CTkComboBox(
            max_snooze_frame,
            variable=self.max_snooze_var,
            values=[str(m) for m in max_snooze_options],
            width=150
        )
        self.max_snooze_combo.grid(row=0, column=1, padx=(10, 20), pady=15, sticky="w")

        # Quiet hours
        quiet_frame = ctk.CTkFrame(self.notifications_frame)
        quiet_frame.grid(row=6, column=0, padx=20, pady=10, sticky="ew")
        quiet_frame.grid_columnconfigure(0, weight=1)

        quiet_title = ctk.CTkLabel(
            quiet_frame,
            text="Quiet Hours",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        quiet_title.grid(row=0, column=0, padx=20, pady=(15, 10), sticky="w")

        self.quiet_enabled_var = ctk.BooleanVar(value=self.config.get("quiet_hours_enabled", False))
        quiet_cb = ctk.CTkCheckBox(
            quiet_frame,
            text="Enable quiet hours",
            variable=self.quiet_enabled_var,
            command=self.toggle_quiet_hours
        )
        quiet_cb.grid(row=1, column=0, padx=20, pady=5, sticky="w")

        # Quiet hours time (initially disabled)
        self.quiet_times_frame = ctk.CTkFrame(quiet_frame)
        self.quiet_times_frame.grid(row=2, column=0, padx=20, pady=(5, 15), sticky="ew")

        start_label = ctk.CTkLabel(self.quiet_times_frame, text="From:")
        start_label.pack(side="left", padx=10, pady=10)

        self.quiet_start_var = ctk.StringVar(value=self.config.get("quiet_hours_start", "22:00"))
        self.quiet_start_entry = ctk.CTkEntry(
            self.quiet_times_frame,
            textvariable=self.quiet_start_var,
            width=80,
            state="disabled"
        )
        self.quiet_start_entry.pack(side="left", padx=5, pady=10)

        end_label = ctk.CTkLabel(self.quiet_times_frame, text="To:")
        end_label.pack(side="left", padx=10, pady=10)

        self.quiet_end_var = ctk.StringVar(value=self.config.get("quiet_hours_end", "08:00"))
        self.quiet_end_entry = ctk.CTkEntry(
            self.quiet_times_frame,
            textvariable=self.quiet_end_var,
            width=80,
            state="disabled"
        )
        self.quiet_end_entry.pack(side="left", padx=5, pady=10)

    def create_alarm_settings(self, parent):
        """Create alarm settings panel."""
        self.alarms_frame = ctk.CTkFrame(parent)
        self.alarms_frame.grid(row=0, column=1, sticky="nsew", padx=(0, 20), pady=20)
        self.alarms_frame.grid_columnconfigure(0, weight=1)

        # Section title
        title_label = ctk.CTkLabel(
            self.alarms_frame,
            text="⏰ Alarm Settings",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        # Persistent alarms
        persistent_frame = ctk.CTkFrame(self.alarms_frame)
        persistent_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        persistent_frame.grid_columnconfigure(1, weight=1)

        self.persistent_var = ctk.BooleanVar(value=self.config.get("persistent_alarms", True))
        persistent_cb = ctk.CTkCheckBox(
            persistent_frame,
            text="Persistent alarms (survive app restart)",
            variable=self.persistent_var
        )
        persistent_cb.grid(row=0, column=0, padx=20, pady=15, sticky="w")

        # Alarm sound file
        sound_frame = ctk.CTkFrame(self.alarms_frame)
        sound_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        sound_frame.grid_columnconfigure(1, weight=1)

        sound_label = ctk.CTkLabel(
            sound_frame,
            text="Alarm Sound:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        sound_label.grid(row=0, column=0, padx=20, pady=15, sticky="w")

        self.alarm_sound_var = ctk.StringVar(value=self.config.get("alarm_sound_file", "default"))
        sound_options = ["default", "gentle", "classic", "digital", "custom"]
        self.alarm_sound_combo = ctk.CTkComboBox(
            sound_frame,
            variable=self.alarm_sound_var,
            values=sound_options,
            width=150
        )
        self.alarm_sound_combo.grid(row=0, column=1, padx=(10, 10), pady=15, sticky="w")

        browse_btn = ctk.CTkButton(
            sound_frame,
            text="Browse",
            command=self.browse_alarm_sound,
            width=80
        )
        browse_btn.grid(row=0, column=2, padx=(0, 20), pady=15)

        # Alarm volume
        alarm_volume_frame = ctk.CTkFrame(self.alarms_frame)
        alarm_volume_frame.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        alarm_volume_frame.grid_columnconfigure(1, weight=1)

        alarm_volume_label = ctk.CTkLabel(
            alarm_volume_frame,
            text="Alarm Volume:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        alarm_volume_label.grid(row=0, column=0, padx=20, pady=15, sticky="w")

        self.alarm_volume_var = ctk.DoubleVar(value=self.config.get("alarm_volume", 0.8))
        self.alarm_volume_slider = ctk.CTkSlider(
            alarm_volume_frame,
            from_=0.0,
            to=1.0,
            variable=self.alarm_volume_var,
            width=200
        )
        self.alarm_volume_slider.grid(row=0, column=1, padx=(10, 20), pady=15, sticky="w")

        self.alarm_volume_label = ctk.CTkLabel(
            alarm_volume_frame,
            text=f"{self.alarm_volume_var.get():.0%}",
            font=ctk.CTkFont(size=12)
        )
        self.alarm_volume_label.grid(row=0, column=2, padx=(0, 20), pady=15)

        self.alarm_volume_slider.configure(command=self.update_alarm_volume_label)

        # Fade in duration
        fade_frame = ctk.CTkFrame(self.alarms_frame)
        fade_frame.grid(row=4, column=0, padx=20, pady=10, sticky="ew")
        fade_frame.grid_columnconfigure(1, weight=1)

        fade_label = ctk.CTkLabel(
            fade_frame,
            text="Fade In (seconds):",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        fade_label.grid(row=0, column=0, padx=20, pady=15, sticky="w")

        self.fade_var = ctk.IntVar(value=self.config.get("alarm_fade_in_seconds", 2))
        fade_options = [0, 1, 2, 3, 5, 10]
        self.fade_combo = ctk.CTkComboBox(
            fade_frame,
            variable=self.fade_var,
            values=[str(s) for s in fade_options],
            width=150
        )
        self.fade_combo.grid(row=0, column=1, padx=(10, 20), pady=15, sticky="w")

        # Auto dismiss
        auto_dismiss_frame = ctk.CTkFrame(self.alarms_frame)
        auto_dismiss_frame.grid(row=5, column=0, padx=20, pady=10, sticky="ew")
        auto_dismiss_frame.grid_columnconfigure(1, weight=1)

        auto_dismiss_label = ctk.CTkLabel(
            auto_dismiss_frame,
            text="Auto Dismiss (minutes):",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        auto_dismiss_label.grid(row=0, column=0, padx=20, pady=15, sticky="w")

        self.auto_dismiss_var = ctk.IntVar(value=self.config.get("alarm_auto_dismiss_minutes", 5))
        auto_dismiss_options = [0, 1, 2, 5, 10, 15]
        self.auto_dismiss_combo = ctk.CTkComboBox(
            auto_dismiss_frame,
            variable=self.auto_dismiss_var,
            values=[str(m) if m > 0 else "Never" for m in auto_dismiss_options],
            width=150
        )
        self.auto_dismiss_combo.grid(row=0, column=1, padx=(10, 20), pady=15, sticky="w")

    def create_data_settings(self, parent):
        """Create data management settings panel."""
        self.data_frame = ctk.CTkFrame(parent)
        self.data_frame.grid(row=0, column=1, sticky="nsew", padx=(0, 20), pady=20)
        self.data_frame.grid_columnconfigure(0, weight=1)

        # Section title
        title_label = ctk.CTkLabel(
            self.data_frame,
            text="💾 Data Management",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        # Auto backup
        backup_frame = ctk.CTkFrame(self.data_frame)
        backup_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        backup_frame.grid_columnconfigure(1, weight=1)

        self.auto_backup_var = ctk.BooleanVar(value=self.config.get("auto_backup_enabled", True))
        auto_backup_cb = ctk.CTkCheckBox(
            backup_frame,
            text="Enable automatic backups",
            variable=self.auto_backup_var,
            command=self.toggle_backup_settings
        )
        auto_backup_cb.grid(row=0, column=0, padx=20, pady=15, sticky="w")

        # Backup interval
        backup_interval_frame = ctk.CTkFrame(backup_frame)
        backup_interval_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=(5, 15), sticky="ew")

        interval_label = ctk.CTkLabel(backup_interval_frame, text="Backup every:")
        interval_label.pack(side="left", padx=10, pady=10)

        self.backup_interval_var = ctk.IntVar(value=self.config.get("auto_backup_interval_hours", 24))
        interval_options = [1, 6, 12, 24, 48]
        self.backup_interval_combo = ctk.CTkComboBox(
            backup_interval_frame,
            variable=self.backup_interval_var,
            values=[f"{h}h" for h in interval_options],
            width=80
        )
        self.backup_interval_combo.pack(side="left", padx=5, pady=10)

        # Manual backup
        manual_backup_frame = ctk.CTkFrame(self.data_frame)
        manual_backup_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        backup_label = ctk.CTkLabel(
            manual_backup_frame,
            text="Manual Backup",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        backup_label.grid(row=0, column=0, padx=20, pady=15, sticky="w")

        backup_btn = ctk.CTkButton(
            manual_backup_frame,
            text="Create Backup Now",
            command=self.create_backup,
            width=150
        )
        backup_btn.grid(row=0, column=1, padx=(10, 20), pady=15)

        # Restore backup
        restore_btn = ctk.CTkButton(
            manual_backup_frame,
            text="Restore Backup",
            command=self.restore_backup,
            width=150,
            fg_color="transparent",
            text_color=self.theme_manager.get_color("text_primary"),
            border_width=1,
            border_color=self.theme_manager.get_color("border")
        )
        restore_btn.grid(row=0, column=2, padx=(5, 20), pady=15)

        # Data cleanup
        cleanup_frame = ctk.CTkFrame(self.data_frame)
        cleanup_frame.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        cleanup_frame.grid_columnconfigure(1, weight=1)

        cleanup_label = ctk.CTkLabel(
            cleanup_frame,
            text="Data Cleanup",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        cleanup_label.grid(row=0, column=0, padx=20, pady=15, sticky="w")

        # Retention days
        retention_frame = ctk.CTkFrame(cleanup_frame)
        retention_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=(5, 15), sticky="ew")

        retention_label = ctk.CTkLabel(retention_frame, text="Keep completed tasks for:")
        retention_label.pack(side="left", padx=10, pady=10)

        self.retention_var = ctk.IntVar(value=self.config.get("completed_tasks_retention_days", 30))
        retention_options = [7, 14, 30, 60, 90, 365, 0]
        self.retention_combo = ctk.CTkComboBox(
            retention_frame,
            variable=self.retention_var,
            values=[f"{d} days" if d > 0 else "Forever" for d in retention_options],
            width=120
        )
        self.retention_combo.pack(side="left", padx=5, pady=10)

        # Cleanup button
        cleanup_btn = ctk.CTkButton(
            cleanup_frame,
            text="Run Cleanup Now",
            command=self.run_cleanup,
            width=150,
            fg_color=self.theme_manager.get_color("priority_medium")
        )
        cleanup_btn.grid(row=0, column=1, padx=(10, 20), pady=15)

        # Import/Export
        import_export_frame = ctk.CTkFrame(self.data_frame)
        import_export_frame.grid(row=4, column=0, padx=20, pady=10, sticky="ew")

        import_export_label = ctk.CTkLabel(
            import_export_frame,
            text="Import/Export",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        import_export_label.grid(row=0, column=0, padx=20, pady=15, sticky="w")

        # Export buttons
        export_frame = ctk.CTkFrame(import_export_frame)
        export_frame.grid(row=1, column=0, padx=20, pady=(5, 10), sticky="ew")

        export_csv_btn = ctk.CTkButton(
            export_frame,
            text="Export to CSV",
            command=lambda: self.export_data("csv"),
            width=120
        )
        export_csv_btn.pack(side="left", padx=10, pady=10)

        export_json_btn = ctk.CTkButton(
            export_frame,
            text="Export to JSON",
            command=lambda: self.export_data("json"),
            width=120
        )
        export_json_btn.pack(side="left", padx=5, pady=10)

        # Import button
        import_btn = ctk.CTkButton(
            import_export_frame,
            text="Import Tasks",
            command=self.import_data,
            width=150,
            fg_color="transparent",
            text_color=self.theme_manager.get_color("text_primary"),
            border_width=1,
            border_color=self.theme_manager.get_color("border")
        )
        import_btn.grid(row=2, column=0, padx=20, pady=(5, 15), sticky="w")

    def create_advanced_settings(self, parent):
        """Create advanced settings panel."""
        self.advanced_frame = ctk.CTkFrame(parent)
        self.advanced_frame.grid(row=0, column=1, sticky="nsew", padx=(0, 20), pady=20)
        self.advanced_frame.grid_columnconfigure(0, weight=1)

        # Section title
        title_label = ctk.CTkLabel(
            self.advanced_frame,
            text="🔧 Advanced Settings",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        # Debug mode
        debug_frame = ctk.CTkFrame(self.advanced_frame)
        debug_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        debug_frame.grid_columnconfigure(1, weight=1)

        self.debug_var = ctk.BooleanVar(value=self.config.get("debug_mode", False))
        debug_cb = ctk.CTkCheckBox(
            debug_frame,
            text="Enable debug mode",
            variable=self.debug_var
        )
        debug_cb.grid(row=0, column=0, padx=20, pady=15, sticky="w")

        # Check for updates
        self.check_updates_var = ctk.BooleanVar(value=self.config.get("check_for_updates", True))
        updates_cb = ctk.CTkCheckBox(
            debug_frame,
            text="Check for updates on startup",
            variable=self.check_updates_var
        )
        updates_cb.grid(row=1, column=0, padx=20, pady=5, sticky="w")

        # Auto start
        self.autostart_var = ctk.BooleanVar(value=self.config.get("auto_start", False))
        autostart_cb = ctk.CTkCheckBox(
            debug_frame,
            text="Start with system",
            variable=self.autostart_var
        )
        autostart_cb.grid(row=2, column=0, padx=20, pady=5, sticky="w")

        # System info
        info_frame = ctk.CTkFrame(self.advanced_frame)
        info_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        info_label = ctk.CTkLabel(
            info_frame,
            text="System Information",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        info_label.grid(row=0, column=0, padx=20, pady=(15, 10), sticky="w")

        info_btn = ctk.CTkButton(
            info_frame,
            text="Show System Info",
            command=self.show_system_info,
            width=150
        )
        info_btn.grid(row=0, column=1, padx=(10, 20), pady=15)

        # Reset settings
        reset_frame = ctk.CTkFrame(self.advanced_frame)
        reset_frame.grid(row=3, column=0, padx=20, pady=10, sticky="ew")

        reset_label = ctk.CTkLabel(
            reset_frame,
            text="Reset Settings",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        reset_label.grid(row=0, column=0, padx=20, pady=15, sticky="w")

        reset_btn = ctk.CTkButton(
            reset_frame,
            text="Reset to Defaults",
            command=self.reset_settings,
            width=150,
            fg_color=self.theme_manager.get_color("priority_high")
        )
        reset_btn.grid(row=0, column=1, padx=(10, 20), pady=15)

    def create_action_buttons(self):
        """Create action buttons at the bottom."""
        action_frame = ctk.CTkFrame(self)
        action_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 20))
        action_frame.grid_columnconfigure(1, weight=1)

        # Cancel button
        cancel_btn = ctk.CTkButton(
            action_frame,
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
        self.save_btn = ctk.CTkButton(
            action_frame,
            text="Save Settings",
            command=self.save_settings,
            width=120,
            height=40,
            fg_color=self.theme_manager.get_color("primary")
        )
        self.save_btn.grid(row=0, column=2, padx=10, pady=20)

        # Apply button
        self.apply_btn = ctk.CTkButton(
            action_frame,
            text="Apply",
            command=self.apply_settings,
            width=120,
            height=40
        )
        self.apply_btn.grid(row=0, column=1, padx=10, pady=20)

    # Tab switching
    def switch_tab(self, tab_name):
        """Switch to a specific settings tab."""
        # Hide all frames
        for frame in [self.appearance_frame, self.notifications_frame,
                     self.alarms_frame, self.data_frame, self.advanced_frame]:
            frame.grid_forget()

        # Show selected frame
        if tab_name == "appearance":
            self.appearance_frame.grid(row=0, column=1, sticky="nsew", padx=(0, 20), pady=20)
        elif tab_name == "notifications":
            self.notifications_frame.grid(row=0, column=1, sticky="nsew", padx=(0, 20), pady=20)
        elif tab_name == "alarms":
            self.alarms_frame.grid(row=0, column=1, sticky="nsew", padx=(0, 20), pady=20)
        elif tab_name == "data":
            self.data_frame.grid(row=0, column=1, sticky="nsew", padx=(0, 20), pady=20)
        elif tab_name == "advanced":
            self.advanced_frame.grid(row=0, column=1, sticky="nsew", padx=(0, 20), pady=20)

    # Settings actions
    def save_settings(self):
        """Save all settings and close."""
        if self.apply_settings():
            if self.app_instance:
                self.app_instance.switch_view("dashboard")

    def apply_settings(self):
        """Apply all settings."""
        try:
            # Appearance settings
            self.config.set("theme", self.theme_var.get())
            self.config.set("font_size", self.font_var.get())
            self.config.set("start_maximized", self.start_maximized_var.get())
            self.config.set("minimize_to_tray", self.minimize_tray_var.get())

            # Notification settings
            self.config.set("enable_notifications", self.enable_notifications_var.get())
            self.config.set("notification_sound", self.sound_var.get())
            self.config.set("notification_volume", self.volume_var.get())
            self.config.set("default_reminder_minutes", self.reminder_var.get())
            self.config.set("snooze_duration_minutes", self.snooze_var.get())
            self.config.set("max_snooze_count", self.max_snooze_var.get())
            self.config.set("quiet_hours_enabled", self.quiet_enabled_var.get())
            self.config.set("quiet_hours_start", self.quiet_start_var.get())
            self.config.set("quiet_hours_end", self.quiet_end_var.get())

            # Alarm settings
            self.config.set("persistent_alarms", self.persistent_var.get())
            self.config.set("alarm_sound_file", self.alarm_sound_var.get())
            self.config.set("alarm_volume", self.alarm_volume_var.get())
            self.config.set("alarm_fade_in_seconds", self.fade_var.get())
            self.config.set("alarm_auto_dismiss_minutes", self.auto_dismiss_var.get())

            # Data settings
            self.config.set("auto_backup_enabled", self.auto_backup_var.get())
            self.config.set("auto_backup_interval_hours", self.backup_interval_var.get())
            self.config.set("completed_tasks_retention_days", self.retention_var.get())

            # Advanced settings
            self.config.set("debug_mode", self.debug_var.get())
            self.config.set("check_for_updates", self.check_updates_var.get())
            self.config.set("auto_start", self.autostart_var.get())

            # Update save status
            self.save_status_label.configure(text="Settings saved successfully!",
                                           text_color=self.theme_manager.get_color("priority_low"))

            # Apply theme if changed
            if hasattr(self.app_instance, 'theme_manager'):
                self.app_instance.theme_manager.set_theme(self.theme_var.get())
                self.app_instance._apply_theme()

            if self.app_instance:
                self.app_instance.set_status("Settings applied successfully")

            return True

        except Exception as e:
            self.save_status_label.configure(text=f"Error: {str(e)}",
                                           text_color=self.theme_manager.get_color("priority_high"))
            if self.app_instance:
                self.app_instance.set_status("Error saving settings")
            return False

    def on_cancel(self):
        """Handle cancel button click."""
        if self.app_instance:
            self.app_instance.switch_view("dashboard")

    # Helper methods
    def update_volume_label(self, value):
        """Update volume label."""
        self.volume_label.configure(text=f"{value:.0%}")

    def update_alarm_volume_label(self, value):
        """Update alarm volume label."""
        self.alarm_volume_label.configure(text=f"{value:.0%}")

    def toggle_notification_settings(self):
        """Toggle notification settings enabled/disabled."""
        enabled = self.enable_notifications_var.get()
        state = "normal" if enabled else "disabled"

        # Enable/disable notification controls
        self.sound_var.set(enabled and self.sound_var.get())
        self.volume_slider.configure(state=state)
        self.reminder_combo.configure(state=state)
        self.snooze_combo.configure(state=state)
        self.max_snooze_combo.configure(state=state)

    def toggle_quiet_hours(self):
        """Toggle quiet hours settings."""
        enabled = self.quiet_enabled_var.get()
        state = "normal" if enabled else "disabled"

        self.quiet_start_entry.configure(state=state)
        self.quiet_end_entry.configure(state=state)

    def toggle_backup_settings(self):
        """Toggle backup settings."""
        enabled = self.auto_backup_var.get()
        state = "normal" if enabled else "disabled"

        self.backup_interval_combo.configure(state=state)

    def browse_alarm_sound(self):
        """Browse for alarm sound file."""
        file_path = filedialog.askopenfilename(
            title="Select Alarm Sound",
            filetypes=[("Audio Files", "*.mp3 *.wav *.m4a *.ogg"), ("All Files", "*.*")]
        )
        if file_path:
            self.alarm_sound_var.set(file_path)

    def create_backup(self):
        """Create a manual backup."""
        try:
            success, message = self.task_manager.backup_data()
            if success:
                messagebox.showinfo("Backup Successful", f"Backup created:\n{message}")
            else:
                messagebox.showerror("Backup Failed", f"Failed to create backup:\n{message}")
        except Exception as e:
            messagebox.showerror("Backup Error", f"Error creating backup: {str(e)}")

    def restore_backup(self):
        """Restore from backup."""
        file_path = filedialog.askopenfilename(
            title="Select Backup File",
            filetypes=[("Database Files", "*.db"), ("All Files", "*.*")]
        )
        if file_path:
            if messagebox.askyesno("Confirm Restore", "This will replace all current data. Continue?"):
                try:
                    success = self.task_manager.db.restore_database(file_path)
                    if success:
                        messagebox.showinfo("Restore Successful", "Database restored successfully!")
                        if self.app_instance:
                            self.app_instance.refresh_current_view()
                    else:
                        messagebox.showerror("Restore Failed", "Failed to restore database")
                except Exception as e:
                    messagebox.showerror("Restore Error", f"Error restoring backup: {str(e)}")

    def run_cleanup(self):
        """Run data cleanup."""
        try:
            retention_days = self.retention_var.get()
            success, message = self.task_manager.cleanup_old_tasks(retention_days)
            if success:
                messagebox.showinfo("Cleanup Successful", message)
            else:
                messagebox.showerror("Cleanup Failed", f"Cleanup failed: {message}")
        except Exception as e:
            messagebox.showerror("Cleanup Error", f"Error during cleanup: {str(e)}")

    def export_data(self, format_type):
        """Export tasks data."""
        file_path = filedialog.asksaveasfilename(
            title=f"Export Tasks as {format_type.upper()}",
            defaultextension=f".{format_type}",
            filetypes=[(f"{format_type.upper()} Files", f"*.{format_type}"), ("All Files", "*.*")]
        )
        if file_path:
            try:
                success, message = self.task_manager.export_tasks(file_path, format_type)
                if success:
                    messagebox.showinfo("Export Successful", message)
                else:
                    messagebox.showerror("Export Failed", f"Export failed: {message}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Error exporting data: {str(e)}")

    def import_data(self):
        """Import tasks data."""
        file_path = filedialog.askopenfilename(
            title="Import Tasks",
            filetypes=[("CSV Files", "*.csv"), ("JSON Files", "*.json"), ("All Files", "*.*")]
        )
        if file_path:
            try:
                success, message = self.task_manager.import_tasks(file_path)
                if success:
                    messagebox.showinfo("Import Successful", message)
                    if self.app_instance:
                        self.app_instance.refresh_current_view()
                else:
                    messagebox.showerror("Import Failed", f"Import failed: {message}")
            except Exception as e:
                messagebox.showerror("Import Error", f"Error importing data: {str(e)}")

    def show_system_info(self):
        """Show system information dialog."""
        try:
            from ...utils.helpers import get_system_info
            info = get_system_info()

            info_text = "System Information:\n\n"
            for key, value in info.items():
                info_text += f"{key.replace('_', ' ').title()}: {value}\n"

            messagebox.showinfo("System Information", info_text)
        except Exception as e:
            messagebox.showerror("Error", f"Error getting system info: {str(e)}")

    def reset_settings(self):
        """Reset all settings to defaults."""
        if messagebox.askyesno("Reset Settings", "This will reset all settings to their default values. Continue?"):
            try:
                self.config.reset_to_defaults()
                messagebox.showinfo("Settings Reset", "All settings have been reset to defaults.")
                # Reload settings
                if self.app_instance:
                    self.app_instance.switch_view("settings")
            except Exception as e:
                messagebox.showerror("Reset Failed", f"Error resetting settings: {str(e)}")