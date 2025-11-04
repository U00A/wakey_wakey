"""
Configuration management for the task scheduler application.
Handles application settings, preferences, and keyboard shortcuts.
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path


class ConfigManager:
    """Manages application configuration and settings."""

    def __init__(self, config_dir: str = "data"):
        self.config_dir = Path(config_dir)
        self.config_file = self.config_dir / "config.json"
        self.shortcuts_file = self.config_dir / "shortcuts.json"
        self.default_config = self._get_default_config()
        self.default_shortcuts = self._get_default_shortcuts()
        self.config = {}
        self.shortcuts = {}

        self._ensure_config_directory()
        self._load_config()
        self._load_shortcuts()

    def _ensure_config_directory(self):
        """Ensure the config directory exists."""
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration values."""
        return {
            # Appearance
            "theme": "dark",
            "accent_color": "#0078d4",
            "font_size": "medium",
            "window_size": [1200, 800],
            "window_position": [100, 100],
            "start_maximized": False,
            "minimize_to_tray": True,

            # Notifications
            "enable_notifications": True,
            "notification_sound": True,
            "notification_volume": 0.7,
            "default_reminder_minutes": 15,
            "snooze_duration_minutes": 5,
            "max_snooze_count": 3,
            "quiet_hours_enabled": False,
            "quiet_hours_start": "22:00",
            "quiet_hours_end": "08:00",

            # Alarms
            "alarm_sound_file": "default",
            "alarm_volume": 0.8,
            "alarm_fade_in_seconds": 2,
            "persistent_alarms": True,
            "alarm_auto_dismiss_minutes": 5,

            # Task Management
            "auto_save_interval": 30,  # seconds
            "completed_tasks_retention_days": 30,
            "default_priority": "Medium",
            "default_category": "Personal",
            "auto_backup_enabled": True,
            "auto_backup_interval_hours": 24,
            "backup_retention_days": 7,

            # Calendar
            "calendar_start_day": "sunday",
            "calendar_view": "month",  # month, week, day
            "show_weekend": True,
            "show_completed_tasks": True,

            # Performance
            "max_recent_tasks": 100,
            "search_results_limit": 50,
            "auto_refresh_interval": 60,  # seconds

            # Advanced
            "debug_mode": False,
            "check_for_updates": True,
            "auto_start": False,
            "data_directory": "data",
            "sound_directory": "assets/sounds"
        }

    def _get_default_shortcuts(self) -> Dict[str, str]:
        """Get default keyboard shortcuts."""
        return {
            # File operations
            "new_task": "Ctrl+N",
            "save_task": "Ctrl+S",
            "delete_task": "Delete",
            "export_tasks": "Ctrl+E",
            "import_tasks": "Ctrl+I",

            # Navigation
            "search": "Ctrl+F",
            "refresh": "F5",
            "dashboard": "Ctrl+1",
            "tasks": "Ctrl+2",
            "calendar": "Ctrl+3",
            "statistics": "Ctrl+4",
            "settings": "Ctrl+5",

            # View
            "toggle_theme": "Ctrl+D",
            "toggle_sidebar": "Ctrl+B",
            "minimize_to_tray": "Ctrl+M",
            "toggle_fullscreen": "F11",

            # Task actions
            "complete_task": "Ctrl+Enter",
            "edit_task": "Ctrl+E",
            "duplicate_task": "Ctrl+D",
            "quick_add": "Ctrl+Shift+N",

            # Application
            "quit": "Ctrl+Q",
            "preferences": "Ctrl+,",
            "help": "F1",
            "about": "Ctrl+Shift+A",

            # Calendar
            "today": "Ctrl+T",
            "next_month": "Ctrl+Right",
            "previous_month": "Ctrl+Left",
            "next_week": "Alt+Right",
            "previous_week": "Alt+Left",
            "week_view": "Ctrl+Alt+W",
            "month_view": "Ctrl+Alt+M",
            "day_view": "Ctrl+Alt+D"
        }

    def _load_config(self):
        """Load configuration from file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    self.config = {**self.default_config, **loaded_config}
            except (json.JSONDecodeError, IOError):
                self.config = self.default_config.copy()
                self._save_config()  # Save corrected config
        else:
            self.config = self.default_config.copy()
            self._save_config()

    def _load_shortcuts(self):
        """Load keyboard shortcuts from file."""
        if self.shortcuts_file.exists():
            try:
                with open(self.shortcuts_file, 'r', encoding='utf-8') as f:
                    loaded_shortcuts = json.load(f)
                    # Merge with defaults
                    self.shortcuts = {**self.default_shortcuts, **loaded_shortcuts}
            except (json.JSONDecodeError, IOError):
                self.shortcuts = self.default_shortcuts.copy()
                self._save_shortcuts()
        else:
            self.shortcuts = self.default_shortcuts.copy()
            self._save_shortcuts()

    def _save_config(self):
        """Save configuration to file."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, sort_keys=True)
        except IOError:
            pass  # Silently fail if we can't save

    def _save_shortcuts(self):
        """Save keyboard shortcuts to file."""
        try:
            with open(self.shortcuts_file, 'w', encoding='utf-8') as f:
                json.dump(self.shortcuts, f, indent=2, sort_keys=True)
        except IOError:
            pass  # Silently fail if we can't save

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        return self.config.get(key, default or self.default_config.get(key))

    def set(self, key: str, value: Any) -> bool:
        """Set a configuration value."""
        if key in self.default_config:
            self.config[key] = value
            self._save_config()
            return True
        return False

    def reset_to_defaults(self) -> bool:
        """Reset configuration to defaults."""
        self.config = self.default_config.copy()
        self._save_config()
        return True

    def get_shortcut(self, action: str) -> str:
        """Get keyboard shortcut for an action."""
        return self.shortcuts.get(action, "")

    def set_shortcut(self, action: str, shortcut: str) -> bool:
        """Set keyboard shortcut for an action."""
        if action in self.default_shortcuts:
            self.shortcuts[action] = shortcut
            self._save_shortcuts()
            return True
        return False

    def reset_shortcuts(self) -> bool:
        """Reset shortcuts to defaults."""
        self.shortcuts = self.default_shortcuts.copy()
        self._save_shortcuts()
        return True

    def get_window_geometry(self) -> Dict[str, Any]:
        """Get window geometry settings."""
        return {
            "size": self.get("window_size", [1200, 800]),
            "position": self.get("window_position", [100, 100]),
            "maximized": self.get("start_maximized", False)
        }

    def set_window_geometry(self, size: list = None, position: list = None, maximized: bool = None):
        """Set window geometry settings."""
        if size is not None:
            self.set("window_size", size)
        if position is not None:
            self.set("window_position", position)
        if maximized is not None:
            self.set("start_maximized", maximized)

    def get_notification_settings(self) -> Dict[str, Any]:
        """Get notification-related settings."""
        return {
            "enabled": self.get("enable_notifications", True),
            "sound": self.get("notification_sound", True),
            "volume": self.get("notification_volume", 0.7),
            "default_reminder": self.get("default_reminder_minutes", 15),
            "snooze_duration": self.get("snooze_duration_minutes", 5),
            "max_snooze": self.get("max_snooze_count", 3),
            "quiet_hours_enabled": self.get("quiet_hours_enabled", False),
            "quiet_hours_start": self.get("quiet_hours_start", "22:00"),
            "quiet_hours_end": self.get("quiet_hours_end", "08:00")
        }

    def get_alarm_settings(self) -> Dict[str, Any]:
        """Get alarm-related settings."""
        return {
            "sound_file": self.get("alarm_sound_file", "default"),
            "volume": self.get("alarm_volume", 0.8),
            "fade_in_seconds": self.get("alarm_fade_in_seconds", 2),
            "persistent": self.get("persistent_alarms", True),
            "auto_dismiss_minutes": self.get("alarm_auto_dismiss_minutes", 5)
        }

    def get_task_settings(self) -> Dict[str, Any]:
        """Get task management settings."""
        return {
            "auto_save_interval": self.get("auto_save_interval", 30),
            "retention_days": self.get("completed_tasks_retention_days", 30),
            "default_priority": self.get("default_priority", "Medium"),
            "default_category": self.get("default_category", "Personal"),
            "auto_backup": self.get("auto_backup_enabled", True),
            "backup_interval": self.get("auto_backup_interval_hours", 24),
            "backup_retention": self.get("backup_retention_days", 7)
        }

    def is_quiet_hours(self) -> bool:
        """Check if current time is within quiet hours."""
        if not self.get("quiet_hours_enabled", False):
            return False

        try:
            from datetime import datetime, time

            start_time = datetime.strptime(self.get("quiet_hours_start", "22:00"), "%H:%M").time()
            end_time = datetime.strptime(self.get("quiet_hours_end", "08:00"), "%H:%M").time()
            current_time = datetime.now().time()

            if start_time <= end_time:
                # Same day (e.g., 22:00 to 08:00 next day doesn't make sense, so assume 08:00 same day)
                return start_time <= current_time <= end_time
            else:
                # Overnight (e.g., 22:00 to 08:00 next day)
                return current_time >= start_time or current_time <= end_time

        except ValueError:
            return False

    def get_data_directory(self) -> Path:
        """Get the data directory path."""
        data_dir = self.get("data_directory", "data")
        if not os.path.isabs(data_dir):
            # Relative to application directory
            return Path.cwd() / data_dir
        return Path(data_dir)

    def get_sound_directory(self) -> Path:
        """Get the sound directory path."""
        sound_dir = self.get("sound_directory", "assets/sounds")
        if not os.path.isabs(sound_dir):
            # Relative to application directory
            return Path.cwd() / sound_dir
        return Path(sound_dir)

    def export_config(self, file_path: str) -> bool:
        """Export configuration to a file."""
        try:
            export_data = {
                "config": self.config,
                "shortcuts": self.shortcuts,
                "version": "1.0",
                "exported_at": datetime.now().isoformat()
            }

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2)

            return True
        except (IOError, TypeError):
            return False

    def import_config(self, file_path: str, merge: bool = True) -> bool:
        """Import configuration from a file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)

            if "config" in import_data:
                if merge:
                    self.config = {**self.config, **import_data["config"]}
                else:
                    self.config = {**self.default_config, **import_data["config"]}

            if "shortcuts" in import_data:
                if merge:
                    self.shortcuts = {**self.shortcuts, **import_data["shortcuts"]}
                else:
                    self.shortcuts = {**self.default_shortcuts, **import_data["shortcuts"]}

            self._save_config()
            self._save_shortcuts()

            return True
        except (IOError, json.JSONDecodeError, KeyError):
            return False


# Global configuration manager instance
config_manager = ConfigManager()


def get_config() -> ConfigManager:
    """Get the global configuration manager instance."""
    return config_manager


def get_setting(key: str, default: Any = None) -> Any:
    """Get a configuration setting."""
    return config_manager.get(key, default)


def set_setting(key: str, value: Any) -> bool:
    """Set a configuration setting."""
    return config_manager.set(key, value)


def get_shortcut(action: str) -> str:
    """Get keyboard shortcut for an action."""
    return config_manager.get_shortcut(action)