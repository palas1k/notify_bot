from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class TaskModelSchema:
    id: int
    created_at: Any
    text: str
    sent: bool
    date: Any
    counter: int
