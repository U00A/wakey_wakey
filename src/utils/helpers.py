"""
Helper utilities for the task scheduler application.
Provides general utility functions and formatting helpers.
"""

import os
import csv
import json
from datetime import datetime, date, time, timedelta
from typing import List, Dict, Any, Optional, Union
from pathlib import Path


def format_datetime(dt: Union[str, datetime], format_type: str = "display") -> str:
    """
    Format datetime for display or storage.

    Args:
        dt: Datetime object or ISO string
        format_type: Type of formatting ('display', 'time', 'date', 'short', 'iso')

    Returns:
        Formatted datetime string
    """
    if not dt:
        return ""

    # Convert string to datetime if needed
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
        except ValueError:
            return dt  # Return original string if parsing fails

    # Format based on type
    if format_type == "display":
        return dt.strftime("%B %d, %Y at %I:%M %p")
    elif format_type == "time":
        return dt.strftime("%I:%M %p")
    elif format_type == "date":
        return dt.strftime("%B %d, %Y")
    elif format_type == "short":
        return dt.strftime("%m/%d/%Y %I:%M %p")
    elif format_type == "iso":
        return dt.isoformat()
    elif format_type == "relative":
        return format_relative_time(dt)
    else:
        return str(dt)


def format_relative_time(dt: Union[str, datetime]) -> str:
    """
    Format datetime as relative time (e.g., "2 hours ago", "in 3 days").

    Args:
        dt: Datetime object or ISO string

    Returns:
        Relative time string
    """
    if not dt:
        return ""

    # Convert string to datetime if needed
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
        except ValueError:
            return dt

    now = datetime.now()
    diff = dt - now

    if diff.days == 0:
        hours = diff.seconds // 3600
        if hours == 0:
            minutes = diff.seconds // 60
            if minutes == 0:
                return "Just now"
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago" if diff.total_seconds() < 0 else f"in {minutes} minute{'s' if minutes != 1 else ''}"
        return f"{hours} hour{'s' if hours != 1 else ''} ago" if diff.total_seconds() < 0 else f"in {hours} hour{'s' if hours != 1 else ''}"
    elif diff.days > 0:
        return f"in {diff.days} day{'s' if diff.days != 1 else ''}"
    else:
        return f"{abs(diff.days)} day{'s' if diff.days != -1 else ''} ago"


def format_duration(minutes: int) -> str:
    """
    Format duration in minutes to human readable format.

    Args:
        minutes: Duration in minutes

    Returns:
        Formatted duration string
    """
    if minutes < 60:
        return f"{minutes} minute{'s' if minutes != 1 else ''}"
    elif minutes < 1440:  # Less than 24 hours
        hours = minutes // 60
        remaining_minutes = minutes % 60
        if remaining_minutes == 0:
            return f"{hours} hour{'s' if hours != 1 else ''}"
        return f"{hours}h {remaining_minutes}m"
    else:  # Days
        days = minutes // 1440
        remaining_hours = (minutes % 1440) // 60
        if remaining_hours == 0:
            return f"{days} day{'s' if days != 1 else ''}"
        return f"{days}d {remaining_hours}h"


def truncate_text(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """
    Truncate text to specified length.

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated

    Returns:
        Truncated text
    """
    if not text or len(text) <= max_length:
        return text

    return text[:max_length - len(suffix)] + suffix


def calculate_completion_percentage(tasks: List[Dict[str, Any]]) -> float:
    """
    Calculate completion percentage for a list of tasks.

    Args:
        tasks: List of task dictionaries

    Returns:
        Completion percentage (0-100)
    """
    if not tasks:
        return 0.0

    completed_tasks = sum(1 for task in tasks if task.get('status') == 'Completed')
    return round((completed_tasks / len(tasks)) * 100, 1)


def generate_task_id() -> str:
    """
    Generate a unique task ID (for temporary use before database save).

    Returns:
        Unique task ID
    """
    import uuid
    return str(uuid.uuid4())


def safe_filename(filename: str) -> str:
    """
    Create a safe filename by removing invalid characters.

    Args:
        filename: Original filename

    Returns:
        Safe filename
    """
    # Remove invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')

    # Remove control characters
    filename = ''.join(char for char in filename if ord(char) >= 32)

    # Limit length
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:255 - len(ext)] + ext

    # Remove leading/trailing spaces and dots
    filename = filename.strip(' .')

    # Ensure it's not empty
    if not filename:
        filename = "unnamed"

    return filename


