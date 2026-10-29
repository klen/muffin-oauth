# API reference

`muffin_oauth` exports `OAuthPlugin` (aliases `OAuth` and `Plugin`) and `OAuthError`.

```python
from muffin_oauth import OAuthError, OAuthPlugin
```

## `OAuthPlugin`

`muffin.plugins.BasePlugin` subclass, `name = "oauth"`, available as `app.plugins["oauth"]`
after setup.

Options: [`clients`, `redirect_uri`, `secret`](configuration.md).

### `client(client_name, **params) -> aioauth_client.Client`

Create a provider client from the registry.

- `client_name` must be present in `clients` **and** registered by `aioauth-client`.
- `params` are merged over the configured client entry (`dict(config, **params)`), so a token
  can be supplied at call time.
- The client gets the default logger of `aioauth-client`; `login()` and `refresh()` pass the
  application logger instead.

Raises `OAuthError("Unconfigured client: <name>")` or
`OAuthError("Unsupported services: <name>")`.

```python
client = oauth.client("github", access_token="...")
```

### `authorize(client, redirect_uri=None, **params) -> str`

Build the authorization URL for an already created client.

- Generates a `state` value (`<hash>.<signature>`) and signs it with `secret`.
- Passes `redirect_uri` and every extra `params` entry to `client.get_authorize_url()`; extra
  `params` win over the entries of the client configuration.
- Stateless: nothing is stored. The callback must still be verified by `login()`.

```python
url = oauth.authorize(oauth.client("github"), "http://localhost:8000/callback")
```

### `async login(client_name, request, redirect_uri=None, headers=None, **params) -> (client, token, data)`

Run one step of the authorization-code flow.

- Without a `code` query parameter: builds the URL with `authorize()` and raises
  `muffin.ResponseRedirect` (a `307` response).
- With a `code`: validates `state`, then calls `client.get_access_token(code,
  redirect_uri=..., headers=...)`.
- `redirect_uri` defaults to `cfg.redirect_uri`, then to `str(request.url.with_query(""))`.
- `params` go to the authorization URL; `headers` go to the token request.
- Returns the client (with `access_token` set), the access token and the raw provider
  response.

Raises `OAuthError` for an unknown client and `ResponseError.NOT_ACCEPTABLE` (`406`) for a
missing or badly signed `state`.

```python
client, token, data = await oauth.login("github", request)
```

### `refresh(client_name, refresh_token, **params) -> awaitable`

Return the coroutine of `client.get_access_token(refresh_token,
grant_type="refresh_token", **params)`, which resolves to `(token, data)`.

```python
token, data = await oauth.refresh("github", refresh_token)
```

The plugin does not store the new token.

## `OAuthError`

`Exception` subclass raised by the plugin itself (not by `aioauth-client`, which raises its own
`OAuthError`). Raised for an unconfigured or unsupported client, i.e. before any network call.

## `sign(msg, key) -> str`

`muffin_oauth.plugin.sign` is the helper used for the `state` signature: base64url of
HMAC-SHA512. It is importable but not part of the documented API; `state` verification goes
through `login()`.
