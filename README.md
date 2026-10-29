# Muffin-OAuth

**Muffin-OAuth** adds OAuth **2** authorization to the [Muffin][muffin] framework on top of
[aioauth-client][aioauth-client]. It builds authorization URLs, keeps the `state` parameter
tamper-proof with an HMAC signature, exchanges the authorization code for an access token and
gives you a ready-to-use API client.

[Read the documentation](https://klen.github.io/muffin-oauth/) for configuration, security
details and the full API reference.

[![Documentation](https://img.shields.io/badge/docs-read%20online-blue)](https://klen.github.io/muffin-oauth/)
[![Tests Status](https://github.com/klen/muffin-oauth/workflows/tests/badge.svg)](https://github.com/klen/muffin-oauth/actions)
[![PyPI Version](https://img.shields.io/pypi/v/muffin-oauth)](https://pypi.org/project/muffin-oauth/)
[![Python Versions](https://img.shields.io/pypi/pyversions/muffin-oauth)](https://pypi.org/project/muffin-oauth/)

## Requirements

- Python 3.11 - 3.15
- Muffin >= 3
- Works with `asyncio`, `Trio` and `Curio`

## Install

```bash
pip install muffin-oauth
```

The example application also needs `uvicorn`:

```bash
pip install "muffin-oauth[uvicorn]"
```

## Quickstart

The same route starts the flow and finishes it. Without a `code` query argument `login()`
raises `ResponseRedirect` (Muffin answers `307`) to the provider. The provider sends the user
back to `redirect_uri` with `code` and `state`, and the second call exchanges the code for a
token.

```python
import muffin
from muffin_oauth import OAuthPlugin

app = muffin.Application(
    "myapp",
    OAUTH_CLIENTS={
        "github": {
            "client_id": "...",
            "client_secret": "...",
            "scope": "user:email",
        },
    },
    OAUTH_REDIRECT_URI="http://localhost:8000/login",
)
oauth = OAuthPlugin(app)


@app.route("/login")
async def login(request):
    # First visit: redirect to GitHub. Callback: validate state, get the token.
    client, token, data = await oauth.login("github", request)

    user = await client.request("GET", "/user")
    return {"login": user["login"], "token": token}
```

Run it and open <http://localhost:8000/login>:

```bash
uvicorn myapp:app --port 8000
```

## Configuration

| Option         | Default                        | Description                                             |
| -------------- | ------------------------------ | ------------------------------------------------------- |
| `clients`      | `{}`                           | Provider name → `aioauth-client` client options         |
| `redirect_uri` | `None`                         | Callback URL; falls back to the current URL without query |
| `secret`       | `important:replace_me_asap!`   | HMAC key for the `state` signature — change it in production |

Options are read from the application config with the `OAUTH_` prefix
(`OAUTH_CLIENTS`, `OAUTH_REDIRECT_URI`, `OAUTH_SECRET`), or from environment variables with the
`{CFG.NAME}_OAUTH_` prefix — `MUFFIN_OAUTH_SECRET` by default, JSON is parsed for complex values:

```bash
export MUFFIN_OAUTH_SECRET=change-me
export MUFFIN_OAUTH_CLIENTS='{"github": {"client_id": "...", "client_secret": "..."}}'
```

`clients` keys are the names registered by `aioauth-client` (for example `github`, `google`,
`vk`, `yandex`, `gitlab`, `discord`). Every other key of a client entry is passed to its
constructor and ends up in the authorization URL: `scope`, `allow_signup`, `access_type`, ...

## API

| Method                                                     | Returns                       | Description                                     |
| ---------------------------------------------------------- | ----------------------------- | ----------------------------------------------- |
| `client(name, **params)`                                   | `aioauth_client.Client`       | Create a configured provider client             |
| `authorize(client, redirect_uri=None, **params)`           | `str`                         | Build the authorization URL with a signed `state` |
| `login(name, request, redirect_uri=None, headers=None, **params)` | `(client, token, data)` | Redirect or exchange the code for a token        |
| `refresh(name, refresh_token, **params)`                   | `await (token, data)`         | Exchange a refresh token for a new access token  |

`login()` returns the client with `access_token` already set, the access token and the raw
provider response. See the [API reference](https://klen.github.io/muffin-oauth/api/) for
arguments and return values.

## Security

- `state` is `<random token>.<base64url HMAC-SHA512 of that token with secret>`; a missing or altered signature
  answers `406 Not Acceptable` and the code is never exchanged.
- Set your own `secret`. The default value is public and lets anyone forge a `state`.
- Without `redirect_uri` the plugin uses the current request URL without its query string, so the
  provider must be registered with that exact URL.

## Errors

| Error                                      | When                                                     |
| ------------------------------------------ | -------------------------------------------------------- |
| `OAuthError`                               | Client is not configured, unknown, or OAuth1             |
| `ResponseError.BAD_REQUEST` (`400`)        | The provider reported an error (user denied the app)     |
| `ResponseError.NOT_ACCEPTABLE` (`406`)     | `state` is missing or its signature does not match       |

## OAuth 2 only

The plugin drives OAuth2 authorization-code flows. OAuth1 providers (`twitter`, `tumblr`,
`flickr`, ...) are registered by `aioauth-client`, but `client()` rejects them with `OAuthError`
because the plugin only looks for the OAuth2 `code` query argument. Use `aioauth_client`
directly for OAuth1.

## Example

[`example.py`](https://github.com/klen/muffin-oauth/blob/develop/example.py) is a working
application with GitHub and Google login and user info rendering:

```bash
uv run --group example uvicorn example:app --port 5000
```

## License

Licensed under the [MIT license](http://opensource.org/licenses/MIT).

[muffin]: https://github.com/klen/muffin
[aioauth-client]: https://github.com/klen/aioauth-client
