"""
Input validation utilities for the task scheduler application.
Provides validation functions for various user inputs.
"""

import re
from datetime import datetime, date, time
from typing import Optional, List, Dict, Any


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


def validate_task_title(title: str) -> str:
    """
    Validate task title.

    Args:
        title: The task title to validate

    Returns:
        Cleaned title

    Raises:
        ValidationError: If title is invalid
    """
    if not title or not title.strip():
        raise ValidationError("Task title is required")

    title = title.strip()

    if len(title) < 1:
        raise ValidationError("Task title must be at least 1 character long")

    if len(title) > 200:
        raise ValidationError("Task title must be 200 characters or less")

    # Check for invalid characters (allow letters, numbers, spaces, and basic punctuation)
    if not re.match(r'^[a-zA-Z0-9\s\.,!?;:\-\'"()]+$', title):
        raise ValidationError("Task title contains invalid characters")

    return title


def validate_task_description(description: Optional[str]) -> Optional[str]:
    """
    Validate task description.

    Args:
        description: The task description to validate

    Returns:
        Cleaned description or None

    Raises:
        ValidationError: If description is invalid
    """
    if description is None:
        return None

    description = description.strip()

    if len(description) > 2000:
        raise ValidationError("Task description must be 2000 characters or less")

    return description if description else None


def validate_priority(priority: str) -> str:
    """
    Validate task priority.

    Args:
        priority: The priority to validate

    Returns:
        Validated priority

    Raises:
        ValidationError: If priority is invalid
    """
    valid_priorities = ['High', 'Medium', 'Low']

    if not priority:
        return 'Medium'  # Default priority

    priority = priority.strip().title()

    if priority not in valid_priorities:
        raise ValidationError(f"Priority must be one of: {', '.join(valid_priorities)}")

    return priority


def validate_status(status: str) -> str:
    """
    Validate task status.

    Args:
        status: The status to validate

    Returns:
        Validated status

    Raises:
        ValidationError: If status is invalid
    """
    valid_statuses = ['Pending', 'Completed', 'Cancelled']

    if not status:
        return 'Pending'

    status = str(status).strip().title()

    if status not in valid_statuses:
        raise ValidationError(f"Status must be one of: {', '.join(valid_statuses)}")

    return status

def validate_category(category: str, existing_categories: List[str] = None) -> str:
    """
    Validate task category.

    Args:
        category: The category to validate
        existing_categories: List of existing categories (optional)

    Returns:
        Validated category

    Raises:
        ValidationError: If category is invalid
    """
    if not category:
        return 'Personal'  # Default category

    category = category.strip()

    if len(category) < 1:
        raise ValidationError("Category name must be at least 1 character long")

    if len(category) > 50:
        raise ValidationError("Category name must be 50 characters or less")

    # Check for invalid characters
    if not re.match(r'^[a-zA-Z0-9\s\-]+$', category):
        raise ValidationError("Category name contains invalid characters")

    return category.title()


def validate_due_date(due_date_str: Optional[str]) -> Optional[str]:
    """
    Validate due date string and convert to ISO format.

    Args:
        due_date_str: The due date string to validate

    Returns:
        ISO formatted datetime string or None

    Raises:
        ValidationError: If due date is invalid
    """
    if not due_date_str or not due_date_str.strip():
        return None

    try:
        # Try to parse various date formats
        due_date_str = due_date_str.strip()

        # ISO format
        if re.match(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}', due_date_str):
            dt = datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
        # Date only format
        elif re.match(r'^\d{4}-\d{2}-\d{2}$', due_date_str):
            dt = datetime.strptime(due_date_str, '%Y-%m-%d')
        # Datetime with AM/PM
        elif re.match(r'^\d{1,2}/\d{1,2}/\d{4}\s+\d{1,2}:\d{2}\s*(AM|PM)$', due_date_str):
            dt = datetime.strptime(due_date_str, '%m/%d/%Y %I:%M %p')
        else:
            raise ValidationError("Invalid date format")

        # Check if date is in the future
        if dt <= datetime.now():
            raise ValidationError("Due date must be in the future")

        return dt.isoformat()

    except ValueError as e:
        raise ValidationError(f"Invalid date format: {str(e)}")


