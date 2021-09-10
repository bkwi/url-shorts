from aiohttp import web


async def healthcheck(request: web.Request) -> web.Response:
    return web.Response(text='OK')
