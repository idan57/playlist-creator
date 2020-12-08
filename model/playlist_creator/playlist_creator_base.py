from threading import Thread, Lock

from gekko import GEKKO

from model.logger.spotify_logger import Logger
from model.playlist_creator.playlist_creator_interface import IPlaylistCreator
from model.playlist_creator.playlist_modes import PlaylistModes


class PlaylistCreatorBase(IPlaylistCreator):
    def __init__(self, music_searcher, mode=PlaylistModes.SONGS):
        self._mode = mode
        self._music_searcher = music_searcher

    def create_playlist(self, music_source, **kwargs):
        if self._mode == PlaylistModes.SONGS:
            return self._songs_creator(music_source, **kwargs)
        elif self._mode == PlaylistModes.ARTISTS:
            return self._artists_creator(music_source)

    def _songs_creator(self, songs, min_time=0, max_time=2400):

        Logger().info("Creating playlist by songs...")
        Logger().info("Appending all similar songs")
        self._append_all_similar_songs(songs)
        Logger().info("Finished appending all similar songs")

        self._add_weight_to_songs(songs)

        songs_vars = PlaylistCreatorBase._optimize_weight(songs)
        songs = PlaylistCreatorBase._get_songs_after_optimization(songs_vars, songs)

        songs_vars = PlaylistCreatorBase._optimize_popularity(songs, min_time, max_time)
        songs = PlaylistCreatorBase._get_songs_after_optimization(songs_vars, songs)
        return songs

    def _add_weight_to_songs(self, songs):
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
        for val in same_artists.values():
            val.sort(key=lambda x: x.Popularity)
            val_len = len(val)
            for i in range(val_len):
                val[i].set_weight(val[i].Weight + (val_len - i) / val_len)

    @staticmethod
    def _optimize_weight(songs):
        m = GEKKO()
        songs_vars = [m.Var(lb=0, ub=1, integer=True) for i in range(len(songs))]
        songs_vars_sum = m.sum(songs_vars)
        weight_params = [m.Param(song.Weight) for song in songs]
        weight = m.sum([song_para * s_var for s_var, song_para in zip(songs_vars, weight_params)])
        m.Equation([songs_vars_sum <= 30, ])
        m.Maximize(weight)
        m.solve()
        return songs_vars

    @staticmethod
    def _optimize_popularity(songs, min_time, max_time):
        m = GEKKO()
        songs_vars = [m.Var(lb=0, ub=1, integer=True) for i in range(len(songs))]
        songs_vars_sum = m.sum(songs_vars)
        popularity_params = [m.Param(song.Popularity) for song in songs]
        duration_params = [m.Param(song.Duration) for song in songs]
        avg_popularity = m.sum([(song_para * s_var) / max(1, songs_vars_sum)
                                for s_var, song_para in zip(songs_vars, popularity_params)])
        sum_time = m.sum([song_para * s_var for s_var, song_para in zip(songs_vars, duration_params)])
        m.Equation([sum_time <= max_time, sum_time >= min_time])
        m.Maximize(avg_popularity)
        m.solve()
        return songs_vars

    def _artists_creator(self, artists):
        pass

    @classmethod
    def _get_songs_after_optimization(cls, songs_vars, songs):
        songs_after_opt = []
        for song, song_var in zip(songs, songs_vars):
            if song_var.VALUE == 1.0:
                songs_after_opt += [song]
        return songs_after_opt

    def _append_all_similar_songs(self, songs):
        lock = Lock()
        threads = []

        def set_simillar_songs(name, artist, songs_list):
            res = self._music_searcher.get_similar_tracks(name, artist)
            Logger().info(f"Adding similar for: {artist} - {name}")
            lock.acquire()
            songs_list += res
            lock.release()

        for song in songs:
            th = Thread(target=set_simillar_songs, args=(song.Name, song.Artists[0], songs))
            th.start()
            threads += [th]

        for t in threads:
            t.join(timeout=2400)
            Logger().info("Still waiting to get all similar songs...")
