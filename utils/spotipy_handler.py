try:
    import spotipy
except:
    print("Module Spotipy not found. Execute 'pip install spotipy'.")
    exit()
from webbrowser import open as openwebbrowser
from time import sleep
import json
import os.path

class SpotipyHandler:
    def __init__(self, spotipyObject=None):
        self.spotipyObject = spotipyObject
        self.token = None
    
    def login(self, cached=False):
        scopes = "playlist-modify-public playlist-modify-private " + \
                 "user-follow-modify user-library-modify user-library-read playlist-read-private user-follow-read"
        try:
            sp_oauth = spotipy.oauth2.SpotifyPKCE(
                client_id='85d1a53a50194a18841106cf4d4a3b01',
                redirect_uri='http://spotyeraser.com/callback',
                scope=scopes,
                open_browser=False,
                username='user'
            )

            if cached:
                token_info = self.get_cached_token(sp_oauth)
                if not token_info:
                    print("No previous login were found!")
                    return False
                self.token = token_info['access_token']
            else:
                url = sp_oauth.get_authorize_url()
                openwebbrowser(url)
                response = input("Paste the link here (http://spotyeraser.com/?code=...): ")
                code = sp_oauth.parse_response_code(response)
                self.token = sp_oauth.get_access_token(code=code, check_cache=False)
                if not self.token:
                    return False
            self.spotipyObject = spotipy.Spotify(auth=self.token)
            return True
        except:
            return False

    def get_cached_token(self, sp_oauth):
        token_info = None
        try:
            path = os.path.join(os.path.dirname(__file__), os.pardir, sp_oauth.cache_path)
            f = open(path)
            token_info_string = f.read()
            f.close()
            token_info = json.loads(token_info_string)
            caca = sp_oauth._is_scope_subset(sp_oauth.scope, token_info["scope"])
            if "scope" not in token_info or not caca:
                return None
            if sp_oauth.is_token_expired(token_info):
                token_info = sp_oauth.refresh_access_token(token_info["refresh_token"])
        except:
            return None
        return token_info

    def erase_user_saved_tracks(self, q):
        all_tracks = self.current_user_saved_tracks()
        if not all_tracks:
            q.put(False)
            return
        try:
            all_tracks = [all_tracks[i:i + 50] for i in range(0, len(all_tracks), 50)]
            for chunked_tracks in all_tracks:
                self.spotipyObject.current_user_saved_tracks_delete(tracks=chunked_tracks)
                sleep(0.3)
            q.put(True)
        except:
            q.put(False)
    
    def current_user_saved_tracks(self):
        all_tracks = []
        offset = -50
        try:
            while True:
                response = self.spotipyObject.current_user_saved_tracks(limit=50, offset=offset+50)
                if not response:
                    return None
                all_tracks = all_tracks + [r['track']['id'] for r in response['items']]
                if response['next'] == None:
                    break
                offset += 50
                sleep(0.3)
            return all_tracks
        except:
            return None

    def erase_user_saved_artists(self, q):
        all_artists = self.current_user_saved_artists()
        if not all_artists:
            q.put(False)
            return
        try:
            all_artists = [all_artists[i:i + 50] for i in range(0, len(all_artists), 50)]
            for chunked_artists in all_artists:
                self.spotipyObject.user_unfollow_artists(ids=chunked_artists)
                sleep(0.3)
            q.put(True)
        except:
            q.put(False)
    
    def current_user_saved_artists(self):
        all_artists = []
        last_id = ''
        try:
            while True:
                if not last_id:
                    response = self.spotipyObject.current_user_followed_artists(limit=50)
                else:
                    response = self.spotipyObject.current_user_followed_artists(limit=50, after=last_id)
                if not response:
                    return None
                all_artists = all_artists + [r['id'] for r in response['artists']['items']]
                if response['artists']['next'] == None:
                    break
                last_id = all_artists[-1]
                sleep(0.3)
            return all_artists
        except:
            return None
    
    def erase_user_saved_albums(self, q):
        all_albums = self.current_user_saved_albums()
        if not all_albums:
            q.put(False)
            return
        try:
            all_albums = [all_albums[i:i + 50] for i in range(0, len(all_albums), 50)]
            for chunked_albums in all_albums:
                self.spotipyObject.current_user_saved_albums_delete(albums=chunked_albums)
                sleep(0.3)
            q.put(True)
        except:
            q.put(False)

    def current_user_saved_albums(self):
        all_albums = []
        offset = -50
        try:
            while True:
                response = self.spotipyObject.current_user_saved_albums(limit=50, offset=offset+50)
                if not response:
                    return None
                all_albums = all_albums + [r['album']['id'] for r in response['items']]
                if response['next'] == None:
                    break
                offset += 50
                sleep(0.3)
            return all_albums
        except:
            return None

    def erase_user_saved_shows(self, q):
        all_shows = self.current_user_saved_shows()
        if not all_shows:
            q.put(False)
            return
        try:
            all_shows = [all_shows[i:i + 50] for i in range(0, len(all_shows), 50)]
            for chunked_shows in all_shows:
                self.spotipyObject.current_user_saved_shows_delete(shows=chunked_shows)
                sleep(0.3)
            q.put(True)
        except:
            q.put(False)

    def current_user_saved_shows(self):
        all_shows = []
        offset = -50
        try:
            while True:
                response = self.spotipyObject.current_user_saved_shows(limit=50, offset=offset+50)
                if not response:
                    return None
                all_shows = all_shows + [r['show']['id'] for r in response['items']]
                if response['next'] == None:
                    break
                offset += 50
                sleep(0.3)
            return all_shows
        except:
            return None