def validate_reminder_time(reminder_str: Optional[str], due_date_str: Optional[str] = None) -> Optional[str]:
    """
    Validate reminder time.

    Args:
        reminder_str: The reminder time string to validate
        due_date_str: The due date string for comparison

    Returns:
        ISO formatted datetime string or None

    Raises:
        ValidationError: If reminder time is invalid
    """
    if not reminder_str or not reminder_str.strip():
        return None

    try:
        reminder_str = reminder_str.strip()

        # ISO format
        if re.match(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}', reminder_str):
            reminder_dt = datetime.fromisoformat(reminder_str.replace('Z', '+00:00'))
        # Date only format
        elif re.match(r'^\d{4}-\d{2}-\d{2}$', reminder_str):
            reminder_dt = datetime.strptime(reminder_str, '%Y-%m-%d')
        # Datetime with AM/PM
        elif re.match(r'^\d{1,2}/\d{1,2}/\d{4}\s+\d{1,2}:\d{2}\s*(AM|PM)$', reminder_str):
            reminder_dt = datetime.strptime(reminder_str, '%m/%d/%Y %I:%M %p')
        else:
            raise ValidationError("Invalid reminder time format")

        # Check if reminder is in the future
        if reminder_dt <= datetime.now():
            raise ValidationError("Reminder time must be in the future")

        # Check if reminder is before due date
        if due_date_str:
            try:
                if re.match(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}', due_date_str):
                    due_dt = datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
                else:
                    due_dt = datetime.fromisoformat(due_date_str)

                if reminder_dt >= due_dt:
                    raise ValidationError("Reminder time must be before due date")
            except ValueError:
                pass  # Skip due date comparison if it's invalid

        return reminder_dt.isoformat()

    except ValueError as e:
        raise ValidationError(f"Invalid reminder time format: {str(e)}")


def validate_recurring_type(recurring_type: str) -> str:
    """
    Validate recurring task type.

    Args:
        recurring_type: The recurring type to validate

    Returns:
        Validated recurring type

    Raises:
        ValidationError: If recurring type is invalid
    """
    valid_types = ['None', 'Daily', 'Weekly', 'Monthly', 'Custom']

    if not recurring_type:
        return 'None'  # Default

    recurring_type = recurring_type.strip()

    if recurring_type not in valid_types:
        raise ValidationError(f"Recurring type must be one of: {', '.join(valid_types)}")

    return recurring_type


def validate_recurring_interval(interval: str, recurring_type: str) -> int:
    """
    Validate recurring interval.

    Args:
        interval: The interval string to validate
        recurring_type: The recurring type for context

    Returns:
        Validated interval as integer

    Raises:
        ValidationError: If interval is invalid
    """
    if recurring_type == 'None':
        return 1  # Default for non-recurring tasks

    if not interval:
        return 1  # Default interval

    try:
        interval_int = int(interval.strip())

        if interval_int < 1:
            raise ValidationError("Interval must be at least 1")

        if interval_int > 365:
            raise ValidationError("Interval cannot exceed 365")

        # Additional validation based on recurring type
        if recurring_type == 'Daily' and interval_int > 30:
            raise ValidationError("Daily recurring interval cannot exceed 30 days")
        elif recurring_type == 'Weekly' and interval_int > 52:
            raise ValidationError("Weekly recurring interval cannot exceed 52 weeks")
        elif recurring_type == 'Monthly' and interval_int > 12:
            raise ValidationError("Monthly recurring interval cannot exceed 12 months")

        return interval_int

    except ValueError:
        raise ValidationError("Interval must be a valid number")


def validate_volume(volume: str) -> float:
    """
    Validate alarm volume.

    Args:
        volume: The volume string to validate

    Returns:
        Validated volume as float

    Raises:
        ValidationError: If volume is invalid
    """
    if not volume:
        return 0.7  # Default volume

    try:
        volume_float = float(volume.strip())

        if volume_float < 0.0:
            raise ValidationError("Volume cannot be negative")

        if volume_float > 1.0:
            raise ValidationError("Volume cannot exceed 1.0")

        return round(volume_float, 2)

    except ValueError:
        raise ValidationError("Volume must be a valid number between 0.0 and 1.0")


