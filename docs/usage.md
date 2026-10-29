# Usage

## Setup

```python
import muffin
from muffin_oauth import OAuthPlugin

app = muffin.Application(
    "myapp",
    OAUTH_CLIENTS={
        "github": {"client_id": "...", "client_secret": "...", "scope": "user:email"},
    },
    OAUTH_REDIRECT_URI="http://localhost:8000/login",
)
oauth = OAuthPlugin(app)
```

`OAuthPlugin(app)` binds the application immediately and registers the plugin as
`app.plugins["oauth"]`. Without an application (`OAuthPlugin()`) the plugin is created
unbound; call `oauth.setup(app)` later.

Every key of a client entry except `client_id` and `client_secret` is passed to the
`aioauth-client` constructor (`scope`, `access_token_url`, `base_url`, `transport`, ...).
Constructor options that are not consumed by the client end up as query parameters of the
authorization URL, which is how `scope` reaches the provider.

## Login flow

`login()` does two things depending on the request:

1. **No `code` in the query** — it builds the authorization URL and raises
   `muffin.ResponseRedirect`. Muffin turns that into a `307` response, so the browser goes to
   the provider.
2. **`code` in the query** — it verifies `state`, exchanges the code, and returns
   `(client, token, data)`.

```python
from muffin import ResponseError

@app.route("/login")
async def login(request):
    try:
        client, token, data = await oauth.login("github", request)
    except ResponseError as exc:
        return exc  # invalid state (406)

    request.session["token"] = token
    user = await client.request("GET", "/user")
    return {"login": user["login"], "raw": data}
```

- `client` is the provider client with `access_token` already set, so `client.request(...)`
  and `client.user_info()` are authenticated.
- `token` is the access token string (empty when the provider returned no `access_token`).
- `data` is the raw provider response for the token request. Some providers put extra fields
  there (`refresh_token`, `expires_in`, `scope`).

### Separate callback route

If you prefer `/login` and `/callback` as two routes, pass the same `redirect_uri` to both and
register it at the provider:

```python
@app.route("/login")
async def login(request):
    return await oauth.login("github", request, redirect_uri="http://localhost:8000/callback")


@app.route("/callback")
async def callback(request):
    client, token, data = await oauth.login(
        "github", request, redirect_uri="http://localhost:8000/callback"
    )
    request.session["token"] = token
    return {"ok": True}
```

`redirect_uri` must be byte-identical in the authorization request and the token exchange,
otherwise the provider rejects the exchange. Keeping it in configuration
(`OAUTH_REDIRECT_URI`) is the safest option.

### Passing extra parameters

`login()` forwards `**params` to the authorization URL only:

```python
await oauth.login("github", request, allow_signup="false")
```

`headers` is forwarded to the token request instead, which is useful for providers that want
basic auth or a custom `Accept` header:

```python
await oauth.login("github", request, headers={"Accept": "application/json"})
```

## Refresh tokens

`refresh()` returns a coroutine of `(token, data)` from the token endpoint:

```python
token, data = await oauth.refresh("github", request.session["refresh_token"])
```

Extra `**params` go into the token request payload:

```python
token, data = await oauth.refresh("vk", refresh_token, scope="email")
```

The refreshed token is not stored anywhere — save it yourself, the plugin has no session.

## Calling the provider API

```python
client = oauth.client("github", access_token="...")
data = await client.request("GET", "/user")

user, raw = await client.user_info()  # when the client knows user_info_url
```

`oauth.client(name, **params)` merges `params` over the configured client entry, so a token
received elsewhere can be plugged in without touching the configuration.

## Building an authorization URL yourself

```python
client = oauth.client("github")
url = oauth.authorize(client, "http://localhost:8000/callback", scope="user:email")
return f'<a href="{url}">Login</a>'
```

`authorize()` only builds the URL; the `state` it adds is signed but not stored, so the
callback must still go through `login()` to be verified.

## Errors

| Situation                                    | Result                                  |
| -------------------------------------------- | --------------------------------------- |
| Client name is not in `OAUTH_CLIENTS`         | `OAuthError`                            |
| Client name is unknown to `aioauth-client`    | `OAuthError`                            |
| `state` is missing on the callback            | `ResponseError.NOT_ACCEPTABLE` (`406`)  |
| `state` signature does not match              | `ResponseError.NOT_ACCEPTABLE` (`406`)  |
| Provider reports an error (`error=...`)       | `ResponseError.BAD_REQUEST` (`400`)     |
| Provider rejects the code                     | `aioauth_client.OAuthError`             |

`OAuthError` from `muffin_oauth` is raised by `client()`, and therefore by `login()` and
`refresh()`, before any network call.

## Working example

[`example.py`](https://github.com/klen/muffin-oauth/blob/develop/example.py) runs GitHub and
Google logins and renders the user info:

```bash
uv run --group example uvicorn example:app --port 5000
```

Then open <http://localhost:5000>. The example uses one route, `/oauth/{provider}`, which
first redirects to the provider and handles the callback on the way back — the same trick as
the single-route quickstart.
