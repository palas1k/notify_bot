from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class TaskModelSchema:
    id: int
    text: str
    sended: bool
    date: Any
    counter: int