def validate_snooze_duration(snooze_minutes: str) -> int:
    """
    Validate snooze duration.

    Args:
        snooze_minutes: The snooze duration string to validate

    Returns:
        Validated snooze duration in minutes

    Raises:
        ValidationError: If snooze duration is invalid
    """
    if not snooze_minutes:
        return 5  # Default snooze duration

    try:
        snooze_int = int(snooze_minutes.strip())

        if snooze_int < 1:
            raise ValidationError("Snooze duration must be at least 1 minute")

        if snooze_int > 60:
            raise ValidationError("Snooze duration cannot exceed 60 minutes")

        return snooze_int

    except ValueError:
        raise ValidationError("Snooze duration must be a valid number of minutes")


def validate_email(email: str) -> str:
    """
    Validate email address (for future contact features).

    Args:
        email: The email to validate

    Returns:
        Validated email

    Raises:
        ValidationError: If email is invalid
    """
    if not email:
        return email  # Email is optional

    email = email.strip().lower()

    if not email:
        return email

    # Basic email validation
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    if not re.match(email_pattern, email):
        raise ValidationError("Invalid email address format")

    return email


def validate_search_query(query: str) -> str:
    """
    Validate search query.

    Args:
        query: The search query to validate

    Returns:
        Validated query

    Raises:
        ValidationError: If query is invalid
    """
    if not query:
        raise ValidationError("Search query is required")

    query = query.strip()

    if len(query) < 1:
        raise ValidationError("Search query must be at least 1 character long")

    if len(query) > 100:
        raise ValidationError("Search query must be 100 characters or less")

    return query


def validate_file_path(file_path: str, must_exist: bool = False) -> str:
    """
    Validate file path.

    Args:
        file_path: The file path to validate
        must_exist: Whether the file must exist

    Returns:
        Validated file path

    Raises:
        ValidationError: If file path is invalid
    """
    if not file_path:
        raise ValidationError("File path is required")

    file_path = file_path.strip()

    if not file_path:
        raise ValidationError("File path cannot be empty")

    # Check for invalid characters
    invalid_chars = '<>:"|?*' if os.name == 'nt' else '\0'
    for char in invalid_chars:
        if char in file_path:
            raise ValidationError(f"File path contains invalid character: {char}")

    if must_exist and not os.path.exists(file_path):
        raise ValidationError("File does not exist")

    return file_path


def validate_task_data(data: Dict[str, Any], existing_categories: List[str] = None) -> Dict[str, Any]:
    """
    Validate complete task data.

    Args:
        data: Dictionary containing task data
        existing_categories: List of existing categories

    Returns:
        Validated task data

    Raises:
        ValidationError: If any data is invalid
    """
    validated_data = {}

    # Validate required fields
    if 'title' in data:
        validated_data['title'] = validate_task_title(data['title'])

    # Validate optional fields
    if 'description' in data:
        validated_data['description'] = validate_task_description(data.get('description'))

    if 'priority' in data:
        validated_data['priority'] = validate_priority(data['priority'])

    if 'status' in data:
        validated_data['status'] = validate_status(data['status'])

    if 'category' in data:
        validated_data['category'] = validate_category(data['category'], existing_categories)

    if 'due_date' in data:
        validated_data['due_date'] = validate_due_date(data.get('due_date'))

    if 'reminder_time' in data:
        validated_data['reminder_time'] = validate_reminder_time(
            data.get('reminder_time'),
            validated_data.get('due_date')
        )

    if 'recurring_type' in data:
        validated_data['recurring_type'] = validate_recurring_type(data['recurring_type'])

    if 'recurring_interval' in data:
        validated_data['recurring_interval'] = validate_recurring_interval(
            str(data['recurring_interval']),
            validated_data.get('recurring_type', 'None')
        )

    return validated_data


def sanitize_input(input_string: str) -> str:
    """
    Sanitize user input by removing potentially harmful characters.

    Args:
        input_string: The input string to sanitize

    Returns:
        Sanitized string
    """
    if not input_string:
        return ""

    # Remove HTML tags
    sanitized = re.sub(r'<[^>]+>', '', input_string)

    # Remove potential SQL injection patterns
    sanitized = re.sub(r'(?i)(union|select|drop|delete|insert|update|create|alter|exec|execute)', '', sanitized)

    # Remove control characters except newlines and tabs
    sanitized = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', sanitized)

    return sanitized.strip()