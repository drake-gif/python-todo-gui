"""Smoke test for the window. Skipped automatically when no display is available
(e.g. a headless server); it runs on your desktop and under xvfb in CI."""
import pytest

tk = pytest.importorskip("tkinter")

from todo_gui.app import TodoApp
from todo_gui.core import TodoList


@pytest.fixture
def app(tmp_path):
    try:
        window = TodoApp(TodoList(tmp_path / "tasks.json"))
    except tk.TclError:
        pytest.skip("no display available")
    window.withdraw()
    yield window
    window.destroy()


def test_add_task_through_the_window(app):
    app.entry.insert(0, "Buy milk")
    app.add_task()
    assert [t.title for t in app.todo.tasks] == ["Buy milk"]
    assert len(app.tree.get_children()) == 1
    assert app.entry.get() == ""


def test_toggle_marks_task_done(app):
    app.entry.insert(0, "Write tests")
    app.add_task()
    app.tree.selection_set(app.tree.get_children()[0])
    app.toggle_task()
    assert app.todo.tasks[0].done is True
    assert "1 done" in app.status_var.get()


def test_filter_hides_completed_tasks(app):
    for title in ("a", "b"):
        app.entry.insert(0, title)
        app.add_task()
    app.todo.complete(1)
    app.filter_var.set("pending")
    app.refresh()
    assert len(app.tree.get_children()) == 1
