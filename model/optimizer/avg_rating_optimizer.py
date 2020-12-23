from gekko import GEKKO


class AvgRatingOptimizer(object):
    def __init__(self, songs):
        self.songs = songs
        self.m = GEKKO()
        self.songs_vars = [self.m.Var(lb=0, ub=1, integer=True) for i in range(len(songs))]
        self.popularity_params = [self.m.Param(song.Popularity) for song in songs]
        self.avg_popularity = self.m.sum([(song_para * s_var) /
                                          max(1, sum([song.VALUE.value for song in self.songs_vars]))
                                          for s_var, song_para in zip(self.songs_vars, self.popularity_params)])
        duration_params = [self.m.Param(song.Duration) for song in self.songs]
        self.sum_time = self.m.sum([song_para * s_var for s_var, song_para in zip(self.songs_vars, duration_params)])
        self.sum_genre = None
        self.sum_atleast = None
        self._equatations = []

    def add_min_time_constraint(self, min_time):
        self._equatations += [self.sum_time >= min_time]

    def add_max_time_constraint(self, max_time):
        self._equatations += [self.sum_time <= max_time]

    def add_genres_constraint(self, genre, number):
        genre_params = [self.m.Param(1) if genre in song.Genres else self.m.Param(0) for song in self.songs]
        self.sum_genre = self.m.sum([s_var * gen for s_var, gen in zip(self.songs_vars, genre_params)])
        self._equatations += [self.sum_genre >= number]

    def add_artists_constraint(self, artists):
        for artist in artists:
            artist_params = [self.m.Param(1) if artist in song.Artists else self.m.Param(0) for song in
                             self.songs]
            sum_artist = self.m.sum(
                [s_var * art for s_var, art in zip(self.songs_vars, artist_params)])
            self._equatations += [sum_artist >= 1]

    def add_atleast_given_songs(self, songs, number):
        songs_params = [self.m.Param(1) if s in songs else self.m.Param(0) for s in self.songs]
        self.sum_atleast = self.m.sum([s_var * song for s_var, song in zip(self.songs_vars, songs_params)])
        self._equatations += [self.sum_atleast >= number]

    def solve(self):
        self.m.Equation(self._equatations)
        self.m.options.SOLVER = 1
        self.m.Maximize(self.avg_popularity)
        self.m.solve()
        songs_after_opt = []
        for song, song_var in zip(self.songs, self.songs_vars):
            if song_var.VALUE.value[0] == 1.0:
                songs_after_opt += [song]
        return songs_after_opt
