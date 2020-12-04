import json

import requests
from spotipy import SpotifyClientCredentials, Spotify

from model.lyrics_getter.lyrics_getter import LyricsGetter
from model.music_objs.album import Album
from model.music_objs.artist import Artist
from model.music_objs.song import Song
from model.songs_searchers.music_searcher_interface import IMusicSearcher


class SpotifySearcher(IMusicSearcher):
    def __init__(self, client_id, client_secret):
        client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
        self._id = client_id
        self._sp = Spotify(auth_manager=client_credentials_manager)

    def get_song_info(self, song, artist):
        lyric_getter = LyricsGetter()
        tracks = self._sp.search(song, limit=50)["tracks"]["items"]
        parsed = self._parse_artist(artist)
        res = None
        should_stop = False
        for tr in tracks:
            artists = tr["artists"]
            for ar in artists:
                if artist.lower() in ar["name"].lower():
                    res = tr
                    should_stop = True
                    break
            if should_stop:
                break
            if self._in_artists(parsed, artists):
                res = tr
                break
        if res:
            self._set_genre(res, artist)
            lyrics = lyric_getter.get(artist, song)
            res["lyrics"] = lyrics
            return Song(res)

    def get_album_info(self, album, artist):
        tracks = self._sp.search(album, limit=50)["tracks"]["items"]
        res = None
        parsed = self._parse_artist(artist)
        for tr in tracks:
            al = tr["album"]
            if album == al["name"] and self._is_artist(al["artists"], artist):
                res = al
                break
            elif album == al["name"] and self._in_artists(parsed, al["artists"]):
                res = al
                break

        self._set_genre(res, artist)
        return Album(res)

    def get_artist_info(self, artist):
        tracks = self._sp.search(artist, limit=50)["tracks"]["items"]
        res = None
        for tr in tracks:
            artists = tr["artists"]
            for a in artists:
                if artist == a["name"]:
                    res = a
                    break

        self._set_genre(res, artist)
        return Artist(res)

    def get_similar_artists(self, artist):
        artist_obj = self.get_artist_info(artist)
        similar_artists = self._sp.artist_related_artists(artist_obj.ID)
        res = []
        for sim_ar in similar_artists:
            res += [Artist(sim_ar)]

        return res

    def get_artists_top_tracks(self, artist, country="US"):
        artist_obj = self.get_artist_info(artist)
        top_tracks = self._sp.artist_top_tracks(artist_obj.ID, country=country)
        res = []
        for song in top_tracks:
            res += [Song(song)]

        return res

    def get_song_analysis(self, song, artist):
        song_obj = self.get_song_info(song, artist)
        analysis = self._sp.audio_analysis(song_obj.ID)
        return analysis

    def get_similar_tracks(self, song, artist):
        lyric_getter = LyricsGetter()
        song_obj = self.get_song_info(song, artist)
        artist_obj = self.get_artist_info(artist)
        access_token = self._sp.auth_manager.token_info["access_token"]
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        url = f"https://api.spotify.com/v1/recommendations?seed_artists={artist_obj.ID}&seed_tracks={song_obj.ID}"
        tracks = json.loads(requests.request("GET", url, headers=headers).text)["tracks"]
        res = []
        for track in tracks:
            artist_n = track["artists"][0]["name"]
            self._set_genre(track, artist_n)
            track["duration"] = track["duration_ms"] / 1000
            lyrics = lyric_getter.get(artist_n, track["name"])
            track["lyrics"] = lyrics
            res += [Song(track)]
        return res

    def _get_response(self, action):
        url = f"https://itunes.apple.com/search?term={action}"
        return requests.request("GET", url)

    def _is_artist(self, artists, artist):
        for ar in artists:
            if artist.lower() in ar["name"].lower():
                return True

        return False

    def _set_genre(self, res, artist):
        if not res:
            return
        response = self._get_response(artist)
        results = json.loads(response.text)["results"]
        for r in results:
            if r["artistName"].lower() == artist.lower():
                res["genre"] = r["primaryGenreName"]
                break

    def _parse_artist(self, artist):
        res = artist.strip().lower()
        return [f.strip() for r in res.split("&") for t in r.split(",") for f in t.split("x")]

    def _in_artists(self, parsed, artists):
        n = 0
        for artist in artists:
            if artist["name"] in parsed:
                n += 1

        return n == len(parsed)

