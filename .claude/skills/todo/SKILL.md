---
name: todo
description: Manage personal tasks with the todo-cli tool — create, list, show, close, edit, and delete todo items. Use whenever the user wants to track, review, or update their todos.
---

# todo

`todo` is a command-line task manager installed globally on this machine.
Tasks are stored in a SQLite database at `~/.todo-cli`.

## How to use it

Run the `todo` CLI via Bash to fulfil the user's request.

**Do not guess command names, arguments, or flags.** Discover the exact
interface from the tool's own help output before running a command:

- `todo --help` — lists every available command and what it does.
- `todo <command> --help` — shows the arguments, options, and behaviour of a
  specific command.

Read the relevant `--help` output first, then construct the command that
matches what the user asked for. If a command needs a task id, run the list
command to find it.

## Notes

- All state lives in `~/.todo-cli` — no configuration is required.
- Deletion is permanent; prefer closing a task over deleting it unless the
  user explicitly asks to delete.
- When an action changes data (close, edit, delete), confirm back to the user
  what changed.
