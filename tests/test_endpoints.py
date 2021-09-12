import re
from unittest.mock import patch


async def test_healthcheck(client):
    response = await client.get('/health')
    assert response.status == 200


async def test_unexpected_exception(client):
    with patch('shorts.handlers.web.Response') as mocked_response:
        mocked_response.side_effect = Exception('oops')
        response = await client.get('/')

    assert response.status == 500
    assert await response.json() == {'error': 'unexpected error'}


async def test_ui(client):
    response = await client.get('/')
    assert response.status == 200
    assert '<title>URL Shorts</title>' in await response.text()


async def test_shorten_url(client, test_redis, test_pg):
    long_url = 'http://hello.there'
    response = await client.post('/shorten', json={'url': long_url})
    assert response.status == 200
    short_url = (await response.json())['short_url']
    assert re.match(r'http://localhost:8000/s/\w{7}$', short_url)

    short_id = short_url.split('/')[-1]
    assert long_url == (await test_redis.get(short_id)).decode()

    async with test_pg.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute('SELECT * FROM short_urls;')
            result = await cur.fetchone()

    _, db_short_id, db_url = result
    assert db_short_id == short_id
    assert db_url == long_url


async def test_id_not_found(client):
    response = await client.get('/s/no-such-id')
    assert response.status == 404


async def test_id_from_redis(client, test_redis):
    short_id = 'zxc'
    url = 'http://a.com'
    await test_redis.set(short_id, url)
    response = await client.get(f'/s/{short_id}', allow_redirects=False)
    assert response.status == 302
    assert response.headers['Location'] == url


async def test_id_from_db(client, test_redis, test_pg):
    short_id = 'abc'
    url = 'http://b.com'
    assert await test_redis.get(short_id) is None

    query = '''
        INSERT INTO short_urls(short_id, url)
        VALUES(%(short_id)s, %(url)s)
    '''
    query_params = {'short_id': short_id, 'url': url}
    async with test_pg.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(query, query_params)

    response = await client.get(f'/s/{short_id}', allow_redirects=False)
    assert response.status == 302
    assert response.headers['Location'] == url
