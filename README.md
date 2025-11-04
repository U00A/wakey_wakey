# Task Scheduler Pro

A modern, feature-rich task scheduler desktop application built with Python and CustomTkinter. Manage your tasks efficiently with advanced scheduling, alarms, notifications, and beautiful UI.

## Features

### 📝 Task Management
- ✅ Add, edit, delete, and mark tasks as complete
- 🎯 Set task priority levels (High, Medium, Low) with color coding
- 📁 Categorize tasks (Work, Personal, Health, etc.)
- 📄 Add detailed descriptions and notes to tasks
- 🔄 Recurring tasks (daily, weekly, monthly, custom intervals)

### ⏰ Advanced Scheduling
- 📅 Date and time picker for task deadlines
- ⏰ Set reminders before task deadline (5 min, 15 min, 1 hour, custom)
- 🔔 Multiple alarms per task
- 😴 Snooze functionality for alarms

### 🔔 Alarm System
- 🔊 Built-in alarm with custom sound notifications
- 💻 Desktop notifications for upcoming tasks
- ⚡ Persistent alarms that trigger even if app is minimized
- 🔊 Volume control for alarm sounds

### 🎨 UI/UX Design
- 🌓 Dark/Light mode toggle
- 📊 Calendar view and list view options
- 📈 Dashboard with today's tasks, upcoming tasks, and statistics
- 🔍 Search and filter functionality
- 🎨 Color-coded priority system
- 📊 Progress bars for task completion tracking

### 📊 Additional Features
- 📈 Task statistics (completion rate, productivity charts)
- 📤 Export tasks to CSV/JSON
- 📥 Import tasks from file
- 💾 Data persistence using SQLite database
- 📱 System tray integration (minimize to tray)
- ⌨️ Keyboard shortcuts for quick actions

## Installation

### Prerequisites

- Python 3.8 or higher
- Windows, macOS, or Linux operating system

### Quick Installation

1. **Clone or download the repository:**
   ```bash
   git clone <repository-url>
   cd wakey_wakey
   ```

2. **Create and activate a virtual environment (recommended):**
   ```bash
   # On Windows
   python -m venv venv
   venv\Scripts\activate

   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   python main.py
   ```

### Manual Installation

1. Install required Python packages:
   ```bash
   pip install customtkinter==5.2.1
   pip install playsound==1.3.0
   pip install plyer==2.1.0
   pip install schedule==1.2.0
   pip install Pillow==10.1.0
   ```

2. Run the application:
   ```bash
   python src/app.py
   ```

## Usage

### Getting Started

1. **Launch the application** by running `python main.py`
2. **The dashboard** opens showing today's tasks and statistics
3. **Create your first task** using the "New Task" button (Ctrl+N)
4. **Explore different views** using the sidebar navigation

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+N` | New Task |
| `Ctrl+S` | Save/Update Task |
| `Ctrl+F` | Search Tasks |
| `Ctrl+E` | Edit Task |
| `Ctrl+D` | Toggle Dark/Light Theme |
| `Ctrl+M` | Minimize to Tray |
| `Ctrl+Q` | Quit Application |
| `F5` | Refresh Current View |
| `F1` | Show Help |
| `Ctrl+1` | Dashboard View |
| `Ctrl+2` | Tasks View |
| `Ctrl+3` | Calendar View |
| `Ctrl+4` | Statistics View |
| `Ctrl+5` | Settings View |

## Configuration

### Data Storage

- **Database**: SQLite database stored in `data/tasks.db`
- **Backups**: Automatic backups in `data/backups/`
- **Exports**: Save location for CSV/JSON exports
- **Configuration**: Settings in `data/config.json`

## Troubleshooting

### Common Issues

**Application won't start:**
1. Check Python version (requires 3.8+)
2. Install all dependencies: `pip install -r requirements.txt`
3. Run from the project directory

**Database errors:**
1. Ensure `data/` directory exists and is writable
2. Check disk space availability

## Project Structure

```
wakey_wakey/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── assets/                # Icons, sounds, and UI resources
│   ├── icons/
│   └── sounds/
├── src/
│   ├── app.py            # Main application class
│   ├── database/         # Database models and manager
│   ├── ui/               # User interface components
│   ├── core/             # Core business logic
│   └── utils/            # Utility functions
└── data/                 # Database and configuration files
```

## Dependencies

- **CustomTkinter**: Modern UI framework
- **SQLite**: Database storage
- **Playsound**: Alarm sounds
- **Plyer**: Desktop notifications
- **Schedule**: Task scheduling
- **Pillow**: Image processing

## License

This project is licensed under the MIT License.

---

**Thank you for using Task Scheduler Pro!** 🎉