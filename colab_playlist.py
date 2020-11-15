import requests
import datetime
from config import oauth_token, playlists

# TODO:
# Update get_playlist_tracks to handle more than 100 tracks in a playlist
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

    def put(self, uri, json):
        r = requests.put(f"https://api.spotify.com/v1{uri}",
            json = json,
            headers = self.headers)
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
            yield track

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

    def update_playlist(self, tracks, playlist_id):
        for chunk_of_tracks in chunks(tracks, 100):
            self.put(f"/playlists/{playlist_id}/tracks", {"uris": chunk_of_tracks})

if __name__ == "__main__":
    spotify = SpotifyAPI(oauth_token)
    tracks = []
    for playlist in playlists:
        for track in spotify.get_playlist_tracks(playlist):
            tracks.append({"added_at": track["added_at"], "uri": track["track"]["uri"]})
    tracks.sort(key=lambda x: x["added_at"])
    tracks = list(map(lambda x: x["uri"], tracks))
    # If a playlist_id is provided in the config update it, otherwise create a
    # new one
    try:
        from config import playlist_id
    except ImportError:
        print("Created with Playlist ID:", spotify.create_playlist(tracks, name="Songs of the weeks"))
    else:
        spotify.update_playlist(tracks, playlist_id)
