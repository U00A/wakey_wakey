#!/usr/bin/env python3
"""
Task Scheduler Pro - Main Entry Point

A modern, feature-rich task scheduler desktop application built with Python and CustomTkinter.
Features include task management, scheduling, alarms, notifications, calendar views, and more.

Author: Task Scheduler Pro Team
Version: 1.0.0
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Import application
try:
    from app import main as app_main
except ImportError as e:
    print(f"Error importing application: {e}")
    print("Please ensure all dependencies are installed:")
    print("pip install -r requirements.txt")
    sys.exit(1)


def check_dependencies():
    """Check if required dependencies are available."""
    required_modules = [
        'customtkinter',
        'sqlite3',  # Built-in
        'playsound',
        'plyer',
        'schedule',
        'PIL'  # Pillow
    ]

    missing_modules = []

    for module in required_modules:
        try:
            if module == 'sqlite3':
                import sqlite3
            elif module == 'PIL':
                import PIL
            else:
                __import__(module)
        except ImportError:
            missing_modules.append(module)

    if missing_modules:
        print("Missing required dependencies:")
        for module in missing_modules:
            print(f"  - {module}")
        print("\nInstall them with:")
        print("pip install -r requirements.txt")
        return False

    return True


def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print(f"Error: Python 3.8 or higher is required. You are using Python {sys.version}.")
        return False
    return True


def setup_environment():
    """Set up the application environment."""
    # Ensure data directory exists
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)

    # Ensure assets directories exist
    assets_dirs = ["assets/icons", "assets/sounds"]
    for dir_path in assets_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)

    # Set working directory to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)


def main():
    """Main entry point for the application."""
    print("=" * 50)
    print("Task Scheduler Pro v1.0.0")
    print("=" * 50)

    # Check Python version
    if not check_python_version():
        sys.exit(1)

    # Check dependencies
    print("Checking dependencies...")
    if not check_dependencies():
        sys.exit(1)
    print("✓ All dependencies found")

    # Setup environment
    print("Setting up environment...")
    setup_environment()
    print("✓ Environment ready")

    # Start the application
    print("Starting Task Scheduler Pro...")
    print("-" * 50)

    try:
        app_main()
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
    except Exception as e:
        print(f"\nFatal error: {e}")
        print("Please check the error above and try again.")
        sys.exit(1)
    finally:
        print("Application closed")


if __name__ == "__main__":
    main()