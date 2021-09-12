import time
import asyncio
from datetime import datetime

from aiohttp import ClientTimeout
from pydantic import BaseModel, Field
from influxdb.line_protocol import make_line

from shorts import config


async def metrics_consumer(redis, http):
    datalines = []
    last_sent = time.time()
    while True:
        try:
            if dataline := await redis.rpop(config.REDIS_METRICS_QUEUE):
                datalines.append(dataline.decode())
            else:
                await asyncio.sleep(1)

            enough_collected = len(datalines) > config.METRICS_BATCH_SIZE
            time_to_send_anyway = time.time() - last_sent > config.METRICS_BATCH_INTERVAL
            if enough_collected or time_to_send_anyway:
                await send_metrics(datalines, http)
                datalines = []
                last_sent = time.time()

        except asyncio.CancelledError:
            await send_metrics(datalines, http)
            break
        except Exception as e:
            print('Something went wrong', e)


async def send_metrics(datalines, http):
    if not datalines:
        return

    if not all(config.INFLUXDB_CONFIG.values()):
        print('InfluxDB not configured')
        return

    cfg = config.INFLUXDB_CONFIG
    params = {
        'db': cfg['database'], 'u': cfg['username'], 'p': cfg['password']
    }
    url = f'http://{cfg["host"]}:{cfg["port"]}/write'
    data = '\n'.join(datalines) + '\n'
    try:
        async with http.post(url, params=params, data=data, timeout=ClientTimeout(total=5)) as response:
            response.raise_for_status()
    except Exception as e:
        print('Something went wrong:', e)


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


class Request(BaseModel):
    path: str
    request_id: str
    measurement = 'requests'
    time_str: datetime = Field(default_factory=metric_timestamp)

    @property
    def fields(self):
        return {'request_id': self.request_id}

    @property
    def tags(self):
        return {'path': self.path}


class Response(BaseModel):
    status: int
    request_path: str
    request_id: str
    time_used_ms: int
    measurement = 'responses'
    time_str: datetime = Field(default_factory=metric_timestamp)

    @property
    def fields(self):
        return {
            'request_id': self.request_id,
            'time_used_ms': self.time_used_ms
        }

    @property
    def tags(self):
        return {
            'status': self.status,
            'path': self.request_path
        }
