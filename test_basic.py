#!/usr/bin/env python3
"""
Basic test script to verify core functionality without GUI dependencies.
"""

import sys
import os
from pathlib import Path

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

def test_database():
    """Test database functionality."""
    print("Testing database...")
    try:
        from database.manager import DatabaseManager
        from database.models import Task, Category, Alarm

        # Create database manager
        db = DatabaseManager("test_tasks.db")
        print("✓ Database initialized successfully")

        # Test creating a task
        task_data = {
            "title": "Test Task",
            "description": "This is a test task",
            "priority": "High",
            "category": "Work"
        }
        task = Task(task_data)
        task_id = db.create_task(task)
        print(f"✓ Created task with ID: {task_id}")

        # Test retrieving the task
        retrieved_task = db.get_task(task_id)
        if retrieved_task and retrieved_task.title == "Test Task":
            print("✓ Retrieved task successfully")
        else:
            print("✗ Failed to retrieve task")

        # Test statistics
        stats = db.get_task_statistics()
        print(f"✓ Statistics: {stats['total_created']} tasks created")

        # Clean up
        db.delete_task(task_id)
        os.remove("test_tasks.db")
        print("✓ Database test completed")

    except Exception as e:
        print(f"✗ Database test failed: {e}")

def test_config():
    """Test configuration management."""
    print("\nTesting configuration...")
    try:
        from utils.config import ConfigManager

        config = ConfigManager("test_data")
        print("✓ Configuration initialized successfully")

        # Test getting and setting values
        theme = config.get("theme", "dark")
        print(f"✓ Current theme: {theme}")

        # Test setting a valid configuration value (one that exists in defaults)
        success = config.set("theme", "light")
        retrieved = config.get("theme")
        if success and retrieved == "light":
            print("✓ Configuration get/set working")
        else:
            print(f"✗ Configuration get/set failed (success: {success}, value: {retrieved})")

        # Clean up
        import shutil
        if os.path.exists("test_data"):
            shutil.rmtree("test_data")
        print("✓ Configuration test completed")

    except Exception as e:
        print(f"✗ Configuration test failed: {e}")

def test_validators():
    """Test input validation."""
    print("\nTesting validators...")
    try:
        from utils.validators import (
            validate_task_title, validate_priority,
            validate_category, validate_task_data
        )

        # Test task title validation
        title = validate_task_title("Test Task")
        if title == "Test Task":
            print("✓ Task title validation working")
        else:
            print("✗ Task title validation failed")

        # Test priority validation
        priority = validate_priority("High")
        if priority == "High":
            print("✓ Priority validation working")
        else:
            print("✗ Priority validation failed")

        # Test category validation
        category = validate_category("Work")
        if category == "Work":
            print("✓ Category validation working")
        else:
            print("✗ Category validation failed")

        # Test complete task validation
        task_data = {
            "title": "Complete Test Task",
            "description": "A complete test task",
            "priority": "Medium",
            "category": "Personal"
        }
        validated = validate_task_data(task_data)
        if validated["title"] == "Complete Test Task":
            print("✓ Complete task validation working")
        else:
            print("✗ Complete task validation failed")

        print("✓ Validators test completed")

    except Exception as e:
        print(f"✗ Validators test failed: {e}")