def export_tasks_to_csv(tasks: List[Dict[str, Any]], file_path: str) -> bool:
    """
    Export tasks to CSV file.

    Args:
        tasks: List of task dictionaries
        file_path: Output file path

    Returns:
        True if successful, False otherwise
    """
    try:
        fieldnames = [
            'id', 'title', 'description', 'priority', 'category', 'status',
            'due_date', 'reminder_time', 'recurring_type', 'recurring_interval',
            'created_at', 'updated_at', 'completed_at'
        ]

        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for task in tasks:
                # Ensure all fields are present
                row = {field: task.get(field, '') for field in fieldnames}
                writer.writerow(row)

        return True
    except (IOError, csv.Error):
        return False


def export_tasks_to_json(tasks: List[Dict[str, Any]], file_path: str) -> bool:
    """
    Export tasks to JSON file.

    Args:
        tasks: List of task dictionaries
        file_path: Output file path

    Returns:
        True if successful, False otherwise
    """
    try:
        export_data = {
            "tasks": tasks,
            "exported_at": datetime.now().isoformat(),
            "version": "1.0",
            "total_tasks": len(tasks)
        }

        with open(file_path, 'w', encoding='utf-8') as jsonfile:
            json.dump(export_data, jsonfile, indent=2, ensure_ascii=False)

        return True
    except (IOError, TypeError):
        return False


