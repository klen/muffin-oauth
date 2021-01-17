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
        'bitbucket': {
            'consumer_key': '4DKzbyW8JSbnkFyRS5',
            'consumer_secret': 'AvzZhtvRJhrEJMsGAMsPEuHTRWdMPX9z',
        },
        'twitter': {
            'consumer_key': 'oUXo1M7q1rlsPXm4ER3dWnMt8',
            'consumer_secret': 'YWzEvXZJO9PI6f9w2FtwUJenMvy9SPLrHOvnNkVkc5LdYjKKup',
        },
        'facebook': {
            'client_id': '384739235070641',
            'client_secret': '8e3374a4e1e91a2bd5b830a46208c15a',
            'scope': 'email',
        },
        'google': {
            'client_id': '150775235058-9fmas709maee5nn053knv1heov12sh4n.apps.googleusercontent.com',  # noqa
            'client_secret': 'df3JwpfRf8RIBz-9avNW8Gx7',
            'scope': 'profile email',
        },
        'yandex': {
            'client_id': 'e19388a76a824b3385f38beec67f98f1',
            'client_secret': '1d2e6fdcc23b45849def6a34b43ac2d8',
        }
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
                    <a class="nav-link" href="/oauth/bitbucket">Login with Bitbucket</a></li>
                <li class="nav-item">
                    <a class="nav-link" href="/oauth/facebook">Login with Facebook</a></li>
                <li class="nav-item">
                    <a class="nav-link" href="/oauth/github">Login with Github</a></li>
                <li class="nav-item">
                    <a class="nav-link" href="/oauth/google">Login with Google</a></li>
                <li class="nav-item">
                    <a class="nav-link" href="/oauth/yandex">Login with Yandex</a></li>
            </ul>
        </div>
    """


@app.route('/oauth/{provider}')
async def oauth_info(request):
    """Oauth example."""
    provider = request.path_params.get('provider')
    client, _ = await oauth.login(provider, request)
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