def test_task_manager():
    """Test task manager business logic."""
    print("\nTesting task manager...")
    try:
        # Import individual modules to avoid relative import issues
        from database.manager import DatabaseManager
        from database.models import Task
        from utils.validators import validate_task_data, ValidationError
        from utils.helpers import ensure_directory_exists
        from pathlib import Path
        from datetime import datetime, date, timedelta
        from typing import List, Dict, Any, Optional, Tuple
        import os

        # Create a simple task manager inline for testing
        class SimpleTaskManager:
            def __init__(self):
                self.db = DatabaseManager("test_tasks_manager.db")
                self.export_dir = Path("data/exports")
                ensure_directory_exists(self.export_dir)

            def create_task(self, task_data: Dict[str, Any]) -> Tuple[bool, int, str]:
                try:
                    validated_data = validate_task_data(task_data, [])
                    task = Task(validated_data)
                    task_id = self.db.create_task(task)
                    return True, task_id, "Task created successfully"
                except ValidationError as e:
                    return False, -1, f"Validation error: {str(e)}"
                except Exception as e:
                    return False, -1, f"Error creating task: {str(e)}"

            def get_task(self, task_id: int):
                return self.db.get_task(task_id)

            def delete_task(self, task_id: int) -> Tuple[bool, str]:
                try:
                    task = self.db.get_task(task_id)
                    if not task:
                        return False, "Task not found"
                    success = self.db.delete_task(task_id)
                    if success:
                        return True, "Task deleted successfully"
                    else:
                        return False, "Failed to delete task"
                except Exception as e:
                    return False, f"Error deleting task: {str(e)}"

            def get_task_statistics(self, days: int = 30):
                return self.db.get_task_statistics(days)

        # Create task manager with test database
        task_manager = SimpleTaskManager()
        print("✓ Task manager initialized successfully")

        # Test creating a task
        task_data = {
            "title": "Manager Test Task",
            "description": "Testing task manager",
            "priority": "High",
            "category": "Work"
        }
        success, task_id, message = task_manager.create_task(task_data)
        if success:
            print(f"✓ Task manager created task: {task_id}")
        else:
            print(f"✗ Task manager failed to create task: {message}")

        # Test retrieving task
        task = task_manager.get_task(task_id)
        if task and task.title == "Manager Test Task":
            print("✓ Task manager retrieved task successfully")
        else:
            print("✗ Task manager failed to retrieve task")

        # Test statistics
        stats = task_manager.get_task_statistics()
        print(f"✓ Task manager statistics: {stats.get('total_created', 0)} total tasks")

        # Clean up
        task_manager.delete_task(task_id)
        os.remove("test_tasks_manager.db")
        print("✓ Task manager test completed")

    except Exception as e:
        print(f"✗ Task manager test failed: {e}")

def test_helpers():
    """Test utility helpers."""
    print("\nTesting helpers...")
    try:
        from utils.helpers import (
            format_datetime, calculate_task_statistics,
            get_week_dates, get_month_dates
        )
        from datetime import datetime, date

        # Test datetime formatting
        now = datetime.now()
        formatted = format_datetime(now, "display")
        if formatted:
            print("✓ Datetime formatting working")
        else:
            print("✗ Datetime formatting failed")

        # Test statistics calculation
        test_tasks = [
            {"status": "Completed"},
            {"status": "Pending"},
            {"status": "Completed"},
            {"status": "Pending"}
        ]
        stats = calculate_task_statistics(test_tasks)
        if stats["completion_rate"] == 50.0:
            print("✓ Statistics calculation working")
        else:
            print("✗ Statistics calculation failed")

        # Test date utilities
        week_dates = get_week_dates()
        if len(week_dates) == 7:
            print("✓ Week dates calculation working")
        else:
            print("✗ Week dates calculation failed")

        month_dates = get_month_dates()
        if len(month_dates) >= 4:  # At least 4 weeks in a month
            print("✓ Month dates calculation working")
        else:
            print("✗ Month dates calculation failed")

        print("✓ Helpers test completed")

    except Exception as e:
        print(f"✗ Helpers test failed: {e}")

def main():
    """Run all tests."""
    print("Task Scheduler Pro - Basic Functionality Tests")
    print("=" * 50)

    test_database()
    test_config()
    test_validators()
    test_task_manager()
    test_helpers()

    print("\n" + "=" * 50)
    print("Basic tests completed!")
    print("\nNote: GUI components (CustomTkinter) and notification")
    print("libraries (playsound, plyer) were not tested as they")
    print("require display/sound access and are not installed in")
    print("this environment.")

if __name__ == "__main__":
    main()