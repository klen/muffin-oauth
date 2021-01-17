from unittest import mock

import jwt
import muffin
import muffin_session
import pytest


@pytest.fixture(params=[
    pytest.param('asyncio'),
    pytest.param('trio'),
], autouse=True)
def anyio_backend(request):
    return request.param


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

    muffin_session.Plugin(app, secret_key='tests')
    oauth = muffin_oauth.Plugin(app)

    @app.route('/github')
    async def auth(request):
        client, (token, data) = await oauth.login('github', request)
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


async def test_muffin_oauth(client):
    res = await client.get('/github', allow_redirects=False)
    assert res.status_code == 307
    assert res.headers['location'].startswith('https://github.com/login/oauth')
    assert res.cookies['session']
    ses = jwt.decode(res.cookies['session'], options={'verify_signature': False})
    assert ses['muffin_oauth']
    assert ses['muffin_oauth'] in res.headers['location']

    res = await client.get('/github?code=000')
    assert res.status_code == 406

    ses = jwt.decode(client.cookies['session'].value, options={'verify_signature': False})
    state = ses['muffin_oauth']

    with mock.patch('aioauth_client.OAuth2Client._request') as mocked:
        mocked.return_value = {'access_token': 'test_passed'}
        res = await client.get('/github?code=000&state=%s' % state)
        assert res.status_code == 200
        assert res.json() == {'access_token': 'test_passed'}
