import json
from concurrent.futures.thread import ThreadPoolExecutor
from threading import Thread, Lock

import requests
from spotipy import SpotifyClientCredentials, Spotify

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
        tracks = self._sp.search(song, limit=50)["tracks"]["items"]
        parsed = self._parse_artist(artist)
        res = None
        should_stop = False
        for tr in tracks:
            artists = tr["artists"]
            for ar in artists:
                if artist.lower() in ar["name"].lower():
                    res = tr
                    self._set_genre(res, ar)
                    should_stop = True
                    break
            if should_stop:
                break
            if self._in_artists(parsed, artists):
                res = tr
                break
        if res:
            return Song(res)

    def get_album_info(self, album, artist):
        tracks = self._sp.search(album, limit=50)["tracks"]["items"]
        res = None
        parsed = self._parse_artist(artist)
        al = None
        for tr in tracks:
            al = tr["album"]
            if album.lower() == al["name"].lower() and self._is_artist(al["artists"], artist):
                res = al
                break
            elif album.lower() == al["name"].lower() and self._in_artists(parsed, al["artists"]):
                res = al
                break

        if al and res:
            artist = self._get_artist_from_list(al["artists"], artist)
            self._set_genre(res, artist)
        return Album(res)

    def get_artist_info(self, artist):
        tracks = self._sp.search(artist, limit=50)["tracks"]["items"]
        res = None
        for tr in tracks:
            artists = tr["artists"]
            for a in artists:
                if artist == a["name"]:
                    res = self._sp.artist(a["id"])
                    break
        if res:
            return Artist(res)

    def get_similar_artists(self, artist, num_of_simillar=20):
        artist_obj = self.get_artist_info(artist)
        similar_artists = self._sp.artist_related_artists(artist_obj.ID)["artists"]
        res = []
        parsed = 0
        while True:
            if parsed >= num_of_simillar:
                break
            sim_ar = similar_artists[0]
            res += [Artist(sim_ar)]
            similar_artists = similar_artists[1:] + self._sp.artist_related_artists(sim_ar["id"])["artists"]
            parsed += 1

        return res

    def get_artists_top_tracks(self, artist, country="US"):
        artist_obj = self.get_artist_info(artist)
        top_tracks = self._sp.artist_top_tracks(artist_obj.ID, country=country)
        res = []
        for song in top_tracks["tracks"]:
            song["genres"] = artist_obj.Genres
            res += [Song(song)]

        return res

    def get_song_analysis(self, song, artist):
        song_obj = self.get_song_info(song, artist)
        analysis = self._sp.audio_analysis(song_obj.ID)
        return analysis

    def get_similar_tracks(self, song, artist, num_of_similar=20):
        if not num_of_similar:
            return []
        song_obj = self.get_song_info(song, artist)
        tracks = self.get_recommendations(songs_ids=[song_obj.ID])["tracks"][:num_of_similar]
        workers = []
        res = []
        lock = Lock()
        for track in tracks:
            worker = Thread(target=self._set_similar_song, args=(track, res, lock))
            worker.start()
            workers += [worker]
        for t in workers:
            t.join()
        res += self.get_similar_tracks(song, artist, num_of_similar=(num_of_similar - len(res)))
        return res

    def get_recommendations(self, artists_ids=None, songs_ids=None, genres_list=None):
        recommendations = None
        if songs_ids:
            recommendations = self._sp.recommendations(seed_tracks=songs_ids)
        if artists_ids:
            recommendations = self._sp.recommendations(seed_artists=artists_ids)
        if genres_list:
            recommendations = self._sp.recommendations(seed_genres=genres_list)

        return recommendations

    def _set_similar_song(self, track, res, lock):
        artist_n = track["artists"][0]["name"]
        track["duration"] = track["duration_ms"] / 1000
        artist_info = self.get_artist_info(artist_n)
        if not artist_info:
            return
        track["genres"] = artist_info.Genres
        lock.acquire()
        res += [Song(track)]
        lock.release()

    @classmethod
    def _is_artist(cls, artists, artist):
        for ar in artists:
            if artist.lower() in ar["name"].lower():
                return True

        return False

    def _set_genre(self, res, artist):
        artist = self._sp.artist(artist["id"])
        res["genres"] = artist["genres"]

    @classmethod
    def _parse_artist(cls, artist):
        res = artist.strip().lower()
        return [f.strip() for r in res.split("&") for t in r.split(",") for f in t.split("x")]

    @classmethod
    def _in_artists(cls, parsed, artists):
        n = 0
        for artist in artists:
            if artist["name"] in parsed:
                n += 1

        return n == len(parsed)

    @classmethod
    def _get_artist_from_list(cls, artists, artist):
        for a in artists:
            if a["name"].lower() == artist.lower():
                return a
