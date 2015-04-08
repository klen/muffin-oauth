""" Example application. """

import muffin


app = muffin.Application('oauth', CONFIG='example.config')


@app.register('/')
def index(request):
    """ Index Page. """
    return """
        <ul>
            <li><a href="/bitbucket">Bitbucket</a></li>
            <li><a href="/github">Github</a></li>
            <li><a href="/twitter">Twitter</a></li>
        </ul>
    """


@app.register('/bitbucket')
@app.ps.oauth.login('bitbucket')
def bitbucket(request, client):
    """ Bitbucket example. """
    response = yield from client.request('GET', 'user')
    data = yield from response.json()
    return "<ul>%s</ul>" % "".join("<li><b>%s</b>: %s</li>" % item
                                   for item in data['user'].items())


@app.register('/twitter')
@app.ps.oauth.login('twitter')
def twitter(request, client):
    """ Twitter example. """
    response = yield from client.request('GET', 'account/verify_credentials.json')
    data = yield from response.json()
    return "<ul>%s</ul>" % "".join("<li><b>%s</b>: %s</li>" % item for item in data.items())


@app.register('/github')
@app.ps.oauth.login('github')
def github(request, client):
    """ Github example. """
    response = yield from client.request('GET', 'user')
    data = yield from response.json()
    return "<ul>%s</ul>" % "".join("<li><b>%s</b>: %s</li>" % item for item in data.items())
