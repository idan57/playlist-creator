from threading import Thread, Lock

from spotipy import SpotifyClientCredentials, Spotify

from model.logger.spotify_logger import Logger
from model.music_objs.album import Album
from model.music_objs.artist import Artist
from model.music_objs.playlist import Playlist
from model.music_objs.song import Song
from model.songs_searchers.music_searcher_interface import IMusicSearcher
import pycountry


class SpotifySearcher(IMusicSearcher):
    """
    A class that uses Spotify's API to search music info and get data regarding artists, tracks, etc.
    """
    CACHE = {
        "artists": {},
        "songs": {},
        "albums": {}
    }
    CACHE_LOCK = Lock()
    COUNTRY_CODES = ['AD', 'AR', 'AU', 'AT', 'BE', 'BO', 'BR', 'BG', 'CA', 'CL', 'CO', 'CR', 'CY', 'CZ', 'DK', 'DO',
                     'EC', 'SV', 'EE', 'FI', 'FR', 'DE', 'GR', 'GT', 'HN', 'HK', 'HU', 'IS', 'ID', 'IE', 'IT', 'JP',
                     'LV', 'LI', 'LT', 'LU', 'MY', 'MT', 'MX', 'MC', 'NL', 'NZ', 'NI', 'NO', 'PA', 'PY', 'PE', 'PH',
                     'PL', 'PT', 'SG', 'ES', 'SK', 'SE', 'CH', 'TW', 'TR', 'GB', 'US', 'UY']
    CATAGORIES = {}

    def __init__(self, client_id, client_secret, disable_exceptions=True):
        """
        :param client_id: ID for Spotify developer API
        :param client_secret: Secret ID for Spotify developer API
        :param disable_exceptions: disable raising exceptions during search
        """
        client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
        self._id = client_id
        self._sp = Spotify(auth_manager=client_credentials_manager)
        self._lock = Lock()
        self._disable_exceptions = disable_exceptions
        self.logger = Logger()

    def get_song_info(self, song, artist):
        """
        Getting a song info by song and artist name.

        :param song: song name
        :param artist: artist name
        :return: list of Song objects
        """
        self.logger.info(f"Getting song info for: '{artist} - {song}'")

        # Checking if song is in cache
        if f"{song.lower()}+{artist.lower()}" in self.CACHE["songs"]:
            return self.CACHE["songs"][f"{song.lower()}+{artist.lower()}"]
        self._lock.acquire()

        try:
            tracks = self._sp.search(song, limit=50)["tracks"]["items"]
        except Exception as e:
            self.logger.error(str(e))
            if not self._disable_exceptions:
                raise
            else:
                return []

        self._lock.release()

        parsed = self._parse_artist(artist)
        res = None
        should_stop = False
        for tr in tracks:
            artists = tr["artists"]
            for ar in artists:
                if artist.lower() in ar["name"].lower():
                    res = tr
                    ar_obj = self.get_artist_info(ar["name"])
                    SpotifySearcher._set_genre(res, ar_obj)
                    should_stop = True
                    break
            if should_stop:
                break
            if self._in_artists(parsed, artists):
                res = tr
                break
        if res:
            song_res = Song(res)
            SpotifySearcher.CACHE_LOCK.acquire()
            self.CACHE["songs"][f"{song.lower()}+{artist.lower()}"] = song_res
            SpotifySearcher.CACHE_LOCK.release()
            self.logger.info(f"Got song info for '{artist} - {song}' successfully")
            return song_res

    def get_album_info(self, album, artist):
        """
        Get an album by its name and artist name.

        :param album: album name
        :param artist: artist name
        :return: Album object
        """
        # Checking if song is in cache
        if f"{album}+{artist}" in self.CACHE["albums"]:
            return self.CACHE["albums"][f"{album}+{artist}"]
        self._lock.acquire()

        try:
            tracks = self._sp.search(album, limit=50)["tracks"]["items"]
        except Exception as e:
            self.logger.error(str(e))
            if not self._disable_exceptions:
                raise
            else:
                return []

        self._lock.release()
        res = None
        parsed = self._parse_artist(artist)
        al = None
        for tr in tracks:
            al = tr["album"]
            if album.lower() == al["name"].lower() and self._is_artist(al["artists"], artist):
                res = self._sp.album(al["id"])
                break
            elif album.lower() == al["name"].lower() and self._in_artists(parsed, al["artists"]):
                res = self._sp.album(al["id"])
                break

        if res:
            artist_obj = self._get_artist_from_list(res["artists"], artist)
            SpotifySearcher.CACHE_LOCK.acquire()
            SpotifySearcher.CACHE_LOCK.release()
            SpotifySearcher._set_genre(res, artist_obj)
            self._set_tracks_for_album(res, artist_obj)
            album_res = Album(res)
            SpotifySearcher.CACHE_LOCK.acquire()
            self.CACHE["albums"][f"{album}+{artist}"] = album_res
            SpotifySearcher.CACHE_LOCK.release()
            return album_res

    def _get_artist_from_list(self, artists, artist):
        """
        Get Artist object from list of artist dicts by artist name.

        :param artists: artist dicts
        :param artist: artist name
        :return: Artist object
        """
        for a in artists:
            if a["name"].lower() == artist.lower():
                res = self.get_artist_info(artist)
                return res

    def get_artist_info(self, artist):
        """
        Get an Artist object by an artist name.

        :param artist: artist name
        :return: Artist object
        """
        self.logger.info(f"Getting info of artist: '{artist}'")
        if artist.lower() in self.CACHE["artists"]:
            return self.CACHE["artists"][artist.lower()]

        self._lock.acquire()
        try:
            tracks = self._sp.search(artist, limit=50)["tracks"]["items"]
        except Exception as e:
            self.logger.error(str(e))
            if not self._disable_exceptions:
                raise
            else:
                return []

        self._lock.release()
        res = None
        done = False
        for tr in tracks:
            artists = tr["artists"]
            for a in artists:
                if artist.lower() == a["name"].lower():
                    self._lock.acquire()

                    try:
                        res = self._sp.artist(a["id"])
                    except Exception as e:
                        self.logger.error(str(e))
                        if not self._disable_exceptions:
                            raise

                    self._lock.release()
                    done = True
                    break
                if done:
                    break
        if res:
            self.logger.info(f"Got info of artist: '{artist}'")
            artist_res = Artist(res)
            SpotifySearcher.CACHE_LOCK.acquire()
            self.CACHE["artists"][artist.lower()] = artist_res
            SpotifySearcher.CACHE_LOCK.release()
            return artist_res

    def get_similar_artists(self, artist, num_of_similar=20):
        """
        Getting similar artists for a given artist name.

        :param artist: artist name
        :param num_of_similar: number of requested similar
        :return: List of Artist objects
        """
        self.logger.info(f"Getting similar artists for: '{artist}'")
        artist_obj = self.get_artist_info(artist)
        self._lock.acquire()

        try:
            similar_artists = self._sp.artist_related_artists(artist_obj.ID)["artists"]
        except Exception as e:
            self.logger.error(str(e))
            if not self._disable_exceptions:
                raise
            else:
                return []

        self._lock.release()
        res = []
        parsed = 0
        while True:
            # We parsed all requested similar artists
            if parsed >= num_of_similar:
                break
            sim_ar = similar_artists[0]
            self.logger.info(f"Getting similar artist: '{sim_ar['name']}'")

            SpotifySearcher.CACHE_LOCK.acquire()
            # Checking for artist in the cache
            if sim_ar['name'] in self.CACHE["artists"]:
                new_sim_ar = self.CACHE["artists"][sim_ar['name']]
            else:
                new_sim_ar = Artist(sim_ar)
                self.CACHE["artists"][new_sim_ar.Name] = new_sim_ar
            SpotifySearcher.CACHE_LOCK.release()

            res += [new_sim_ar]

            self._lock.acquire()

            if (parsed + 1) < num_of_similar:
                try:
                    similar_artists = similar_artists[1:] + self._sp.artist_related_artists(sim_ar["id"])["artists"]
                except Exception as e:
                    self.logger.error(str(e))
                    if not self._disable_exceptions:
                        raise

            self._lock.release()
            parsed += 1

        return res

    def get_artists_top_tracks(self, artist, country="US"):
        """
        Get top tracks for artist in a given country.

        :param artist: artist name
        :param country: country name
        :return: artists top tracks in a list of Song objects
        """
        artist_obj = self.get_artist_info(artist)
        country_code = SpotifySearcher._get_country_code_by_name(country)
        self._lock.acquire()

        try:
            top_tracks = self._sp.artist_top_tracks(artist_obj.ID, country=country_code)
        except Exception as e:
            self.logger.error(str(e))
            if not self._disable_exceptions:
                raise
            else:
                return []

        self._lock.release()
        res = []
        for song in top_tracks["tracks"]:
            self.logger.info(f"Got top track: {song['name']}")
            song["genres"] = artist_obj.Genres
            sim_song = Song(song)

            SpotifySearcher.CACHE_LOCK.acquire()
            self.CACHE["songs"][f"{sim_song.Name}+{artist_obj.Name}"] = sim_song
            SpotifySearcher.CACHE_LOCK.release()
            res += [sim_song]

        return res

    def get_similar_tracks(self, song, artist, num_of_similar=20):
        """
        Get similar tracks for a given song and artist.

        :param song: song name
        :param artist: artist name
        :param num_of_similar: number of requested similar songs
        :return: list of Song objects that are similar songs
        """
        if num_of_similar == 0:
            return []

        self.logger.info(f"Getting similar tracks for: '{artist} - {song}'")
        if not num_of_similar:
            return []

        song_obj = self.get_song_info(song, artist)
        tracks = self.get_recommendations(songs_ids=[song_obj.ID])["tracks"][:num_of_similar]
        workers = []
        res = []
        lock = Lock()

        # Running the getting of the songs in threads
        for track in tracks:
            worker = Thread(target=self._set_similar_song, args=(track, res, lock))
            worker.start()
            workers += [worker]
        for t in workers:
            t.join()
        res += self.get_similar_tracks(song, artist, num_of_similar=(num_of_similar - len(res)))
        return res

    def _set_similar_song(self, track, res, lock):
        """
        Setting result of a similar track to res list.

        :param track: track name
        :param res: list of resulted similar Song objects
        :param lock: lock for multithreading
        """
        artist_n = track["artists"][0]["name"]
        track["duration"] = track["duration_ms"] / 1000
        artist_info = self.get_artist_info(artist_n)
        if not artist_info:
            return
        track["genres"] = artist_info.Genres
        self.logger.info(f"Set similar song: {track['artists'][0]['name']} - {track['name']}")
        lock.acquire()
        res += [Song(track)]
        lock.release()

    def get_songs_by_genres(self, genres):
        """
        By a given list of genres, get songs in the genre.

        :param genres: list of genres
        :return: list of Song objects that are in the genre
        """
        self.logger.info(f"Getting songs for the genres: {', '.join(genres)}")
        recommendations = self.get_recommendations(genres_list=genres)
        songs = []
        for track in recommendations["tracks"]:
            artist_name = track['artists'][0]['name']
            self.logger.info(f"Got Track: {artist_name} - {track['name']}")
            song = self.get_song_info(track['name'], artist_name)
            if song:
                songs += [song]

        return songs

    def get_playlists_by_country(self, country, limit=20):
        """
        Get playlists by a given country.

        :param country: country name
        :param limit: limit of number of playlists
        :return: list of Playlist objects
        """
        if limit > 50:
            raise Exception(f"The limit '{limit}' is not supported. Maximum value for limit is 50!")

        country = pycountry.countries.get(name=country)
        if country is None:
            return
        country_code = country.alpha_2
        if country_code in SpotifySearcher.COUNTRY_CODES:
            featured_playlists = self._sp.featured_playlists(country=country_code, limit=limit)
            new_playlists = self._get_playlists_with_songs(featured_playlists["playlists"]["items"])
            return [Playlist(playlist) for playlist in new_playlists]

    def _get_playlists_with_songs(self, playlists):
        """
        Setting tracks to all playlists extracted.

        :param playlists: list of playlist dicts
        """

        def song_getter(playlist):
            for item in playlist["tracks"]["items"]:
                song = item["track"]
                song = self._sp.track(song["id"])
                song["duration"] = song["duration_ms"] / 1000
                artist = song["album"]["artists"][0]["name"]
                artist = self.get_artist_info(artist)
                if artist:
                    song["genres"] = artist.Genres
                    playlist["genres"] = set(list(playlist["genres"]) + artist.Genres)
                    new_song = Song(song)

                    SpotifySearcher.CACHE_LOCK.acquire()
                    SpotifySearcher.CACHE["songs"][f"{new_song.Name.lower()}+{artist.Name.lower()}"] = new_song
                    SpotifySearcher.CACHE_LOCK.release()

                    playlist["songs"] += [new_song]

        threads = []
        new_playlists = []
        for playlist in playlists:
            playlist = self._sp.playlist(playlist["id"])
            new_playlists += [playlist]
            playlist["songs"] = []
            playlist["genres"] = set()
            t = Thread(target=song_getter, args=(playlist, ))
            t.start()
            threads += [t]
        for t in threads:
            t.join()
        return new_playlists

    def get_recommendations(self, artists_ids=None, songs_ids=None, genres_list=None):
        """
        Get recommendation by given ids - only one supported at a time.

        :param artists_ids: list of artist ids
        :param songs_ids: list of song ids
        :param genres_list: list of genre ids
        :return: dict of recommended songs
        """
        recommendations = None
        self._lock.acquire()
        try:
            if songs_ids:
                recommendations = self._sp.recommendations(seed_tracks=songs_ids)
            if artists_ids:
                recommendations = self._sp.recommendations(seed_artists=artists_ids)
            if genres_list:
                recommendations = self._sp.recommendations(seed_genres=genres_list)
        except Exception as e:
            self.logger.error(str(e))
            if not self._disable_exceptions:
                raise
            else:
                return []
        self._lock.release()
        return recommendations

    @classmethod
    def _is_artist(cls, artists, artist):
        """
        Check if artist is in a list of artists.

        :param artists: list of artists
        :param artist: artist name
        :return: True - artist is an artist in artists; False - O.W.
        """
        for ar in artists:
            if artist.lower() in ar["name"].lower():
                return True

        return False

    @staticmethod
    def _set_genre(res, artist):
        """
        Set genre for a given result.

        :param res: result
        :param artist: Artis object
        """
        res["genres"] = artist.Genres

    @classmethod
    def _parse_artist(cls, artist):
        """
        Parses artist's name and gets only the main artist of the song (no ft. or &)
        :param artist: artist name
        :return: main artist name
        """
        res = artist.strip().lower()
        return [f.strip() for r in res.split("&") for t in r.split(",") for f in t.split("x")]

    @classmethod
    def _in_artists(cls, parsed, artists):
        """
        Check if all artist are in another artists list

        :param parsed: one artists list
        :param artists: other artists list
        :return: True - artists are at 'artists' are also at 'parsed' ; False - O.W.
        """
        n = 0
        for artist in artists:
            if artist["name"] in parsed:
                n += 1

        return n == len(parsed)

    def _set_tracks_for_album(self, album, artist):
        """
        Get all Song objects in the album and set them to the album.

        :param album: album dict
        :param artist: artist name
        """
        lock = Lock()

        def get_song_runner(song):
            res = self.get_song_info(song, artist.Name)
            lock.acquire()
            tracks = get_song_runner.__getattribute__("tracks")
            tracks += [res]
            lock.release()

        get_song_runner.__setattr__("tracks", [])
        threads = []
        for track in album["tracks"]["items"]:
            t = Thread(target=get_song_runner, args=(track["name"],))
            t.start()
            threads += [t]
        for t in threads:
            t.join()
        album["tracks"]["items"] = get_song_runner.__getattribute__("tracks")

    @staticmethod
    def _get_country_code_by_name(country):
        """
        Gets country code by name: united states -> US

        :param country: country name
        :return: country code
        """
        country_obj = pycountry.countries.get(country)
        return country_obj.alpha_2
