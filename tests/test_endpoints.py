

async def test_healthcheck(client):
    response = await client.get('/health')
    assert response.status == 200
