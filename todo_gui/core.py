"""Core to-do list logic: tasks and JSON file storage."""
from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional


class TaskNotFoundError(Exception):
    """Raised when a task id does not exist."""


@dataclass
class Task:
    id: int
    title: str
    done: bool = False
    created_at: str = ""


class TodoList:
    """A list of tasks saved to a JSON file after every change."""

    def __init__(self, path: Path):
        self.path = Path(path)
        self.tasks: List[Task] = []
        self._load()

    # ---------- storage ----------
    def _load(self) -> None:
        if not self.path.exists():
            return
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            self.tasks = [Task(**item) for item in data]
        except (json.JSONDecodeError, TypeError) as exc:
            raise ValueError(f"Could not read {self.path}: file is corrupted ({exc})")

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(
            json.dumps([asdict(t) for t in self.tasks], indent=2), encoding="utf-8"
        )
        os.replace(tmp, self.path)  # atomic: never leaves a half-written file

    # ---------- queries ----------
    def get(self, task_id: int) -> Task:
        for task in self.tasks:
            if task.id == task_id:
                return task
        raise TaskNotFoundError(f"No task with id {task_id}")

    def list(self, status: Optional[str] = None) -> List[Task]:
        """status: None/'all', 'pending' or 'done'."""
        if status == "pending":
            return [t for t in self.tasks if not t.done]
        if status == "done":
            return [t for t in self.tasks if t.done]
        return list(self.tasks)

    # ---------- changes ----------
    def add(self, title: str) -> Task:
        title = title.strip()
        if not title:
            raise ValueError("Task title cannot be empty")
        next_id = max((t.id for t in self.tasks), default=0) + 1
        task = Task(next_id, title, False, datetime.now().isoformat(timespec="seconds"))
        self.tasks.append(task)
        self._save()
        return task

    def complete(self, task_id: int) -> Task:
        task = self.get(task_id)
        task.done = True
        self._save()
        return task

    def reopen(self, task_id: int) -> Task:
        task = self.get(task_id)
        task.done = False
        self._save()
        return task

    def edit(self, task_id: int, title: str) -> Task:
        title = title.strip()
        if not title:
            raise ValueError("Task title cannot be empty")
        task = self.get(task_id)
        task.title = title
        self._save()
        return task

    def remove(self, task_id: int) -> Task:
        task = self.get(task_id)
        self.tasks.remove(task)
        self._save()
        return task

    def clear_done(self) -> int:
        before = len(self.tasks)
        self.tasks = [t for t in self.tasks if not t.done]
        self._save()
        return before - len(self.tasks)
