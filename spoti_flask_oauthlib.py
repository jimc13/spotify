from flask import Flask, redirect, url_for, session, request, render_template
from flask_oauthlib.client import OAuth, OAuthException
import requests
import pprint
from config import app_client_id, app_client_secret, app_session_key

# https://stackoverflow.com/questions/26726165/python-spotify-oauth-flow

pp = pprint.PrettyPrinter(indent=4)
app = Flask(__name__)
app.debug = True
app.secret_key = app_session_key
oauth = OAuth(app)

spotify = oauth.remote_app(
    'spotify',
    consumer_key=app_client_id,
    consumer_secret=app_client_secret,
    # Change the scope to match whatever it us you need
    # list of scopes can be found in the url below
    # https://developer.spotify.com/web-api/using-scopes/
    request_token_params={'scope': 'user-top-read user-modify-playback-state user-read-playback-state'},
    base_url='https://accounts.spotify.com',
    request_token_url=None,
    access_token_url='/api/token',
    authorize_url='https://accounts.spotify.com/authorize'
)


@app.route('/', methods=['GET', 'POST'])
def index():
    if 'oauth_token' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        if 'volume' in request.form:
            if 0 <= int(request.form['volume']) <= 100:
                r = requests.put('https://api.spotify.com/v1/me/player/volume',
                    params =    {   'volume_percent': request.form['volume']},
                    headers =   {   "Authorization": "Bearer {}".format(session['oauth_token']),
                                    "Accept": "application/json",
                                    "Content-Type": "application/json"})
                print(r.status_code)
                print(r.text)

    r = requests.get('https://api.spotify.com/v1/me/player',
        headers =   {   "Authorization": "Bearer {}".format(session['oauth_token']),
                        "Accept": "application/json",
                        "Content-Type": "application/json"})
    #pp.pprint(r.json())
    volume = r.json()['device']['volume_percent']
    device = r.json()['device']['name']
    current = r.json()['item']['name']
    artist = ' & '.join([ i['name'] for i in r.json()['item']['artists'] ])
    min = 0
    max = 100
    step_low = (volume - min) // 5
    step_high = (max - volume) // 6
    return render_template('main.html', current=current, volume=volume, device=device, artist=artist, min=min, max=max, step_low=step_low, step_high=step_high)


@app.route('/login')
def login():
    callback = url_for(
        'spotify_authorized',
        next=request.args.get('next') or request.referrer or None,
        _external=True
    )
    return spotify.authorize(callback=callback)


@app.route('/login/authorized')
def spotify_authorized():
    resp = spotify.authorized_response()
    if resp is None:
        return 'Access denied: reason={0} error={1}'.format(
            request.args['error_reason'],
            request.args['error_description']
        )
    if isinstance(resp, OAuthException):
        return 'Access denied: {0}'.format(resp.message)

    session['oauth_token'] = resp['access_token']
    r = requests.get('https://api.spotify.com/v1/me/top/artists',
        headers =   {   "Authorization": "Bearer {}".format(resp['access_token']),
                        "Accept": "application/json",
                        "Content-Type": "application/json"})

    pp.pprint(r.json())
    return redirect(url_for('index'))


@spotify.tokengetter
def get_spotify_oauth_token():
    return session.get('oauth_token')


if __name__ == '__main__':
    app.run()
