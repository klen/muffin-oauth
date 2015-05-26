""" Example application. """

import muffin


app = muffin.Application('oauth', CONFIG='example.config')


@app.register('/')
def index(request):
    """ Index Page. """
    return """
        <ul>
            <li><a href="/oauth/bitbucket">Bitbucket</a></li>
            <li><a href="/oauth/facebook">Facebook</a></li>
            <li><a href="/oauth/github">Github</a></li>
            <li><a href="/oauth/google">Google</a></li>
            <li><a href="/oauth/twitter">Twitter</a></li>
        </ul>
    """


@app.register('/oauth/{provider}')
def oauth(request):
    """ Oauth example. """
    provider = request.match_info.get('provider')
    client = yield from app.ps.oauth.login(provider, request)
    data = yield from client.user_info()
    return "<ul>%s</ul>" % "".join("<li><b>%s</b>: %s</li>" % item for item in data.items())
