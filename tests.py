from unittest import mock

import jwt
import muffin
import pytest
import sys
from yarl import URL


@pytest.fixture(params=[
    pytest.param('asyncio'),
    pytest.param('trio'),
], autouse=True)
def anyio_backend(request):
    return request.param


# XXX: python 3.7
def to_coro(value):
    async def coro():
        return value
    return coro()


@pytest.fixture
def app():
    import muffin_oauth

    app = muffin.Application('oauth', DEBUG=True, OAUTH_CLIENTS={
        'github': {
            'client_id': 'b6281b6fe88fa4c313e6',
            'client_secret': '21ff23d9f1cad775daee6a38d230e1ee05b04f7c',
            'params': {
                'scope': 'user:email'
            }
        }
    })

    oauth = muffin_oauth.Plugin(app)

    @app.route('/github')
    async def auth(request):
        client, token, data = await oauth.login('github', request)
        return await client.request('GET', '/user')

    return app


def test_client(app):
    from aioauth_client import GithubClient
    from muffin_oauth import OAuthException

    oauth = app.plugins['oauth']
    client = oauth.client('github')
    assert client
    assert isinstance(client, GithubClient)

    with pytest.raises(OAuthException):
        oauth.client('google')

    with pytest.raises(OAuthException):
        oauth.client('unknown')


async def test_muffin_oauth(app, client):
    from muffin_oauth import sign

    res = await client.get('/github', allow_redirects=False)
    assert res.status_code == 307
    location = URL(res.headers['location'])
    assert location.host == 'github.com'
    state = location.query.get('state')
    assert state

    res = await client.get('/github?code=000')
    assert res.status_code == 406

    with mock.patch('aioauth_client.OAuth2Client._request') as mocked:
        mocked.return_value = {'access_token': 'test_passed'}
        if sys.version_info < (3, 8):
            mocked.side_effect = [
                to_coro(mocked.return_value),
                to_coro(mocked.return_value),
            ]

        res = await client.get('/github?code=000&state=%s' % state)
        assert res.status_code == 200
        assert await res.json() == {'access_token': 'test_passed'}
