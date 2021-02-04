try:
    import spotipy
except:
    print("Module Spotipy not found. Execute 'pip install spotipy'.")
    exit()
from PyQt5.QtCore import QObject, pyqtSignal
from webbrowser import open as openwebbrowser
from time import sleep
import json
import os.path
import logging

logging.basicConfig(format="%(message)s", level=logging.INFO)

SCOPES = "playlist-modify-public playlist-modify-private user-follow-modify user-library-modify user-library-read playlist-read-private user-follow-read"

class SpotipyHandler(QObject):
    started = pyqtSignal(object)
    finished = pyqtSignal(object)
    progress = pyqtSignal(object)

    def __init__(self, spotipyObject=None):
        super().__init__()
        self.spotipyObject = spotipyObject
        self.token = None
        self.sp_oauth = spotipy.oauth2.SpotifyPKCE(
                client_id='85d1a53a50194a18841106cf4d4a3b01',
                redirect_uri='http://spotyeraser.com/callback',
                scope=SCOPES,
                open_browser=False,
                username='user'
            )
    
    def login(self, cached=False, cmd=True):
        try:
            if cached:
                token_info = self.get_cached_token()
                if not token_info:
                    print("No previous login were found!")
                    return False
                self.token = token_info['access_token']
                self.spotipyObject = spotipy.Spotify(auth=self.token)
            else:
                url = self.sp_oauth.get_authorize_url()
                openwebbrowser(url)
                if cmd:
                    link = input("Paste the link here (http://spotyeraser.com/?code=...): ")
                    if not self.set_token_from_link(link):
                        return False
            return True
        except:
            return False
    
    def set_token_from_link(self, link):
        self.started.emit(None)
        try:
            code = self.sp_oauth.parse_response_code(link)
            self.token = self.sp_oauth.get_access_token(code=code, check_cache=False)
            if not self.token:
                self.finished.emit(False)
            self.spotipyObject = spotipy.Spotify(auth=self.token)
            self.finished.emit(True)
        except:
            self.finished.emit(False)

    def get_cached_token(self):
        token_info = None
        try:
            path = os.path.join(os.path.dirname(__file__), os.pardir, self.sp_oauth.cache_path)
            f = open(path)
            token_info_string = f.read()
            f.close()
            token_info = json.loads(token_info_string)
            caca = self.sp_oauth._is_scope_subset(self.sp_oauth.scope, token_info["scope"])
            if "scope" not in token_info or not caca:
                return None
            if self.sp_oauth.is_token_expired(token_info):
                token_info = self.sp_oauth.refresh_access_token(token_info["refresh_token"])
        except:
            return None
        return token_info

    def erase_user_saved_tracks(self, tracks=None):
        self.started.emit(None)
        if not tracks:
            tracks = self.current_user_saved_tracks()
            if not tracks:
                self.finished.emit(False)
        try:
            total = len(tracks)
            erased = 0
            tracks = [track['id'] for track in tracks]
            tracks = [tracks[i:i + 50] for i in range(0, len(tracks), 50)]
            for chunked_tracks in tracks:
                self.spotipyObject.current_user_saved_tracks_delete(tracks=chunked_tracks)
                erased += len(chunked_tracks)
                self.progress.emit(f"Erasing {erased}/{total}...")
            self.finished.emit(True)
        except Exception as e:
            self.finished.emit(False)
    
    def current_user_saved_tracks(self):
        all_tracks = []
        offset = -50
        try:
            while True:
                self.started.emit(None)
                response = self.spotipyObject.current_user_saved_tracks(limit=50, offset=offset+50)
                if not response:
                    self.finished.emit(None)
                all_tracks = all_tracks + [r['track'] for r in response['items']]
                self.progress.emit(f"Loading {len(all_tracks)}/{response['total']} tracks...")
                if response['next'] == None:
                    break
                offset += 50
            self.finished.emit(all_tracks)
        except:
            self.finished.emit(None)

    def erase_user_saved_artists(self, artists=None):
        self.started.emit(None)
        if not artists:
            artists = self.current_user_saved_artists()
            if not artists:
                self.finished.emit(False)
        try:
            total = len(artists)
            erased = 0
            artists = [artist['id'] for artist in artists]
            artists = [artists[i:i + 50] for i in range(0, len(artists), 50)]
            for chunked_artists in artists:
                self.spotipyObject.user_unfollow_artists(ids=chunked_artists)
                erased += len(chunked_artists)
                self.progress.emit(f"Erasing {erased}/{total}...")
            self.finished.emit(True)
        except:
            self.finished.emit(False)
    
    def current_user_saved_artists(self):
        all_artists = []
        last_id = ''
        self.started.emit(None)
        try:
            while True:
                if not last_id:
                    response = self.spotipyObject.current_user_followed_artists(limit=50)
                else:
                    response = self.spotipyObject.current_user_followed_artists(limit=50, after=last_id)
                if not response:
                    self.finished.emit(None)
                all_artists = all_artists + [r for r in response['artists']['items']]
                self.progress.emit(f"Loading {len(all_artists)}/{response['artists']['total']} artists...")
                if response['artists']['next'] == None:
                    break
                last_id = all_artists[-1]['id']
            self.finished.emit(all_artists)
        except:
            self.finished.emit(None)
    
    def erase_user_saved_albums(self, albums=None):
        self.started.emit(None)
        if not albums:
            albums = self.current_user_saved_albums()
            if not albums:
                self.finished.emit(False)
        try:
            total = len(albums)
            erased = 0
            albums = [album['id'] for album in albums]
            albums = [albums[i:i + 50] for i in range(0, len(albums), 50)]
            for chunked_albums in albums:
                self.spotipyObject.current_user_saved_albums_delete(albums=chunked_albums)
                erased += len(chunked_albums)
                self.progress.emit(f"Erasing {erased}/{total}...")
            self.finished.emit(True)
        except:
            self.finished.emit(False)

    def current_user_saved_albums(self):
        all_albums = []
        offset = -50
        self.started.emit(None)
        try:
            while True:
                response = self.spotipyObject.current_user_saved_albums(limit=50, offset=offset+50)
                if not response:
                    self.finished.emit(None)
                all_albums = all_albums + [r['album'] for r in response['items']]
                self.progress.emit(f"Loading {len(all_albums)}/{response['total']} albums...")
                if response['next'] == None:
                    break
                offset += 50
            self.finished.emit(all_albums)
        except:
            self.finished.emit(None)

    def erase_user_saved_shows(self, shows=None):
        self.started.emit(None)
        if not shows:
            shows = self.current_user_saved_shows()
            if not shows:
                self.finished.emit(False)
        try:
            total = len(shows)
            erased = 0
            shows = [show['id'] for show in shows]
            shows = [shows[i:i + 50] for i in range(0, len(shows), 50)]
            for chunked_shows in shows:
                self.spotipyObject.current_user_saved_shows_delete(shows=chunked_shows)
                erased += len(chunked_shows)
                self.progress.emit(f"Erasing {erased}/{total}...")
            self.finished.emit(True)
        except:
            self.finished.emit(False)

    def current_user_saved_shows(self):
        all_shows = []
        offset = -50
        self.started.emit(None)
        try:
            while True:
                response = self.spotipyObject.current_user_saved_shows(limit=50, offset=offset+50)
                if not response:
                    self.finished.emit(None)
                all_shows = all_shows + [r['show'] for r in response['items']]
                self.progress.emit(f"Loading {len(all_shows)}/{response['total']} podcasts...")
                if response['next'] == None:
                    break
                offset += 50
            self.finished.emit(all_shows)
        except:
            self.finished.emit(None)

    def get_user_data(self, **kwargs):
        try:
            self.started.emit(None)
            username = self.spotipyObject.current_user()
            if username and 'display_name' in username:
                username = username['display_name']
            else:
                username = '???'
            total_tracks = self.spotipyObject.current_user_saved_tracks()
            if total_tracks and 'total' in total_tracks:
                total_tracks = total_tracks['total']
            else:
                total_tracks = '???'
            total_albums = self.spotipyObject.current_user_saved_albums()
            if total_albums and 'total' in total_albums:
                total_albums = total_albums['total']
            else:
                total_albums = '???'
            total_artists = self.spotipyObject.current_user_followed_artists()
            if total_artists and 'artists' in total_artists and 'total' in total_artists['artists']:
                total_artists = total_artists['artists']['total']
            else:
                total_artists = '???'
            total_shows = self.spotipyObject.current_user_saved_shows()
            if total_shows and 'total' in total_shows:
                total_shows = total_shows['total']
            else:
                total_shows = '???'
            self.finished.emit({ 
                'username': username, 
                'total_tracks': total_tracks,
                'total_albums': total_albums,
                'total_artists': total_artists,
                'total_shows': total_shows
                })
        except Exception as e:
            self.finished.emit(None)

    def get_track_info_as_string(self, track):
        if 'name' in track:
            name = track['name']
        else:
            name = '???'
        if 'album' in track and 'artists' in track and track['artists'] and 'name' in track['artists'][0]:
            artist = track['artists'][0]['name']
        else:
            artist = '???'
        if 'album' in track and 'name' in track['album']:
            album = track['album']['name']
        else:
            album = '???'
        return f"{name} - {artist} - {album}"

    def get_artist_info_as_string(self, artist):
        if 'name' in artist:
            name = artist['name']
        else:
            name = '???'
        return f"{name}"

    def get_album_info_as_string(self, album):
        if 'name' in album:
            name = album['name']
        else:
            name = '???'
        if 'artists' in album and album['artists'] and album['artists'][0]:
            artist = album['artists'][0]['name']
        else:
            artist = '???'
        if 'release_date_precision' and album['release_date_precision']:
            if album['release_date_precision'] == 'day' or album['release_date_precision'] == 'month':
                release_date = album['release_date'][0:4]
            elif album['release_date_precision'] == 'year':
                release_date = album['release_date']
            else:
                release_date = '???'
        else:
            release_date = '???'
        return f"{name} ({release_date}) - {artist}"

    def get_show_info_as_string(self, show):
        if 'name' in show:
            name = show['name']
        else:
            name = '???'
        if 'publisher' in show:
            publisher = show['publisher']
        else:
            publisher = '???'
        return f"{name} - {publisher}"
