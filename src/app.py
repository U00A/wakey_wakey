"""
Main application class for the task scheduler desktop application.
Handles application lifecycle, window management, and system integration.
"""

import os
import sys
from typing import Optional, Dict, Any
from pathlib import Path

import customtkinter as ctk
from tkinter import messagebox

# Add src directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.manager import DatabaseManager
from ui.themes.theme_manager import ThemeManager, get_theme_manager
from utils.config import get_config
from utils.helpers import ensure_directory_exists, get_system_info


class TaskSchedulerApp:
    """Main application class for the task scheduler."""

    def __init__(self):
        # Initialize CustomTkinter
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Initialize components
        self.config = get_config()
        self.theme_manager = get_theme_manager()
        self.database = DatabaseManager()

        # Set up application directories
        self._setup_directories()

        # Initialize window
        self.root = None
        self.setup_window()

        # Initialize UI components
        self.current_view = "dashboard"
        self.views = {}
        self.sidebar = None
        self.main_content = None

        # System tray (will be implemented later)
        self.tray_icon = None

        # Application state
        self.is_running = True
        self.current_task = None

        # Apply initial theme
        self._apply_theme()

    def _setup_directories(self):
        """Ensure all required directories exist."""
        directories = [
            self.config.get("data_directory", "data"),
            self.config.get("sound_directory", "assets/sounds"),
            "data/backups",
            "data/exports"
        ]

        for directory in directories:
            ensure_directory_exists(directory)

    def setup_window(self):
        """Set up the main application window."""
        self.root = ctk.CTk()
        self.root.title("Task Scheduler Pro")
        self.root.geometry(f"{1200}x{800}")
        self.root.minsize(800, 600)

        # Set window icon (will be added later)
        # self.root.iconbitmap("assets/icons/app.ico")

        # Configure window grid
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        # Apply window geometry from config
        geometry = self.config.get_window_geometry()
        if geometry["size"]:
            self.root.geometry(f"{geometry['size'][0]}x{geometry['size'][1]}")

        # Bind window events
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.bind("<Configure>", self.on_window_resize)

        # Bind keyboard shortcuts
        self._setup_keyboard_shortcuts()

    def _setup_keyboard_shortcuts(self):
        """Set up global keyboard shortcuts."""
        shortcuts = {
            "<Control-n>": self.new_task,
            "<Control-f>": self.search_tasks,
            "<Control-d>": self.toggle_theme,
            "<Control-q>": self.quit_application,
            "<F5>": self.refresh_current_view,
            "<F1>": self.show_help,
            "<Control-m>": self.minimize_to_tray,
            "<Control-1>": lambda: self.switch_view("dashboard"),
            "<Control-2>": lambda: self.switch_view("tasks"),
            "<Control-3>": lambda: self.switch_view("calendar"),
            "<Control-4>": lambda: self.switch_view("statistics"),
            "<Control-5>": lambda: self.switch_view("settings"),
        }

        for shortcut, command in shortcuts.items():
            self.root.bind(shortcut, lambda e, cmd=command: cmd())

    def _apply_theme(self):
        """Apply the current theme to the application."""
        self.theme_manager._apply_theme_to_ctk()

        # Apply theme colors to root window
        theme_colors = self.theme_manager.get_theme_colors()
        self.root.configure(fg_color=theme_colors["background"])

    def create_ui(self):
        """Create the main UI components."""
        self.create_sidebar()
        self.create_main_content()
        self.create_status_bar()

        # Initialize default view
        self.switch_view("dashboard")

    def create_sidebar(self):
        """Create the navigation sidebar."""
        self.sidebar = ctk.CTkFrame(self.root, width=250, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(10, weight=1)  # Give space for expansion
        self.sidebar.grid_propagate(False)

        # App title
        title_frame = ctk.CTkFrame(self.sidebar)
        title_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        app_title = ctk.CTkLabel(
            title_frame,
            text="Task Scheduler Pro",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        app_title.pack(pady=10)

        # Theme toggle button
        theme_button = ctk.CTkButton(
            title_frame,
            text="🌙 Dark Mode" if self.theme_manager.is_dark_theme() else "☀️ Light Mode",
            command=self.toggle_theme,
            width=200
        )
        theme_button.pack(pady=5)

        # Navigation buttons
        navigation_items = [
            ("📊 Dashboard", "dashboard", "Ctrl+1"),
            ("📝 Tasks", "tasks", "Ctrl+2"),
            ("📅 Calendar", "calendar", "Ctrl+3"),
            ("📈 Statistics", "statistics", "Ctrl+4"),
            ("⚙️ Settings", "settings", "Ctrl+5")
        ]

        for i, (text, view_name, shortcut) in enumerate(navigation_items, start=1):
            btn = ctk.CTkButton(
                self.sidebar,
                text=f"{text}\n{shortcut}",
                command=lambda v=view_name: self.switch_view(v),
                width=200,
                height=50,
                anchor="w"
            )
            btn.grid(row=i, column=0, padx=10, pady=5, sticky="ew")

        # Quick actions section
        quick_actions_frame = ctk.CTkFrame(self.sidebar)
        quick_actions_frame.grid(row=6, column=0, padx=10, pady=20, sticky="ew")

        quick_actions_title = ctk.CTkLabel(
            quick_actions_frame,
            text="Quick Actions",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        quick_actions_title.pack(pady=5)

        new_task_btn = ctk.CTkButton(
            quick_actions_frame,
            text="➕ New Task (Ctrl+N)",
            command=self.new_task,
            width=200
        )
        new_task_btn.pack(pady=5)

        search_btn = ctk.CTkButton(
            quick_actions_frame,
            text="🔍 Search (Ctrl+F)",
            command=self.search_tasks,
            width=200
        )
        search_btn.pack(pady=5)

        # System tray toggle
        tray_btn = ctk.CTkButton(
            quick_actions_frame,
            text="📱 Minimize to Tray (Ctrl+M)",
            command=self.minimize_to_tray,
            width=200
        )
        tray_btn.pack(pady=5)

        # Statistics preview
        stats_frame = ctk.CTkFrame(self.sidebar)
        stats_frame.grid(row=8, column=0, padx=10, pady=20, sticky="ew")

        stats_title = ctk.CTkLabel(
            stats_frame,
            text="Today's Overview",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        stats_title.pack(pady=5)

        self.stats_label = ctk.CTkLabel(
            stats_frame,
            text="Loading...",
            justify="left"
        )
        self.stats_label.pack(pady=5, padx=10)

        # Exit button
        exit_btn = ctk.CTkButton(
            self.sidebar,
            text="🚪 Exit (Ctrl+Q)",
            command=self.quit_application,
            width=200,
            fg_color="red",
            hover_color="darkred"
        )
        exit_btn.grid(row=9, column=0, padx=10, pady=10, sticky="ew")

    def create_main_content(self):
        """Create the main content area."""
        self.main_content = ctk.CTkFrame(self.root)
        self.main_content.grid(row=0, column=1, sticky="nsew")
        self.main_content.grid_columnconfigure(0, weight=1)
        self.main_content.grid_rowconfigure(0, weight=1)

        # Initialize views (placeholders for now)
        self._initialize_views()

    def _initialize_views(self):
        """Initialize all view components."""
        # These will be replaced with actual view components
        self.views = {
            "dashboard": self._create_placeholder_view("Dashboard"),
            "tasks": self._create_placeholder_view("Tasks"),
            "calendar": self._create_placeholder_view("Calendar"),
            "statistics": self._create_placeholder_view("Statistics"),
            "settings": self._create_placeholder_view("Settings")
        }

    def _create_placeholder_view(self, view_name: str) -> ctk.CTkFrame:
        """Create a placeholder view for development."""
        view_frame = ctk.CTkFrame(self.main_content)
        view_frame.grid_columnconfigure(0, weight=1)
        view_frame.grid_rowconfigure(0, weight=1)

        placeholder = ctk.CTkLabel(
            view_frame,
            text=f"{view_name} View\n(Coming Soon)",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        placeholder.grid(row=0, column=0, padx=20, pady=20)

        return view_frame

    def create_status_bar(self):
        """Create the status bar at the bottom of the window."""
        status_bar = ctk.CTkFrame(self.root, height=30)
        status_bar.grid(row=1, column=0, columnspan=2, sticky="ew")
        status_bar.grid_propagate(False)

        # Status message
        self.status_label = ctk.CTkLabel(
            status_bar,
            text="Ready",
            anchor="w"
        )
        self.status_label.pack(side="left", padx=10)

        # Task count
        self.task_count_label = ctk.CTkLabel(
            status_bar,
            text="0 tasks",
            anchor="e"
        )
        self.task_count_label.pack(side="right", padx=10)

        # Current time
        self.time_label = ctk.CTkLabel(
            status_bar,
            text="",
            anchor="center"
        )
        self.time_label.pack(side="right", padx=10)

        # Update time
        self.update_status_bar()

    def update_status_bar(self):
        """Update status bar information."""
        # Update time
        from datetime import datetime
        current_time = datetime.now().strftime("%I:%M:%S %p")
        self.time_label.configure(text=current_time)

        # Update task count
        try:
            stats = self.database.get_task_statistics()
            total_tasks = stats['total']
            pending_tasks = stats['pending']
            self.task_count_label.configure(text=f"{pending_tasks}/{total_tasks} pending")
        except:
            self.task_count_label.configure(text="0 tasks")

        # Schedule next update
        if self.is_running:
            self.root.after(1000, self.update_status_bar)  # Update every second

    def switch_view(self, view_name: str):
        """Switch to a different view."""
        if view_name not in self.views:
            self.show_error(f"Unknown view: {view_name}")
            return

        # Hide current view
        if self.current_view in self.views:
            self.views[self.current_view].grid_forget()

        # Show new view
        self.views[view_name].grid(row=0, column=0, sticky="nsew")
        self.current_view = view_name

        # Update status
        self.set_status(f"Switched to {view_name.title()} view")

        # Update view-specific data
        self._update_view_data(view_name)

    def _update_view_data(self, view_name: str):
        """Update data for the current view."""
        if view_name == "dashboard":
            self._update_dashboard_stats()
        # Other views will be implemented later

    def _update_dashboard_stats(self):
        """Update dashboard statistics."""
        try:
            stats = self.database.get_task_statistics()
            stats_text = (
                f"Total: {stats['total']}\n"
                f"Completed: {stats['completed']}\n"
                f"Pending: {stats['pending']}\n"
                f"Completion: {stats['completion_rate']}%"
            )
            self.stats_label.configure(text=stats_text)
        except:
            self.stats_label.configure(text="Stats unavailable")

    # Window event handlers
    def on_window_resize(self, event):
        """Handle window resize events."""
        # Save window geometry
        if hasattr(self, 'root') and self.root:
            try:
                size = f"{self.root.winfo_width()}x{self.root.winfo_height()}"
                position = f"+{self.root.winfo_x()}+{self.root.winfo_y()}"
                self.config.set_window_geometry(
                    size=[self.root.winfo_width(), self.root.winfo_height()],
                    position=[self.root.winfo_x(), self.root.winfo_y()]
                )
            except:
                pass

    def on_closing(self):
        """Handle application closing."""
        if self.config.get("minimize_to_tray", True):
            self.minimize_to_tray()
        else:
            self.quit_application()

    # Application control methods
    def new_task(self):
        """Open new task dialog."""
        self.show_info("New Task dialog will be implemented")

    def search_tasks(self):
        """Open search dialog."""
        self.show_info("Search functionality will be implemented")

    def toggle_theme(self):
        """Toggle between dark and light themes."""
        new_theme = self.theme_manager.toggle_theme()
        self._apply_theme()

        # Update theme button text
        if self.sidebar:
            # Find and update theme button
            for widget in self.sidebar.winfo_children():
                if isinstance(widget, ctk.CTkFrame):
                    for child in widget.winfo_children():
                        if isinstance(child, ctk.CTkButton) and "Mode" in str(child.cget("text")):
                            theme_text = "🌙 Dark Mode" if self.theme_manager.is_dark_theme() else "☀️ Light Mode"
                            child.configure(text=theme_text)
                            break

        self.set_status(f"Switched to {new_theme} theme")

    def refresh_current_view(self):
        """Refresh the current view."""
        self._update_view_data(self.current_view)
        self.set_status("View refreshed")

    def minimize_to_tray(self):
        """Minimize application to system tray."""
        self.root.withdraw()
        self.set_status("Minimized to system tray")
        # System tray implementation will be added later

    def restore_from_tray(self):
        """Restore application from system tray."""
        self.root.deiconify()
        self.root.lift()
        self.set_status("Restored from system tray")

    def show_help(self):
        """Show help dialog."""
        help_text = """
Task Scheduler Pro - Help

Keyboard Shortcuts:
• Ctrl+N - New Task
• Ctrl+F - Search
• Ctrl+D - Toggle Theme
• Ctrl+M - Minimize to Tray
• Ctrl+Q - Quit
• F5 - Refresh View
• F1 - Help

View Navigation:
• Ctrl+1 - Dashboard
• Ctrl+2 - Tasks
• Ctrl+3 - Calendar
• Ctrl+4 - Statistics
• Ctrl+5 - Settings

For more help, check the documentation.
        """
        messagebox.showinfo("Help", help_text.strip())

    def quit_application(self):
        """Quit the application."""
        if messagebox.askyesno("Quit", "Are you sure you want to quit?"):
            self.is_running = False
            self.root.quit()
            self.root.destroy()

    # Status and message methods
    def set_status(self, message: str):
        """Set status bar message."""
        if hasattr(self, 'status_label'):
            self.status_label.configure(text=message)

    def show_info(self, message: str):
        """Show info message."""
        messagebox.showinfo("Information", message)

    def show_error(self, message: str):
        """Show error message."""
        messagebox.showerror("Error", message)

    def show_warning(self, message: str):
        """Show warning message."""
        messagebox.showwarning("Warning", message)

    # Application lifecycle
    def run(self):
        """Run the application."""
        try:
            self.create_ui()
            self.set_status("Application started successfully")
            self.root.mainloop()
        except Exception as e:
            messagebox.showerror("Startup Error", f"Failed to start application: {str(e)}")
            self.is_running = False


def main():
    """Main entry point for the application."""
    try:
        app = TaskSchedulerApp()
        app.run()
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
    except Exception as e:
        print(f"Application error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()