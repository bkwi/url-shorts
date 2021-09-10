import time
import asyncio
from datetime import datetime

from pydantic import BaseModel, Field
from influxdb.line_protocol import make_line

from shorts import config


async def metrics_consumer(redis, http):
    datalines = []
    last_sent = time.time()
    while True:
        try:
            dataline = await redis.rpop(config.REDIS_METRICS_QUEUE)

            if dataline:
                datalines.append(dataline)
            else:
                await asyncio.sleep(1)

            enough_collected = len(datalines) > 10
            time_to_send_anyway = time.time() - last_sent > 10
            if enough_collected or time_to_send_anyway:
                await send_metrics(datalines, http)
                datalines = []
                last_sent = time.time()

        except asyncio.CancelledError:
            await send_metrics(datalines, http)
            break


async def send_metrics(datalines, http):
    if not datalines:
        return

    print('SEND DATALINES', datalines)


def metric_timestamp():
    return datetime.utcnow().isoformat(timespec='microseconds') + 'Z'


async def add(metric_item, redis):
    dataline = make_line(
        metric_item.measurement,
        tags=metric_item.tags,
        fields=metric_item.fields,
        time=metric_item.time_str
    )
    await redis.lpush(config.REDIS_METRICS_QUEUE, dataline)


class Metric(BaseModel):
    time_str: datetime = Field(default_factory=metric_timestamp)


class Request(Metric):
    path: str
    request_id: str
    measurement = 'requests'

    @property
    def fields(self):
        return {
            'path': self.path
        }

    @property
    def tags(self):
        return {
            'request_id': self.request_id
        }
