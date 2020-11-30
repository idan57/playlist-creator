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

