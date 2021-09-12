import uuid

from aiohttp import web

from shorts import schemas, config


async def healthcheck(request: web.Request) -> web.Response:
    return web.Response(text='OK')


@schemas.validate(schemas.ShortenRequest)
async def shorten(request: web.Request) -> web.Response:
    url = request['data'].url
    short_id = uuid.uuid4().hex[:config.SHORT_ID_LENGTH]
    await request.app['redis'].setex(short_id, 30, str(url))

    query = 'INSERT INTO short_urls(short_id, url) VALUES(%(short_id)s, %(url)s)'
    query_params = {'short_id': short_id, 'url': url}
    async with request.app['postgres'].acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(query, query_params)

    return web.json_response({'short_url': f'http://localhost:8000/s/{short_id}'})


async def resolve(request: web.Request) -> web.Response:
    short_id = request.match_info.get('short_id')
    url = await request.app['redis'].get(short_id)

    if url:
        url = url.decode()
    else:
        query = 'SELECT url FROM short_urls WHERE short_id = %(short_id)s'
        async with request.app['postgres'].acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, {'short_id': short_id})
                if result := await cur.fetchone():
                    url = result[0]
                else:
                    return web.Response(text='short id not matched', status=404)

    raise web.HTTPFound(url)
