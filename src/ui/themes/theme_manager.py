"""
Theme manager for the task scheduler application.
Handles dark/light mode theming with CustomTkinter.
"""

import os
import json
from typing import Dict, Any
import customtkinter as ctk


class ThemeManager:
    """Manages application themes and color schemes."""

    def __init__(self, config_path: str = "data/theme_config.json"):
        self.config_path = config_path
        self.current_theme = "dark"
        self.themes = self._define_themes()
        self._ensure_config_directory()
        self._load_theme_config()

    def _ensure_config_directory(self):
        """Ensure the config directory exists."""
        config_dir = os.path.dirname(self.config_path)
        if config_dir and not os.path.exists(config_dir):
            os.makedirs(config_dir)

    def _define_themes(self) -> Dict[str, Dict[str, str]]:
        """Define available color themes."""
        return {
            "dark": {
                # Background colors
                "background": "#1a1a1a",
                "surface": "#2d2d2d",
                "surface_variant": "#3a3a3a",
                "card": "#404040",

                # Primary colors
                "primary": "#0078d4",
                "primary_variant": "#106ebe",
                "on_primary": "#ffffff",

                # Text colors
                "text_primary": "#ffffff",
                "text_secondary": "#b3b3b3",
                "text_disabled": "#666666",

                # Priority colors
                "priority_high": "#ff4444",
                "priority_medium": "#ffaa00",
                "priority_low": "#44ff44",

                # Status colors
                "status_pending": "#ffaa00",
                "status_completed": "#44ff44",
                "status_cancelled": "#ff4444",

                # Border and outline
                "border": "#555555",
                "outline": "#666666",

                # Accent colors
                "accent": "#0078d4",
                "accent_variant": "#106ebe",

                # UI elements
                "button": "#404040",
                "button_hover": "#4a4a4a",
                "input": "#333333",
                "input_border": "#555555",

                # Calendar specific
                "calendar_today": "#0078d4",
                "calendar_weekend": "#ff4444",
                "calendar_other_month": "#666666"
            },
            "light": {
                # Background colors
                "background": "#ffffff",
                "surface": "#f5f5f5",
                "surface_variant": "#eeeeee",
                "card": "#fafafa",

                # Primary colors
                "primary": "#0078d4",
                "primary_variant": "#106ebe",
                "on_primary": "#ffffff",

                # Text colors
                "text_primary": "#000000",
                "text_secondary": "#666666",
                "text_disabled": "#999999",

                # Priority colors
                "priority_high": "#d32f2f",
                "priority_medium": "#f57c00",
                "priority_low": "#388e3c",

                # Status colors
                "status_pending": "#f57c00",
                "status_completed": "#388e3c",
                "status_cancelled": "#d32f2f",

                # Border and outline
                "border": "#dddddd",
                "outline": "#cccccc",

                # Accent colors
                "accent": "#0078d4",
                "accent_variant": "#106ebe",

                # UI elements
                "button": "#f0f0f0",
                "button_hover": "#e0e0e0",
                "input": "#ffffff",
                "input_border": "#dddddd",

                # Calendar specific
                "calendar_today": "#0078d4",
                "calendar_weekend": "#d32f2f",
                "calendar_other_month": "#999999"
            }
        }

    def _load_theme_config(self):
        """Load theme configuration from file."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    self.current_theme = config.get('theme', 'dark')
            except (json.JSONDecodeError, IOError):
                # Use default theme if config is corrupted
                self.current_theme = "dark"

    def _save_theme_config(self):
        """Save theme configuration to file."""
        config = {
            'theme': self.current_theme
        }
        try:
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
        except IOError:
            pass  # Silently fail if we can't save config

    def get_current_theme(self) -> str:
        """Get the current theme name."""
        return self.current_theme

    def set_theme(self, theme_name: str) -> bool:
        """Set the current theme."""
        if theme_name in self.themes:
            self.current_theme = theme_name
            self._save_theme_config()
            self._apply_theme_to_ctk()
            return True
        return False

    def toggle_theme(self) -> str:
        """Toggle between dark and light themes."""
        new_theme = "light" if self.current_theme == "dark" else "dark"
        self.set_theme(new_theme)
        return new_theme

    def get_color(self, color_name: str) -> str:
        """Get a color from the current theme."""
        return self.themes[self.current_theme].get(color_name, "#000000")

    def get_priority_color(self, priority: str) -> str:
        """Get color for task priority."""
        priority_map = {
            "High": "priority_high",
            "Medium": "priority_medium",
            "Low": "priority_low"
        }
        color_key = priority_map.get(priority, "priority_medium")
        return self.get_color(color_key)

    def get_status_color(self, status: str) -> str:
        """Get color for task status."""
        status_map = {
            "Pending": "status_pending",
            "Completed": "status_completed",
            "Cancelled": "status_cancelled"
        }
        color_key = status_map.get(status, "status_pending")
        return self.get_color(color_key)

    def _apply_theme_to_ctk(self):
        """Apply theme to CustomTkinter."""
        if self.current_theme == "dark":
            ctk.set_appearance_mode("dark")
        else:
            ctk.set_appearance_mode("light")

    def get_ctk_color_map(self) -> Dict[str, str]:
        """Get CustomTkinter compatible color map."""
        theme = self.themes[self.current_theme]
        return {
            "fg-color": theme["background"],
            "top_fg-color": theme["surface"],
            "border_color": theme["border"],
            "text_color": theme["text_primary"],
            "button_color": theme["button"],
            "button_hover_color": theme["button_hover"],
            "frame_color": theme["surface"],
            "frame_border": theme["border"],
            "scrollbar_button_color": theme["surface_variant"],
            "scrollbar_button_hover_color": theme["card"],
            "entry_color": theme["input"],
            "entry_border_color": theme["input_border"],
            "entry_fg_color": theme["text_primary"],
            "progress_bar_color": theme["primary"],
            "switch_fg_color": theme["primary"],
            "switch_border_color": theme["border"],
            "switch_button_color": theme["card"],
            "switch_button_hover_color": theme["button_hover"],
            "checkmark_color": theme["primary"],
            "radiobutton_fg_color": theme["button"],
            "radiobutton_hover_color": theme["button_hover"],
            "dropdown_color": theme["surface"],
            "dropdown_hover_color": theme["card"],
            "dropdown_text_color": theme["text_primary"],
            "font_color": theme["text_primary"],
            "segmented_button_fg_color": theme["button"],
            "segmented_button_selected_color": theme["primary"],
            "segmented_button_unselected_color": theme["surface_variant"],
            "segmented_button_selected_hover_color": theme["primary_variant"],
            "segmented_button_unselected_hover_color": theme["button_hover"],
            "tab_fg_color": theme["surface"],
            "tab_bg_color": theme["background"],
            "tab_selected_color": theme["primary"],
            "tab_unselected_color": theme["surface_variant"],
            "tab_text_color": theme["text_primary"],
            "tab_selected_text_color": theme["on_primary"],
            "title_text_color": theme["text_primary"],
            "text_color_disabled": theme["text_disabled"],
        }

    def apply_theme_to_widget(self, widget, widget_type: str = "default"):
        """Apply theme colors to a CustomTkinter widget."""
        color_map = self.get_ctk_color_map()

        # Apply common colors
        if hasattr(widget, 'configure'):
            try:
                widget.configure(fg_color=color_map.get("fg-color"))
            except:
                pass  # Ignore if widget doesn't support this property

    def get_available_themes(self) -> list:
        """Get list of available theme names."""
        return list(self.themes.keys())

    def add_custom_theme(self, name: str, colors: Dict[str, str]) -> bool:
        """Add a custom theme."""
        # Validate that all required color keys are present
        required_keys = set(self.themes["dark"].keys())
        provided_keys = set(colors.keys())

        if not required_keys.issubset(provided_keys):
            return False

        self.themes[name] = colors
        return True

    def get_theme_colors(self, theme_name: str = None) -> Dict[str, str]:
        """Get all colors for a theme."""
        if theme_name is None:
            theme_name = self.current_theme
        return self.themes.get(theme_name, {})

    def is_dark_theme(self) -> bool:
        """Check if current theme is dark."""
        return self.current_theme == "dark"

    def get_contrast_color(self, background_color: str) -> str:
        """Get appropriate text color for background (for custom components)."""
        # Simple luminance calculation
        color = background_color.lstrip('#')
        r, g, b = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255

        return "#000000" if luminance > 0.5 else "#ffffff"


# Global theme manager instance
theme_manager = ThemeManager()


def get_theme_manager() -> ThemeManager:
    """Get the global theme manager instance."""
    return theme_manager


def apply_theme(app, root_window=None):
    """Apply current theme to the entire application."""
    theme_manager._apply_theme_to_ctk()

    if root_window:
        # Apply theme to root window if provided
        theme_colors = theme_manager.get_theme_colors()
        root_window.configure(bg=theme_colors["background"])


def get_color(color_name: str) -> str:
    """Get a color from the current theme."""
    return theme_manager.get_color(color_name)


def toggle_theme() -> str:
    """Toggle between themes and return new theme name."""
    return theme_manager.toggle_theme()


def set_theme(theme_name: str) -> bool:
    """Set a specific theme."""
    return theme_manager.set_theme(theme_name)