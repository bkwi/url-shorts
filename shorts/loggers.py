import sys
from datetime import datetime
from contextvars import ContextVar

from aiologger import Logger
from aiologger.handlers.streams import AsyncStreamHandler
from aiologger.formatters.base import Formatter
from aiologger.handlers.base import Handler
from aioredis import create_redis_pool
from influxdb.line_protocol import make_line

from shorts import config


class ShortsLogger(Logger):

    def setup(self, request_id):
        self.request_id = ContextVar('request_id', default=None)
        self.request_id.set(request_id)

    def _log(self, level, msg, *args, **kwargs):
        if req_id := self.request_id.get():
            msg = f'[{req_id}] {msg}'
        return super()._log(level, msg, *args, **kwargs)


class RedisHandler(Handler):
    def __init__(self, formatter=None):
        super().__init__()
        self.redis = None
        if formatter:
            self.formatter = formatter

    @property
    def initialized(self):
        return self.redis is not None

    async def close(self):
        self.redis.close()
        await self.redis.wait_closed()

    async def emit(self, record):
        if not self.initialized:
            self.redis = await create_redis_pool(
                f'redis://{config.REDIS_HOST}:{config.REDIS_PORT}'
            )
        msg = self.formatter.format(record)
        log_dataline = make_line(
            'app_logs',
            tags={'level': record.levelname},
            fields={'message': msg, 'details': 'what?'},
            time=datetime.fromtimestamp(record.created).isoformat(timespec='microseconds') + 'Z'
        )
        await self.redis.lpush(config.REDIS_METRICS_QUEUE, log_dataline)


logger = ShortsLogger(name='shorts')
formatter = Formatter(
    '%(asctime)s - %(levelname)s -- %(name)s[%(process)d] :: %(message)s'
)
logger.add_handler(AsyncStreamHandler(stream=sys.stdout, formatter=formatter))
logger.add_handler(RedisHandler(formatter=formatter))
