from gekko import GEKKO


class AvgRatingOptimizer(object):
    """
    A class that wraps GEKKO optimizer.
    """
    def __init__(self, songs):
        """
        :param songs: songs to optimize
        """
        self.songs = songs
        self.m = GEKKO()
        self.songs_vars = [self.m.Var(lb=0, ub=1, integer=True) for i in range(len(songs))]
        self._sum_songs_var = self.m.sum(self.songs_vars)
        self.popularity_params = [self.m.Param(song.Popularity) for song in songs]
        exist_param = [self.m.Param(1) for _ in songs]
        self.avg_popularity = self.m.sum([(song_para * s_var) / self.m.max2(1, self._sum_songs_var)
                                          for s_var, song_para in zip(self.songs_vars, self.popularity_params)])
        duration_params = [self.m.Param(song.Duration) for song in self.songs]
        self.sum_time = self.m.sum([song_para * s_var for s_var, song_para in zip(self.songs_vars, duration_params)])
        self.sum_genre = None
        self.sum_atleast = None
        self._equatations = [self.m.sum([song * exist for song, exist in zip(self.songs_vars, exist_param)]) == self._sum_songs_var]

    def add_min_time_constraint(self, min_time):
        """
        Add minimum time constraint for the playlist
        :param min_time: minimum time
        """
        self._equatations += [self.sum_time >= min_time]

    def add_max_time_constraint(self, max_time):
        """
        Add maximum time constraint for the playlist
        :param max_time: maximum time
        """
        self._equatations += [self.sum_time <= max_time]

    def add_genres_constraint(self, genre, number):
        """
        Add constraint for a genre that should be part of the song
        :param genre: the genre's name
        :param number: number of songs that should be from the genre
        """
        genre_params = [self.m.Param(1) if genre in song.Genres else self.m.Param(0) for song in self.songs]
        self.sum_genre = self.m.sum([s_var * gen for s_var, gen in zip(self.songs_vars, genre_params)])
        self._equatations += [self.sum_genre >= number]

    def add_artists_constraint(self, artists):
        """
        Add a constraint for specific artists that should be in the playlist
        :param artists: artists names
        """
        for artist in artists:
            artist_params = [self.m.Param(1) if artist in song.Artists else self.m.Param(0) for song in
                             self.songs]
            sum_artist = self.m.sum(
                [s_var * art for s_var, art in zip(self.songs_vars, artist_params)])
            self._equatations += [sum_artist >= 1]

    def add_atleast_given_songs(self, songs, number):
        """
        Add a constraint for a specific number of songs that should appear in the playlist
        :param songs: songs that must appear from self.songs
        :param number: number of songs that must appear
        """
        songs_params = [self.m.Param(1) if s in songs else self.m.Param(0) for s in self.songs]
        self.sum_atleast = self.m.sum([s_var * song for s_var, song in zip(self.songs_vars, songs_params)])
        self._equatations += [self.sum_atleast >= number]

    def solve(self):
        """
        Solve the optimization problem
        :return: songs for playlist
        """
        self.m.Equation(self._equatations)
        self.m.options.SOLVER = 1
        self.m.Maximize(self.avg_popularity)
        self.m.solve()
        songs_after_opt = []
        for song, song_var in zip(self.songs, self.songs_vars):
            if song_var.VALUE.value[0] == 1.0:
                songs_after_opt += [song]
        return songs_after_opt
