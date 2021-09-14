import uuid

from aiohttp import web

from shorts import schemas, config, metrics
from shorts.loggers import logger


async def healthcheck(request: web.Request) -> web.Response:
    return web.Response(text='OK')


async def ui(request: web.Request) -> web.Response:
    return web.Response(text=request.app['main_html'], content_type='text/html')


@schemas.validate(schemas.ShortenRequest)
async def shorten(request: web.Request) -> web.Response:
    url = request['data'].url
    short_id = uuid.uuid4().hex[:config.SHORT_ID_LENGTH]
    await request.app['redis'].setex(short_id, config.CACHE_TTL, str(url))

    query = 'INSERT INTO short_urls(short_id, url) VALUES(%(short_id)s, %(url)s)'
    query_params = {'short_id': short_id, 'url': url}
    async with request.app['postgres'].acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(query, query_params)

    logger.info(f'Short id {short_id} now stores {url}')
    return web.json_response({'short_url': f'http://{config.APP_HOSTNAME}/r/{short_id}'})


async def resolve(request: web.Request) -> web.Response:
    short_id = request.match_info.get('short_id')
    url = await request.app['redis'].get(short_id)

    if url:
        cache = 'hit'
        url = url.decode()
    else:
        cache = 'miss'
        query = 'SELECT url FROM short_urls WHERE short_id = %(short_id)s'
        async with request.app['postgres'].acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, {'short_id': short_id})
                if result := await cur.fetchone():
                    url = result[0]
                else:
                    return web.Response(text='short id not matched', status=404)

    await metrics.add(
        metrics.URLCache(status=cache, short_id=short_id, request_id=request['id']),
        request.app['redis']
    )
    await request.app['redis'].setex(short_id, config.CACHE_TTL, url)
    return web.Response(status=302, headers={'Location': url})
