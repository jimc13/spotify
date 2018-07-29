import requests
import random
import auth
oauth_token = auth.get_token()

# https://github.com/plamere/spotipy
# There is a good library but I want to make raw api calls, I will move this
# over to a class so the token doesn't need passing around
# It also makes sense to have a base call function that is built on to reduce
# the amount of duplicate code
# I also want to write the auth "myself" using requests OAuth2

def get_artist_id(artist_name, oauth_token):
    r = requests.get("https://api.spotify.com/v1/search",
        params =    {   "q": '"{}"'.format(artist_name), "type": "artist"},
        headers =   {   "Authorization": "Bearer {}".format(oauth_token),
                        "Accept": "application/json",
                        "Content-Type": "application/json"})
    r.raise_for_status()
    matching_artists = 0
    for artist in r.json()["artists"]["items"]:
        if artist["name"] == artist_name:
            matching_artists += 1
            id = artist["id"]

    assert matching_artists == 1, "{} artists found matching '{}'".format(matching_artists, artist_name)
    return id

def get_random_album_id(artist_id, oauth_token):
    r = requests.get("https://api.spotify.com/v1/artists/{}/albums".format(artist_id),
        headers =   {   "Authorization": "Bearer {}".format(oauth_token),
                        "Accept": "application/json",
                        "Content-Type": "application/json"})
    r.raise_for_status()
    return random.choice(r.json()["items"])["id"]

def get_random_track_uri(album_id, oauth_token):
    r = requests.get("https://api.spotify.com/v1/albums/{}/tracks".format(album_id),
        headers =   {   "Authorization": "Bearer {}".format(oauth_token),
                        "Accept": "application/json",
                        "Content-Type": "application/json"})
    r.raise_for_status()
    return random.choice(r.json()["items"])["uri"]

def main(artist):
    """
    A flaw in the current random selection is that albums are all given equal
    weight meaning songs on large albums are less likely to be selected and
    singles will be played more often.  I would like to fix this without making
    excessive API requests but am not sure this is possible.
    Another flaw is that duplicate albums are not filtered and singles are not
    discarded but this is probably not worth attempting to fix
    """
    import auth
    token = auth.get_token()
    artist_id = get_artist_id(artist, token)
    album_id = get_random_album_id(artist_id, token)
    track_uri = get_random_track_uri(album_id, oauth_token)
    print(track_uri)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("artist")
    args = parser.parse_args()
    main(args.artist)
