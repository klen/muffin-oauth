"""Support OAuth in Muffin Framework."""
from hashlib import sha1
from random import SystemRandom

import muffin
from aioauth_client import ClientRegistry, OAuth1Client, OAuth2Client
from muffin.plugins import BasePlugin
from muffin_session import Plugin as SPlugin


__version__ = "0.5.2"
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
    dependencies = {
        'session': SPlugin
    }

    def client(self, client_name, **params):
        """Initialize OAuth client from registry."""
        if client_name not in self.cfg.clients:
            raise OAuthException('Unconfigured client: %s' % client_name)

        if client_name not in ClientRegistry.clients:
            raise OAuthException('Unsupported services: %s' % client_name)

        params = dict(self.cfg.clients[client_name], **params)
        return ClientRegistry.clients[client_name](**params)

    async def login(self, client_name, request, redirect_uri=None, **params):
        """Process login with OAuth.

        :param client_name: A name one of configured clients
        :param request: Web request
        :param redirect_uri: An URI for authorization redirect
        """
        client = self.client(client_name, logger=self.app.logger)

        redirect_uri = redirect_uri or self.cfg.redirect_uri or '%s://%s%s' % (
            request.scheme, request.host, request.path)
        session = await self.app.ps.session(request)

        if isinstance(client, OAuth1Client):
            oauth_verifier = request.query.get('oauth_verifier')
            if not oauth_verifier:

                # Get request credentials
                data = await client.get_request_token(
                    oauth_callback=redirect_uri)

                token, secret = data[:2]

                # Save the credentials in current user session
                session['oauth_token'] = token
                session['oauth_token_secret'] = secret

                url = client.get_authorize_url()
                raise muffin.HTTPFound(url)

            # Check request_token
            oauth_token = request.query.get('oauth_token')
            if session['oauth_token'] != oauth_token:
                raise muffin.HTTPForbidden(reason='Invalid token.')

            client.oauth_token = oauth_token
            client.oauth_token_secret = session.get('oauth_token_secret')

            # Get access tokens
            return client, await client.get_access_token(oauth_verifier)

        if isinstance(client, OAuth2Client):
            code = request.query.get('code')
            if not code:

                # Authorize an user
                state = sha1(str(random()).encode('ascii')).hexdigest()
                session['oauth_secret'] = state
                url = client.get_authorize_url(
                    redirect_uri=redirect_uri, state=state, **params)
                raise muffin.HTTPFound(url)

            # Check state
            state = request.query.get('state')
            oauth_secret = session.pop('oauth_secret', '')
            if oauth_secret != state:
                raise muffin.HTTPForbidden(reason='Invalid token "%s".' % oauth_secret)

            # Get access token
            return client, await client.get_access_token(code, redirect_uri=redirect_uri)

        return client

    def refresh(self, client_name, refresh_token, **params):
        """Get refresh token.

        :param client_name: A name one of configured clients
        :param redirect_uri: An URI for authorization redirect
        :returns: a coroutine
        """
        client = self.client(client_name, logger=self.app.logger)
        return client.get_access_token(refresh_token, grant_type='refresh_token', **params)
