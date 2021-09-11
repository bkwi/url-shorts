import re


async def test_healthcheck(client):
    response = await client.get('/health')
    assert response.status == 200


async def test_shorten_url(client):
    response = await client.post('/shorten', json={'url': 'http://abc.com'})
    assert response.status == 200
    short_url = (await response.json())['short_url']
    assert re.match(r'http://localhost:8000/s/\w{7}$', short_url)
