import asyncio

import aiopg
from aiohttp import web, ClientSession
from aioredis import create_redis_pool

from shorts import config, handlers, middlewares, metrics


async def setup_redis(app):
    app['redis'] = await create_redis_pool(
        f'redis://{config.REDIS_HOST}:{config.REDIS_PORT}'
    )
    yield
    app['redis'].close()
    await app['redis'].wait_closed()


async def setup_postgres(app):
    app['postgres'] = await aiopg.create_pool(config.POSTGRES_URI)
    yield
    app['postgres'].close()
    await app['postgres'].wait_closed()


async def http_client(app):
    app['http'] = ClientSession()
    yield
    await app['http'].close()


async def main_html(app):
    with open('/app/shorts/html/index.html') as f:
        app['main_html'] = f.read()
    yield


async def background_tasks(app):
    loop = asyncio.get_event_loop()
    tasks = [
        loop.create_task(metrics.metrics_consumer(app['redis'], app['http']))
    ]
    yield
    for task in tasks:
        task.cancel()


async def create_app():
    app = web.Application(
        middlewares=[
            middlewares.metrics_middleware,
            middlewares.exception_middleware
        ]
    )

    app.cleanup_ctx.extend([
        setup_redis,
        setup_postgres,
        http_client,
        main_html,
        background_tasks
    ])

    app.router.add_routes([
        web.get('/', handlers.ui),
        web.get('/health', handlers.healthcheck),
        web.get('/r/{short_id}', handlers.resolve),
        web.post('/shorten', handlers.shorten)
    ])

    return app
