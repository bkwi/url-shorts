import asyncio

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


async def http_client(app):
    app['http'] = ClientSession()
    yield
    await app['http'].close()


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
        http_client,
        background_tasks
    ])

    app.router.add_routes([
        web.get('/health', handlers.healthcheck),
        web.post('/shorten', handlers.shorten)
    ])

    return app
