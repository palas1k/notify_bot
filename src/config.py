import os
from dataclasses import dataclass, field

from adaptix import Retort
from dynaconf import Dynaconf


@dataclass(slots=True)
class DatabaseConfig:
    host: str
    port: int
    username: str
    password: str
    database: str
    driver: str = 'postgresql+asyncpg'

    @property
    def dsn(self) -> str:
        return f'{self.driver}://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}'


@dataclass(slots=True)
class LoggingConfig:
    level: str
    human_readable_logs: bool = True


@dataclass(slots=True)
class RedisConfig:
    host: str
    port: int
    username: str | None
    password: str | None
    database: str = 0
    driver: str = 'redis'

    @property
    def dsn(self, database: str | None = None) -> str:
        if self.username is None and self.password is None:
            return f'{self.host}:{self.port}/{self.database}'
        return f'{self.driver}://{self.username}:{self.password}@{self.host}:{self.port}/{database or self.database}'


@dataclass(slots=True)
class TelegramConfig:
    token: str
    fsm_storage_database: str = '1'


@dataclass(slots=True)
class Config:
    database: DatabaseConfig
    logging: LoggingConfig
    redis: RedisConfig
    telegram: TelegramConfig


def get_config() -> Config:
    dynaconf = Dynaconf(
        envvar_prefix='UM',
        settings_file=[os.getenv('CONFIG_PATH')],
        load_dotenv=True,
    )
    retort = Retort()

    return retort.load(dynaconf, Config)
