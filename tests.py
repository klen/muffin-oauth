import pytest
import muffin


@pytest.fixture(scope='session')
def app():
    app = muffin.Application(
        'oauth',
        PLUGINS=['muffin_session', 'muffin_oauth'],
        OAUTH_CLIENTS={
            'github': {
                'client_id': 'b6281b6fe88fa4c313e6',
                'client_secret': '21ff23d9f1cad775daee6a38d230e1ee05b04f7c',
                'params': {
                    'scope': 'user:email'
                }
            }
        }
    )

    @app.register('/github')
    async def auth(request):
        client = await app.ps.oauth.login('github', request)
        response = await client.request('GET', '/user')
        data = await response.json()
        return data

    return app


async def test_muffin_oauth(client):
    async with client.get('/github', allow_redirects=False) as resp:
        assert resp.status == 302
        assert resp.headers['location'].startswith('https://github.com/login/oauth')

    async with client.get('/github?code=000') as resp:
        assert resp.status == 403
        text = await resp.text()
        assert 'Invalid token' in text
