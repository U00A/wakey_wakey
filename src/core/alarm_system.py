"""
Alarm System for the task scheduler application.
Handles task reminders, sound notifications, and alarm management.
"""

import os
import sys
import time
import threading
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Callable
from pathlib import Path

from ..database.manager import DatabaseManager
from ..database.models import Alarm, Task
from ..utils.config import get_config
from ..ui.themes.theme_manager import get_theme_manager


class AlarmSystem:
    """Comprehensive alarm system for task reminders."""

    def __init__(self):
        self.db = DatabaseManager()
        self.config = get_config()
        self.theme_manager = get_theme_manager()

        # Alarm state
        self.is_running = False
        self.check_interval = 30  # seconds
        self.active_alarms = []
        self.snoozed_alarms = {}
        self.notification_callbacks = []

        # Sound system
        self.sound_enabled = self.config.get("notification_sound", True)
        self.volume = self.config.get("notification_volume", 0.7)
        self.default_sound = self.config.get("alarm_sound_file", "default")

        # Alarm settings
        self.snooze_duration = self.config.get("snooze_duration_minutes", 5)
        self.max_snooze_count = self.config.get("max_snooze_count", 3)
        self.auto_dismiss_minutes = self.config.get("alarm_auto_dismiss_minutes", 5)
        self.persistent_alarms = self.config.get("persistent_alarms", True)

        # Thread management
        self.alarm_thread = None
        self.thread_lock = threading.Lock()

        # Sound files
        self.sound_directory = Path(self.config.get("sound_directory", "assets/sounds"))
        self.ensure_sound_directory()

    def ensure_sound_directory(self):
        """Ensure sound directory exists."""
        self.sound_directory.mkdir(parents=True, exist_ok=True)

        # Create default sound files if they don't exist
        self.create_default_sounds()

    def create_default_sounds(self):
        """Create default alarm sound files."""
        # This would create actual sound files
        # For now, we'll just ensure the directory exists
        default_sounds = {
            "default.wav": "Default system sound",
            "gentle.wav": "Gentle wake sound",
            "classic.wav": "Classic alarm sound",
            "digital.wav": "Digital beep sound"
        }

        for sound_file, description in default_sounds.items():
            sound_path = self.sound_directory / sound_file
            if not sound_path.exists():
                # Create a placeholder file (in real implementation, would create actual audio)
                sound_path.touch()

    def start(self):
        """Start the alarm system."""
        if self.is_running:
            return

        with self.thread_lock:
            self.is_running = True
            self.alarm_thread = threading.Thread(target=self.alarm_loop, daemon=True)
            self.alarm_thread.start()

        print("Alarm system started")

    def stop(self):
        """Stop the alarm system."""
        with self.thread_lock:
            self.is_running = False

        if self.alarm_thread and self.alarm_thread.is_alive():
            self.alarm_thread.join(timeout=5)

        print("Alarm system stopped")

    def alarm_loop(self):
        """Main alarm checking loop."""
        while self.is_running:
            try:
                self.check_alarms()
                time.sleep(self.check_interval)
            except Exception as e:
                print(f"Error in alarm loop: {e}")
                time.sleep(self.check_interval)

    def check_alarms(self):
        """Check for due alarms and trigger them."""
        now = datetime.now()
        due_alarms = self.db.get_pending_alarms()

        for alarm_data in due_alarms:
            try:
                alarm = Alarm(alarm_data)

                # Check if alarm is due
                if alarm.is_triggered():
                    # Check if alarm is snoozed
                    if alarm.id in self.snoozed_alarms:
                        snooze_info = self.snoozed_alarms[alarm.id]
                        if now >= snooze_info['next_trigger']:
                            self.trigger_alarm(alarm)
                        else:
                            continue  # Still snoozed
                    else:
                        self.trigger_alarm(alarm)

            except Exception as e:
                print(f"Error processing alarm {alarm.id}: {e}")

    def trigger_alarm(self, alarm: Alarm):
        """Trigger an alarm."""
        try:
            # Get associated task
            task = self.db.get_task(alarm.task_id)
            if not task:
                return

            # Check quiet hours
            if self.config.get("quiet_hours_enabled", False) and self.config.is_quiet_hours():
                return

            # Create alarm notification
            self.create_alarm_notification(task, alarm)

            # Play sound
            if self.sound_enabled:
                self.play_alarm_sound(alarm.sound_file or self.default_sound)

            # Add to active alarms
            self.active_alarms.append(alarm)

            # Schedule auto-dismiss
            if self.auto_dismiss_minutes > 0:
                dismiss_time = datetime.now() + timedelta(minutes=self.auto_dismiss_minutes)
                threading.Timer(
                    self.auto_dismiss_minutes * 60,
                    lambda: self.auto_dismiss_alarm(alarm.id)
                ).start()

            # Update alarm status
            self.db.update_alarm(alarm.id, {"is_active": False})

            # Recurring task handling
            if task.recurring_type != "None" and task.status != "Completed":
                self.schedule_next_recurring_alarm(task, alarm)

            # Notify callbacks
            for callback in self.notification_callbacks:
                try:
                    callback(task, alarm)
                except Exception as e:
                    print(f"Error in notification callback: {e}")

        except Exception as e:
            print(f"Error triggering alarm: {e}")

    def create_alarm_notification(self, task: Task, alarm: Alarm):
        """Create a desktop notification for the alarm."""
        try:
            # Try to use plyer for notifications
            from plyer import notification

            title = f"Task Reminder: {task.title}"
            message = self.format_alarm_message(task, alarm)

            # Use different notification templates based on priority
            app_name = "Task Scheduler Pro"
            app_icon = None  # Could be set to app icon path

            if task.priority == "High":
                notification.notify(
                    title=title,
                    message=message,
                    app_name=app_name,
                    app_icon=app_icon,
                    timeout=10
                )
            elif task.priority == "Medium":
                notification.notify(
                    title=title,
                    message=message,
                    app_name=app_name,
                    timeout=7
                )
            else:  # Low priority
                notification.notify(
                    title=title,
                    message=message,
                    app_name=app_name,
                    timeout=5
                )

        except ImportError:
            # Fallback to console notification
            print(f"ALARM: {task.title}")
            print(f"Message: {self.format_alarm_message(task, alarm)}")
        except Exception as e:
            print(f"Error creating notification: {e}")

    def format_alarm_message(self, task: Task, alarm: Alarm) -> str:
        """Format alarm message based on task and alarm details."""
        message_parts = []

        # Priority indicator
        priority_emoji = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}.get(task.priority, "")
        if priority_emoji:
            message_parts.append(priority_emoji)

        # Task description
        if task.description:
            message_parts.append(f"Description: {task.description[:100]}...")
        else:
            message_parts.append("No description provided")

        # Due time
        if task.due_date:
            try:
                due_time = datetime.fromisoformat(task.due_date.replace('Z', '+00:00'))
                if due_time.date() == datetime.now().date():
                    time_str = due_time.strftime("%I:%M %p")
                    message_parts.append(f"Due today at {time_str}")
                else:
                    date_str = due_time.strftime("%B %d at %I:%M %p")
                    message_parts.append(f"Due {date_str}")
            except ValueError:
                pass

        # Category
        if task.category:
            message_parts.append(f"Category: {task.category}")

        # Snooze count
        if alarm.snooze_count > 0:
            message_parts.append(f"Snoozed {alarm.snooze_count} time(s)")

        return " | ".join(message_parts)

    def play_alarm_sound(self, sound_file: str):
        """Play alarm sound."""
        try:
            # Try to use playsound
            from playsound import playsound

            sound_path = self.get_sound_path(sound_file)
            if sound_path and sound_path.exists():
                # Adjust volume (this would require audio processing)
                playsound(str(sound_path))
            else:
                # Use system default sound
                import platform
                if platform.system() == "Windows":
                    import winsound
                    winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
                elif platform.system() == "Darwin":  # macOS
                    os.system("afplay /System/Library/Sounds/Glass.aiff")
                else:  # Linux
                    os.system("paplay /usr/share/sounds/alsa/Front_Left.wav")

        except ImportError:
            # Fallback to system beep
            print("\a")  # Bell character
        except Exception as e:
            print(f"Error playing sound: {e}")

    def get_sound_path(self, sound_file: str) -> Optional[Path]:
        """Get the full path to a sound file."""
        if sound_file == "default":
            return None  # Use system default

        sound_path = self.sound_directory / sound_file
        return sound_path if sound_path.exists() else None

    def snooze_alarm(self, alarm_id: int, minutes: int = None):
        """Snooze an alarm."""
        try:
            snooze_minutes = minutes or self.snooze_duration

            # Get alarm details
            alarms = self.db.get_pending_alarms()
            alarm_data = next((a for a in alarms if a['id'] == alarm_id), None)

            if not alarm_data:
                return False

            alarm = Alarm(alarm_data)

            # Check snooze limit
            if alarm.snooze_count >= self.max_snooze_count:
                return False

            # Calculate next trigger time
            next_trigger = datetime.now() + timedelta(minutes=snooze_minutes)

            # Update snooze information
            self.snoozed_alarms[alarm_id] = {
                'next_trigger': next_trigger,
                'snooze_count': alarm.snooze_count + 1
            }

            # Update alarm in database
            self.db.update_alarm(alarm_id, {
                'snooze_count': alarm.snooze_count + 1,
                'alarm_time': next_trigger.isoformat(),
                'is_active': True
            })

            return True

        except Exception as e:
            print(f"Error snoozing alarm: {e}")
            return False

    def dismiss_alarm(self, alarm_id: int):
        """Dismiss an alarm."""
        try:
            # Remove from active alarms
            self.active_alarms = [a for a in self.active_alarms if a.id != alarm_id]

            # Remove from snoozed alarms
            if alarm_id in self.snoozed_alarms:
                del self.snoozed_alarms[alarm_id]

            # Update alarm in database
            self.db.update_alarm(alarm_id, {"is_active": False})

            return True

        except Exception as e:
            print(f"Error dismissing alarm: {e}")
            return False

    def auto_dismiss_alarm(self, alarm_id: int):
        """Automatically dismiss an alarm after timeout."""
        self.dismiss_alarm(alarm_id)

    def create_alarm(self, task_id: int, alarm_time: datetime, sound_file: str = None,
                    volume: float = None) -> bool:
        """Create a new alarm for a task."""
        try:
            alarm = Alarm({
                'task_id': task_id,
                'alarm_time': alarm_time.isoformat(),
                'is_active': True,
                'sound_file': sound_file or self.default_sound,
                'volume': volume or self.volume,
                'snooze_count': 0
            })

            alarm_id = self.db.create_alarm(alarm)
            return alarm_id > 0

        except Exception as e:
            print(f"Error creating alarm: {e}")
            return False

    def schedule_next_recurring_alarm(self, task: Task, old_alarm: Alarm):
        """Schedule the next alarm for a recurring task."""
        try:
            if task.recurring_type == "None":
                return

            # Calculate next due date
            if task.due_date:
                due_date = datetime.fromisoformat(task.due_date.replace('Z', '+00:00'))
            else:
                return

            next_due = self.calculate_next_recurring_date(task, due_date)
            if not next_due:
                return

            # Calculate next alarm time (reminder before due date)
            if old_alarm.alarm_time and task.due_date:
                try:
                    alarm_time = datetime.fromisoformat(old_alarm.alarm_time.replace('Z', '+00:00'))
                    due_time = datetime.fromisoformat(task.due_date.replace('Z', '+00:00'))
                    time_diff = due_time - alarm_time

                    next_alarm_time = next_due - time_diff
                except ValueError:
                    next_alarm_time = next_due - timedelta(minutes=15)  # Default 15 minutes
            else:
                next_alarm_time = next_due - timedelta(minutes=15)

            # Create next alarm
            self.create_alarm(task.id, next_alarm_time, old_alarm.sound_file, old_alarm.volume)

        except Exception as e:
            print(f"Error scheduling recurring alarm: {e}")

    def calculate_next_recurring_date(self, task: Task, current_due: datetime) -> Optional[datetime]:
        """Calculate the next due date for a recurring task."""
        try:
            if task.recurring_type == "Daily":
                next_due = current_due + timedelta(days=task.recurring_interval)
            elif task.recurring_type == "Weekly":
                next_due = current_due + timedelta(weeks=task.recurring_interval)
            elif task.recurring_type == "Monthly":
                # Handle month rollover
                next_month = current_due.month + task.recurring_interval
                year = current_due.year + (next_month - 1) // 12
                month = (next_month - 1) % 12 + 1

                # Handle day overflow (e.g., January 31 -> February 28/29)
                day = min(current_due.day, self.get_days_in_month(year, month))
                next_due = current_due.replace(year=year, month=month, day=day)
            elif task.recurring_type == "Custom":
                next_due = current_due + timedelta(days=task.recurring_interval)
            else:
                return None

            return next_due

        except Exception as e:
            print(f"Error calculating next recurring date: {e}")
            return None

    def get_days_in_month(self, year: int, month: int) -> int:
        """Get the number of days in a month."""
        import calendar
        return calendar.monthrange(year, month)[1]

    def get_active_alarms(self) -> List[Dict[str, Any]]:
        """Get list of currently active alarms."""
        active_alarms_data = []
        for alarm in self.active_alarms:
            task = self.db.get_task(alarm.task_id)
            if task:
                active_alarms_data.append({
                    'alarm_id': alarm.id,
                    'task': task,
                    'alarm_time': alarm.alarm_time,
                    'sound_file': alarm.sound_file,
                    'snooze_count': alarm.snooze_count
                })

        return active_alarms_data

    def get_upcoming_alarms(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get alarms scheduled within the specified hours."""
        future_time = datetime.now() + timedelta(hours=hours)
        upcoming_alarms = self.db.get_all_tasks()  # This would need to be modified for alarms

        # For now, return empty list
        return []

    def add_notification_callback(self, callback: Callable):
        """Add a callback function to be called when alarms trigger."""
        self.notification_callbacks.append(callback)

    def remove_notification_callback(self, callback: Callable):
        """Remove a notification callback."""
        if callback in self.notification_callbacks:
            self.notification_callbacks.remove(callback)

    def update_settings(self, settings: Dict[str, Any]):
        """Update alarm system settings."""
        if 'sound_enabled' in settings:
            self.sound_enabled = settings['sound_enabled']

        if 'volume' in settings:
            self.volume = settings['volume']

        if 'default_sound' in settings:
            self.default_sound = settings['default_sound']

        if 'snooze_duration' in settings:
            self.snooze_duration = settings['snooze_duration']

        if 'max_snooze_count' in settings:
            self.max_snooze_count = settings['max_snooze_count']

        if 'auto_dismiss_minutes' in settings:
            self.auto_dismiss_minutes = settings['auto_dismiss_minutes']

        if 'persistent_alarms' in settings:
            self.persistent_alarms = settings['persistent_alarms']

    def test_alarm(self, sound_file: str = None):
        """Test alarm sound and notification."""
        try:
            # Create a test task
            test_task = Task({
                'id': 0,  # Test ID
                'title': 'Test Alarm',
                'description': 'This is a test alarm',
                'priority': 'Medium',
                'category': 'Testing'
            })

            # Create test alarm
            test_alarm = Alarm({
                'id': 0,  # Test ID
                'task_id': 0,
                'alarm_time': datetime.now().isoformat(),
                'is_active': True,
                'sound_file': sound_file or self.default_sound,
                'volume': self.volume,
                'snooze_count': 0
            })

            # Trigger test alarm
            self.create_alarm_notification(test_task, test_alarm)
            if self.sound_enabled:
                self.play_alarm_sound(sound_file or self.default_sound)

            return True

        except Exception as e:
            print(f"Error testing alarm: {e}")
            return False


# Global alarm system instance
alarm_system = AlarmSystem()


def get_alarm_system() -> AlarmSystem:
    """Get the global alarm system instance."""
    return alarm_system