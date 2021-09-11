from unittest.mock import patch

import pytest
import fakeredis.aioredis as fakeredis

from shorts.app import create_app

pytest_plugins = 'aiohttp.pytest_plugin'


@pytest.fixture()
async def client(aiohttp_client, loop):
    with patch('shorts.app.create_redis_pool') as create_pool:
        create_pool.return_value = await fakeredis.create_redis_pool()
        client = await aiohttp_client(await create_app())
        yield client
