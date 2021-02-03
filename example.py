"""Example application.

Requirements:
    uvicorn

Run the example with uvicorn:

    $ uvicorn --port 5000 example:app

"""

import muffin
import muffin_oauth
import muffin_session
import html
from pprint import pformat


app = muffin.Application(
    'oauth', DEBUG=True,
    OAUTH_CLIENTS={
        'github': {
            'client_id': 'b6281b6fe88fa4c313e6',
            'client_secret': '21ff23d9f1cad775daee6a38d230e1ee05b04f7c',
            'scope': 'user:email',
        },
        'google': {
            'client_id': '150775235058-9fmas709maee5nn053knv1heov12sh4n.apps.googleusercontent.com',  # noqa
            'client_secret': 'df3JwpfRf8RIBz-9avNW8Gx7',
            'scope': 'profile email',
        },
    })

session = muffin_session.Plugin(app, secret_key='Example')
oauth = muffin_oauth.Plugin(app)


@app.route('/')
async def index(request):
    """Index Page."""
    return """
        <link rel="stylesheet"
            href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" />
        <div class="container">
            <header class="navbar navbar-dark" style="background-color: #7952b3">
                <h2 class="navbar-brand">Muffin OAuth Example</h2>
            </header>
            <ul class="nav flex-column mt-5">
                <li class="nav-item">
                    <a class="nav-link" href="/oauth/github">Login with Github</a></li>
                <li class="nav-item">
                    <a class="nav-link" href="/oauth/google">Login with Google</a></li>
            </ul>
        </div>
    """


@app.route('/oauth/{provider}')
async def oauth_info(request):
    """Oauth example."""
    provider = request.path_params.get('provider')
    client, *_ = await oauth.login(provider, request)
    user, data = await client.user_info()
    return f"""
        <link rel="stylesheet"
            href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" />
        <div class="container">
            <header class="navbar navbar-dark" style="background-color: #7952b3">
                <h2 class="navbar-brand">Muffin OAuth Example ({ client.name })</h2>
            </header>
            <a class="btn btn-primary mt-4" href='/'>Return back</a>
            <table class="table mt-4">
                <tr><td> ID </td><td> { user.id } </td></tr>
                <tr><td> Username </td><td> { user.username } </td></tr>
                <tr><td>First, last name</td><td>{ user.first_name }, { user.last_name }</td></tr>
                <tr><td>Gender</td><td> { user.gender } </td></tr>
                <tr><td>Email</td><td> { user.email } </td></tr>
                <tr><td>Link</td><td> { user.link } </td></tr>
                <tr><td>Picture</td><td> { user.picture } </td></tr>
                <tr><td>Country, City</td><td> { user.country }, { user.city } </td></tr>
            </table>
            <h3 class="mt-4">Raw data</h3>
            <pre>{ html.escape(pformat(data)) }</pre>
        </div>
    """
