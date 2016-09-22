"""Example application."""

import muffin
import html


app = muffin.Application('oauth', CONFIG='example.config')


@app.register('/')
def index(request):
    """Index Page."""
    return """
        <ul>
            <li><a href="/oauth/bitbucket">Bitbucket</a></li>
            <li><a href="/oauth/facebook">Facebook</a></li>
            <li><a href="/oauth/github">Github</a></li>
            <li><a href="/oauth/google">Google</a></li>
            <li><a href="/oauth/twitter">Twitter</a></li>
            <li><a href="/oauth/yandex">Yandex</a></li>
        </ul>
    """


@app.register('/oauth/{provider}')
def oauth(request):
    """Oauth example."""
    provider = request.match_info.get('provider')
    client, _ = yield from app.ps.oauth.login(provider, request)
    user, data = yield from client.user_info()
    response = (
        "<a href='/'>back</a><br/><br/>"
        "<ul>"
        "<li>ID: %(id)s</li>"
        "<li>Username: %(username)s</li>"
        "<li>First, last name: %(first_name)s, %(last_name)s</li>"
        "<li>Email: %(email)s</li>"
        "<li>Link: %(link)s</li>"
        "<li>Picture: %(picture)s</li>"
        "<li>Country, city: %(country)s, %(city)s</li>"
        "</ul>"
    ) % user.__dict__
    response += "<code>%s</code>" % html.escape(repr(data))
    return response
