import uuid

from aiohttp import web

from shorts import schemas


async def healthcheck(request: web.Request) -> web.Response:
    return web.Response(text='OK')


@schemas.validate(schemas.ShortenRequest)
async def shorten(request: web.Request) -> web.Response:
    url = request['data'].url
    short_id = uuid.uuid4().hex[:7]
    await request.app['redis'].setex(short_id, 30, str(url))
    return web.json_response({'short_url': f'http://localhost:8000/s/{short_id}'})


async def resolve(request: web.Request) -> web.Response:
    short_id = request.match_info.get('short_id')
    url = await request.app['redis'].get(short_id)

    if not url:
        return web.Response(text='short id not matched', status=404)

    raise web.HTTPFound(url.decode())
