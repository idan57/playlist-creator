import json

from model.playlist_creator.playlist_creator_base import *
from model.runners.runner_interface import IRunner
from model.savers.playlist_saver import PlaylistSaver
from model.songs_directory.directory_reader import DirectoryReader
from model.songs_searchers.spotify_searcher import SpotifySearcher


class PlaylistCreatorRunner(IRunner):
    def __init__(self):
        self._logger = Logger()

    def run(self, args):
        client_id = '03e69fa5ec5d479a82bb066e019a722b'
        client_secret = '0ae6f5bb823a4ac281dc1b7c07180706'
        searcher = SpotifySearcher(client_id, client_secret)
        self._logger.beautiful_info("SpotifySearcher Initialization Step Complete - Gathering Data")
        mode = -1
        songs = None
        artists = None
        albums = None
        genres = None
        if args.songs_path:
            songs = []
            reader = DirectoryReader()
            songs_obj = reader.get_songs(args.songs_path)
            for obj in songs_obj:
                song = searcher.get_song_info(obj["name"], obj["artist"])
                if song:
                    songs += [song]
            mode = PlaylistModes.SONGS
        if args.albums_list:
            with open(args.albums_list, 'r') as f:
                albums_lines = f.readlines()
            albums = []
            for album_n_artist in albums_lines:
                album, artist = album_n_artist.replace("\n", "").split()
                albums += [searcher.get_album_info(album, artist)]
            if mode == -1:
                mode = PlaylistModes.ALBUMS
        if args.artists_list:
            with open(args.artists_list, 'r') as f:
                artists_lines = f.readlines()
            artists = []
            for artist in artists_lines:
                artist = artist.replace("\n", "")
                artists += [searcher.get_artist_info(artist)]
            if mode == -1:
                mode = PlaylistModes.ARTISTS
        if args.genres_list:
            with open(args.genres_list, 'r') as f:
                genres = json.load(f)

            if mode == -1:
                mode = PlaylistModes.GENRES
        min_songs = args.minimum_songs
        min_time = args.down * 60
        max_time = args.up * 60
        p = PlaylistCreatorBase(searcher, mode=mode, country=args.country)
        res = []
        msg = "Playlist Creation Step: \n"
        if mode == PlaylistModes.SONGS:
            self._logger.beautiful_info(f"-- SONGS --\n{msg} Minimum Time: {min_time}\n Maximum Time: {max_time}\n"
                                        f" Number of songs required: {min_songs}")
            res = p.create_playlist(songs, min_time=min_time, max_time=max_time, genres=genres,
                                    artists=artists, num_of_songs=min_songs)
        if mode == PlaylistModes.ARTISTS:
            if genres:
                self._logger.beautiful_info(f"-- ARTISTS --\n{msg} Minimum Time: {min_time}\n Maximum Time: {max_time}\n"
                                            f" Genres: {', '.join(genres)}\n")
            else:
                self._logger.beautiful_info(
                    f"-- ARTISTS --\n{msg} Minimum Time: {min_time}\n Maximum Time: {max_time}\n")
            res = p.create_playlist(artists, min_time=min_time, max_time=max_time, genres=genres)
        if mode == PlaylistModes.GENRES:
            self._logger.beautiful_info(f"-- GENRES --{msg} Minimum Time: {min_time}\n Maximum Time: {max_time}\n")
            res = p.create_playlist(genres, min_time=min_time, max_time=max_time)
        if mode == PlaylistModes.ALBUMS:
            self._logger.beautiful_info(f"-- ALBUMS --{msg} Minimum Time: {min_time}\n Maximum Time: {max_time}\n"
                                        f" Number of songs required: {min_songs}")
            res = p.create_playlist(albums, min_time=min_time, max_time=max_time, genres=genres,
                                    artists=artists)
        saver = PlaylistSaver()
        saver.save(res)
