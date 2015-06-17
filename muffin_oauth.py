""" Support OAuth in Muffin Framework. """
import asyncio
from hashlib import sha1
from random import SystemRandom

import muffin
from aioauth_client import * # noqa
from muffin.plugins import BasePlugin, PluginException


__version__ = "0.0.14"
__project__ = "muffin-oauth"
__author__ = "Kirill Klenov <horneds@gmail.com>"
__license__ = "MIT"


random = SystemRandom().random


class OAuthException(Exception):

    """ Implement an exception in OAUTH process. """

    pass


class Plugin(BasePlugin):

    """ Support OAuth. """

    name = 'oauth'
    defaults = {
        'clients': {},
        'redirect_uri': None,
    }

    def setup(self, app):
        """ Ensure muffin_session is installed. """
        if 'session' not in app.plugins:
            raise PluginException('muffin_session should be installed.')
        super().setup(app)

    def client(self, client_name, **params):
        """ Initialize OAuth client from registry. """
        if client_name not in self.options.clients:
            raise OAuthException('Unconfigured client: %s' % client_name)

        if client_name not in ClientRegistry.clients:
            raise OAuthException('Unsupported services: %s' % client_name)

        params = dict(self.options.clients[client_name], **params)
        return ClientRegistry.clients[client_name](**params)

    @asyncio.coroutine
    def login(self, client_name, request, redirect_uri=None, **params):
        """ Process login with OAuth.

        :param client_name: A name one of configured clients
        :param request: Web request
        :param redirect_uri: An URI for authorization redirect

        """
        if client_name not in self.options.clients:
            raise OAuthException('Unconfigured client: %s' % client_name)

        if client_name not in ClientRegistry.clients:
            raise OAuthException('Unsupported services: %s' % client_name)

        client = self.client(client_name, logger=self.app.logger)

        redirect_uri = redirect_uri or self.options.redirect_uri or '%s://%s%s' % (
            request.scheme, request.host, request.path)
        session = yield from self.app.ps.session(request)

        if isinstance(client, OAuth1Client):
            oauth_verifier = request.GET.get('oauth_verifier')
            if not oauth_verifier:

                # Get request credentials
                token, secret = yield from client.get_request_token(
                    oauth_callback=redirect_uri)

                # Save the credentials in current user session
                session['oauth_token'] = token
                session['oauth_token_secret'] = secret

                url = client.get_authorize_url()
                raise muffin.HTTPFound(url)

            # Check request_token
            oauth_token = request.GET.get('oauth_token')
            if session['oauth_token'] != oauth_token:
                raise muffin.HTTPForbidden(reason='Invalid token.')

            client.oauth_token = oauth_token
            client.oauth_token_secret = session.get('oauth_token_secret')

            # Get access tokens
            yield from client.get_access_token(oauth_verifier)

        elif isinstance(client, OAuth2Client):
            code = request.GET.get('code')
            if not code:

                # Authorize an user
                state = sha1(str(random()).encode('ascii')).hexdigest()
                session['oauth_secret'] = state
                url = client.get_authorize_url(
                    redirect_uri=redirect_uri, state=state, **params)
                raise muffin.HTTPFound(url)

            # Check state
            state = request.GET.get('state')
            oauth_secret = session.pop('oauth_secret')
            if oauth_secret != state:
                raise muffin.HTTPForbidden(reason='Invalid token.')

            # Get access token
            yield from client.get_access_token(code, redirect_uri=redirect_uri)

        return client
