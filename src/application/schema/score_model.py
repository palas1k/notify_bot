from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class ScoreModelSchema:
    id: int
    telegram_id: str
    scores: dict
