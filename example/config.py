""" Setup the application. """

PLUGINS = 'muffin_session', 'muffin_oauth',
DEBUG = True

OAUTH_CLIENTS = {
    'github': {
        'client_id': 'b6281b6fe88fa4c313e6',
        'client_secret': '21ff23d9f1cad775daee6a38d230e1ee05b04f7c',
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

    },
}
