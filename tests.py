import pytest
import muffin


@pytest.fixture(scope='session')
def app(loop):
    app = muffin.Application(
        'oauth', loop=loop,

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
    @app.ps.oauth.login('github')
    def auth(request, service):
        response = yield from service.request('GET', '/user')
        data = yield from response.json()
        return data

    return app


def test_muffin_oauth(client):

    response = client.get('/github')
    assert response.status_code == 302
    assert response.location.startswith('https://github.com/login/oauth')

    response = client.get('/github?code=000', status=403)
    assert 'Invalid token' in response.text
