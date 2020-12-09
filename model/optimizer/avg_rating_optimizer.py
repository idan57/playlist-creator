from gekko import GEKKO
class AvgRatingOptimizer:
    def __init__(self,songs):
        self.songs = songs
        self.m = GEKKO()
        self.songs_vars = [self.m.Var(lb=0, ub=1, integer=True) for i in range(len(songs))]
        popularity_params = [self.m.Param(song.Popularity) for song in songs]

        self.avg_popularity = self.m.sum([(song_para * s_var) / max(1, sum([song.VALUE.value for song in self.songs_vars]))
                                for s_var, song_para in zip(self.songs_vars, popularity_params)])



    def add_min_time_constraint(self,min_time):
        duration_params = [self.m.Param(song.Duration) for song in self.songs]
        sum_time = self.m.sum([song_para * s_var for s_var, song_para in zip(self.songs_vars, duration_params)])
        self.m.Equation([sum_time >= min_time])

    def add_max_time_constraint(self,max_time):
        duration_params = [self.m.Param(song.Duration) for song in self.songs]
        sum_time = self.m.sum([song_para * s_var for s_var, song_para in zip(self.songs_vars, duration_params)])
        self.m.Equation([sum_time <= max_time])

    def add_genres_constraint(self,genres):
        for genre in genres:
            sum_genre = self.m.sum([s_var if genre in song.Genres else 0 for s_var,song in zip(self.songs_vars,self.songs)])
            self.m.Equation([sum_genre >= 1])
    def add_artists_constraint(self,artists):
        for artist in artists:
            sum_artist = self.m.sum([s_var if artist in song.Artists else 0 for s_var,song in zip(self.songs_vars,self.songs)])
            self.m.Equation([sum_artist >= 1])
    # def add_atleast_given_songs(self,songs,number):
    #     self.m.sum([])



    def solve(self):
        self.m.options.SOLVER = 1
        self.m.Maximize(self.avg_popularity)
        self.solve()
        songs_after_opt = []
        for song, song_var in zip(self.songs, self.songs_vars):
            if song_var.VALUE.value[0] == 1.0:
                songs_after_opt += [song]
        return songs_after_opt

