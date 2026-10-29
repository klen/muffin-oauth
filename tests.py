# ruff: noqa: S105 (test tokens are not secrets)
from unittest import mock

import muffin
import pytest
from yarl import URL


@pytest.fixture
def app():
    import muffin_oauth

    app = muffin.Application(
        DEBUG=True,
        OAUTH_CLIENTS={
            "github": {
                "client_id": "b6281b6fe88fa4c313e6",
                "client_secret": "21ff23d9f1cad775daee6a38d230e1ee05b04f7c",
                "scope": "user:email",
            },
        },
    )

    oauth = muffin_oauth.Plugin(app)

    @app.route("/github")
    async def auth(request):
        client, _token, _data = await oauth.login("github", request)
        return await client.request("GET", "/user")

    return app


def test_client(app):
    from aioauth_client import GithubClient

    from muffin_oauth import OAuthError

    oauth = app.plugins["oauth"]
    client = oauth.client("github")
    assert client
    assert isinstance(client, GithubClient)

    with pytest.raises(OAuthError):
        oauth.client("google")

    with pytest.raises(OAuthError):
        oauth.client("unknown")


async def test_muffin_oauth(app, client):
    res = await client.get("/github", follow_redirect=False)
    assert res.status_code == 307
    location = URL(res.headers["location"])
    assert location.host == "github.com"
    state = location.query.get("state")
    assert state

    res = await client.get("/github?code=000")
    assert res.status_code == 406

    with mock.patch("aioauth_client.OAuth2Client._request") as mocked:
        mocked.return_value = {"access_token": "test_passed"}
        res = await client.get(f"/github?code=000&state={state}")
        assert res.status_code == 200
        assert await res.json() == {"access_token": "test_passed"}


async def test_login_redirect_uri_fallback(app, client):
    """Without a configured redirect_uri the current URL (no query) is used."""
    res = await client.get("/github", follow_redirect=False)
    location = URL(res.headers["location"])
    assert location.query["redirect_uri"] == "http://localhost/github"


async def test_login_state_signature(app, client):
    res = await client.get("/github", follow_redirect=False)
    state = URL(res.headers["location"]).query["state"]

    # A locally signed state with another secret must be rejected
    res = await client.get(f"/github?code=000&state={state[:-4]}AAAA")
    assert res.status_code == 406

    res = await client.get("/github?code=000&state=unsigned")
    assert res.status_code == 406


async def test_refresh(app):
    oauth = app.plugins["oauth"]
    with mock.patch("aioauth_client.OAuth2Client._request") as mocked:
        mocked.return_value = {"access_token": "refreshed"}
        token, data = await oauth.refresh("github", "refresh-token")

    assert token == "refreshed"
    assert data == {"access_token": "refreshed"}
    payload = mocked.call_args.kwargs["data"]
    assert payload["grant_type"] == "refresh_token"
    assert payload["refresh_token"] == "refresh-token"


def test_oauth1_is_not_supported():
    """OAuth1 clients are registered by aioauth-client but the plugin cannot drive them."""
    from aioauth_client import OAuth1Client

    import muffin_oauth

    app = muffin.Application(
        OAUTH_CLIENTS={"twitter": {"consumer_key": "key", "consumer_secret": "secret"}}
    )
    oauth = muffin_oauth.Plugin(app)
    client = oauth.client("twitter")
    assert isinstance(client, OAuth1Client)

    # No request token is exchanged, so the authorize URL carries oauth_token=None
    url = URL(oauth.authorize(client, "http://localhost/callback"))
    assert url.query["oauth_token"] == "None"


def test_config_from_env(monkeypatch):
    """Plugin options are read from <CFG.NAME>_OAUTH_* environment variables."""
    import muffin_oauth

    monkeypatch.setenv("MUFFIN_OAUTH_SECRET", "from-env")
    app = muffin.Application()
    oauth = muffin_oauth.Plugin(app)
    assert oauth.cfg.secret == "from-env"


async def test_client_options_are_sent_to_provider(app, client):
    res = await client.get("/github", follow_redirect=False)
    location = URL(res.headers["location"])
    assert location.query["client_id"] == "b6281b6fe88fa4c313e6"
    assert location.query["scope"] == "user:email"
