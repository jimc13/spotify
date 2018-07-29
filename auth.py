from config import client_id, client_secret
import requests
from requests.auth import HTTPBasicAuth

def get_token():
    r = requests.post("https://accounts.spotify.com/api/token",
        auth = HTTPBasicAuth(client_id, client_secret),
        data = {"grant_type": "client_credentials"})
    r.raise_for_status()
    return r.json()["access_token"]
