"""
Core task manager for the task scheduler application.
Handles business logic for task operations, recurring tasks, and statistics.
"""

import os
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

from ..database.manager import DatabaseManager
from ..database.models import Task, Category, Alarm
from ..utils.validators import validate_task_data, ValidationError
from ..utils.helpers import (
    export_tasks_to_csv, export_tasks_to_json,
    import_tasks_from_csv, import_tasks_from_json,
    calculate_task_statistics, format_datetime, ensure_directory_exists
)


class TaskManager:
    """Core business logic for task management."""

    def __init__(self, db_manager: DatabaseManager = None):
        self.db = db_manager or DatabaseManager()
        self.export_dir = Path("data/exports")
        self.backup_dir = Path("data/backups")

        # Ensure directories exist
        ensure_directory_exists(self.export_dir)
        ensure_directory_exists(self.backup_dir)

    # Task CRUD Operations
    def create_task(self, task_data: Dict[str, Any]) -> Tuple[bool, int, str]:
        """
        Create a new task.

        Args:
            task_data: Dictionary containing task information

        Returns:
            Tuple of (success: bool, task_id: int, message: str)
        """
        try:
            # Validate task data
            validated_data = validate_task_data(task_data, self._get_existing_categories())

            # Create task object
            task = Task(validated_data)

            # Save to database
            task_id = self.db.create_task(task)

            # Create alarms if reminder time is set
            if task.reminder_time:
                self._create_task_alarms(task_id, task)

            # Handle recurring task creation
            if task.recurring_type != "None":
                self._create_recurring_tasks(task)

            return True, task_id, "Task created successfully"

        except ValidationError as e:
            return False, -1, f"Validation error: {str(e)}"
        except Exception as e:
            return False, -1, f"Error creating task: {str(e)}"

    def get_task(self, task_id: int) -> Optional[Task]:
        """Get a single task by ID."""
        return self.db.get_task(task_id)

    def update_task(self, task_id: int, updates: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Update an existing task.

        Args:
            task_id: ID of task to update
            updates: Dictionary of fields to update

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Get existing task
            existing_task = self.db.get_task(task_id)
            if not existing_task:
                return False, "Task not found"

            # Validate updates
            validated_updates = validate_task_data(updates, self._get_existing_categories())

            # Handle status changes
            if 'status' in validated_updates:
                new_status = validated_updates['status']
                if new_status == 'Completed' and existing_task.status != 'Completed':
                    validated_updates['completed_at'] = datetime.now().isoformat()

                    # Create next instance of recurring task
                    if existing_task.recurring_type != 'None':
                        self._create_next_recurring_task(existing_task)

            # Update database
            success = self.db.update_task(task_id, validated_updates)
            if not success:
                return False, "Failed to update task in database"

            # Update alarms if reminder time changed
            if 'reminder_time' in validated_updates or 'due_date' in validated_updates:
                self._update_task_alarms(task_id, existing_task, validated_updates)

            return True, "Task updated successfully"

        except ValidationError as e:
            return False, f"Validation error: {str(e)}"
        except Exception as e:
            return False, f"Error updating task: {str(e)}"

    def delete_task(self, task_id: int) -> Tuple[bool, str]:
        """
        Delete a task.

        Args:
            task_id: ID of task to delete

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Check if task exists
            task = self.db.get_task(task_id)
            if not task:
                return False, "Task not found"

            # Delete from database (alarms will be deleted due to foreign key constraint)
            success = self.db.delete_task(task_id)
            if success:
                return True, "Task deleted successfully"
            else:
                return False, "Failed to delete task"

        except Exception as e:
            return False, f"Error deleting task: {str(e)}"

    def get_all_tasks(self, filters: Dict[str, Any] = None) -> List[Task]:
        """Get all tasks with optional filtering."""
        return self.db.get_all_tasks(filters)

    def search_tasks(self, query: str) -> List[Task]:
        """Search tasks by title and description."""
        if not query or len(query.strip()) < 1:
            return []
        return self.db.search_tasks(query.strip())

    # Task filtering and queries
    def get_tasks_by_date(self, target_date: date) -> List[Task]:
        """Get tasks for a specific date."""
        return self.db.get_tasks_by_date(target_date)

    def get_tasks_for_week(self, start_date: date = None) -> List[Task]:
        """Get tasks for a week starting from start_date."""
        if start_date is None:
            start_date = date.today()

        end_date = start_date + timedelta(days=6)
        filters = {
            'date_from': start_date.isoformat(),
            'date_to': end_date.isoformat()
        }
        return self.db.get_all_tasks(filters)

    def get_upcoming_tasks(self, hours: int = 24) -> List[Task]:
        """Get tasks due within the specified hours."""
        return self.db.get_upcoming_tasks(hours)

    def get_overdue_tasks(self) -> List[Task]:
        """Get all overdue tasks."""
        return self.db.get_overdue_tasks()

    def get_today_tasks(self) -> List[Task]:
        """Get tasks due today."""
        today = date.today()
        return self.get_tasks_by_date(today)

    # Task status operations
    def complete_task(self, task_id: int) -> Tuple[bool, str]:
        """Mark a task as completed."""
        return self.update_task(task_id, {'status': 'Completed'})

    def cancel_task(self, task_id: int) -> Tuple[bool, str]:
        """Cancel a task."""
        return self.update_task(task_id, {'status': 'Cancelled'})

    def reopen_task(self, task_id: int) -> Tuple[bool, str]:
        """Reopen a cancelled or completed task."""
        return self.update_task(task_id, {'status': 'Pending', 'completed_at': None})

    # Recurring tasks
    def _create_recurring_tasks(self, base_task: Task):
        """Create recurring task instances."""
        # This will create future instances based on the recurring pattern
        # Implementation will depend on the specific requirements
        pass

    def _create_next_recurring_task(self, completed_task: Task):
        """Create the next instance of a recurring task."""
        if completed_task.recurring_type == "None":
            return

        # Calculate next due date based on recurring type
        next_due_date = self._calculate_next_recurring_date(completed_task)

        if next_due_date:
            next_task_data = {
                'title': completed_task.title,
                'description': completed_task.description,
                'priority': completed_task.priority,
                'category': completed_task.category,
                'due_date': next_due_date.isoformat(),
                'reminder_time': self._calculate_next_reminder_time(completed_task, next_due_date),
                'recurring_type': completed_task.recurring_type,
                'recurring_interval': completed_task.recurring_interval
            }

            self.create_task(next_task_data)

    def _calculate_next_recurring_date(self, task: Task) -> Optional[datetime]:
        """Calculate the next due date for a recurring task."""
        if not task.due_date:
            return None

        try:
            current_due = datetime.fromisoformat(task.due_date.replace('Z', '+00:00'))
        except ValueError:
            return None

        if task.recurring_type == "Daily":
            next_date = current_due + timedelta(days=task.recurring_interval)
        elif task.recurring_type == "Weekly":
            next_date = current_due + timedelta(weeks=task.recurring_interval)
        elif task.recurring_type == "Monthly":
            # Handle month rollover
            next_date = current_due.replace(month=current_due.month + task.recurring_interval)
        elif task.recurring_type == "Custom":
            next_date = current_due + timedelta(days=task.recurring_interval)
        else:
            return None

        return next_date

    def _calculate_next_reminder_time(self, task: Task, next_due_date: datetime) -> Optional[str]:
        """Calculate reminder time for the next recurring task."""
        if not task.reminder_time or not next_due_date:
            return None

        try:
            current_reminder = datetime.fromisoformat(task.reminder_time.replace('Z', '+00:00'))
            current_due = datetime.fromisoformat(task.due_date.replace('Z', '+00:00'))

            # Calculate the time difference between reminder and due date
            time_diff = current_due - current_reminder

            # Apply the same difference to the next due date
            next_reminder = next_due_date - time_diff

            return next_reminder.isoformat()
        except ValueError:
            return None

    # Alarm management
    def _create_task_alarms(self, task_id: int, task: Task):
        """Create alarms for a task."""
        if not task.reminder_time:
            return

        alarm = Alarm({
            'task_id': task_id,
            'alarm_time': task.reminder_time,
            'is_active': True,
            'sound_file': 'default',
            'volume': 0.7,
            'snooze_count': 0
        })

        self.db.create_alarm(alarm)

    def _update_task_alarms(self, task_id: int, old_task: Task, updates: Dict[str, Any]):
        """Update alarms when task is modified."""
        # Deactivate existing alarms
        existing_alarms = self.db.get_alarms_for_task(task_id)
        for alarm in existing_alarms:
            self.db.deactivate_alarm(alarm.id)

        # Create new alarms if reminder time is updated
        new_reminder_time = updates.get('reminder_time') or old_task.reminder_time
        if new_reminder_time:
            alarm = Alarm({
                'task_id': task_id,
                'alarm_time': new_reminder_time,
                'is_active': True,
                'sound_file': 'default',
                'volume': 0.7,
                'snooze_count': 0
            })
            self.db.create_alarm(alarm)

    # Statistics and analytics
    def get_task_statistics(self, days: int = 30) -> Dict[str, Any]:
        """Get comprehensive task statistics."""
        return self.db.get_task_statistics(days)

    def get_productivity_trends(self, days: int = 30) -> Dict[str, Any]:
        """Get productivity trends over time."""
        end_date = date.today()
        start_date = end_date - timedelta(days=days)

        # Get daily completion counts
        daily_stats = {}
        current_date = start_date
        while current_date <= end_date:
            day_tasks = self.get_tasks_by_date(current_date)
            completed_count = sum(1 for task in day_tasks if task.status == 'Completed')
            daily_stats[current_date.isoformat()] = completed_count
            current_date += timedelta(days=1)

        # Calculate trends
        completion_rates = []
        for i in range(0, len(daily_stats) - 6, 7):  # Weekly averages
            week_data = list(daily_stats.values())[i:i+7]
            if week_data:
                week_avg = sum(week_data) / len(week_data)
                completion_rates.append(week_avg)

        return {
            'daily_stats': daily_stats,
            'weekly_averages': completion_rates,
            'period_days': days,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat()
        }

    def get_category_distribution(self) -> Dict[str, int]:
        """Get task distribution by category."""
        all_tasks = self.db.get_all_tasks()
        category_counts = {}

        for task in all_tasks:
            category = task.category or 'Uncategorized'
            category_counts[category] = category_counts.get(category, 0) + 1

        return category_counts

    def get_priority_distribution(self) -> Dict[str, int]:
        """Get task distribution by priority."""
        all_tasks = self.db.get_all_tasks()
        priority_counts = {'High': 0, 'Medium': 0, 'Low': 0}

        for task in all_tasks:
            priority = task.priority or 'Medium'
            if priority in priority_counts:
                priority_counts[priority] += 1

        return priority_counts

    # Import/Export operations
    def export_tasks(self, file_path: str, format_type: str = "json",
                    filters: Dict[str, Any] = None) -> Tuple[bool, str]:
        """
        Export tasks to file.

        Args:
            file_path: Output file path
            format_type: Export format ('json' or 'csv')
            filters: Optional filters to apply

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Get tasks to export
            tasks = self.db.get_all_tasks(filters)
            task_dicts = [task.to_dict() for task in tasks]

            # Export based on format
            if format_type.lower() == "json":
                success = export_tasks_to_json(task_dicts, file_path)
            elif format_type.lower() == "csv":
                success = export_tasks_to_csv(task_dicts, file_path)
            else:
                return False, f"Unsupported format: {format_type}"

            if success:
                return True, f"Exported {len(tasks)} tasks to {file_path}"
            else:
                return False, "Export failed"

        except Exception as e:
            return False, f"Export error: {str(e)}"

    def import_tasks(self, file_path: str, merge_strategy: str = "skip") -> Tuple[bool, str]:
        """
        Import tasks from file.

        Args:
            file_path: Input file path
            merge_strategy: How to handle duplicates ('skip', 'update', 'duplicate')

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Determine file format and import
            file_ext = Path(file_path).suffix.lower()

            if file_ext == ".json":
                task_data = import_tasks_from_json(file_path)
            elif file_ext == ".csv":
                task_data = import_tasks_from_csv(file_path)
            else:
                return False, f"Unsupported file format: {file_ext}"

            if not task_data:
                return False, "No tasks found in file"

            # Import tasks with merge strategy
            imported_count = 0
            skipped_count = 0
            error_count = 0

            for task_dict in task_data:
                try:
                    # Check for existing task
                    existing_task = None
                    if 'id' in task_dict and task_dict['id']:
                        existing_task = self.db.get_task(task_dict['id'])

                    if existing_task:
                        if merge_strategy == "skip":
                            skipped_count += 1
                            continue
                        elif merge_strategy == "update":
                            success, _ = self.update_task(existing_task.id, task_dict)
                            if success:
                                imported_count += 1
                            else:
                                error_count += 1
                        elif merge_strategy == "duplicate":
                            # Remove ID to create new task
                            task_dict.pop('id', None)
                            success, _, _ = self.create_task(task_dict)
                            if success:
                                imported_count += 1
                            else:
                                error_count += 1
                    else:
                        # New task
                        success, _, _ = self.create_task(task_dict)
                        if success:
                            imported_count += 1
                        else:
                            error_count += 1

                except Exception as e:
                    error_count += 1
                    continue

            message = f"Imported {imported_count} tasks"
            if skipped_count > 0:
                message += f", skipped {skipped_count} duplicates"
            if error_count > 0:
                message += f", {error_count} errors"

            return True, message

        except Exception as e:
            return False, f"Import error: {str(e)}"

    # Data maintenance
    def cleanup_old_tasks(self, days: int = 30) -> Tuple[bool, str]:
        """
        Clean up completed tasks older than specified days.

        Args:
            days: Age threshold in days

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            cutoff_str = cutoff_date.isoformat()

            # Get old completed tasks
            filters = {
                'status': 'Completed',
                'date_to': cutoff_str
            }
            old_tasks = self.db.get_all_tasks(filters)

            deleted_count = 0
            for task in old_tasks:
                success = self.db.delete_task(task.id)
                if success:
                    deleted_count += 1

            return True, f"Cleaned up {deleted_count} old completed tasks"

        except Exception as e:
            return False, f"Cleanup error: {str(e)}"

    def backup_data(self, backup_path: str = None) -> Tuple[bool, str]:
        """
        Create a backup of the database.

        Args:
            backup_path: Custom backup path (optional)

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            if not backup_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = self.backup_dir / f"tasks_backup_{timestamp}.db"

            success = self.db.backup_database(str(backup_path))
            if success:
                return True, f"Backup created: {backup_path}"
            else:
                return False, "Backup failed"

        except Exception as e:
            return False, f"Backup error: {str(e)}"

    # Helper methods
    def _get_existing_categories(self) -> List[str]:
        """Get list of existing category names."""
        categories = self.db.get_all_categories()
        return [cat.name for cat in categories]

    def get_task_completion_rate(self, period_days: int = 30) -> float:
        """Get task completion rate for the specified period."""
        stats = self.get_task_statistics(period_days)
        return stats.get('completion_rate', 0.0)

    def get_most_productive_day(self) -> Optional[str]:
        """Find the most productive day of the week."""
        # This would analyze historical data to determine patterns
        # For now, return a placeholder
        return "Monday"  # Placeholder implementation

    def get_upcoming_deadlines(self, hours: int = 72) -> List[Dict[str, Any]]:
        """Get upcoming task deadlines with urgency indicators."""
        upcoming_tasks = self.get_upcoming_tasks(hours)
        now = datetime.now()

        result = []
        for task in upcoming_tasks:
            if task.due_date:
                try:
                    due_dt = datetime.fromisoformat(task.due_date.replace('Z', '+00:00'))
                    hours_until = (due_dt - now).total_seconds() / 3600

                    urgency = "low"
                    if hours_until <= 2:
                        urgency = "critical"
                    elif hours_until <= 6:
                        urgency = "high"
                    elif hours_until <= 24:
                        urgency = "medium"

                    result.append({
                        'task': task,
                        'hours_until': hours_until,
                        'urgency': urgency
                    })
                except ValueError:
                    continue

        return sorted(result, key=lambda x: x['hours_until'])