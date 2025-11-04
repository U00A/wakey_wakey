"""
Database models for the task scheduler application.
Defines the SQLite database schema for tasks, categories, and alarms.
"""

import sqlite3
import datetime
from typing import Optional, List, Dict, Any


class DatabaseModel:
    """Base class for database models with common operations."""

    def __init__(self, db_path: str = "data/tasks.db"):
        self.db_path = db_path
        self._initialize_database()

    def _initialize_database(self):
        """Create database tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    priority TEXT CHECK(priority IN ('High', 'Medium', 'Low')) DEFAULT 'Medium',
                    category TEXT DEFAULT 'Personal',
                    status TEXT CHECK(status IN ('Pending', 'Completed', 'Cancelled')) DEFAULT 'Pending',
                    due_date DATETIME,
                    reminder_time DATETIME,
                    recurring_type TEXT CHECK(recurring_type IN ('None', 'Daily', 'Weekly', 'Monthly', 'Custom')) DEFAULT 'None',
                    recurring_interval INTEGER DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    completed_at DATETIME
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    color TEXT DEFAULT '#0078d4',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS alarms (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id INTEGER NOT NULL,
                    alarm_time DATETIME NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    sound_file TEXT DEFAULT 'default',
                    volume REAL DEFAULT 0.7,
                    snooze_count INTEGER DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (task_id) REFERENCES tasks (id) ON DELETE CASCADE
                )
            """)

            # Insert default categories
            default_categories = [
                ('Work', '#0078d4'),
                ('Personal', '#44ff44'),
                ('Health', '#ff4444'),
                ('Shopping', '#ffaa00'),
                ('Study', '#aa44ff')
            ]

            conn.executemany(
                "INSERT OR IGNORE INTO categories (name, color) VALUES (?, ?)",
                default_categories
            )

            conn.commit()


class Task:
    """Task model representing a single task."""

    def __init__(self, data: Dict[str, Any] = None):
        self.id = data.get('id') if data else None
        self.title = data.get('title', '') if data else ''
        self.description = data.get('description', '') if data else ''
        self.priority = data.get('priority', 'Medium') if data else 'Medium'
        self.category = data.get('category', 'Personal') if data else 'Personal'
        self.status = data.get('status', 'Pending') if data else 'Pending'
        self.due_date = data.get('due_date') if data else None
        self.reminder_time = data.get('reminder_time') if data else None
        self.recurring_type = data.get('recurring_type', 'None') if data else 'None'
        self.recurring_interval = data.get('recurring_interval', 1) if data else 1
        self.created_at = data.get('created_at') if data else None
        self.updated_at = data.get('updated_at') if data else None
        self.completed_at = data.get('completed_at') if data else None

    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'priority': self.priority,
            'category': self.category,
            'status': self.status,
            'due_date': self.due_date,
            'reminder_time': self.reminder_time,
            'recurring_type': self.recurring_type,
            'recurring_interval': self.recurring_interval,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'completed_at': self.completed_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create task from dictionary."""
        return cls(data)

    def is_overdue(self) -> bool:
        """Check if task is overdue."""
        if not self.due_date or self.status == 'Completed':
            return False
        try:
            due_date = datetime.datetime.fromisoformat(self.due_date.replace('Z', '+00:00'))
            return datetime.datetime.now() > due_date
        except (ValueError, AttributeError):
            return False

    def is_due_today(self) -> bool:
        """Check if task is due today."""
        if not self.due_date:
            return False
        try:
            due_date = datetime.datetime.fromisoformat(self.due_date.replace('Z', '+00:00')).date()
            return due_date == datetime.date.today()
        except (ValueError, AttributeError):
            return False

    def days_until_due(self) -> int:
        """Calculate days until due date."""
        if not self.due_date:
            return None
        try:
            due_date = datetime.datetime.fromisoformat(self.due_date.replace('Z', '+00:00')).date()
            today = datetime.date.today()
            return (due_date - today).days
        except (ValueError, AttributeError):
            return None


class Category:
    """Category model for task organization."""

    def __init__(self, data: Dict[str, Any] = None):
        self.id = data.get('id') if data else None
        self.name = data.get('name', '') if data else ''
        self.color = data.get('color', '#0078d4') if data else '#0078d4'
        self.created_at = data.get('created_at') if data else None

    def to_dict(self) -> Dict[str, Any]:
        """Convert category to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'color': self.color,
            'created_at': self.created_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create category from dictionary."""
        return cls(data)


class Alarm:
    """Alarm model for task reminders."""

    def __init__(self, data: Dict[str, Any] = None):
        self.id = data.get('id') if data else None
        self.task_id = data.get('task_id') if data else None
        self.alarm_time = data.get('alarm_time') if data else None
        self.is_active = data.get('is_active', True) if data else True
        self.sound_file = data.get('sound_file', 'default') if data else 'default'
        self.volume = data.get('volume', 0.7) if data else 0.7
        self.snooze_count = data.get('snooze_count', 0) if data else 0
        self.created_at = data.get('created_at') if data else None

    def to_dict(self) -> Dict[str, Any]:
        """Convert alarm to dictionary."""
        return {
            'id': self.id,
            'task_id': self.task_id,
            'alarm_time': self.alarm_time,
            'is_active': self.is_active,
            'sound_file': self.sound_file,
            'volume': self.volume,
            'snooze_count': self.snooze_count,
            'created_at': self.created_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create alarm from dictionary."""
        return cls(data)

    def is_triggered(self) -> bool:
        """Check if alarm should be triggered now."""
        if not self.is_active or not self.alarm_time:
            return False
        try:
            alarm_time = datetime.datetime.fromisoformat(self.alarm_time.replace('Z', '+00:00'))
            return datetime.datetime.now() >= alarm_time
        except (ValueError, AttributeError):
            return False