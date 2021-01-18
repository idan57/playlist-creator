import time
from collections import defaultdict
from threading import Thread, Lock

import numpy as np
from dateutil.parser import parse

from model.logger.spotify_logger import Logger
from model.optimizer.avg_rating_optimizer import AvgRatingOptimizer
from model.playlist_creator.playlist_creator_interface import IPlaylistCreator
from model.playlist_creator.playlist_modes import PlaylistModes


class PlaylistCreatorBase(IPlaylistCreator):
    """
    A class that gets a music song and creates a playlist from it in various ways.
    """

    def __init__(self, music_searcher, mode=PlaylistModes.SONGS, num_of_can=50, country="US"):
        """
        :param music_searcher: A IMusicSearcher object
        :param mode: mode to create a playlist by
        """
        self._mode = mode
        self._music_searcher = music_searcher
        self.logger = Logger()
        self._num_of_can = num_of_can
        self._country = country

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

    def _songs_creator(self, songs, genres=None, min_time=0, max_time=2400,
                       append=True, artists=None, num_of_songs=0):
        """
        Create a playlist from songs

        :param songs: songs to create a playlist from
        :param genres: genres wanted for the songs
        :param min_time: minimum time required for a playlist
        :param max_time: maximum time required for the playlist
        :param append: append similar songs
        :return:
        """
        self.logger.info("Creating playlist by songs...")
        self.logger.beautiful_info(f"Optimizing {len(songs)} songs!!!")
        initial_songs = [s for s in songs]
        if append:
            self.logger.info("Appending all similar songs")
            self._append_all_similar_songs(songs)
            self.logger.info(f"Finished appending all similar songs, got {len(songs)} songs")
            self._num_of_can = int((2 / 3) * len(songs))
            songs = self._get_similar(songs)

        PlaylistCreatorBase._add_weight_to_songs(songs)

        songs = PlaylistCreatorBase._optimize_weight(songs)
        if self._mode == PlaylistModes.SONGS:
            songs += [s for s in initial_songs if s not in songs]

        return PlaylistCreatorBase._optimize_popularity(songs + initial_songs, min_time, max_time,
                                                        genres, artists, initial_songs, num_of_songs)

    def _append_all_similar_songs(self, songs):
        """
        Get more similar songs from given songs.

        :param songs: songs
        :return: appended list of songs
        """
        lock = Lock()

        def set_simillar_songs(name, artist, songs_list):
            try:
                res = self._music_searcher.get_similar_tracks(name, artist, num_of_similar=50)
                self.logger.info(f"Adding similar for: {artist} - {name}")
                lock.acquire()
                songs_list += res
            finally:
                lock.release()

        PlaylistCreatorBase._run_in_thread_loop(songs, target=set_simillar_songs,
                                                args_method=lambda song, songs_list: (song.Name, song.Artists[0],
                                                                                      songs_list))

    @staticmethod
    def _add_weight_to_songs(songs):
        """
        Add weight to songs by their popularity and by the artists that are in the song

        :param songs: Songs list
        """
        Logger().info("Calculating weights for songs...")
        same_artists = {}
        for song in songs:
            for artist in song.Artists:
                if artist not in same_artists:
                    same_artists[artist] = []
                same_artists[artist] += [song]

        Logger().info("Setting weights for songs...")
        PlaylistCreatorBase._set_weights(same_artists)
        Logger().info("Setting weights for songs is done.")

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
                val[i].set_weight(val[i].Weight + ((val_len - i) / val_len) * val[i].Popularity)

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
        third = int(len(songs) * (2 / 3))
        return songs[:third]

    @staticmethod
    def _optimize_popularity(songs, min_time, max_time, genres, artists, initial_songs, num_of_songs):
        """
        Optimize songs by their popularity.

        :param songs: songs list
        :param min_time: min time for playlist
        :param max_time: max time for playlist
        :param genres: required genres
        :param initial_songs: songs before append
        :param num_of_songs: at number of songs to take from initial_songs
        :return: indexes of songs to take to playlist
        """
        optimizer = AvgRatingOptimizer(songs)
        optimizer.add_min_time_constraint(min_time)
        optimizer.add_max_time_constraint(max_time)
        if genres:
            for genre, num in genres.items():
                optimizer.add_genres_constraint(genre, num)
        if artists:
            optimizer.add_artists_constraint(artists)
        if num_of_songs:
            optimizer.add_atleast_given_songs(initial_songs, num_of_songs)
        return optimizer.solve()

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
        artists = [a for a in artists if a is not None]
        self.logger.beautiful_info(f"Optimizing {len(artists)} artists!!!")
        top_tracks = self._get_top_tracks(artists)
        artists_names = [ar.Name for ar in artists]

        more_artists = self._get_more_artists(top_tracks, artists_names)

        more_artists = [a for a in more_artists if a is not None]
        actual_artists = self._get_similar(more_artists)
        actual_artists = [a for a in actual_artists if a is not None]

        top_tracks += self._get_top_tracks(actual_artists)
        self.logger.info(f"Got songs top tracks for artists, got {len(top_tracks)} songs")

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
            res = self._music_searcher.get_artists_top_tracks(name, country=self._country)
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
        genres_keys = [gen for gen in genres.keys()]
        songs = []
        while i < n:
            three = []
            for j in range(i, min(i + 3, n)):
                three += [genres_keys[j]]
            i += 3
            songs += self._music_searcher.get_songs_by_genres(genres=three)
        self.logger.info(f"Got songs for genres, got {len(songs)} songs")
        return self._songs_creator(songs, append=False, genres=genres, **kwargs)

    def _albums_creator(self, albums, **kwargs):
        """
        Create playlist from albums.

        :param albums: Albums list
        :param kwargs: arguments
        :return: playlist
        """
        albums = self._get_similar(albums)
        songs = []
        for album in albums:
            songs += album.Tracks
        self.logger.info(f"Got songs for albums, got {len(songs)} songs")
        return self._songs_creator(songs, append=False, **kwargs)

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
            if item:
                th = Thread(target=target, args=args_method(item, list_to_run))
                th.start()
                threads += [th]

        for t in threads:
            t.join()
            Logger().info("Still waiting to finish...")

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

        if self._mode == PlaylistModes.SONGS:
            return self._get_candidates_for_songs(music_source, genres_counts)
        if self._mode == PlaylistModes.ARTISTS:
            return self._get_candidates_for_artists(music_source, genres_counts)
        if self._mode == PlaylistModes.ALBUMS:
            return self._get_candidates_for_albums(music_source, genres_counts)

    def _get_candidates_for_songs(self, songs, genres_counts):
        """
        Get candidates by songs.

        :param songs: songs data
        :param genres_counts: count of generes
        :return: candidates
        """
        num_of_cat = len(genres_counts)
        num_of_music = len(songs)
        vectors = np.zeros((num_of_music, num_of_cat + 1))
        for music, vec in zip(songs, vectors):
            vec[0] = music.Popularity
            for genre in music.Genres:
                cost, index = genres_counts[genre]
                if (index + 1) < (num_of_cat + 1):
                    vec[index + 1] = cost

        return self._get_similar_from_vecs(vectors, songs, num_of_music)

    def _get_candidates_for_artists(self, artists, genres_counts):
        """
        Get candidates by artists.

        :param artists: songs data
        :param genres_counts: count of generes
        :return: candidates
        """
        num_of_cat = len(genres_counts)
        num_of_music = len(artists)
        vectors = np.zeros((num_of_music, num_of_cat + 2))
        for music, vec in zip(artists, vectors):
            vec[0] = music.Popularity
            vec[1] = music.NumOfFollowers
            for genre in music.Genres:
                cost, index = genres_counts[genre]
                vec[index + 2] = cost

        return self._get_similar_from_vecs(vectors, artists, num_of_music)

    def _get_candidates_for_albums(self, albums, genres_counts):
        """
        Get candidates by albums.

        :param albums: songs data
        :param genres_counts: count of genres
        :return: candidates
        """
        num_of_cat = len(genres_counts)
        num_of_music = len(albums)
        vectors = np.zeros((num_of_music, num_of_cat + 4))
        times = []
        for music, vec in zip(albums, vectors):
            vec[0] = music.Popularity
            vec[1] = music.NumOfTracks
            vec[2] = music.AvgTracksPopularity
            album_time = parse(music.ReleaseDate)
            actual_time = time.mktime(album_time.timetuple())
            times += [actual_time]
            vec[3] = actual_time
            for genre in music.Genres:
                cost, index = genres_counts[genre]
                vec[index + 4] = cost
        times = np.array(times)
        mean, std = times.mean(), times.std()
        for vec in vectors:
            vec[3] = (vec[3] - mean) / std

        return self._get_similar_from_vecs(vectors, albums, num_of_music)

    def _get_similar_from_vecs(self, vectors, music_source, num_of_music):
        """
        Get candidates by doing evaluating the dot product for all music sources.

        :param vectors: vectors after weighting
        :param music_source: the music source
        :param num_of_music: number of music objects
        :return: candidates
        """
        for i in range(num_of_music):
            mat_without_i = np.array(vectors[:i].tolist() + vectors[i + 1:].tolist())
            music_source[i].set_similarity((mat_without_i @ vectors[i].T).sum())

        music_source.sort(key=lambda m: m.Similarity)
        return music_source[:self._num_of_can]
