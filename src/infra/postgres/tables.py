from datetime import datetime, date
from typing import Any

from sqlalchemy import func, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, declarative_base

from src.infra.postgres.utils import integer_id

Base = declarative_base()


class BaseDBModel(Base):
    __abstract__ = True
    __tablename__ : Any
    __table_args__ = {'schema': 'tasks_schema'}


class TaskModel(BaseDBModel):
    __tablename__ = "tasks"
    __table_args__ = {'schema': 'tasks_schema'},
    CheckConstraint('counter >= 0 AND counter <= 4', 'ck_counter_range')

    id: Mapped[integer_id]
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
    text: Mapped[str] = mapped_column(nullable=False)
    sended: Mapped[bool] = mapped_column(default=False)
    date: Mapped[datetime] = mapped_column(nullable=False)
    counter: Mapped[int] = mapped_column(default=0)
