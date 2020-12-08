from pulp import pulp, LpBinary, LpProblem, LpMaximize

from model.songs_directory.directory_reader import DerictoryReader
from model.songs_searchers.spotify_searcher import SpotifySearcher


def test_last_fm_searcher():
    dr = DerictoryReader()
    songs = dr.get_songs("C:\\Users\\Idan Cohen\\Desktop\\songs")
    songs_objs = []
    client_id = '03e69fa5ec5d479a82bb066e019a722b'
    client_secret = '0ae6f5bb823a4ac281dc1b7c07180706'
    searcher = SpotifySearcher(client_id, client_secret)
    res_s, res_a = [], []
    for song in songs:
        s = searcher.get_song_info(song["name"], song["artist"])
        s.set_file(song)
        res_s += [s]
        res_a += [searcher.get_artist_info(song["artist"])]

    song_ids = [s.ID for s in res_s]
    art_ids = [s.ID for s in res_a]

    res = searcher.get_similar_tracks(song["name"], song["artist"])
    r = res[0].Duration
    songs = ["x1", "x2", "x3", "x4", "x5"]
    ratings = [40, 50, 60, 70, 80]
    times = [300, 200, 130, 44, 123]

    s = pulp.LpVariable.dicts("songs", songs, 0, 1, LpBinary)
    r_s = pulp.lpSum((son * r) / max(1, sum([1 for p in s.values() if p.value()])) for son, r in zip(s.values(),
                                                                                                     ratings))
    t_s = pulp.lpSum(t * son for son, t in zip(s.values(), times))

    prob = LpProblem("MMM", LpMaximize)
    prob += r_s
    prob += t_s >= 100
    prob += t_s <= 200
    r = prob.solve()

    assert True
