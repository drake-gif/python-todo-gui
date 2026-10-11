import json

import pytest

from todo_gui.core import TaskNotFoundError, TodoList


@pytest.fixture
def todo(tmp_path):
    return TodoList(tmp_path / "tasks.json")


def test_add_assigns_incrementing_ids(todo):
    assert todo.add("one").id == 1
    assert todo.add("two").id == 2


def test_add_strips_whitespace(todo):
    assert todo.add("  buy milk  ").title == "buy milk"


def test_add_empty_title_fails(todo):
    with pytest.raises(ValueError):
        todo.add("   ")


def test_complete_and_reopen(todo):
    task = todo.add("x")
    assert todo.complete(task.id).done is True
    assert todo.reopen(task.id).done is False


def test_edit(todo):
    task = todo.add("old")
    assert todo.edit(task.id, "new").title == "new"
    with pytest.raises(ValueError):
        todo.edit(task.id, "")


def test_remove(todo):
    task = todo.add("x")
    todo.remove(task.id)
    assert todo.list() == []


def test_unknown_id_raises(todo):
    with pytest.raises(TaskNotFoundError):
        todo.complete(99)


def test_filters(todo):
    a, b = todo.add("a"), todo.add("b")
    todo.complete(a.id)
    assert [t.id for t in todo.list("done")] == [a.id]
    assert [t.id for t in todo.list("pending")] == [b.id]


def test_clear_done(todo):
    a, _ = todo.add("a"), todo.add("b")
    todo.complete(a.id)
    assert todo.clear_done() == 1
    assert len(todo.list()) == 1


def test_data_persists_between_instances(tmp_path):
    path = tmp_path / "sub" / "tasks.json"
    TodoList(path).add("saved")
    assert [t.title for t in TodoList(path).list()] == ["saved"]


def test_corrupted_file_raises_value_error(tmp_path):
    path = tmp_path / "tasks.json"
    path.write_text("{not json", encoding="utf-8")
    with pytest.raises(ValueError):
        TodoList(path)


def test_file_is_valid_json(tmp_path):
    path = tmp_path / "tasks.json"
    TodoList(path).add("x")
    assert json.loads(path.read_text())[0]["title"] == "x"
