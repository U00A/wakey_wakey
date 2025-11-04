"""
Database manager for the task scheduler application.
Handles all SQLite database operations including CRUD operations for tasks, categories, and alarms.
"""

import sqlite3
import os
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
from .models import Task, Category, Alarm, DatabaseModel


class DatabaseManager(DatabaseModel):
    """Main database manager class with all CRUD operations."""

    def __init__(self, db_path: str = "data/tasks.db"):
        super().__init__(db_path)
        self._ensure_data_directory()

    def _ensure_data_directory(self):
        """Ensure the data directory exists."""
        data_dir = os.path.dirname(self.db_path)
        if data_dir and not os.path.exists(data_dir):
            os.makedirs(data_dir)

    # Task CRUD Operations
    def create_task(self, task: Task) -> int:
        """Create a new task and return its ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO tasks (title, description, priority, category, status,
                                  due_date, reminder_time, recurring_type, recurring_interval)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                task.title,
                task.description,
                task.priority,
                task.category,
                task.status,
                task.due_date,
                task.reminder_time,
                task.recurring_type,
                task.recurring_interval
            ))
            task_id = cursor.lastrowid
            conn.commit()
            return task_id

    def get_task(self, task_id: int) -> Optional[Task]:
        """Retrieve a single task by ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
            row = cursor.fetchone()
            if row:
                return Task(dict(row))
            return None

    def get_all_tasks(self, filters: Dict[str, Any] = None) -> List[Task]:
        """Get all tasks with optional filtering."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            query = "SELECT * FROM tasks WHERE 1=1"
            params = []

            if filters:
                if 'status' in filters:
                    query += " AND status = ?"
                    params.append(filters['status'])
                if 'priority' in filters:
                    query += " AND priority = ?"
                    params.append(filters['priority'])
                if 'category' in filters:
                    query += " AND category = ?"
                    params.append(filters['category'])
                if 'date_from' in filters:
                    query += " AND due_date >= ?"
                    params.append(filters['date_from'])
                if 'date_to' in filters:
                    query += " AND due_date <= ?"
                    params.append(filters['date_to'])

            query += " ORDER BY due_date ASC, created_at DESC"

            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [Task(dict(row)) for row in rows]

    def update_task(self, task_id: int, updates: Dict[str, Any]) -> bool:
        """Update an existing task."""
        if not updates:
            return False

        # Add updated_at timestamp
        updates['updated_at'] = datetime.now().isoformat()

        set_clause = ", ".join([f"{key} = ?" for key in updates.keys()])
        values = list(updates.values())
        values.append(task_id)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"UPDATE tasks SET {set_clause} WHERE id = ?", values)
            conn.commit()
            return cursor.rowcount > 0

    def delete_task(self, task_id: int) -> bool:
        """Delete a task by ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            conn.commit()
            return cursor.rowcount > 0

    def get_tasks_by_date(self, target_date: date) -> List[Task]:
        """Get tasks for a specific date."""
        date_str = target_date.isoformat()
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM tasks
                WHERE DATE(due_date) = DATE(?)
                ORDER BY due_date ASC
            """, (date_str,))
            rows = cursor.fetchall()
            return [Task(dict(row)) for row in rows]

    def get_upcoming_tasks(self, hours: int = 24) -> List[Task]:
        """Get tasks due within the specified hours."""
        future_time = (datetime.now() + timedelta(hours=hours)).isoformat()
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM tasks
                WHERE due_date <= ? AND status = 'Pending'
                ORDER BY due_date ASC
            """, (future_time,))
            rows = cursor.fetchall()
            return [Task(dict(row)) for row in rows]

    def search_tasks(self, query: str) -> List[Task]:
        """Search tasks by title and description."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM tasks
                WHERE title LIKE ? OR description LIKE ?
                ORDER BY due_date ASC
            """, (f"%{query}%", f"%{query}%"))
            rows = cursor.fetchall()
            return [Task(dict(row)) for row in rows]

    def get_overdue_tasks(self) -> List[Task]:
        """Get all overdue tasks."""
        now = datetime.now().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM tasks
                WHERE due_date < ? AND status = 'Pending'
                ORDER BY due_date ASC
            """, (now,))
            rows = cursor.fetchall()
            return [Task(dict(row)) for row in rows]

    # Category CRUD Operations
    def create_category(self, category: Category) -> int:
        """Create a new category."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO categories (name, color)
                VALUES (?, ?)
            """, (category.name, category.color))
            category_id = cursor.lastrowid
            conn.commit()
            return category_id

    def get_all_categories(self) -> List[Category]:
        """Get all categories."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM categories ORDER BY name ASC")
            rows = cursor.fetchall()
            return [Category(dict(row)) for row in rows]

    def get_category_by_name(self, name: str) -> Optional[Category]:
        """Get a category by name."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM categories WHERE name = ?", (name,))
            row = cursor.fetchone()
            if row:
                return Category(dict(row))
            return None

    def update_category(self, category_id: int, updates: Dict[str, Any]) -> bool:
        """Update an existing category."""
        if not updates:
            return False

        set_clause = ", ".join([f"{key} = ?" for key in updates.keys()])
        values = list(updates.values())
        values.append(category_id)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"UPDATE categories SET {set_clause} WHERE id = ?", values)
            conn.commit()
            return cursor.rowcount > 0

    def delete_category(self, category_id: int) -> bool:
        """Delete a category by ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM categories WHERE id = ?", (category_id,))
            conn.commit()
            return cursor.rowcount > 0

    # Alarm CRUD Operations
    def create_alarm(self, alarm: Alarm) -> int:
        """Create a new alarm."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO alarms (task_id, alarm_time, is_active, sound_file, volume, snooze_count)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                alarm.task_id,
                alarm.alarm_time,
                alarm.is_active,
                alarm.sound_file,
                alarm.volume,
                alarm.snooze_count
            ))
            alarm_id = cursor.lastrowid
            conn.commit()
            return alarm_id

    def get_alarms_for_task(self, task_id: int) -> List[Alarm]:
        """Get all alarms for a specific task."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM alarms
                WHERE task_id = ? AND is_active = 1
                ORDER BY alarm_time ASC
            """, (task_id,))
            rows = cursor.fetchall()
            return [Alarm(dict(row)) for row in rows]

    def get_pending_alarms(self) -> List[Alarm]:
        """Get all pending alarms that should trigger now."""
        now = datetime.now().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM alarms
                WHERE alarm_time <= ? AND is_active = 1
                ORDER BY alarm_time ASC
            """, (now,))
            rows = cursor.fetchall()
            return [Alarm(dict(row)) for row in rows]

    def update_alarm(self, alarm_id: int, updates: Dict[str, Any]) -> bool:
        """Update an existing alarm."""
        if not updates:
            return False

        set_clause = ", ".join([f"{key} = ?" for key in updates.keys()])
        values = list(updates.values())
        values.append(alarm_id)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"UPDATE alarms SET {set_clause} WHERE id = ?", values)
            conn.commit()
            return cursor.rowcount > 0

    def delete_alarm(self, alarm_id: int) -> bool:
        """Delete an alarm by ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM alarms WHERE id = ?", (alarm_id,))
            conn.commit()
            return cursor.rowcount > 0

    def deactivate_alarm(self, alarm_id: int) -> bool:
        """Deactivate an alarm."""
        return self.update_alarm(alarm_id, {'is_active': False})

    # Statistics and Analytics
    def get_task_statistics(self, days: int = 30) -> Dict[str, Any]:
        """Get task completion statistics for the specified period."""
        start_date = (date.today() - timedelta(days=days)).isoformat()

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Total tasks created in period
            cursor.execute("""
                SELECT COUNT(*) FROM tasks
                WHERE created_at >= ?
            """, (start_date,))
            total_created = cursor.fetchone()[0]

            # Tasks completed in period
            cursor.execute("""
                SELECT COUNT(*) FROM tasks
                WHERE completed_at >= ? AND status = 'Completed'
            """, (start_date,))
            total_completed = cursor.fetchone()[0]

            # Tasks by priority
            cursor.execute("""
                SELECT priority, COUNT(*) FROM tasks
                WHERE created_at >= ?
                GROUP BY priority
            """, (start_date,))
            priority_stats = dict(cursor.fetchall())

            # Tasks by category
            cursor.execute("""
                SELECT category, COUNT(*) FROM tasks
                WHERE created_at >= ?
                GROUP BY category
            """, (start_date,))
            category_stats = dict(cursor.fetchall())

            # Overdue tasks
            now = datetime.now().isoformat()
            cursor.execute("""
                SELECT COUNT(*) FROM tasks
                WHERE due_date < ? AND status = 'Pending'
            """, (now,))
            overdue_count = cursor.fetchone()[0]

            completion_rate = (total_completed / total_created * 100) if total_created > 0 else 0

            return {
                'total_created': total_created,
                'total_completed': total_completed,
                'completion_rate': completion_rate,
                'priority_stats': priority_stats,
                'category_stats': category_stats,
                'overdue_count': overdue_count,
                'period_days': days
            }

    def backup_database(self, backup_path: str) -> bool:
        """Create a backup of the database."""
        try:
            with sqlite3.connect(self.db_path) as source:
                with sqlite3.connect(backup_path) as backup:
                    source.backup(backup)
            return True
        except Exception:
            return False

    def restore_database(self, backup_path: str) -> bool:
        """Restore database from backup."""
        try:
            if os.path.exists(backup_path):
                # Copy backup to current database
                with sqlite3.connect(backup_path) as backup:
                    with sqlite3.connect(self.db_path) as target:
                        backup.backup(target)
                return True
            return False
        except Exception:
            return False