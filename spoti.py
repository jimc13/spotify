from flask import Flask, redirect, url_for, session, request, render_template
from authlib.flask.client import OAuth
import requests
import pprint
from config import app_client_id, app_client_secret, app_session_key

# https://docs.authlib.org/en/latest/client/flask.html

pp = pprint.PrettyPrinter(indent=4)
app = Flask(__name__)
app.debug = True
app.secret_key = app_session_key
oauth = OAuth(app)

spotify = oauth.register(
    'spotify',
    client_id=app_client_id,
    client_secret=app_client_secret,
    # Change the scope to match whatever it us you need
    # list of scopes can be found in the url below
    # https://developer.spotify.com/web-api/using-scopes/
    client_kwargs={'scope': 'user-top-read user-modify-playback-state user-read-playback-state'},
    request_token_url=None,
    access_token_url='https://accounts.spotify.com/api/token',
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
    current_song = r.json()['item']['name']
    artist = ' & '.join([ i['name'] for i in r.json()['item']['artists'] ])
    # Silly maths used to generate a gradual slider... poorly
    min = 0
    max = 100
    step_low = (volume - min) // 5
    step_high = (max - volume) // 6
    return render_template('main.html', current_song=current_song, volume=volume, device=device, artist=artist, min=min, max=max, step_low=step_low, step_high=step_high)


@app.route('/login')
def login():
    print(url_for('authorize', _external=True))
    return spotify.authorize_redirect(redirect_uri=url_for('authorize', _external=True))


@app.route('/authorized')
def authorize():
    resp = spotify.authorize_access_token()
    print(resp)
    session['oauth_token'] = resp['access_token']

    r = requests.get('https://api.spotify.com/v1/me/top/artists',
        headers =   {   "Authorization": "Bearer {}".format(session['oauth_token']),
                        "Accept": "application/json",
                        "Content-Type": "application/json"})

    print(r.status_code)
    print(r.text)
    pp.pprint(r.json())
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run()
    # Return a self signed cert
    #app.run(ssl_context='adhoc')
