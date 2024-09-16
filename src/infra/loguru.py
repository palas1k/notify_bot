import logging
import sys
import traceback
from datetime import datetime, UTC
from typing import Any

import orjson
from loguru import logger

from src.config import LoggingConfig


def setup_logging(config: LoggingConfig) -> None:
    def serialize_extra(record: Any) -> str:
        exception = record['exception']
        extra = record['extra']
        exc, exc_value, tb = (None, None, None)

        if exception:
            exc, exc_value, tb = exception

            if tb:
                tb = traceback.format_tb(tb)

        subset = {
            'level': record['level'].name,
            'message': record['message'],
            'additional_data': dict(extra),
            'datetime_uts': datetime.now(tz=UTC).strftime('%d.%m.%Y, %H:%M:%S'),
            'timestamp': record['time'].timestamp(),
            'exception': str(exc),
            'exc_value': str(exc_value),
            'traceback': tb,
        }
        return orjson.dumps(subset).decode('utf-8')

    def formatter(record: Any) -> str:
        record['extra']['serialized'] = serialize_extra(record)
        return '{extra[serialized]}\n'

    if not config.human_readable_logs:
        logger.add(sys.stdout, format=formatter, level=config.level)
