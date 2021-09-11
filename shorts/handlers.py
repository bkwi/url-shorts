from aiohttp import web

from shorts import schemas


async def healthcheck(request: web.Request) -> web.Response:
    return web.Response(text='OK')


@schemas.validate(schemas.ShortenRequest)
async def shorten(request: web.Request) -> web.Response:
    return web.json_response({'msg': 'ok'})
