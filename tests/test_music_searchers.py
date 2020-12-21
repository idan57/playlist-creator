import datetime
import logging
from pathlib import Path


from model.playlist_creator.playlist_creator_base import PlaylistCreatorBase
from model.playlist_creator.playlist_modes import PlaylistModes
from model.songs_directory.directory_reader import DerictoryReader
from model.songs_searchers.spotify_searcher import SpotifySearcher

from gekko import GEKKO


def test_last_fm_searcher():
    dr = DerictoryReader()
    songs = dr.get_songs("C:\\Users\\Idan Cohen\\Desktop\\songs")
    songs_objs = []
    client_id = '03e69fa5ec5d479a82bb066e019a722b'
    client_secret = '0ae6f5bb823a4ac281dc1b7c07180706'
    searcher = SpotifySearcher(client_id, client_secret)
    res_s, res_a = [], []
    s = searcher.get_song_info("too much to ask", "niall horan")
    res_s += [s]

    p = PlaylistCreatorBase(searcher, mode=PlaylistModes.SONGS)
    res = p.create_playlist(res_s, min_time=1000, max_time=2400)
    assert True

    #
    # song_ids = [s.ID for s in res_s]
    # art_ids = [s.ID for s in res_a]
    #
    # res = searcher.get_similar_tracks(song["name"], song["artist"])
    # r = res[0].Duration
    # songs = ["x1", "x2", "x3", "x4", "x5"]
    # ratings = [40, 50, 60, 70, 80]
    # times = [300, 200, 130, 44, 123]
    #
    # m = GEKKO()  # create GEKKO model
    # songs_vars = [m.Var(lb=0, ub=1, integer=True) for i in range(5)]
    # songs_vars_sum = m.sum(songs_vars)
    # weight_params = [1,2,3,4,5]
    # weight = m.sum([(song_para * s_var) for s_var, song_para in zip(songs_vars, weight_params)])
    # m.Equation([songs_vars_sum <= 30, ])
    # m.Maximize(weight)
    # m.solve()
    # print(1)
    # s = [m.Var(lb=0, ub=1, integer=True) for i in range(5)]  # define new variable, default=0
    # tt = m.sum([s * m.Param(t) for s, t in zip(s, times)])
    # rr = m.sum([p * m.Param(r) / max(1, sum([v.value for v in s])) for p, r in zip(s, ratings)])
    # m.Equations([tt >= 100, tt <= 200])  # equations
    # m.Maximize(rr)
    # m.options.SOLVER = 1  # APOPT solver
    # m.solve()
    # print(1)
    # s = pulp.LpVariable.dicts("songs", songs, 0, 1, LpBinary)
    # r_s = pulp.lpSum((son * r) / max(1, sum([1 for p in s.values() if p.value()])) for son, r in zip(s.values(),
    #                                                                                                  ratings))
    # t_s = pulp.lpSum(t * son for son, t in zip(s.values(), times))
    #
    # prob = LpProblem("MMM", LpMaximize)
    # prob += r_s
    # prob += t_s >= 100
    # prob += t_s <= 200
    # r = prob.solve()


test_last_fm_searcher()
