# Configuration

The plugin has three options. All of them come from the application config with the `OAUTH_`
prefix, from keyword arguments of `OAuthPlugin(app, ...)`, or from environment variables.

| Option         | Config key        | Default                      | Description                                         |
| -------------- | ----------------- | ---------------------------- | --------------------------------------------------- |
| `clients`      | `OAUTH_CLIENTS`   | `{}`                         | Provider name → `aioauth-client` client options     |
| `redirect_uri` | `OAUTH_REDIRECT_URI` | `None`                    | Default callback URL for `login()` and `authorize()` |
| `secret`       | `OAUTH_SECRET`    | `important:replace_me_asap!` | HMAC key used to sign the `state` parameter         |
| `disabled`     | `OAUTH_DISABLED`  | `False`                      | Inherited from `BasePlugin`; disables the plugin    |

```python
app = muffin.Application(
    "myapp",
    OAUTH_CLIENTS={"github": {...}},
    OAUTH_REDIRECT_URI="http://localhost:8000/callback",
    OAUTH_SECRET="change-me",
)

# equivalent
oauth = OAuthPlugin(app, clients={"github": {...}}, redirect_uri="...", secret="change-me")
```

## Environment variables

Muffin prefixes plugin environment variables with the application config name (`CFG.NAME`,
`muffin` by default) and the plugin name:

```
{MUFFIN}_OAUTH_CLIENTS
{MUFFIN}_OAUTH_REDIRECT_URI
{MUFFIN}_OAUTH_SECRET
```

With the default `CFG.NAME="muffin"` that is `MUFFIN_OAUTH_SECRET`, not `OAUTH_SECRET`. Set a
name when your deployment uses one application per container if you want distinct prefixes:

```python
app = muffin.Application(NAME="shop")
# now reads SHOP_OAUTH_SECRET, SHOP_OAUTH_CLIENTS, ...
```

Values are JSON-decoded when possible, so complex options fit in one variable:

```bash
export MUFFIN_OAUTH_SECRET=change-me
export MUFFIN_OAUTH_CLIENTS='{"github": {"client_id": "...", "client_secret": "..."}}'
```

Precedence (lowest to highest): plugin defaults, application config, `OAuthPlugin(app, ...)`
keyword arguments, environment variables.

## Clients

The key of a client entry is the name registered by `aioauth-client`; the value is passed to
that client's constructor. Names available in `aioauth-client` 0.30 include `github`,
`google`, `gitlab`, `discord`, `facebook`, `vk`, `yandex`, `twitter`, `slack`, `microsoft`,
and others.

```python
OAUTH_CLIENTS = {
    "github": {"client_id": "...", "client_secret": "...", "scope": "user:email"},
    "google": {
        "client_id": "...",
        "client_secret": "...",
        "scope": "profile email",
    },
    "gitlab": {
        "client_id": "...",
        "client_secret": "...",
        "base_url": "https://gitlab.example.com",  # self-hosted provider
    },
}
```

Configured clients are also the allow-list: `client("anything-else")` raises `OAuthError`, so
an unconfigured name cannot be used even if `aioauth-client` knows it.

### Custom providers

Anything the client constructor accepts can be set. To point a client at a different provider:

```python
{
    "myoauth": {
        "client_id": "...",
        "client_secret": "...",
        "authorize_url": "https://auth.example.com/oauth/authorize",
        "access_token_url": "https://auth.example.com/oauth/token",
        "base_url": "https://api.example.com",
    }
}
```

This works only for providers that `aioauth-client` implements by name; the plugin does not
create generic clients.

## redirect_uri

`login()` resolves the callback URL in this order:

1. the `redirect_uri` argument of the call,
2. `OAUTH_REDIRECT_URI`,
3. the current request URL without its query string.

The third fallback means a single `/login` route works without configuration, but it also means
that a query string or a trailing slash in the login URL must be accepted by the provider.
Providers compare the value byte for byte, so configure it explicitly in production.

## secret

`secret` signs the `state` parameter with HMAC-SHA512. The default
`important:replace_me_asap!` is public; anyone can sign a `state` with it, which defeats the
CSRF protection. Set `OAUTH_SECRET` in production and rotate it deliberately: changing the
secret invalidates all `state` values that are currently in flight, so users who are
mid-login get a `406` and have to start again.
