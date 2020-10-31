import requests
import datetime
from config import oauth_token, playlists

# TODO:
# Order songs by date added
# Update get_playlist_tracks to handle more than 100 tracks in a playlist
# Create update_playlist
# Add support for whatever Google's music service is called at the time of reaching this

# Token is currently being created using spoti.py and put into config by hand
# Playlist docs https://developer.spotify.com/documentation/web-api/reference/playlists/

# https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks
def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

class SpotifyAPI:
    def __init__(self, oauth_token):
        self.oauth_token = oauth_token
        self.headers = {    "Authorization": f"Bearer {self.oauth_token}",
                            "Accept": "application/json",
                            "Content-Type": "application/json"}

    def get(self, uri):
        r = requests.get(f"https://api.spotify.com/v1{uri}",
            headers =  self.headers)
        r.raise_for_status()
        return r

    def post(self, uri, json):
        r = requests.post(f"https://api.spotify.com/v1{uri}",
            json = json,
            headers = self.headers)
        r.raise_for_status()
        return r

    def get_playlist_tracks(self, playlist_id):
        r = self.get(f"/playlists/{playlist_id}/tracks")
        for track in r.json()["items"]:
            yield track["track"]["uri"]

    def create_playlist(self, tracks, name=None):
        if not name:
            name = datetime.date.today().isoformat()

        user_id = self.get("/me").json()["id"]
        playlist_id = self.post(f"/users/{user_id}/playlists", {"name": name}).json()["id"]
        # A maximum of 100 items can be added in one request.
        # https://developer.spotify.com/documentation/web-api/reference/playlists/add-tracks-to-playlist/
        for chunk_of_tracks in chunks(tracks, 100):
            self.post(f"/playlists/{playlist_id}/tracks", {"uris": chunk_of_tracks})

        return playlist_id

    def update_playlist(self, tracks, name):
        pass

if __name__ == "__main__":
    spotify = SpotifyAPI(oauth_token)
    tracks = []
    for playlist in playlists:
        for track in spotify.get_playlist_tracks(playlist):
            tracks.append(track)
    print(spotify.create_playlist(tracks, name="Songs of the weeks"))