def import_tasks_from_csv(file_path: str) -> List[Dict[str, Any]]:
    """
    Import tasks from CSV file.

    Args:
        file_path: Input file path

    Returns:
        List of task dictionaries
    """
    try:
        tasks = []

        with open(file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                # Clean up empty values
                task = {k: v.strip() if v and v.strip() else None for k, v in row.items()}
                tasks.append(task)

        return tasks
    except (IOError, csv.Error):
        return []


def import_tasks_from_json(file_path: str) -> List[Dict[str, Any]]:
    """
    Import tasks from JSON file.

    Args:
        file_path: Input file path

    Returns:
        List of task dictionaries
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as jsonfile:
            data = json.load(jsonfile)

        if isinstance(data, dict) and 'tasks' in data:
            return data['tasks']
        elif isinstance(data, list):
            return data
        else:
            return []
    except (IOError, json.JSONDecodeError, KeyError):
        return []


def validate_file_path(file_path: str, extensions: List[str] = None) -> bool:
    """
    Validate file path and optional file extensions.

    Args:
        file_path: File path to validate
        extensions: List of allowed extensions (e.g., ['.csv', '.json'])

    Returns:
        True if valid, False otherwise
    """
    if not file_path or not os.path.exists(file_path):
        return False

    if extensions:
        file_ext = Path(file_path).suffix.lower()
        return file_ext in [ext.lower() for ext in extensions]

    return True


def get_file_extension(file_path: str) -> str:
    """
    Get file extension from file path.

    Args:
        file_path: File path

    Returns:
        File extension (including dot)
    """
    return Path(file_path).suffix.lower()


def calculate_task_statistics(tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate various statistics for a list of tasks.

    Args:
        tasks: List of task dictionaries

    Returns:
        Dictionary containing statistics
    """
    if not tasks:
        return {
            'total': 0,
            'completed': 0,
            'pending': 0,
            'cancelled': 0,
            'completion_rate': 0,
            'by_priority': {},
            'by_category': {},
            'overdue': 0
        }

    total = len(tasks)
    completed = sum(1 for task in tasks if task.get('status') == 'Completed')
    pending = sum(1 for task in tasks if task.get('status') == 'Pending')
    cancelled = sum(1 for task in tasks if task.get('status') == 'Cancelled')

    # Calculate overdue tasks
    now = datetime.now()
    overdue = 0
    for task in tasks:
        if task.get('status') == 'Pending' and task.get('due_date'):
            try:
                due_date = datetime.fromisoformat(task['due_date'].replace('Z', '+00:00'))
                if due_date < now:
                    overdue += 1
            except ValueError:
                continue

    # Tasks by priority
    by_priority = {}
    for task in tasks:
        priority = task.get('priority', 'Unknown')
        by_priority[priority] = by_priority.get(priority, 0) + 1

    # Tasks by category
    by_category = {}
    for task in tasks:
        category = task.get('category', 'Unknown')
        by_category[category] = by_category.get(category, 0) + 1

    return {
        'total': total,
        'completed': completed,
        'pending': pending,
        'cancelled': cancelled,
        'completion_rate': round((completed / total) * 100, 1) if total > 0 else 0,
        'by_priority': by_priority,
        'by_category': by_category,
        'overdue': overdue
    }


def create_date_range(start_date: date, end_date: date) -> List[date]:
    """
    Create a list of dates from start_date to end_date inclusive.

    Args:
        start_date: Start date
        end_date: End date

    Returns:
        List of dates
    """
    if start_date > end_date:
        return []

    dates = []
    current_date = start_date
    while current_date <= end_date:
        dates.append(current_date)
        current_date += timedelta(days=1)

    return dates


def get_week_dates(target_date: date = None) -> List[date]:
    """
    Get all dates in the week containing the target date.

    Args:
        target_date: Target date (defaults to today)

    Returns:
        List of dates for the week (Monday to Sunday)
    """
    if target_date is None:
        target_date = date.today()

    # Find Monday of the week
    monday = target_date - timedelta(days=target_date.weekday())

    # Generate week dates
    week_dates = []
    for i in range(7):
        week_dates.append(monday + timedelta(days=i))

    return week_dates


def get_month_dates(target_date: date = None) -> List[List[date]]:
    """
    Get calendar month layout as weeks.

    Args:
        target_date: Target date (defaults to today)

    Returns:
        List of weeks, each week is a list of dates
    """
    if target_date is None:
        target_date = date.today()

    # Get first day of month
    first_day = target_date.replace(day=1)

    # Find first Monday of the calendar view
    days_from_monday = first_day.weekday()
    calendar_start = first_day - timedelta(days=days_from_monday)

    # Get last day of month
    next_month = first_day.replace(month=first_day.month % 12 + 1, year=first_day.year + (first_day.month // 12))
    last_day = next_month - timedelta(days=1)

    # Find last Sunday of the calendar view
    days_to_sunday = 6 - last_day.weekday()
    calendar_end = last_day + timedelta(days=days_to_sunday)

    # Generate calendar weeks
    weeks = []
    current_date = calendar_start
    current_week = []

    while current_date <= calendar_end:
        current_week.append(current_date)

        if len(current_week) == 7:
            weeks.append(current_week)
            current_week = []

        current_date += timedelta(days=1)

    # Add the last week if it has dates
    if current_week:
        weeks.append(current_week)

    return weeks


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in bytes to human readable format.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted size string
    """
    if size_bytes == 0:
        return "0 B"

    units = ['B', 'KB', 'MB', 'GB', 'TB']
    unit_index = 0

    while size_bytes >= 1024 and unit_index < len(units) - 1:
        size_bytes /= 1024
        unit_index += 1

    return f"{size_bytes:.1f} {units[unit_index]}"


def ensure_directory_exists(directory: str) -> bool:
    """
    Ensure a directory exists, create it if necessary.

    Args:
        directory: Directory path

    Returns:
        True if directory exists or was created successfully
    """
    try:
        Path(directory).mkdir(parents=True, exist_ok=True)
        return True
    except OSError:
        return False


def get_system_info() -> Dict[str, Any]:
    """
    Get basic system information for debugging.

    Returns:
        Dictionary with system information
    """
    import platform
    import sys

    return {
        "platform": platform.system(),
        "platform_release": platform.release(),
        "platform_version": platform.version(),
        "architecture": platform.machine(),
        "processor": platform.processor(),
        "python_version": sys.version,
        "python_executable": sys.executable,
        "current_directory": os.getcwd(),
        "user_directory": os.path.expanduser("~")
    }