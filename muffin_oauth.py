""" Support OAuth in Muffin Framework. """
import asyncio
import functools
from hashlib import sha1
from random import SystemRandom

import aioauth_client as oauth
import muffin
from muffin.plugins import BasePlugin, PluginException
from muffin.utils import to_coroutine


__version__ = "0.0.0"
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
        'clients': {}
    }

    def setup(self, app):
        """ Ensure muffin_session is installed. """
        if 'session' not in app.plugins:
            raise PluginException('muffin_session should be installed.')
        super().setup(app)

    def login(self, client_name):
        """ Process login with OAuth. """
        def decorator(view):

            if client_name not in self.options.clients:
                raise OAuthException('Unconfigured client: %s' % client_name)

            if client_name not in oauth.ClientRegistry.clients:
                raise OAuthException('Unsupported services: %s' % client_name)

            name = client_name
            view = to_coroutine(view)

            @asyncio.coroutine
            @functools.wraps(view)
            def wrapper(request):
                params = request.app.ps.oauth.options.clients[name]
                client = oauth.ClientRegistry.clients[name](logger=request.app.logger, **params)

                redirect_url = 'http://%s%s' % (request.host, request.path_qs)

                if isinstance(client, oauth.OAuth1Client):
                    oauth_verifier = request.GET.get('oauth_verifier')
                    if not oauth_verifier:

                        # Get request credentials
                        token, secret = yield from client.get_request_token(
                            oauth_callback=redirect_url)

                        # Save the credentials in current user session
                        request.session['oauth_token'] = token
                        request.session['oauth_token_secret'] = secret

                        url = client.get_authorize_url()
                        return muffin.HTTPFound(url)

                    # Check request_token
                    oauth_token = request.GET.get('oauth_token')
                    if request.session['oauth_token'] != oauth_token:
                        raise muffin.HTTPForbidden(reason='Invalid token.')

                    client.oauth_token = oauth_token
                    client.oauth_token_secret = request.session.get('oauth_token_secret')

                    # Get access tokens
                    yield from client.get_access_token(oauth_verifier)

                elif isinstance(client, oauth.OAuth2Client):
                    code = request.GET.get('code')
                    if not code:

                        # Authorize an user
                        state = sha1(str(random()).encode('ascii')).hexdigest()
                        request.session['oauth_secret'] = state
                        url = client.get_authorize_url(redirect_url=redirect_url, state=state)
                        raise muffin.HTTPFound(url)

                    # Check state
                    state = request.GET.get('state')
                    if request.session['oauth_secret'] != state:
                        raise muffin.HTTPForbidden(reason='Invalid token.')

                    # Get access token
                    yield from client.get_access_token(code, redirect_url=redirect_url)

                return (yield from view(request, client))

            return wrapper

        return decorator
