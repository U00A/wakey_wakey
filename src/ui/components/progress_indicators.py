"""
Progress Indicators and Loading States component.
Provides modern progress bars, loading spinners, and status indicators.
"""

import os
import sys
import threading
import time
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime

import customtkinter as ctk

# Add parent directories to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ..themes.theme_manager import get_theme_manager


class LoadingSpinner(ctk.CTkFrame):
    """Animated loading spinner component."""

    def __init__(self, parent, size="medium", **kwargs):
        super().__init__(parent, **kwargs)

        self.theme_manager = get_theme_manager()
        self.is_spinning = False
        self.animation_angle = 0

        # Size options
        self.sizes = {
            "small": 20,
            "medium": 30,
            "large": 40
        }

        self.spinner_size = self.sizes.get(size, 30)

        # Configure frame
        self.configure(width=self.spinner_size, height=self.spinner_size)
        self.grid_propagate(False)

        # Create spinner canvas
        self.canvas = ctk.CTkCanvas(
            self,
            width=self.spinner_size,
            height=self.spinner_size,
            highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)

        # Start animation
        self.start_spinning()

    def start_spinning(self):
        """Start the spinning animation."""
        if not self.is_spinning:
            self.is_spinning = True
            self.animate()

    def stop_spinning(self):
        """Stop the spinning animation."""
        self.is_spinning = False

    def animate(self):
        """Animate the spinner."""
        if not self.is_spinning:
            return

        # Clear canvas
        self.canvas.delete("all")

        # Draw spinner
        center_x = self.spinner_size // 2
        center_y = self.spinner_size // 2
        radius = (self.spinner_size // 2) - 5

        # Draw spinner arcs
        num_segments = 8
        segment_angle = 360 / num_segments

        for i in range(num_segments):
            start_angle = self.animation_angle + (i * segment_angle)
            extent = segment_angle - 10  # Leave gaps between segments

            # Calculate arc coordinates
            start_rad = math.radians(start_angle)
            extent_rad = math.radians(extent)

            start_x = center_x + radius * math.cos(start_rad)
            start_y = center_y + radius * math.sin(start_rad)
            end_x = center_x + radius * math.cos(start_rad + extent_rad)
            end_y = center_y + radius * math.sin(start_rad + extent_rad)

            # Draw arc
            self.canvas.create_arc(
                center_x - radius, center_y - radius,
                center_x + radius, center_y + radius,
                start_angle, start_angle + extent,
                outline=self.theme_manager.get_color("primary"),
                width=3,
                style="arc"
            )

        # Update angle
        self.animation_angle = (self.animation_angle + 15) % 360

        # Schedule next animation frame
        self.after(50, self.animate)

    def __del__(self):
        """Cleanup when destroyed."""
        self.stop_spinning()


class ProgressBar(ctk.CTkFrame):
    """Modern progress bar component."""

    def __init__(self, parent, width=300, height=20, **kwargs):
        super().__init__(parent, **kwargs)

        self.theme_manager = get_theme_manager()

        # Configure frame
        self.configure(width=width, height=height)
        self.grid_propagate(False)

        # Progress variables
        self.progress = 0.0
        self.maximum = 100.0
        self.show_percentage = True
        self.indeterminate = False

        # Create progress bar
        self.create_progress_bar()

    def create_progress_bar(self):
        """Create the progress bar visual."""
        # Background
        self.bg_bar = ctk.CTkFrame(
            self,
            fg_color=self.theme_manager.get_color("surface"),
            height=16
        )
        self.bg_bar.pack(fill="x", pady=2)

        self.bg_bar.grid_columnconfigure(0, weight=1)

        # Progress fill
        self.progress_bar = ctk.CTkFrame(
            self.bg_bar,
            fg_color=self.theme_manager.get_color("primary"),
            height=16
        )
        self.progress_bar.grid(row=0, column=0, sticky="w", padx=2, pady=2)
        self.progress_bar.grid_columnconfigure(0, weight=1)

        # Progress text
        self.progress_text = ctk.CTkLabel(
            self,
            text="0%",
            font=ctk.CTkFont(size=10)
        )
        self.progress_text.place(relx=0.5, rely=0.5, anchor="center")

    def set_progress(self, value: float):
        """Set progress value (0-100)."""
        self.progress = max(0, min(100, value))
        self.update_display()

    def set_maximum(self, maximum: float):
        """Set maximum value."""
        self.maximum = max(1, maximum)
        self.update_display()

    def set_show_percentage(self, show: bool):
        """Show/hide percentage text."""
        self.show_percentage = show
        if show:
            self.progress_text.grid()
        else:
            self.progress_text.grid_forget()

    def set_indeterminate(self, indeterminate: bool):
        """Set indeterminate state."""
        self.indeterminate = indeterminate
        if indeterminate:
            self.start_indeterminate_animation()
        else:
            self.stop_indeterminate_animation()

    def update_display(self):
        """Update the progress display."""
        if self.indeterminate:
            return

        # Calculate percentage
        percentage = (self.progress / self.maximum) * 100

        # Update progress bar width
        try:
            parent_width = self.bg_bar.winfo_width()
            if parent_width > 0:
                progress_width = int((percentage / 100) * parent_width)
                self.progress_bar.configure(width=progress_width)
        except:
            pass

        # Update text
        if self.show_percentage:
            self.progress_text.configure(text=f"{percentage:.1f}%")

    def start_indeterminate_animation(self):
        """Start indeterminate animation."""
        self.indeterminate_thread = threading.Thread(target=self.animate_indeterminate, daemon=True)
        self.indeterminate_thread.start()

    def stop_indeterminate_animation(self):
        """Stop indeterminate animation."""
        # Thread will stop on its own when indeterminate is False

    def animate_indeterminate(self):
        """Animate indeterminate progress bar."""
        while self.indeterminate:
            # Simple sliding animation
            self.progress_bar.place(relx=-0.3, rely=0.5, anchor="center")
            time.sleep(0.8)
            self.progress_bar.place(relx=0.3, rely=0.5, anchor="center")
            time.sleep(0.8)

    def reset(self):
        """Reset progress to zero."""
        self.set_progress(0)


class CircularProgress(ctk.CTkFrame):
    """Circular progress indicator."""

    def __init__(self, parent, size=80, **kwargs):
        super().__init__(parent, **kwargs)

        self.theme_manager = get_theme_manager()

        # Size options
        self.sizes = {
            "small": 40,
            "medium": 80,
            "large": 120
        }

        self.size = self.sizes.get(size, 80)
        self.progress = 0.0
        self.maximum = 100.0
        self.show_percentage = True

        # Configure frame
        self.configure(width=self.size, height=self.size)
        self.grid_propagate(False)

        # Create canvas for circular progress
        self.canvas = ctk.CTkCanvas(
            self,
            width=self.size,
            height=self.size,
            highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)

        # Progress text
        self.progress_text = ctk.CTkLabel(
            self,
            text="0%",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.progress_text.place(relx=0.5, rely=0.5, anchor="center")

        # Initial draw
        self.update_display()

    def set_progress(self, value: float):
        """Set progress value (0-100)."""
        self.progress = max(0, min(100, value))
        self.update_display()

    def set_maximum(self, maximum: float):
        """Set maximum value."""
        self.maximum = max(1, maximum)
        self.update_display()

    def set_show_percentage(self, show: bool):
        """Show/hide percentage text."""
        self.show_percentage = show
        self.progress_text.configure(text=f"{self.progress / self.maximum * 100:.1f}%" if show else "")

    def update_display(self):
        """Update the circular progress display."""
        # Clear canvas
        self.canvas.delete("all")

        center = self.size // 2
        radius = (self.size // 2) - 10

        # Draw background circle
        self.canvas.create_oval(
            center - radius, center - radius,
            center + radius, center + radius,
            outline=self.theme_manager.get_color("border"),
            width=2,
            style="outline"
        )

        # Calculate progress angle
        percentage = (self.progress / self.maximum) if self.maximum > 0 else 0
        angle_extent = (percentage / 100) * 360

        # Draw progress arc
        if percentage > 0:
            self.canvas.create_arc(
                center - radius, center - radius,
                center + radius, center + radius,
                -90, -90 + angle_extent,
                outline=self.theme_manager.get_color("primary"),
                width=8,
                style="arc"
            )

        # Update text
        if self.show_percentage:
            self.progress_text.configure(text=f"{percentage:.1f}%")


class StatusIndicator(ctk.CTkFrame):
    """Status indicator with color-coded states."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        self.theme_manager = get_theme_manager()

        self.current_status = "info"  # success, warning, error, info

        # Configure
        self.grid_propagate(False)

        # Create indicator
        self.create_indicator()

    def create_indicator(self):
        """Create the status indicator."""
        # Indicator circle
        self.indicator = ctk.CTkLabel(
            self,
            text="●",
            font=ctk.CTkFont(size=16),
            text_color=self.get_status_color("info")
        )
        self.indicator.pack(padx=10, pady=5)

        # Status text
        self.status_text = ctk.CTkLabel(
            self,
            text="Ready",
            font=ctk.CTkFont(size=10),
            text_color=self.theme_manager.get_color("text_secondary")
        )
        self.status_text.pack(pady=(0, 5))

    def set_status(self, status: str, message: str = None):
        """Set status and update appearance."""
        self.current_status = status

        # Update indicator color
        self.indicator.configure(text_color=self.get_status_color(status))

        # Update text
        text = message or self.get_default_message(status)
        self.status_text.configure(text=text)

    def get_status_color(self, status: str) -> str:
        """Get color for status."""
        colors = {
            "success": self.theme_manager.get_color("priority_low"),
            "warning": self.theme_manager.get_color("priority_medium"),
            "error": self.theme_manager.get_color("priority_high"),
            "info": self.theme_manager.get_color("primary")
        }
        return colors.get(status, colors["info"])

    def get_default_message(self, status: str) -> str:
        """Get default message for status."""
        messages = {
            "success": "Success",
            "warning": "Warning",
            "error": "Error",
            "info": "Ready"
        }
        return messages.get(status, "Ready")


class ProgressModal(ctk.CTkToplevel):
    """Modal dialog with progress indication."""

    def __init__(self, parent, title: str, message: str = "",
                 show_progress: bool = True, on_cancel: Optional[Callable] = None):
        super().__init__(parent)

        self.title = title
        self.message = message
        self.show_progress = show_progress
        self.on_cancel = on_cancel
        self.is_cancelled = False

        # Configure window
        self.geometry("400x200")
        self.resizable(False)
        self.transient(parent)
        self.grab_set()

        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Apply theme
        theme_colors = self.get_theme_colors()
        self.configure(fg_color=theme_colors["background"])

        # Handle close
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # Create UI
        self.create_content()

    def get_theme_colors(self):
        """Get theme colors."""
        theme_manager = get_theme_manager()
        return theme_manager.get_theme_colors()

    def create_content(self):
        """Create modal content."""
        # Title
        title_label = ctk.CTkLabel(
            self,
            text=self.title,
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")

        # Message
        if self.message:
            message_label = ctk.CTkLabel(
                self,
                text=self.message,
                font=ctk.CtkFont(size=12),
                wraplength=350
            )
            message_label.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="ew")

        # Progress indicator
        if self.show_progress:
            self.progress_bar = ProgressBar(self, width=350)
            self.progress_bar.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="ew")

            # Set indeterminate by default for loading
            self.progress_bar.set_indeterminate(True)

        # Cancel button
        if self.on_cancel:
            cancel_btn = ctk.CTkButton(
                self,
                text="Cancel",
                command=self.on_cancel_clicked,
                width=100
            )
            cancel_btn.grid(row=3, column=0, padx=20, pady=(0, 20))

    def set_progress(self, value: float):
        """Set progress value."""
        if hasattr(self, 'progress_bar'):
            self.progress_bar.set_progress(value)

    def set_message(self, message: str):
        """Set message text."""
        # This would need to update the message label
        pass

    def on_close(self):
        """Handle window close."""
        if self.on_cancel:
            self.is_cancelled = True
        else:
            self.destroy()

    def on_cancel_clicked(self):
        """Handle cancel button click."""
        self.is_cancelled = True
        self.destroy()


class LoadingModal(ProgressModal):
    """Loading modal with indeterminate progress."""

    def __init__(self, parent, title: str = "Loading...", message: str = "",
                 on_cancel: Optional[Callable] = None):
        super().__init__(parent, title, message, True, on_cancel)


class StepProgress(ctk.CTkFrame):
    """Multi-step progress indicator."""

    def __init__(self, parent, steps: List[str], **kwargs):
        super().__init__(parent, **kwargs)

        self.theme_manager = get_theme_manager()

        self.steps = steps
        self.current_step = 0
       .step_states = ["pending"] * len(steps)

        # Configure frame
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Create step indicators
        self.create_step_indicators()

        # Step info
        self.create_step_info()

    def create_step_indicators(self):
        """Create step indicator circles."""
        self.step_frame = ctk.CTkFrame(self)
        self.step_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        self.step_frame.grid_columnconfigure(len(self.steps) - 1, weight=1)

        self.step_circles = []

        for i, step in enumerate(self.steps):
            circle_frame = ctk.CTkFrame(self.step_frame)
            circle_frame.grid(row=0, column=i, padx=5, pady=10, sticky="ew")

            # Circle indicator
            circle_label = ctk.CTkLabel(
                circle_frame,
                text="○",
                font=ctk.CTkFont(size=16),
                text_color=self.theme_manager.get_color("text_secondary")
            )
            circle_label.pack()

            # Step number
            number_label = ctk.CTkLabel(
                circle_frame,
                text=str(i + 1),
                font=ctk.CtkFont(size=10),
                text_color=self.theme_manager.get_color("text_secondary")
            )
            number_label.pack()

            # Store reference
            self.step_circles.append({
                "label": circle_label,
                "number": number_label,
                "frame": circle_frame,
                "step": i
            })

    def create_step_info(self):
        """Create step information display."""
        self.info_frame = ctk.CTkFrame(self)
        self.info_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 20))
        self.info_frame.grid_columnconfigure(0, weight=1)

        self.step_title = ctk.CTkLabel(
            self.info_frame,
            text="Step 1 of " + str(len(self.steps)),
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.step_title.pack(pady=10)

        self.step_description = ctk.CTkLabel(
            self.info_frame,
            text=self.steps[0] if self.steps else "Starting...",
            font=ctk.CTkFont(size=12),
            text_color=self.theme_manager.get_color("text_secondary"),
            wraplength=400
        )
        self.step_description.pack(pady=(0, 10))

    def set_current_step(self, step: int):
        """Set the current step (0-indexed)."""
        if 0 <= step < len(self.steps):
            self.current_step = step
            self.update_display()

    def mark_step_completed(self, step: int):
        """Mark a step as completed."""
        if 0 <= step < len(self.steps):
            self.step_states[step] = "completed"
            self.update_display()

    def mark_step_error(self, step: int):
        """Mark a step as error."""
        if 0 <= step < len(self.steps):
            self.step_states[step] = "error"
            self.update_display()

    def mark_step_pending(self, step: int):
        """Mark a step as pending."""
        if 0 <= step < len(self.steps):
            self.step_states[step] = "pending"
            self.update_display()

    def update_display(self):
        """Update the display to reflect current state."""
        # Update step circles
        for i, step_circle in enumerate(self.step_circles):
            state = self.step_states[i]
            step = step_circle["step"]

            # Update circle appearance
            if state == "completed":
                step_circle["label"].configure(text="●")
                step_circle["label"].configure(
                    text_color=self.theme_manager.get_color("priority_low")
                )
            elif state == "error":
                step_circle["label"].configure(text="●")
                step_circle["label"].configure(
                    text_color=self.theme_manager.get_color("priority_high")
                )
            elif state == "active" or (i == self.current_step and state == "pending"):
                step_circle["label"].configure(text="◐")
                step_circle["label"].configure(
                    text_color=self.theme_manager.get_color("primary")
                )
            else:  # pending
                step_circle["label"].configure(text="○")
                step_circle["label"].configure(
                    text_color=self.theme_manager.get_color("text_secondary")
                )

        # Update step info
        if self.current_step < len(self.steps):
            step_title = f"Step {self.current_step + 1} of {len(self.steps)}"
            step_description = self.steps[self.current_step]

            self.step_title.configure(text=step_title)
            self.step_description.configure(text=step_description)

    def get_progress_percentage(self) -> float:
        """Get overall progress percentage."""
        if not self.steps:
            return 0.0

        completed = sum(1 for state in self.step_states if state == "completed")
        return (completed / len(self.steps)) * 100


# Utility functions
def show_loading_modal(parent, title: str = "Loading...", message: str = "",
                       on_cancel: Optional[Callable] = None) -> LoadingModal:
    """Show a loading modal and return the modal instance."""
    return LoadingModal(parent, title, message, on_cancel)


def show_progress_modal(parent, title: str, message: str = "",
                          on_cancel: Optional[Callable] = None) -> ProgressModal:
    """Show a progress modal and return the modal instance."""
    return ProgressModal(parent, title, message, on_cancel=on_cancel)


# Example usage functions
def create_loading_indicator(parent, size="medium") -> LoadingSpinner:
    """Create a loading spinner."""
    return LoadingSpinner(parent, size)


def create_progress_bar(parent, width=300, height=20) -> ProgressBar:
    """Create a progress bar."""
    return ProgressBar(parent, width, height)


def create_circular_progress(parent, size=80) -> CircularProgress:
    """Create a circular progress indicator."""
    return CircularProgress(parent, size)


def create_status_indicator(parent) -> StatusIndicator:
    """Create a status indicator."""
    return StatusIndicator(parent)