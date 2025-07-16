# Muffin‑OAuth

**Muffin‑OAuth** adds OAuth 1 and 2 support to the Muffin\_ framework, enabling both client-side and server-side authentication flows.

[![Tests Status](https://github.com/klen/muffin-oauth/workflows/tests/badge.svg)](https://github.com/klen/muffin-oauth/actions)
[![PyPI Version](https://img.shields.io/pypi/v/muffin-oauth)](https://pypi.org/project/muffin-oauth/)
[![Python Versions](https://img.shields.io/pypi/pyversions/muffin-oauth)](https://pypi.org/project/muffin-oauth/)

# Requirements

- Python >= 3.10
- Compatible with `asyncio`, `Trio`, and `Curio`

# Installation

Install via pip:

    pip install muffin-oauth

# Usage

Here's a basic example using OAuth2:

```python
from muffin import Application
from muffin_oauth import OAuthPlugin

app = Application("auth-example")
oauth = OAuthPlugin()
oauth.setup(app, providers={
    "github": {
        "client_id": "...",
        "client_secret": "...",
        "authorize_url": "https://github.com/login/oauth/authorize",
        "access_token_url": "https://github.com/login/oauth/access_token",
        "api_base_url": "https://api.github.com"
    }
})

@app.route("/")
async def login(request):
    return await oauth.authorize_redirect(request, "github", redirect_uri="http://localhost:8000/callback")

@app.route("/callback")
async def callback(request):
    token = await oauth.authorize_access_token(request, "github")
    request.session["token"] = token
    return "Logged in"

@app.route("/user")
async def user(request):
    client = oauth.client("github", token=request.session.get("token"))
    resp = await client.get("/user")
    return resp.json()
```

Run the example app:

```bash
$ make example
http://localhost:5000
```

Client-side usage:

```python
client = oauth.client("github", access_token="...")
resp = await client.request("GET", "/user")
user_info = resp.json()
```

This supports both OAuth1 and OAuth2 flows, with automatic token handling and resource access via configured providers.

## Testing & Security

- Test coverage for major flows is provided in `tests.py`.
- Minimal dependencies and async-native design.
- Production-ready, MIT-licensed.

## Bug Tracker & Contributing

Found an issue or have an idea? Report it at:
https://github.com/klen/muffin-oauth/issues

Contributions welcome! Fork the repo and submit a PR.

## Contributors

- [klen](https://github.com/klen) (Kirill Klenov)

## License

Licensed under the [MIT license](http://opensource.org/licenses/MIT).

[Muffin]: https://github.com/klen/muffin
