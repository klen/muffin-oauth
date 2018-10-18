"""Example application."""

import muffin
import html


app = muffin.Application(
    'oauth',
    PLUGINS=['muffin_session', 'muffin_oauth'],
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
async def oauth(request):
    """Oauth example."""
    provider = request.match_info.get('provider')
    client, _ = await app.ps.oauth.login(provider, request)
    user, data = await client.user_info()
    response = (
        "<a href='/'>back</a><br/><br/>"
        "<ul>"
        "<li>ID: {u.id}</li>"
        "<li>Username: {u.username}</li>"
        "<li>First, last name: {u.first_name}, {u.last_name}</li>"
        "<li>Email: {u.email}</li>"
        "<li>Link: {u.link}</li>"
        "<li>Picture: {u.picture}</li>"
        "<li>Country, city: {u.country}, {u.city}</li>"
        "</ul>"
    ).format(u=user)
    response += "<code>%s</code>" % html.escape(repr(data))
    return response
