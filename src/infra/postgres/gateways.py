from adaptix import Retort
from loguru import logger
from sqlalchemy import delete, insert, update, select
from sqlalchemy.exc import DatabaseError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from datetime import date

from src.application.schema.task_model import TaskModelSchema
from src.infra.postgres.tables import BaseDBModel, TaskModel


class BasePostgresGateway:
    def __init__(self, retort: Retort, session: AsyncSession, table: type[BaseDBModel]) -> None:
        self.retort = retort
        self.session = session
        self.table = table

    async def delete_by_id(self, entity_id: int | str) -> int | str:
        stmt = delete(self.table).where(self.table.id == int(entity_id))

        try:
            result = await self.session.execute(stmt)
            if result.rowcount != 1:
                raise f"{str(DatabaseError)} {self.table} not found!"
            return entity_id
        except IntegrityError as e:
            raise e


class TaskGateway(BasePostgresGateway):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(
            retort=Retort(),
            session=session,
            table=TaskModel
        )

    async def create_task(self,
                          text: str,
                          day: date) -> list[TaskModelSchema]:
        stmt = (
            insert(TaskModel)
            .values(
                text=text,
                date=day,
                counter=1,
            )
            .returning(TaskModel.text,
                       TaskModel.date,
                       TaskModel.sended,
                       TaskModel.id,
                       TaskModel.counter)
        )
        try:
            result = (await self.session.execute(stmt)).mappings().first()
            logger.info(result)
            if result is None:
                raise DatabaseError
            return self.retort.load([result], list[TaskModelSchema])
        except IntegrityError as e:
            raise e

    async def update_task_status(self,
                                 task_id: int, ) -> int | str:
        stmt = (
            update(TaskModel)
            .where(TaskModel.id == int(task_id))
            .values(sended=True)
        )
        try:
            result = await self.session.execute(stmt)
            if result.rowcount != 1:
                raise DatabaseError
            return task_id
        except IntegrityError as e:
            raise e

    async def get_all_tasks(self) -> list[TaskModelSchema]:
        stmt = (
            select(TaskModel)
            .where(TaskModel.sended == False)
            .with_only_columns(TaskModel.id,
                               TaskModel.text,
                               TaskModel.sended,
                               TaskModel.date,
                               TaskModel.counter)
        )

        result = (await self.session.execute(stmt)).mappings().fetchall()
        return self.retort.load(result, list[TaskModelSchema]) if len(result) > 0 else []

    async def get_today_task(self) -> list[TaskModelSchema]:
        stmt = (
            select(TaskModel)
            .where(TaskModel.sended == False, TaskModel.date == date.today())
            .with_only_columns(TaskModel.id,
                               TaskModel.text,
                               TaskModel.sended,
                               TaskModel.date,
                               TaskModel.counter)
        )

        result = (await self.session.execute(stmt)).mappings().fetchall()
        return self.retort.load(result, list[TaskModelSchema]) if len(result) > 0 else []

    async def update_task_counter(self, task_id: int):
        stmt = (
            update(TaskModel)
            .where(TaskModel.id == int(task_id))
            .values(counter=TaskModel.counter + 1)
        )
        try:
            result = await self.session.execute(stmt)
            if result.rowcount != 1:
                raise DatabaseError
            return task_id
        except IntegrityError as e:
            raise e
