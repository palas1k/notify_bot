from collections.abc import AsyncIterable

from dishka import Provider, provide, Scope, provide_all
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, async_sessionmaker, AsyncSession

from src.config import Config
from src.infra.postgres.gateways import UserGateway, ScoreGateway


class DishkaProvider(Provider):
    def __init__(
            self,
            config: Config,
    ) -> None:
        self.config = config
        super().__init__()

    @provide(scope=Scope.APP)
    async def _get_engine(self) -> AsyncIterable[AsyncEngine]:
        engine: AsyncEngine | None = None
        try:
            if engine is None:
                engine = create_async_engine(self.config.database.dsn)

            yield engine
        except ConnectionRefusedError as e:
            logger.error('Error connecting to database', e)
        finally:
            if engine is not None:
                await engine.dispose()

    @provide(scope=Scope.APP)
    async def _get_session_maker(
            self, engine: AsyncEngine
    ) -> async_sessionmaker[AsyncSession]:
        return async_sessionmaker(engine, autoflush=False, expire_on_commit=False)

    @provide(scope=Scope.REQUEST)
    async def _get_session(
            self, session_maker: async_sessionmaker[AsyncSession]
    ) -> AsyncIterable[AsyncSession]:
        async with session_maker() as session:
            yield session

    _get_gateways = provide_all(
        UserGateway,
        ScoreGateway,
        scope=Scope.REQUEST
    )

    _get_usecases = provide_all(
        scope=Scope.REQUEST,
    )
