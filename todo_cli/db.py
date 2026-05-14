"""Database setup, storage location, and schema migrations.

All data lives in ~/.todo-cli:
  - todo.db      the SQLite database
  - version.txt  the schema version, used to apply migrations on upgrade
"""

from pathlib import Path

from sqlmodel import SQLModel, create_engine

from todo_cli import models  # noqa: F401  (ensures Task is registered on metadata)

DATA_DIR = Path.home() / ".todo-cli"
DB_PATH = DATA_DIR / "todo.db"
VERSION_PATH = DATA_DIR / "version.txt"

# Bump this whenever the schema changes, and add a matching entry to MIGRATIONS.
SCHEMA_VERSION = 1

engine = create_engine(f"sqlite:///{DB_PATH}")


def _migration_1(conn) -> None:
    """Baseline schema — created by SQLModel.metadata.create_all, nothing to do."""


# Map of target version -> function that upgrades the DB *to* that version.
# Example for a future change:
#   def _migration_2(conn):
#       conn.execute(text("ALTER TABLE task ADD COLUMN due_date DATETIME"))
#   MIGRATIONS = {1: _migration_1, 2: _migration_2}
MIGRATIONS = {1: _migration_1}


def _read_version() -> int:
    if VERSION_PATH.exists():
        try:
            return int(VERSION_PATH.read_text().strip())
        except ValueError:
            return 0
    return 0


def _write_version(version: int) -> None:
    VERSION_PATH.write_text(str(version))


def init_db() -> None:
    """Ensure the data directory, database, and schema are ready to use.

    Runs on every command. Creates the DB on first use and applies any
    pending migrations when upgrading to a newer version of the tool.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    fresh = not DB_PATH.exists()

    SQLModel.metadata.create_all(engine)

    if fresh:
        _write_version(SCHEMA_VERSION)
        return

    current = _read_version()
    if current < SCHEMA_VERSION:
        with engine.begin() as conn:
            for version in range(current + 1, SCHEMA_VERSION + 1):
                migrate = MIGRATIONS.get(version)
                if migrate is not None:
                    migrate(conn)
        _write_version(SCHEMA_VERSION)
