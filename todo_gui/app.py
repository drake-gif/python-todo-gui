"""Tkinter window for the to-do list."""
from __future__ import annotations

import os
import tkinter as tk
import tkinter.font as tkfont
from pathlib import Path
from tkinter import messagebox, simpledialog, ttk
from typing import Optional

from .core import TaskNotFoundError, TodoList

DONE_MARK = "\u2713"  # check mark


def default_path() -> Path:
    env = os.environ.get("TODO_FILE")
    if env:
        return Path(env)
    return Path.home() / ".todo-gui" / "tasks.json"


class TodoApp(tk.Tk):
    def __init__(self, todo: Optional[TodoList] = None):
        super().__init__()
        self.title("To-do list")
        self.geometry("560x480")
        self.minsize(420, 360)

        self.todo = todo or TodoList(default_path())
        self.filter_var = tk.StringVar(value="all")
        self.status_var = tk.StringVar()

        self._build_widgets()
        self._bind_keys()
        self.refresh()
        self.entry.focus_set()

    # ---------- layout ----------
    def _build_widgets(self) -> None:
        pad = {"padx": 12}

        # add row
        add_row = ttk.Frame(self)
        add_row.pack(fill="x", pady=(12, 8), **pad)
        self.entry = ttk.Entry(add_row)
        self.entry.pack(side="left", fill="x", expand=True)
        ttk.Button(add_row, text="Add task", command=self.add_task).pack(
            side="left", padx=(8, 0)
        )

        # filter row
        filter_row = ttk.Frame(self)
        filter_row.pack(fill="x", pady=(0, 8), **pad)
        for label, value in (("All", "all"), ("To do", "pending"), ("Done", "done")):
            ttk.Radiobutton(
                filter_row,
                text=label,
                value=value,
                variable=self.filter_var,
                command=self.refresh,
            ).pack(side="left", padx=(0, 12))

        # task list
        list_frame = ttk.Frame(self)
        list_frame.pack(fill="both", expand=True, **pad)
        self.tree = ttk.Treeview(
            list_frame,
            columns=("done", "title"),
            show="headings",
            selectmode="browse",
        )
        self.tree.heading("done", text="")
        self.tree.heading("title", text="Task", anchor="w")
        self.tree.column("done", width=36, stretch=False, anchor="center")
        self.tree.column("title", anchor="w")
        scroll = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        strike = tkfont.nametofont("TkDefaultFont").copy()
        strike.configure(overstrike=True)
        self.tree.tag_configure("done", foreground="#8a8a8a", font=strike)

        # action row
        actions = ttk.Frame(self)
        actions.pack(fill="x", pady=(8, 4), **pad)
        ttk.Button(actions, text="Mark done / undo", command=self.toggle_task).pack(
            side="left"
        )
        ttk.Button(actions, text="Edit", command=self.edit_task).pack(
            side="left", padx=6
        )
        ttk.Button(actions, text="Delete", command=self.delete_task).pack(side="left")
        ttk.Button(actions, text="Clear completed", command=self.clear_done).pack(
            side="right"
        )

        # status bar
        ttk.Label(self, textvariable=self.status_var, foreground="#6b6b6b").pack(
            anchor="w", padx=12, pady=(0, 10)
        )

    def _bind_keys(self) -> None:
        self.entry.bind("<Return>", lambda _e: self.add_task())
        self.tree.bind("<Double-1>", lambda _e: self.toggle_task())
        self.tree.bind("<Delete>", lambda _e: self.delete_task())
        self.tree.bind("<space>", lambda _e: self.toggle_task())

    # ---------- helpers ----------
    def selected_id(self) -> Optional[int]:
        selection = self.tree.selection()
        return int(selection[0]) if selection else None

    def _need_selection(self) -> Optional[int]:
        task_id = self.selected_id()
        if task_id is None:
            messagebox.showinfo("No task selected", "Select a task in the list first.")
        return task_id

    def refresh(self) -> None:
        selected = self.selected_id()
        self.tree.delete(*self.tree.get_children())
        for task in self.todo.list(self.filter_var.get()):
            self.tree.insert(
                "",
                "end",
                iid=str(task.id),
                values=(DONE_MARK if task.done else "", task.title),
                tags=("done",) if task.done else (),
            )
        if selected is not None and self.tree.exists(str(selected)):
            self.tree.selection_set(str(selected))

        pending = len(self.todo.list("pending"))
        done = len(self.todo.list("done"))
        if not self.todo.tasks:
            self.status_var.set("Nothing here yet. Type a task above and press Enter.")
        else:
            self.status_var.set(f"{pending} to do, {done} done")

    # ---------- actions ----------
    def add_task(self) -> None:
        title = self.entry.get()
        try:
            self.todo.add(title)
        except ValueError:
            messagebox.showwarning("Empty task", "Type a task before adding it.")
            return
        self.entry.delete(0, "end")
        self.refresh()

    def toggle_task(self) -> None:
        task_id = self._need_selection()
        if task_id is None:
            return
        try:
            task = self.todo.get(task_id)
            if task.done:
                self.todo.reopen(task_id)
            else:
                self.todo.complete(task_id)
        except TaskNotFoundError:
            pass
        self.refresh()

    def edit_task(self) -> None:
        task_id = self._need_selection()
        if task_id is None:
            return
        task = self.todo.get(task_id)
        new_title = simpledialog.askstring(
            "Edit task", "Task:", initialvalue=task.title, parent=self
        )
        if new_title is None:
            return
        try:
            self.todo.edit(task_id, new_title)
        except ValueError:
            messagebox.showwarning("Empty task", "A task needs a title.")
        self.refresh()

    def delete_task(self) -> None:
        task_id = self._need_selection()
        if task_id is None:
            return
        task = self.todo.get(task_id)
        if messagebox.askyesno("Delete task", f'Delete "{task.title}"?'):
            self.todo.remove(task_id)
            self.refresh()

    def clear_done(self) -> None:
        if not self.todo.list("done"):
            messagebox.showinfo("Nothing to clear", "No completed tasks yet.")
            return
        if messagebox.askyesno("Clear completed", "Delete all completed tasks?"):
            self.todo.clear_done()
            self.refresh()


def main() -> None:
    TodoApp().mainloop()


if __name__ == "__main__":
    main()
