from collections import defaultdict
from threading import Thread, Lock
import numpy as np
from dateutil.parser import parse
import time

from gekko import GEKKO

from model.logger.spotify_logger import Logger
from model.playlist_creator.playlist_creator_interface import IPlaylistCreator
from model.playlist_creator.playlist_modes import PlaylistModes


class PlaylistCreatorBase(IPlaylistCreator):
    """
    A class that gets a music song and creates a playlist from it in various ways.
    """

    def __init__(self, music_searcher, mode=PlaylistModes.SONGS, num_of_can=50):
        """
        :param music_searcher: A IMusicSearcher object
        :param mode: mode to create a playlist by
        """
        self._mode = mode
        self._music_searcher = music_searcher
        self.logger = Logger()
        self._num_of_can = num_of_can

    def create_playlist(self, music_source, **kwargs):
        """
        Create a playlist from a given music source.

        :param music_source: music source
        :param kwargs: any argument needed for a specific mode
        :return: playlist
        """
        if self._mode == PlaylistModes.SONGS:
            return self._songs_creator(music_source, **kwargs)
        elif self._mode == PlaylistModes.ARTISTS:
            return self._artists_creator(music_source, **kwargs)
        elif self._mode == PlaylistModes.GENRES:
            return self._genres_creator(music_source, **kwargs)
        elif self._mode == PlaylistModes.ALBUMS:
            return self._albums_creator(music_source, **kwargs)

    def _songs_creator(self, songs, genres=None, min_time=0, max_time=2400, append=True):
        """
        Create a playlist from songs

        :param songs: songs to create a playlist from
        :param genres: genres wanted for the songs
        :param min_time: minimum time required for a playlist
        :param max_time: maximum time required for the playlist
        :param append:
        :return:
        """
        if genres:
            genres = []

        self.logger.info("Creating playlist by songs...")
        if append:
            self.logger.info("Appending all similar songs")
            self._append_all_similar_songs(songs)
            self.logger.info("Finished appending all similar songs")
            songs = self._get_similar(songs)

        PlaylistCreatorBase._add_weight_to_songs(songs)

        songs = PlaylistCreatorBase._optimize_weight(songs)

        songs_vars = PlaylistCreatorBase._optimize_popularity(songs, min_time, max_time)
        songs = PlaylistCreatorBase._get_songs_after_optimization(songs_vars, songs)
        return songs

    def _append_all_similar_songs(self, songs):
        """
        Get more similar songs from given songs.

        :param songs: songs
        :return: appended list of songs
        """
        lock = Lock()

        def set_simillar_songs(name, artist, songs_list):
            res = self._music_searcher.get_similar_tracks(name, artist)
            self.logger.info(f"Adding similar for: {artist} - {name}")
            lock.acquire()
            songs_list += res
            lock.release()

        PlaylistCreatorBase._run_in_thread_loop(songs, target=set_simillar_songs,
                                                args_method=lambda song, songs: (song.Name, song.Artists[0], songs))

    @staticmethod
    def _add_weight_to_songs(songs):
        """
        Add weight to songs by their popularity and by the artists that are in the song

        :param songs: Songs list
        """
        Logger().logger.info("Calculating weights for songs...")
        same_artists = {}
        for song in songs:
            for artist in song.Artists:
                if artist not in same_artists:
                    same_artists[artist] = []
                same_artists[artist] += [song]

        Logger().logger.info("Setting weights for songs...")
        PlaylistCreatorBase._set_weights(same_artists)
        Logger().logger.info("Setting weights for songs is done.")

    @staticmethod
    def _set_weights(same_artists):
        """
        Set the weight for the songs by a given dict of artist -> Songs list.

        :param same_artists: dict
        """
        for val in same_artists.values():
            val.sort(key=lambda x: x.Popularity, reverse=True)
            val_len = len(val)
            for i in range(val_len):
                val[i].set_weight(val[i].Weight + (val_len - i) / val_len)

    @staticmethod
    def _optimize_weight(songs):
        """
        Get optimal weighted songs.

        :param songs: list of Songs
        :return: optimal weighted songs
        """
        if len(songs) < 30:
            return songs
        songs.sort(key=lambda x: x.Weight, reverse=True)
        return songs[:30]

    @staticmethod
    def _optimize_popularity(songs, min_time, max_time):
        """
        Optimize songs by their popularity.

        :param songs: songs list
        :param min_time: min time for playlist
        :param max_time: max time for playlist
        :return: indexes of songs to take to playlist
        """
        m = GEKKO()
        songs_vars = [m.Var(lb=0, ub=1, integer=True) for i in range(len(songs))]
        popularity_params = [m.Param(song.Popularity) for song in songs]
        duration_params = [m.Param(song.Duration) for song in songs]
        avg_popularity = m.sum([(song_para * s_var) / max(1, sum([song.VALUE.value for song in songs_vars]))
                                for s_var, song_para in zip(songs_vars, popularity_params)])
        sum_time = m.sum([song_para * s_var for s_var, song_para in zip(songs_vars, duration_params)])
        m.Equation([sum_time <= max_time, sum_time >= min_time])
        m.options.SOLVER = 1
        m.Maximize(avg_popularity)
        m.solve()
        return songs_vars

    @classmethod
    def _get_songs_after_optimization(cls, songs_vars, songs):
        """
        Get songs chosen by optimizer.

        :param songs_vars: list of 1s and 0s (1 if to take the song and 0 O.W.)
        :param songs: Songs list
        :return: songs after filtering
        """
        songs_after_opt = []
        for song, song_var in zip(songs, songs_vars):
            if song_var.VALUE.value[0] == 1.0:
                songs_after_opt += [song]
        return songs_after_opt

    def _artists_creator(self, artists, **kwargs):
        """
        Create a playlist by artists.

        :param artists: list of Artists
        :param kwargs: any argument required for creating playlist by songs
        :return: playlist
        """
        top_tracks = self._get_top_tracks(artists)
        artists_names = [ar.Name for ar in artists]

        more_artists = self._get_more_artists(top_tracks, artists_names)

        top_tracks += self._get_top_tracks(more_artists)

        PlaylistCreatorBase._set_weight_by_artist(top_tracks, artists)

        return self._songs_creator(top_tracks, append=False, **kwargs)

    def _get_top_tracks(self, artists):
        """
        Get top tracks by given list of artists.

        :param artists: Artists list
        :return: top tracks for all artists
        """
        lock = Lock()

        def set_top_tracks(name):
            res = self._music_searcher.get_artists_top_tracks(name)
            Logger().info(f"Adding similar for: {name}")
            lock.acquire()
            tracks = set_top_tracks.__getattribute__("tracks")
            tracks += res
            lock.release()

        set_top_tracks.__setattr__("tracks", [])
        PlaylistCreatorBase._run_in_thread_loop(artists, target=set_top_tracks,
                                                args_method=lambda artist, _: (artist.Name,))

        return set_top_tracks.__getattribute__("tracks")

    def _get_more_artists(self, top_tracks, artists_names):
        """
        Get more artists info from top tracks.

        :param top_tracks: top tracks list
        :param artists_names: artists list
        :return: list of Artists
        """
        more_artists = []
        for track in top_tracks:
            for artist in track.Artists:
                if artist not in artists_names:
                    artists_names += [artist]
                    more_artists += [self._music_searcher.get_artist_info(artist)]
        return more_artists

    @staticmethod
    def _set_weight_by_artist(top_tracks, artists):
        """
        Set weight for tracks by number of follower of the artists that sing in the track.

        :param top_tracks: top tracks list
        :param artists: Artists list 
        """
        artists_followers_dict = {artist.Name: artist.NumOfFollowers for artist in artists}
        total_sum_of_followers = sum([artist.NumOfFollowers for artist in artists])

        for track in top_tracks:
            for artist in track.Artists:
                if artist in artists_followers_dict:
                    track.set_weight(track.Weight + (artists_followers_dict[artist] / total_sum_of_followers))

    def _genres_creator(self, genres, **kwargs):
        """
        Create a playlist by genres.

        :param genres: genres to get songs from
        :param kwargs: any argument needed to optimize by songs
        :return: playlist
        """
        i, n = 0, len(genres)
        songs = []
        while i < n:
            three = []
            for j in range(i, min(i + 3, n)):
                three += [genres[j]]
            i += 3
            songs += self._music_searcher.get_songs_by_genres(genres=three)

    def _albums_creator(self, albums, **kwargs):
        """
        Create playlist from albums.

        :param albums: Albums list
        :param kwargs: arguments
        :return: playlist
        """
        albums = self._get_similar(albums)

    @staticmethod
    def _run_in_thread_loop(list_to_run, target, args_method):
        """
        Run in threads an operation (target) on each item in the list.

        :param list_to_run: list to run operations on each element
        :param target: operation to run
        :param args_method: method to get args for the operation
        """
        threads = []
        for item in list_to_run:
            th = Thread(target=target, args=args_method(item, list_to_run))
            th.start()
            threads += [th]

        for t in threads:
            t.join(timeout=2400)
            Logger().logger.info("Still waiting to finish...")

    def _get_similar(self, music_source):
        """
        Get similar music sources as part of the Candidate Generation step.

        :param music_source: music data
        :return: candidates
        """
        self.logger.info("Doing Candidate Generation step")
        if self._mode == PlaylistModes.GENRES or len(music_source) < self._num_of_can:
            return music_source

        genres_counts = defaultdict(lambda: [0, None])
        i = 0
        for music in music_source:
            for genre in music.Genres:
                genres_counts[genre][0] += 1
                if not genres_counts[genre][1]:
                    genres_counts[genre][1] = i
                    i += 1

        num_of_cat = len(genres_counts)
        if self._mode == PlaylistModes.SONGS:
            return self._get_candidates_for_songs(music_source, genres_counts, num_of_cat)
        if self._mode == PlaylistModes.ARTISTS:
            return self._get_candidates_for_artists(music_source, genres_counts, num_of_cat)
        if self._mode == PlaylistModes.ALBUMS:
            return self._get_candidates_for_albums(music_source, genres_counts, num_of_cat)

    def _get_candidates_for_songs(self, songs, genres_counts, num_of_cat):
        """
        Get candidates by songs.

        :param songs: songs data
        :param genres_counts: count of generes
        :param num_of_cat: number of categoriess
        :return: candidates
        """
        num_of_music = len(songs)
        vectors = np.zeros((num_of_music, num_of_cat + 1))
        for music, vec in zip(songs, vectors):
            vec[0] = music.Popularity
            for genre in music.Genres:
                cost, index = genres_counts[genre]
                vec[index + 1] = cost

        return self._get_similar_from_vecs(vectors, songs, num_of_music, num_of_cat)

    def _get_candidates_for_artists(self, artists, genres_counts, num_of_cat):
        """
        Get candidates by artists.

        :param artists: songs data
        :param genres_counts: count of generes
        :param num_of_cat: number of categoriess
        :return: candidates
        """
        num_of_music = len(artists)
        vectors = np.zeros((num_of_music, num_of_cat + 2))
        for music, vec in zip(artists, vectors):
            vec[0] = music.Popularity
            vec[1] = music.NumOfFollowers
            for genre in music.Genres:
                cost, index = genres_counts[genre]
                vec[index + 2] = cost

        return self._get_similar_from_vecs(vectors, artists, num_of_music, num_of_cat)

    def _get_candidates_for_albums(self, albums, genres_counts, num_of_cat):
        """
        Get candidates by albums.

        :param albums: songs data
        :param genres_counts: count of genres
        :param num_of_cat: number of categories
        :return: candidates
        """
        num_of_music = len(albums)
        vectors = np.zeros((num_of_music, num_of_cat + 4))
        for music, vec in zip(albums, vectors):
            vec[0] = music.Popularity
            vec[1] = music.NumOfTracks
            vec[2] = music.AvgTracksPopularity
            album_time = parse(music.ReleaseDate)
            vec[3] = time.mktime(album_time.timetuple())
            for genre in music.Genres:
                cost, index = genres_counts[genre]
                vec[index + 4] = cost

        return self._get_similar_from_vecs(vectors, albums, num_of_music, num_of_cat)

    def _get_similar_from_vecs(self, vectors, music_source, num_of_music, num_of_cat):
        """
        Get candidates by doing evaluating the dot product for all music sources.

        :param vectors: vectors after weighting
        :param music_source: the music source
        :param num_of_music: number of music objects
        :param num_of_cat: number of categories
        :return: candidates
        """
        for i in range(num_of_music):
            mat_without_i = np.array(vectors[:i].tolist() + [0 for _ in range(num_of_cat)] + vectors[i + 1:].tolist())
            music_source[i].set_similarity((mat_without_i @ vectors[i].T).sum())

        music_source.sort(key=lambda m: m.Similarity)
        return music_source[:self._num_of_can]
