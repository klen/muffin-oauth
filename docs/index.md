# Muffin-OAuth

Muffin-OAuth adds OAuth **2** authorization to [Muffin][muffin] on top of
[aioauth-client][aioauth-client]. The plugin is deliberately small: it builds the
authorization URL with a signed `state`, checks that signature on the callback, exchanges the
authorization code for an access token, and returns an `aioauth-client` instance that is ready
for API calls.

It does not touch your session or your user model. Store the token wherever your application
keeps state (`muffin-session`, a cookie, a database) and decide yourself what a successful
login means.

## Start here

- [Usage](usage.md): the login redirect flow, callback handling, refresh tokens, direct API
  calls.
- [Configuration](configuration.md): `clients`, `redirect_uri`, `secret`, environment
  variables.
- [Security](security.md): how `state` is signed, what is rejected, what stays your job.
- [API reference](api.md): plugin methods, arguments, return values, errors.
- [Development](development.md): local setup, tests, docs, release.

## Install

```bash
pip install muffin-oauth
```

Python 3.11 - 3.15, Muffin 3 and `aioauth-client` are required. The plugin is async-native and
runs on `asyncio`, `Trio` and `Curio`.

## Minimal example

```python
import muffin
from muffin_oauth import OAuthPlugin

app = muffin.Application(
    "myapp",
    OAUTH_CLIENTS={"github": {"client_id": "...", "client_secret": "...", "scope": "user:email"}},
    OAUTH_REDIRECT_URI="http://localhost:8000/login",
)
oauth = OAuthPlugin(app)


@app.route("/login")
async def login(request):
    client, token, data = await oauth.login("github", request)
    user = await client.request("GET", "/user")
    return {"login": user["login"]}
```

## How a login happens

```
Browser                Your app                     Provider
   |  GET /login          |                             |
   |--------------------->| login(): no code            |
   |   307 Location       | authorize() signs state     |
   |<---------------------|                             |
   |  GET authorize?state=<random>.<hmac>&redirect_uri  |
   |--------------------------------------------------->|
   |  GET /login?code=...&state=...                     |
   |<---------------------------------------------------|
   |                      | login(): verify state,      |
   |                      | get_access_token(code)      |
   |                      |---------------------------->|
   |                      |<----------------------------|
   |  200 {..}            | (client, token, data)       |
   |<---------------------|                             |
```

The same route handles both steps, which is why the callback URL equals the login URL unless
you configure `redirect_uri` differently.

## OAuth 2 only

OAuth1 providers (`twitter`, `tumblr`, `flickr`, ...) exist in `aioauth-client` and can be
instantiated with `OAuthPlugin.client()`, but the plugin cannot complete an OAuth1 round trip:
it never calls `get_request_token()` and it only looks for the OAuth2 `code` query argument,
while OAuth1 providers answer with `oauth_token` and `oauth_verifier`. Use `aioauth_client`
directly if you need OAuth1.

[muffin]: https://github.com/klen/muffin
[aioauth-client]: https://github.com/klen/aioauth-client
