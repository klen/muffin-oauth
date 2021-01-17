"""Support OAuth in Muffin Framework."""
from hashlib import sha1
from random import SystemRandom
import muffin
from aioauth_client import ClientRegistry
from muffin.plugin import BasePlugin


__version__ = "0.6.0"
__project__ = "muffin-oauth"
__author__ = "Kirill Klenov <horneds@gmail.com>"
__license__ = "MIT"

random = SystemRandom().random


class OAuthException(Exception):

    """Implement an exception during OAUTH process."""

    pass


class Plugin(BasePlugin):

    """Support OAuth."""

    name = 'oauth'
    defaults = {
        'clients': {},
        'redirect_uri': None,
    }

    def client(self, client_name, **params):
        """Initialize OAuth client from registry."""
        if client_name not in self.cfg.clients:
            raise OAuthException('Unconfigured client: %s' % client_name)

        if client_name not in ClientRegistry.clients:
            raise OAuthException('Unsupported services: %s' % client_name)

        params = dict(self.cfg.clients[client_name], **params)
        return ClientRegistry.clients[client_name](**params)

    async def authorize(self, client, session, redirect_uri=None, **params):
        """Get authorization URL."""
        state = sha1(str(random()).encode('ascii')).hexdigest()
        session['muffin_oauth'] = state
        return client.get_authorize_url(redirect_uri=redirect_uri, state=state, **params)

    async def login(self, client_name, request, redirect_uri=None, headers=None, **params):
        """Process login with OAuth.

        :param client_name: A name one of configured clients
        :param request: Web request
        :param redirect_uri: An URI for authorization redirect
        """
        client = self.client(client_name, logger=self.app.logger)
        session = self.app.plugins['session']

        redirect_uri = redirect_uri or self.cfg.redirect_uri or str(request.url)
        ses = session.load_from_request(request)

        code = request.query.get('code')
        if not code:
            url = await self.authorize(client, ses, redirect_uri, **params)
            res = muffin.ResponseRedirect(url)
            session.save_to_response(ses, res)
            raise res

        # Check state
        state = request.query.get('state')
        stored_state = ses.pop('muffin_oauth', '')
        if stored_state != state:
            raise muffin.ResponseError(406, 'Invalid state: "%s"' % stored_state)

        # Get access token
        return (
            client,
            await client.get_access_token(code, redirect_uri=redirect_uri, headers=headers)
        )

    def refresh(self, client_name, refresh_token, **params):
        """Get refresh token.

        :param client_name: A name one of configured clients
        :param redirect_uri: An URI for authorization redirect
        :returns: a coroutine
        """
        client = self.client(client_name, logger=self.app.logger)
        return client.get_access_token(refresh_token, grant_type='refresh_token', **params)
