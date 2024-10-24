from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class UserModelSchema:
    id: int
    name: str
    last_name: str
    telegram_id: str
