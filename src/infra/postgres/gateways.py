from typing import Any

from adaptix import Retort
from sqlalchemy import delete, insert, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.errors import DatabaseError, NotFoundError, UniqueError
from src.application.schema.score_model import ScoreModelSchema
from src.application.schema.user_model import UserModelSchema
from src.infra.postgres.tables import BaseDBModel, UserModel, ScoreModel


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
        except DatabaseError as e:
            raise e


class UserGateway(BasePostgresGateway):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(
            retort=Retort(),
            session=session,
            table=UserModel
        )

    async def create(self,
                     name: str,
                     last_name: str,
                     telegram_id: str) -> UserModelSchema:
        stmt = (
            insert(UserModel)
            .values(
                name=name,
                last_name=last_name,
                telegram_id=telegram_id
            )
            .returning(*UserModel.group_by_fields())
        )
        try:
            result = (await self.session.execute(stmt)).mappings().first()
            if result is None:
                raise DatabaseError
            return self.retort.load(result, UserModelSchema)
        except DatabaseError as e:
            raise e

    async def get_user_by_telegram_id(self,
                                      telegram_id: str) -> UserModelSchema:
        stmt = (
            select(*UserModel.group_by_fields())
            .where(UserModel.telegram_id == telegram_id)
        )
        result = (await self.session.execute(stmt)).mappings().first()
        if result is None:
            raise NotFoundError(model_name='user')
        else:
            return self.retort.load(result, UserModelSchema)


class ScoreGateway(BasePostgresGateway):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(
            retort=Retort(),
            session=session,
            table=ScoreModel
        )

    async def create(self, telegram_id: str) -> ScoreModelSchema:
        stmt = (
            insert(ScoreModel)
            .values(
                telegram_id=telegram_id)
        ).returning(*ScoreModel.group_by_fields())

        try:
            result = (await self.session.execute(stmt)).mappings().first()
            if result is None:
                raise UniqueError(model_name='score')
            return self.retort.load(result, ScoreModelSchema)
        except IntegrityError as e:
            raise DatabaseError(message=str(e.orig)) from e

    async def get_by_telegram_id(self, telegram_id: str) -> ScoreModelSchema:
        stmt = (
            select(*ScoreModel.group_by_fields())
            .where(ScoreModel.telegram_id == telegram_id)
        )
        result = (await self.session.execute(stmt)).mappings().first()
        if result is None:
            raise NotFoundError(model_name='score')
        else:
            return self.retort.load(result, ScoreModelSchema)

    async def update(self, telegram_id: str, data: dict[str, Any]) -> ScoreModelSchema:
        stmt = (
            update(ScoreModel)
            .where(ScoreModel.telegram_id == telegram_id)
            .values(**data)
            .returning(*ScoreModel.group_by_fields())
        )

        try:
            result = (await self.session.execute(stmt)).mappings().first()
            if result is None:
                raise NotFoundError(model_name='score')
        except IntegrityError as e:
            raise DatabaseError(message=str(e.orig)) from e
        return self.retort.load(result, ScoreModelSchema)
