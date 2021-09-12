import aiopg
import pytest
from aioredis import create_redis_pool
from aioresponses import aioresponses

from shorts import config
from shorts.app import create_app

pytest_plugins = 'aiohttp.pytest_plugin'


@pytest.fixture(autouse=True)
async def test_redis():
    redis = await create_redis_pool(
        f'redis://{config.REDIS_HOST}:{config.REDIS_PORT}'
    )
    await redis.flushall()
    yield redis
    redis.close()
    await redis.wait_closed()


@pytest.fixture(autouse=True)
async def test_pg():
    postgres = await aiopg.create_pool(config.POSTGRES_URI)
    async with postgres.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute('DELETE FROM short_urls;')
    yield postgres
    postgres.close()
    await postgres.wait_closed()


@pytest.fixture
def aiomock():
    with aioresponses(passthrough=['http://127.0.0.1']) as m:
        yield m


@pytest.fixture()
async def client(aiohttp_client, loop):
    client = await aiohttp_client(await create_app())
    yield client
