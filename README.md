# todo-gui

A simple desktop to-do list written in Python with Tkinter (no extra dependencies).
Tasks are saved as JSON in `~/.todo-gui/tasks.json` (override with the `TODO_FILE` environment variable).

## Setup

Tkinter ships with Python on Windows and macOS. On Linux you may need:
`sudo apt install python3-tk`

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

## Run

```bash
python -m todo_gui
```

- Type a task and press Enter (or click **Add task**)
- Double-click a task, or press Space, to mark it done / not done
- **Edit**, **Delete** (or the Delete key) and **Clear completed** work on the selected task
- The **All / To do / Done** buttons filter the list

## Test

```bash
pytest -v
```

The window test is skipped automatically if no display is available.

## Optional: build a standalone app

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name todo-gui todo_gui/__main__.py
# result: dist/todo-gui (or dist/todo-gui.exe on Windows)
```

## Project layout

```
todo_gui/core.py   task logic + JSON storage
todo_gui/app.py    Tkinter window
tests/             pytest tests
.github/workflows/ runs the tests on every push
```
