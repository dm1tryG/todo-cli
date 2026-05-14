"""todo — a simple command-line task manager."""

from datetime import datetime

import typer
from rich.console import Console
from rich.table import Table
from sqlmodel import Session, select

from todo_cli.db import DATA_DIR, init_db, engine
from todo_cli.models import Priority, Status, Task

app = typer.Typer(
    help="todo — a simple command-line task manager.\n\n"
    f"Tasks are stored in a SQLite database in {DATA_DIR}.",
    no_args_is_help=True,
    add_completion=False,
)
console = Console()

_PRIORITY_STYLE = {
    Priority.low: "dim",
    Priority.medium: "yellow",
    Priority.high: "bold red",
}


@app.callback()
def _main() -> None:
    """Initialise the database before running any command."""
    init_db()


def _get_task(session: Session, task_id: int) -> Task:
    task = session.get(Task, task_id)
    if task is None:
        console.print(f"[red]No task found with id {task_id}.[/red]")
        raise typer.Exit(code=1)
    return task


def _render_task(task: Task) -> None:
    console.print(f"[bold]#{task.id}  {task.title}[/bold]")
    console.print(f"  status      : {task.status.value}")
    console.print(
        f"  priority    : [{_PRIORITY_STYLE[task.priority]}]{task.priority.value}[/]"
    )
    console.print(f"  description : {task.description or '-'}")
    console.print(f"  created at  : {task.created_at:%Y-%m-%d %H:%M}")
    if task.closed_at:
        console.print(f"  closed at   : {task.closed_at:%Y-%m-%d %H:%M}")


@app.command()
def add(
    title: str = typer.Argument(..., help="Short title of the task."),
    description: str = typer.Option(
        "", "--description", "-d", help="Longer description or notes for the task."
    ),
    priority: Priority = typer.Option(
        Priority.medium, "--priority", "-p", help="Task priority: low, medium, or high."
    ),
) -> None:
    """Create a new task.

    The task is created with status 'open' and the current date/time as its
    creation date.
    """
    task = Task(title=title, description=description, priority=priority)
    with Session(engine) as session:
        session.add(task)
        session.commit()
        session.refresh(task)
        console.print(f"[green]Created task #{task.id}[/green]: {task.title}")


@app.command(name="list")
def list_tasks(
    show_all: bool = typer.Option(
        False, "--all", "-a", help="Include closed (done) tasks in the output."
    ),
    status: Status = typer.Option(
        None, "--status", "-s", help="Show only tasks with this status."
    ),
    priority: Priority = typer.Option(
        None, "--priority", "-p", help="Show only tasks with this priority."
    ),
) -> None:
    """List tasks.

    By default only open tasks are shown. Use --all to include done tasks,
    or filter explicitly with --status / --priority.
    """
    with Session(engine) as session:
        query = select(Task)
        if status is not None:
            query = query.where(Task.status == status)
        elif not show_all:
            query = query.where(Task.status == Status.open)
        if priority is not None:
            query = query.where(Task.priority == priority)
        query = query.order_by(Task.status, Task.created_at)
        tasks = session.exec(query).all()

    _priority_rank = {Priority.high: 0, Priority.medium: 1, Priority.low: 2}
    tasks.sort(key=lambda t: (t.status.value, _priority_rank[t.priority]))

    if not tasks:
        console.print("[dim]No tasks to show.[/dim]")
        return

    table = Table(show_lines=False)
    table.add_column("ID", justify="right")
    table.add_column("Title")
    table.add_column("Priority")
    table.add_column("Status")
    table.add_column("Created")
    for task in tasks:
        table.add_row(
            str(task.id),
            task.title,
            f"[{_PRIORITY_STYLE[task.priority]}]{task.priority.value}[/]",
            task.status.value,
            f"{task.created_at:%Y-%m-%d %H:%M}",
        )
    console.print(table)


@app.command()
def show(
    task_id: int = typer.Argument(..., help="ID of the task to display."),
) -> None:
    """Show the full details of a single task."""
    with Session(engine) as session:
        task = _get_task(session, task_id)
        _render_task(task)


@app.command()
def close(
    task_id: int = typer.Argument(..., help="ID of the task to mark as done."),
) -> None:
    """Mark a task as done.

    Sets the task status to 'done' and records the close date/time.
    """
    with Session(engine) as session:
        task = _get_task(session, task_id)
        if task.status == Status.done:
            console.print(f"[yellow]Task #{task_id} is already done.[/yellow]")
            raise typer.Exit()
        task.status = Status.done
        task.closed_at = datetime.now()
        session.add(task)
        session.commit()
        console.print(f"[green]Closed task #{task_id}[/green]: {task.title}")


@app.command()
def edit(
    task_id: int = typer.Argument(..., help="ID of the task to change."),
    title: str = typer.Option(None, "--title", "-t", help="New title."),
    description: str = typer.Option(
        None, "--description", "-d", help="New description."
    ),
    priority: Priority = typer.Option(
        None, "--priority", "-p", help="New priority: low, medium, or high."
    ),
    status: Status = typer.Option(
        None, "--status", "-s", help="New status: open or done."
    ),
) -> None:
    """Change a task's title, description, priority, or status.

    Only the fields you pass are modified; everything else is left as-is.
    """
    if all(v is None for v in (title, description, priority, status)):
        console.print("[yellow]Nothing to change — pass at least one option.[/yellow]")
        raise typer.Exit(code=1)

    with Session(engine) as session:
        task = _get_task(session, task_id)
        if title is not None:
            task.title = title
        if description is not None:
            task.description = description
        if priority is not None:
            task.priority = priority
        if status is not None:
            task.status = status
            task.closed_at = datetime.now() if status == Status.done else None
        session.add(task)
        session.commit()
        session.refresh(task)
        console.print(f"[green]Updated task #{task_id}.[/green]")
        _render_task(task)


@app.command()
def delete(
    task_id: int = typer.Argument(..., help="ID of the task to delete."),
    yes: bool = typer.Option(
        False, "--yes", "-y", help="Delete without asking for confirmation."
    ),
) -> None:
    """Permanently delete a task.

    This cannot be undone. Use 'close' instead if you just want to mark a
    task as finished.
    """
    with Session(engine) as session:
        task = _get_task(session, task_id)
        if not yes:
            typer.confirm(
                f"Delete task #{task_id} ({task.title})?", abort=True
            )
        session.delete(task)
        session.commit()
        console.print(f"[green]Deleted task #{task_id}.[/green]")


if __name__ == "__main__":
    app()
