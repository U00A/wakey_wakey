"""
FastAPI backend API exposing task management operations for a C# frontend.
"""

from typing import List, Dict, Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from core.task_manager import TaskManager


app = FastAPI(title="Task Scheduler Pro API", version="1.0.0")
task_manager = TaskManager()


class TaskIn(BaseModel):
    title: str
    description: str | None = None
    priority: str = "Medium"
    category: str = "Personal"
    due_date: str | None = None
    reminder_time: str | None = None
    recurring_type: str = "None"
    recurring_interval: int = 1


class TaskOut(TaskIn):
    id: int
    status: str = "Pending"
    created_at: str | None = None
    updated_at: str | None = None
    completed_at: str | None = None


@app.get("/health")
def health() -> Dict[str, Any]:
    return {"status": "ok"}


@app.get("/tasks", response_model=List[TaskOut])
def list_tasks() -> List[TaskOut]:
    tasks = task_manager.get_all_tasks()
    return [TaskOut(**t.to_dict()) for t in tasks]


@app.post("/tasks", response_model=TaskOut)
def create_task(task: TaskIn) -> TaskOut:
    success, task_id, msg = task_manager.create_task(task.dict())
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    created = task_manager.get_task(task_id)
    if not created:
        raise HTTPException(status_code=500, detail="Task not found after creation")
    return TaskOut(**created.to_dict())


@app.get("/tasks/{task_id}", response_model=TaskOut)
def get_task(task_id: int) -> TaskOut:
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskOut(**task.to_dict())


@app.put("/tasks/{task_id}", response_model=TaskOut)
def update_task(task_id: int, updates: Dict[str, Any]) -> TaskOut:
    success, msg = task_manager.update_task(task_id, updates)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found after update")
    return TaskOut(**task.to_dict())


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int) -> Dict[str, Any]:
    success, msg = task_manager.delete_task(task_id)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"success": True, "message": msg}

