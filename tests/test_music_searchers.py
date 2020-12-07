from model.songs_directory.directory_reader import DerictoryReader
from model.songs_searchers.spotify_searcher import SpotifySearcher
import tokenize


def test_last_fm_searcher():
    dr = DerictoryReader()
    songs = dr.get_songs("C:\\Users\\Idan Cohen\\Desktop\\songs")
    songs_objs = []
    client_id = '03e69fa5ec5d479a82bb066e019a722b'
    client_secret = '0ae6f5bb823a4ac281dc1b7c07180706'
    searcher = SpotifySearcher(client_id, client_secret)
    res_s, res_a = [], []
    for song in songs:
        res_s += [searcher.get_song_info(song["name"], song["artist"])]
        res_a += [searcher.get_artist_info(song["artist"])]

    song_ids = [s.ID for s in res_s]
    art_ids = [s.ID for s in res_a]

    res = searcher.get_similar_tracks(song["name"], song["artist"])

    assert True

