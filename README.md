# todo-cli

A simple command-line task manager built with [Typer](https://typer.tiangolo.com/) and [SQLModel](https://sqlmodel.tiangolo.com/).

## Storage

All data lives in `~/.todo-cli`:

- `todo.db` — the SQLite database
- `version.txt` — the schema version, used to apply migrations on upgrade

The directory and database are created automatically on first run. When you
upgrade the tool, pending schema migrations are applied automatically based on
`version.txt`.

## Installation

Install globally with [pipx](https://pipx.pypa.io/) (recommended — isolated
environment, `todo` available everywhere):

```bash
pipx install git+https://github.com/dm1tryG/todo-cli.git
```

Or from a local clone:

```bash
git clone https://github.com/dm1tryG/todo-cli.git
pipx install ./todo-cli
```

Make sure `~/.local/bin` is on your `PATH` (run `pipx ensurepath` if not).

To upgrade later:

```bash
pipx reinstall todo-cli
```

## Usage

Every command has a `--help` flag with a full description of its arguments and
options.

```bash
todo --help
todo add --help
```

### Create a task

```bash
todo add "Buy milk"
todo add "Write report" -d "Quarterly numbers for Q2" -p high
```

A task is created with status `open` and the current date/time as its creation
date. Priority is one of `low`, `medium`, `high` (default `medium`).

### List tasks

```bash
todo list                  # open tasks only
todo list --all            # include done tasks
todo list --status done    # filter by status
todo list --priority high  # filter by priority
```

### Show a task

```bash
todo show 1
```

### Close a task

```bash
todo close 1
```

Sets the status to `done` and records the close date/time.

### Edit a task

```bash
todo edit 1 --title "Buy oat milk"
todo edit 1 -d "New description" -p low
todo edit 1 --status open
```

Only the fields you pass are changed; everything else is left as-is.

### Delete a task

```bash
todo delete 1        # asks for confirmation
todo delete 1 --yes  # skip confirmation
```

Deletion is permanent. Use `close` instead if you just want to mark a task as
finished.

## Commands

| Command  | Description                                              |
| -------- | -------------------------------------------------------- |
| `add`    | Create a new task.                                       |
| `list`   | List tasks (open only by default).                       |
| `show`   | Show the full details of a single task.                  |
| `close`  | Mark a task as done.                                     |
| `edit`   | Change a task's title, description, priority, or status. |
| `delete` | Permanently delete a task.                               |

## Task fields

| Field         | Description                                  |
| ------------- | -------------------------------------------- |
| `id`          | Auto-incrementing identifier.                |
| `title`       | Short title of the task.                     |
| `description` | Longer notes (optional).                     |
| `priority`    | `low`, `medium`, or `high`.                  |
| `status`      | `open` or `done`.                            |
| `created_at`  | When the task was created.                   |
| `closed_at`   | When the task was closed (if done).          |
