"""Support OAuth in Muffin Framework."""

from __future__ import annotations

import base64
import hmac
from hashlib import sha256, sha512
from random import SystemRandom
from typing import Any, ClassVar, Mapping

from aioauth_client import Client, ClientRegistry
from muffin import Request, ResponseError, ResponseRedirect
from muffin.plugins import BasePlugin

__version__ = "2.3.1"
__project__ = "muffin-oauth"
__author__ = "Kirill Klenov <horneds@gmail.com>"
__license__ = "MIT"

random = SystemRandom().random


class OAuthError(Exception):
    """Implement an exception during OAUTH process."""


class OAuthPlugin(BasePlugin):
    """Support OAuth."""

    name = "oauth"
    defaults: ClassVar = {
        "clients": {},
        "redirect_uri": None,
        "secret": "important:replace_me_asap!",
    }

    def client(self, client_name: str, **params) -> Client:
        """Initialize OAuth client from registry."""
        if client_name not in self.cfg.clients:
            raise OAuthError("Unconfigured client: %s" % client_name)

        if client_name not in ClientRegistry.clients:
            raise OAuthError("Unsupported services: %s" % client_name)

        params = dict(self.cfg.clients[client_name], **params)
        return ClientRegistry.clients[client_name](**params)

    def authorize(self, client: Client, redirect_uri: str | None = None, **params):
        """Get authorization URL."""
        state = sha256(str(random()).encode("ascii")).hexdigest()
        state = f"{ state }.{ sign(state, self.cfg.secret) }"
        return client.get_authorize_url(
            redirect_uri=redirect_uri,
            state=state,
            **params,
        )

    async def login(
        self,
        client_name: str,
        request: Request,
        redirect_uri: str | None = None,
        headers: Mapping[str, str] | None = None,
        **params,
    ) -> tuple[Client, str, Any]:
        """Process login with OAuth.

        :param client_name: A name one of configured clients
        :param request: Web request
        :param redirect_uri: An URI for authorization redirect
        """
        app = self.app
        client = self.client(client_name, logger=app.logger)

        redirect_uri = redirect_uri or self.cfg.redirect_uri
        if not redirect_uri:
            redirect_uri = str(request.url.with_query(""))

        code = request.url.query.get("code")
        if not code:
            url = self.authorize(client, redirect_uri, **params)
            raise ResponseRedirect(url)

        # Check state
        state = request.url.query.get("state")
        if not state:
            raise ResponseError.NOT_ACCEPTABLE("Invalid state")

        state, _, sig = state.partition(".")
        if sig != sign(state, self.cfg.secret):
            raise ResponseError.NOT_ACCEPTABLE("Invalid state")

        # Get access token
        token, data = await client.get_access_token(
            code,
            redirect_uri=redirect_uri,
            headers=headers,
        )
        return client, token, data

    def refresh(self, client_name: str, refresh_token: str, **params):
        """Get refresh token.

        :param client_name: A name one of configured clients
        :param redirect_uri: An URI for authorization redirect
        """
        client = self.client(client_name, logger=self.app.logger)
        return client.get_access_token(
            refresh_token,
            grant_type="refresh_token",
            **params,
        )


def sign(msg: str, key: str) -> str:
    """Sign the given message with the key."""
    sig = hmac.new(key.encode("utf-8"), msg.encode("utf-8"), sha512).digest()
    return base64.urlsafe_b64encode(sig).decode("utf-8")
