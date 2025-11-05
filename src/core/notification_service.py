"""
Notification Service for the task scheduler application.
Handles desktop notifications, system tray notifications, and notification management.
"""

import os
import sys
import threading
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path

from ..utils.config import get_config
from ..ui.themes.theme_manager import get_theme_manager


class NotificationService:
    """Comprehensive notification service for task management."""

    def __init__(self):
        self.config = get_config()
        self.theme_manager = get_theme_manager()

        # Notification settings
        self.enabled = self.config.get("enable_notifications", True)
        self.sound_enabled = self.config.get("notification_sound", True)
        self.volume = self.config.get("notification_volume", 0.7)
        self.default_reminder = self.config.get("default_reminder_minutes", 15)
        self.quiet_hours_enabled = self.config.get("quiet_hours_enabled", False)
        self.quiet_hours_start = self.config.get("quiet_hours_start", "22:00")
        self.quiet_hours_end = self.config.get("quiet_hours_end", "08:00")

        # Notification history
        self.notification_history = []
        self.max_history = 100

        # Notification templates
        self.templates = self.create_notification_templates()

        # Ensure notification directory
        self.notification_dir = Path("data/notifications")
        self.notification_dir.mkdir(parents=True, exist_ok=True)

        # Load custom templates
        self.load_custom_templates()

    def create_notification_templates(self) -> Dict[str, Dict[str, str]]:
        """Create default notification templates."""
        return {
            "task_created": {
                "title": "Task Created",
                "message": "Task '{title}' has been created successfully."
            },
            "task_updated": {
                "title": "Task Updated",
                "message": "Task '{title}' has been updated."
            },
            "task_completed": {
                "title": "Task Completed! 🎉",
                "message": "Great job! You've completed '{title}'."
            },
            "task_overdue": {
                "title": "⚠️ Task Overdue",
                "message": "Task '{title}' is overdue. It was due on {due_date}."
            },
            "task_reminder": {
                "title": "🔔 Task Reminder",
                "message": "Task '{title}' is due soon{time_info}."
            },
            "alarm_triggered": {
                "title": "🚨 Alarm: {title}",
                "message": "It's time for: {title}{priority_info}{category_info}"
            },
            "task_deleted": {
                "title": "Task Deleted",
                "message": "Task '{title}' has been deleted."
            },
            "backup_created": {
                "title": "✅ Backup Created",
                "message": "Your data has been backed up successfully."
            },
            "cleanup_completed": {
                "title": "🧹 Cleanup Completed",
                "message": "Old completed tasks have been cleaned up."
            },
            "import_completed": {
                "title": "✅ Import Completed",
                "message": "Successfully imported {count} tasks."
            }
        }

    def load_custom_templates(self):
        """Load custom notification templates from file."""
        templates_file = self.notification_dir / "custom_templates.json"
        if templates_file.exists():
            try:
                with open(templates_file, 'r', encoding='utf-8') as f:
                    custom_templates = json.load(f)
                    self.templates.update(custom_templates)
            except Exception as e:
                print(f"Error loading custom templates: {e}")

    def save_custom_templates(self):
        """Save custom notification templates."""
        templates_file = self.notification_dir / "custom_templates.json"
        try:
            with open(templates_file, 'w', encoding='utf-8') as f:
                json.dump(self.templates, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving custom templates: {e}")

    def notify(self, template_name: str, **kwargs) -> bool:
        """Send a notification using a template."""
        try:
            # Check if notifications are enabled
            if not self.enabled:
                return False

            # Check quiet hours
            if self.quiet_hours_enabled and self.is_quiet_hours():
                return False

            # Get template
            template = self.templates.get(template_name, {
                "title": "Notification",
                "message": "Task notification"
            })

            # Format template
            title = template["title"].format(**kwargs)
            message = template["message"].format(**kwargs)

            # Add to history
            self.add_to_history(template_name, title, message)

            # Send notification
            return self.send_notification(title, message, template_name, kwargs)

        except Exception as e:
            print(f"Error sending notification: {e}")
            return False

    def send_notification(self, title: str, message: str, template_name: str = None,
                        context: Dict[str, Any] = None) -> bool:
        """Send a desktop notification."""
        try:
            # Try to use plyer for desktop notifications
            return self._send_desktop_notification(title, message, template_name, context)
        except ImportError:
            # Fallback to console notification
            return self._send_console_notification(title, message)

    def _send_desktop_notification(self, title: str, message: str,
                                 template_name: str = None, context: Dict[str, Any] = None) -> bool:
        """Send desktop notification using plyer."""
        try:
            from plyer import notification

            # Determine timeout based on priority
            timeout = self._get_timeout(template_name, context)

            # Get app icon if available
            app_icon = self._get_app_icon()

            # Send notification
            notification.notify(
                title=title,
                message=message,
                app_name="Task Scheduler Pro",
                app_icon=app_icon,
                timeout=timeout
            )

            # Play sound if enabled
            if self.sound_enabled:
                self._play_notification_sound(template_name, context)

            return True

        except Exception as e:
            print(f"Error sending desktop notification: {e}")
            return False

    def _send_console_notification(self, title: str, message: str) -> bool:
        """Send console notification as fallback."""
        try:
            print(f"\n🔔 {title}")
            print(f"   {message}")
            print("-" * 50)
            return True
        except Exception as e:
            print(f"Error sending console notification: {e}")
            return False

    def _get_timeout(self, template_name: str, context: Dict[str, Any] = None) -> int:
        """Get notification timeout based on template and context."""
        # High priority or urgent notifications get longer timeout
        if template_name in ["task_overdue", "alarm_triggered"]:
            return 15
        elif template_name == "task_completed":
            return 10
        elif template_name == "task_reminder":
            return 8
        else:
            return 5

    def _get_app_icon(self) -> Optional[str]:
        """Get application icon path."""
        icon_paths = [
            "assets/icons/app.ico",
            "assets/icons/app.png",
            "assets/icon.png"
        ]

        for icon_path in icon_paths:
            if os.path.exists(icon_path):
                return os.path.abspath(icon_path)

        return None

    def _play_notification_sound(self, template_name: str, context: Dict[str, Any] = None):
        """Play notification sound."""
        try:
            # Try to use playsound
            from playsound import playsound

            sound_file = self._get_notification_sound(template_name, context)
            if sound_file and os.path.exists(sound_file):
                playsound(sound_file)
            else:
                # Use system default sound
                self._play_system_sound()

        except ImportError:
            # Fallback to system beep
            print("\a")  # Bell character
        except Exception as e:
            print(f"Error playing notification sound: {e}")

    def _get_notification_sound(self, template_name: str, context: Dict[str, Any] = None) -> Optional[str]:
        """Get sound file for notification."""
        sound_directory = Path(self.config.get("sound_directory", "assets/sounds"))

        # Map templates to sounds
        sound_map = {
            "task_overdue": "alert.wav",
            "alarm_triggered": "alarm.wav",
            "task_completed": "success.wav",
            "task_reminder": "reminder.wav"
        }

        sound_file = sound_map.get(template_name, "default.wav")
        sound_path = sound_directory / sound_file

        return str(sound_path) if sound_path.exists() else None

    def _play_system_sound(self):
        """Play system default sound."""
        try:
            import platform
            if platform.system() == "Windows":
                import winsound
                winsound.MessageBeep(winsound.MB_ICONINFORMATION)
            elif platform.system() == "Darwin":  # macOS
                os.system("afplay /System/Library/Sounds/Glass.aiff")
            else:  # Linux
                os.system("paplay /usr/share/sounds/alsa/Front_Left.wav")
        except Exception:
            pass  # Silent fail if sound doesn't work

    def is_quiet_hours(self) -> bool:
        """Check if current time is within quiet hours."""
        if not self.quiet_hours_enabled:
            return False

        try:
            from datetime import time

            start_time = time.fromisoformat(self.quiet_hours_start)
            end_time = time.fromisoformat(self.quiet_hours_end)
            current_time = datetime.now().time()

            if start_time <= end_time:
                # Same day interval
                return start_time <= current_time <= end_time
            else:
                # Overnight interval
                return current_time >= start_time or current_time <= end_time

        except ValueError:
            return False

    def add_to_history(self, template_name: str, title: str, message: str):
        """Add notification to history."""
        notification = {
            "timestamp": datetime.now().isoformat(),
            "template": template_name,
            "title": title,
            "message": message
        }

        self.notification_history.append(notification)

        # Limit history size
        if len(self.notification_history) > self.max_history:
            self.notification_history = self.notification_history[-self.max_history:]

        # Save history periodically
        if len(self.notification_history) % 10 == 0:
            self.save_notification_history()

    def save_notification_history(self):
        """Save notification history to file."""
        history_file = self.notification_dir / "notification_history.json"
        try:
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(self.notification_history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving notification history: {e}")

    def get_notification_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent notification history."""
        return self.notification_history[-limit:]

    def clear_notification_history(self):
        """Clear notification history."""
        self.notification_history = []
        history_file = self.notification_dir / "notification_history.json"
        if history_file.exists():
            history_file.unlink()

    def create_custom_template(self, name: str, title: str, message: str) -> bool:
        """Create a custom notification template."""
        try:
            self.templates[name] = {
                "title": title,
                "message": message
            }
            self.save_custom_templates()
            return True
        except Exception as e:
            print(f"Error creating custom template: {e}")
            return False

    def delete_template(self, name: str) -> bool:
        """Delete a custom notification template."""
        try:
            if name in self.templates:
                del self.templates[name]
                self.save_custom_templates()
                return True
            return False
        except Exception as e:
            print(f"Error deleting template: {e}")
            return False

    def get_templates(self) -> Dict[str, Dict[str, str]]:
        """Get all notification templates."""
        return self.templates.copy()

    def update_settings(self, settings: Dict[str, Any]):
        """Update notification settings."""
        if 'enabled' in settings:
            self.enabled = settings['enabled']

        if 'sound_enabled' in settings:
            self.sound_enabled = settings['sound_enabled']

        if 'volume' in settings:
            self.volume = settings['volume']

        if 'quiet_hours_enabled' in settings:
            self.quiet_hours_enabled = settings['quiet_hours_enabled']

        if 'quiet_hours_start' in settings:
            self.quiet_hours_start = settings['quiet_hours_start']

        if 'quiet_hours_end' in settings:
            self.quiet_hours_end = settings['quiet_hours_end']

    # Convenience methods for common notifications
    def notify_task_created(self, task_title: str):
        """Notify when a task is created."""
        self.notify("task_created", title=task_title)

    def notify_task_updated(self, task_title: str):
        """Notify when a task is updated."""
        self.notify("task_updated", title=task_title)

    def notify_task_completed(self, task_title: str):
        """Notify when a task is completed."""
        self.notify("task_completed", title=task_title)

    def notify_task_overdue(self, task_title: str, due_date: str):
        """Notify when a task is overdue."""
        self.notify("task_overdue", title=task_title, due_date=due_date)

    def notify_task_reminder(self, task_title: str, due_time: str = None):
        """Notify for task reminder."""
        time_info = f" at {due_time}" if due_time else ""
        self.notify("task_reminder", title=task_title, time_info=time_info)

    def notify_alarm_triggered(self, task_title: str, priority: str = None, category: str = None):
        """Notify when an alarm is triggered."""
        priority_info = f" (Priority: {priority})" if priority else ""
        category_info = f" (Category: {category})" if category else ""
        self.notify("alarm_triggered", title=task_title, priority_info=priority_info, category_info=category_info)

    def notify_task_deleted(self, task_title: str):
        """Notify when a task is deleted."""
        self.notify("task_deleted", title=task_title)

    def notify_backup_created(self):
        """Notify when backup is created."""
        self.notify("backup_created")

    def notify_cleanup_completed(self):
        """Notify when cleanup is completed."""
        self.notify("cleanup_completed")

    def notify_import_completed(self, count: int):
        """Notify when import is completed."""
        self.notify("import_completed", count=count)

    def test_notification(self, template_name: str = None):
        """Send a test notification."""
        if template_name and template_name in self.templates:
            return self.notify(template_name)
        else:
            return self.send_notification(
                "Test Notification",
                "This is a test notification from Task Scheduler Pro.",
                "test"
            )


# Global notification service instance
notification_service = NotificationService()


def get_notification_service() -> NotificationService:
    """Get the global notification service instance."""
    return notification_service