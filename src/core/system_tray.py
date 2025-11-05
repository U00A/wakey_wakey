"""
System Tray integration for the task scheduler application.
Provides system tray functionality with menu and notifications.
"""

import os
import sys
import threading
from typing import List, Dict, Any, Optional, Callable
from pathlib import Path

from ..utils.config import get_config
from ..ui.themes.theme_manager import get_theme_manager
from ..database.manager import DatabaseManager
from ..core.notification_service import get_notification_service


class SystemTray:
    """System tray integration for the task scheduler."""

    def __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self):
        if hasattr(self, '_initialized'):
            return

        self.config = get_config()
        self.theme_manager = get_theme_manager()
        self.db = DatabaseManager()
        self.notification_service = get_notification_service()

        # Tray state
        self.is_tray_active = False
        self.tray_icon = None
        self.main_window = None
        self.is_minimized = False

        # Menu items
        self.menu_items = []
        self.task_count = 0

        # Tray settings
        self.enable_tray = self.config.get("minimize_to_tray", True)
        self.show_notifications = True

        self._initialized = True

    def initialize(self, main_window):
        """Initialize system tray with main window reference."""
        self.main_window = main_window

        if self.enable_tray:
            self.create_tray_icon()

    def create_tray_icon(self):
        """Create system tray icon."""
        try:
            # Try different tray libraries
            if self._create_tray_with_pystray():
                return
            elif self._create_tray_with_pyrstray():
                return
            elif self._create_tray_with_trayicon():
                return
            else:
                print("No system tray library available")

        except Exception as e:
            print(f"Error creating system tray: {e}")

    def _create_tray_with_pystray(self) -> bool:
        """Create tray icon using pystray."""
        try:
            import pystray
            from PIL import Image, ImageDraw

            # Create icon
            icon_image = self.create_tray_icon_image()

            # Create menu
            menu = pystray.Menu(
                pystray.MenuItem("Show", self.show_window, default=True),
                pystray.MenuItem("New Task", self.new_task),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Dashboard", lambda: self.switch_view("dashboard")),
                pystray.MenuItem("Tasks", lambda: self.switch_view("tasks")),
                pystray.MenuItem("Calendar", lambda: self.switch_view("calendar")),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Settings", lambda: self.switch_view("settings")),
                pystray.MenuItem("Quit", self.quit_application)
            )

            # Create icon
            self.tray_icon = pystray.Icon(
                "Task Scheduler Pro",
                icon_image,
                "Task Scheduler Pro",
                menu
            )

            # Start tray in separate thread
            def run_tray():
                self.tray_icon.run()

            tray_thread = threading.Thread(target=run_tray, daemon=True)
            tray_thread.start()

            self.is_tray_active = True
            return True

        except ImportError:
            return False
        except Exception as e:
            print(f"Error with pystray: {e}")
            return False

    def _create_tray_with_pyrstray(self) -> bool:
        """Create tray icon using pystray (alternative)."""
        try:
            import pystray
            from PIL import Image, ImageDraw

            # This is similar to pystray implementation
            return self._create_tray_with_pystray()

        except ImportError:
            return False
        except Exception as e:
            print(f"Error with pystray: {e}")
            return False

    def _create_tray_with_trayicon(self) -> bool:
        """Create tray icon using trayicon."""
        try:
            import trayicon

            # Create icon
            icon_image = self.create_tray_icon_image()

            # Create menu
            menu = trayicon.Menu(
                trayicon.MenuItem("Show", self.show_window, default=True),
                trayicon.MenuItem("New Task", self.new_task),
                trayicon.Menu.SEPARATOR,
                trayicon.MenuItem("Dashboard", lambda: self.switch_view("dashboard")),
                trayicon.MenuItem("Tasks", lambda: self.switch_view("tasks")),
                trayicon.MenuItem("Calendar", lambda: self.switch_view("calendar")),
                trayicon.Menu.SEPARATOR,
                trayicon.MenuItem("Settings", lambda: self.switch_view("settings")),
                trayicon.MenuItem("Quit", self.quit_application)
            )

            # Create and run icon
            self.tray_icon = trayicon.TrayIcon(
                "Task Scheduler Pro",
                icon_image,
                menu
            )

            # Start in separate thread
            def run_tray():
                self.tray_icon.run()

            tray_thread = threading.Thread(target=run_tray, daemon=True)
            tray_thread.start()

            self.is_tray_active = True
            return True

        except ImportError:
            return False
        except Exception as e:
            print(f"Error with trayicon: {e}")
            return False

    def create_tray_icon_image(self):
        """Create tray icon image."""
        try:
            from PIL import Image, ImageDraw

            # Create a simple 64x64 icon
            size = 64
            image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(image)

            # Draw a simple calendar/task icon
            # Background circle
            if self.theme_manager.is_dark_theme():
                bg_color = (30, 30, 30, 255)  # Dark theme
                text_color = (255, 255, 255, 255)
            else:
                bg_color = (255, 255, 255, 255)  # Light theme
                text_color = (0, 0, 0, 255)

            draw.ellipse([8, 8, 56, 56], fill=bg_color)

            # Draw calendar grid
            grid_color = (100, 100, 100, 255)
            for i in range(3):
                y = 20 + i * 12
                draw.line([16, y, 48, y], fill=grid_color)
            for i in range(7):
                x = 16 + i * 6
                draw.line([x, 20, x, 56], fill=grid_color)

            # Draw checkmark for completed tasks
            check_color = (0, 255, 0, 255)
            draw.polygon([(20, 35), (25, 40), (35, 30), (30, 30), (30, 25), (20, 35)], fill=check_color)

            return image

        except ImportError:
            # If PIL is not available, return None
            return None
        except Exception as e:
            print(f"Error creating tray icon: {e}")
            return None

    def update_tray_icon(self, show_badge: bool = False, badge_count: int = 0):
        """Update tray icon with optional badge."""
        if not self.is_tray_active or not self.tray_icon:
            return

        try:
            # Update icon with badge if needed
            if show_badge and badge_count > 0:
                # Create icon with badge
                icon_image = self.create_tray_icon_with_badge(badge_count)
                if icon_image and hasattr(self.tray_icon, 'update_icon'):
                    self.tray_icon.update_icon(icon_image)
        except Exception as e:
            print(f"Error updating tray icon: {e}")

    def create_tray_icon_with_badge(self, badge_count: int):
        """Create tray icon with notification badge."""
        try:
            from PIL import Image, ImageDraw, ImageFont

            # Get base icon
            base_icon = self.create_tray_icon_image()
            if not base_icon:
                return None

            # Create badge
            badge_size = 20
            badge_image = Image.new('RGBA', (badge_size, badge_size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(badge_image)

            # Draw badge background
            badge_color = (255, 0, 0, 255)  # Red badge
            draw.ellipse([2, 2, 18, 18], fill=badge_color)

            # Draw badge text
            try:
                font = ImageFont.truetype("arial.ttf", 12)
            except:
                font = ImageFont.load_default()

            text_color = (255, 255, 255, 255)
            text = str(badge_count) if badge_count < 100 else "99+"
            text_width, text_height = draw.textsize(text, font=font)
            text_x = (badge_size - text_width) // 2
            text_y = (badge_size - text_height) // 2
            draw.text((text_x, text_y), text, fill=text_color, font=font)

            # Paste badge onto base icon
            base_image.paste(badge_image, (44, 44), badge_image)

            return base_image

        except Exception as e:
            print(f"Error creating badge icon: {e}")
            return None

    def update_task_count(self):
        """Update pending task count."""
        try:
            # Get pending tasks count
            stats = self.db.get_task_statistics()
            self.task_count = stats.get('pending', 0)

            # Update tray icon
            self.update_tray_icon(show_badge=self.task_count > 0, badge_count=self.task_count)

        except Exception as e:
            print(f"Error updating task count: {e}")

    def minimize_to_tray(self):
        """Minimize application to system tray."""
        if not self.main_window or not self.is_tray_active:
            return

        try:
            # Hide main window
            self.main_window.withdraw()
            self.is_minimized = True

            # Show notification
            if self.show_notifications:
                self.notification_service.send_notification(
                    "Minimized to Tray",
                    "Task Scheduler Pro is running in the system tray.",
                    "minimize"
                )

        except Exception as e:
            print(f"Error minimizing to tray: {e}")

    def restore_from_tray(self):
        """Restore application from system tray."""
        if not self.main_window or not self.is_minimized:
            return

        try:
            # Show main window
            self.main_window.deiconify()
            self.main_window.lift()
            self.main_window.focus_force()
            self.is_minimized = False

        except Exception as e:
            print(f"Error restoring from tray: {e}")

    def show_window(self):
        """Show the main window."""
        if self.is_minimized:
            self.restore_from_tray()
        else:
            self.main_window.lift()
            self.main_window.focus_force()

    def new_task(self):
        """Create new task from tray."""
        try:
            if self.main_window:
                # Switch to tasks view and create new task
                if hasattr(self.main_window, 'switch_view'):
                    self.main_window.switch_view("tasks")
                if hasattr(self.main_window, 'new_task'):
                    self.main_window.new_task()

            self.show_window()
        except Exception as e:
            print(f"Error creating task from tray: {e}")

    def switch_view(self, view_name: str):
        """Switch to specific view."""
        try:
            if self.main_window and hasattr(self.main_window, 'switch_view'):
                self.main_window.switch_view(view_name)
            self.show_window()
        except Exception as e:
            print(f"Error switching view from tray: {e}")

    def quit_application(self):
        """Quit the application."""
        try:
            if self.main_window:
                self.main_window.quit()
            elif self.is_tray_active:
                self.is_tray_active = False
                if hasattr(self.tray_icon, 'stop'):
                    self.tray_icon.stop()
        except Exception as e:
            print(f"Error quitting application: {e}")

    def add_menu_item(self, label: str, action: Callable, **kwargs):
        """Add a custom menu item."""
        if not self.is_tray_active:
            return False

        try:
            # This would need to be implemented based on the specific tray library used
            # For now, just return True as placeholder
            return True
        except Exception as e:
            print(f"Error adding menu item: {e}")
            return False

    def remove_menu_item(self, label: str):
        """Remove a menu item."""
        if not self.is_tray_active:
            return False

        try:
            # This would need to be implemented based on the specific tray library used
            return True
        except Exception as e:
            print(f"Error removing menu item: {e}")
            return False

    def show_balloon_notification(self, title: str, message: str, duration: int = 5000):
        """Show balloon notification from tray."""
        if not self.is_tray_active or not self.tray_icon:
            return

        try:
            # Try to show balloon notification
            if hasattr(self.tray_icon, 'show_balloon'):
                self.tray_icon.show_balloon(title, message, duration)
            elif hasattr(self.tray_icon, 'notify'):
                self.tray_icon.notify(title, message, duration)
            else:
                # Fallback to regular notification
                self.notification_service.send_notification(title, message)
        except Exception as e:
            print(f"Error showing balloon notification: {e}")

    def set_tray_tooltip(self, tooltip: str):
        """Set tray icon tooltip."""
        if not self.is_tray_active or not self.tray_icon:
            return

        try:
            if hasattr(self.tray_icon, 'set_tooltip'):
                self.tray_icon.set_tooltip(tooltip)
        except Exception as e:
            print(f"Error setting tray tooltip: {e}")

    def start_task_count_updater(self):
        """Start automatic task count updates."""
        def update_loop():
            while self.is_tray_active:
                self.update_task_count()
                # Update every 30 seconds
                import time
                time.sleep(30)

        updater_thread = threading.Thread(target=update_loop, daemon=True)
        updater_thread.start()

    def stop(self):
        """Stop system tray."""
        if self.is_tray_active and self.tray_icon:
            try:
                if hasattr(self.tray_icon, 'stop'):
                    self.tray_icon.stop()
                self.is_tray_active = False
            except Exception as e:
                print(f"Error stopping system tray: {e}")

    def is_available(self) -> bool:
        """Check if system tray is available."""
        try:
            import pystray
            return True
        except ImportError:
            pass

        try:
            import trayicon
            return True
        except ImportError:
            pass

        return False

    def get_status(self) -> Dict[str, Any]:
        """Get current system tray status."""
        return {
            "is_active": self.is_tray_active,
            "is_minimized": self.is_minimized,
            "task_count": self.task_count,
            "enable_tray": self.enable_tray,
            "show_notifications": self.show_notifications
        }


# Global system tray instance
system_tray = SystemTray()


def get_system_tray() -> SystemTray:
    """Get the global system tray instance."""
    return system_tray