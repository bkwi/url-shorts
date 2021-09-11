import pytest


async def test_404(client):
    response = await client.get('/nothing-here')
    assert response.status == 404


@pytest.mark.parametrize('payload, exp_message', [
    (
        None, 'Could not read request payload'
    ),
    (
        {'a': 'b'}, 'url\n  field required'
    ),
    (
        {'url': 'x'}, 'invalid or missing URL scheme'
    )
])
async def test_invalid_shorten_payload(payload, exp_message, client):
    response = await client.post('/shorten', json=payload)
    assert response.status == 400
    resp_json = await response.json()
    assert exp_message in resp_json['error']
