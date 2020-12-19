from threading import Thread, Lock

from gekko import GEKKO

from model.logger.spotify_logger import Logger
from model.playlist_creator.playlist_creator_interface import IPlaylistCreator
from model.playlist_creator.playlist_modes import PlaylistModes


class PlaylistCreatorBase(IPlaylistCreator):
    """
    A class that gets a music song and creates a playlist from it in various ways.
    """

    def __init__(self, music_searcher, mode=PlaylistModes.SONGS):
        """
        :param music_searcher: A IMusicSearcher object
        :param mode: mode to create a playlist by
        """
        self._mode = mode
        self._music_searcher = music_searcher

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

        Logger().info("Creating playlist by songs...")
        if append:
            Logger().info("Appending all similar songs")
            self._append_all_similar_songs(songs)
            Logger().info("Finished appending all similar songs")

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
            Logger().info(f"Adding similar for: {artist} - {name}")
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
        pass

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
            Logger().info("Still waiting to finish...")
