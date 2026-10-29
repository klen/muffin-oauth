# Security

## The state parameter

`authorize()` adds a `state` value built from two parts:

```
state = <random token>.<base64url HMAC-SHA512 of that token with secret>
```

The signature makes the value stateless: nothing is stored server-side, yet the callback can
prove that the state was produced by this application. `login()` recomputes the signature and
answers `406 Not Acceptable` when:

- `state` is missing from the callback query,
- the signature does not match (including a state from another application or an expired
  `secret`).

The code is exchanged with the provider only after the signature check passes.

## Set your own secret

The default `secret` is `important:replace_me_asap!` and is part of the public source. With the
default, anyone can build a valid `state`, so the protection is gone.

```bash
export MUFFIN_OAUTH_SECRET="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"
```

The plugin reads the secret once at setup, so restart the application after rotating it. All
states signed with the old secret stop validating immediately.

## What the signature does not protect

- **It is not a replay cache.** A signed `state` stays valid as long as the secret does; the
  plugin does not remember which states it has already seen. An attacker who can read a
  callback URL can reuse its `state` until the provider rejects the code (authorization codes
  are single-use). Add a per-session nonce if you need strict one-time states.
- **It does not authenticate the user.** `login()` only proves that the callback belongs to
  this application. Deciding whether the returned identity may sign in is your code.
- **It does not tie the callback to the browser.** Login CSRF: an attacker can start a login,
  copy their own callback URL (a valid `code` with a valid `state`) and send it to a victim.
  The victim's browser completes the exchange and is logged in as the attacker, so anything the
  victim does next lands in the attacker's account. To block it, store your own nonce in the
  user's session when you send them to the provider and compare it in the callback before you
  accept the login.
- **No PKCE.** `aioauth-client` 0.30 does not implement `code_challenge` /
  `code_verifier`, so public clients cannot rely on PKCE; keep `client_secret` on the server.

## redirect_uri

Providers compare `redirect_uri` byte for byte. Prefer an explicit `OAUTH_REDIRECT_URI` over
the fallback (current URL without query): the fallback derives the value from the request, so
behind a proxy with a different host or scheme it can produce a URL the provider rejects, and
it makes the accepted callback depend on how the login page was reached.

The plugin sends the same `redirect_uri` in the authorization request and in the token
exchange, which is what most providers require.

## Tokens

- `login()` returns the token; storing it in `muffin-session`, a cookie or a database is your
  decision. `muffin-session` signs its cookie with its own secret — keep that secret as safe as
  `OAUTH_SECRET`.
- Tokens do not expire in the plugin. Use `refresh()` when the provider issued a refresh token
  and you need a fresh access token.
- `client.request()` sends the token as `Authorization: Bearer <token>`. Do not log raw
  responses from `login()`: `data` may contain tokens and ids.

## Error surface

Invalid `state` answers `406` with `Invalid state` and never exposes the expected signature.
Network and provider errors surface as `aioauth_client.OAuthError`; map them to your own error
pages if you do not want a stack trace in production.
