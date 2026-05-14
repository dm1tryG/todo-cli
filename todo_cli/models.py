from datetime import datetime
from enum import Enum

from sqlmodel import Field, SQLModel


class Priority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class Status(str, Enum):
    open = "open"
    done = "done"


class Task(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    description: str = ""
    priority: Priority = Field(default=Priority.medium)
    status: Status = Field(default=Status.open)
    created_at: datetime = Field(default_factory=datetime.now)
    closed_at: datetime | None = Field(default=None)
