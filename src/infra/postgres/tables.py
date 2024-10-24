from datetime import datetime, date
from typing import Any

from sqlalchemy import func, CheckConstraint, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase

from src.infra.postgres.utils import integer_id, default_dict


class BaseDBModel(DeclarativeBase):
    __tablename__: Any
    __table_args__ = {'schema': 'ege_schema'}

    @classmethod
    def group_by_fields(cls, exclude: list[str] | None = None) -> list:
        """Берем имена всех колонок для группировки.

        Args:
            exclude: list[str] | None исключаемые поля

        Returns:
            list[колонка]
        """

        payload = []
        if not exclude:
            exclude = []

        for column in cls.__table__.columns:
            if column.key in exclude:
                continue

            payload.append(column)

        return payload


class UserModel(BaseDBModel):
    __tablename__ = "user"
    id: Mapped[integer_id]
    name: Mapped[str] = mapped_column(String(30))
    last_name: Mapped[str] = mapped_column(String(30))
    telegram_id: Mapped[str] = mapped_column()


class ScoreModel(BaseDBModel):
    __tablename__ = "score"
    id: Mapped[integer_id]
    telegram_id: Mapped[str] = mapped_column(unique=True)
    scores: Mapped[dict] = mapped_column(JSONB, default=default_dict)
