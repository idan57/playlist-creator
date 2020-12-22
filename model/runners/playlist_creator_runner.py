import json

import numpy as np

from model.music_objs.song import Song
from model.playlist_creator.playlist_creator_base import *
from model.runners.runner_interface import IRunner
from model.savers.playlist_saver import PlaylistSaver
from model.songs_directory.directory_reader import DerictoryReader
from model.songs_searchers.spotify_searcher import SpotifySearcher


class PlaylistCreatorRunner(IRunner):
    def run(self, args):
        client_id = '03e69fa5ec5d479a82bb066e019a722b'
        client_secret = '0ae6f5bb823a4ac281dc1b7c07180706'
        searcher = SpotifySearcher(client_id, client_secret)
        mode = -1
        songs = None
        artists = None
        albums = None
        genres = None
        if args.songs_path:
            songs = []
            reader = DerictoryReader()
            songs_obj = reader.get_songs(args.songs_path)
            for obj in songs_obj:
                song = searcher.get_song_info(obj["name"], obj["artist"])
                if song:
                    songs += [song]
            mode = PlaylistModes.SONGS
        if args.albums_list:
            with open(args.albums_list, 'r') as f:
                albums = f.readlines()
            if mode == -1:
                mode = PlaylistModes.ALBUMS
        if args.artists_list:
            with open(args.artists_list, 'r') as f:
                artists = f.readlines()
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
        p = PlaylistCreatorBase(searcher, mode=mode)
        res = []
        if mode == PlaylistModes.SONGS:
            res = p.create_playlist(songs, min_time=min_time, max_time=max_time, genres=genres,
                                    artists=artists, num_of_songs=min_songs)
        if mode == PlaylistModes.ARTISTS:
            res = p.create_playlist(artists, min_time=min_time, max_time=max_time, genres=genres)
        if mode == PlaylistModes.GENRES:
            res = p.create_playlist(genres, min_time=min_time, max_time=max_time)
        if mode == PlaylistModes.ALBUMS:
            res = p.create_playlist(albums, min_time=min_time, max_time=max_time, genres=genres,
                                    artists=artists)
        saver = PlaylistSaver()
        saver.save(res)
