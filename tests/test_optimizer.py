from model.optimizer.avg_rating_optimizer import AvgRatingOptimizer
from model.music_objs.song import Song
from model.music_objs.artist import Artist
def test_optimizer():
    artist1 = {
        "name": "Metalica"
    }
    #artist1 = Artist(artist1)
    artist2 = {
        "name": "Imagine dragons"
    }
    #artist2 = Artist(artist2)
    artist3 = {
        "name": "Sia"
    }
    #artist3 = Artist(artist3)
    artist4 = {
        "name": "David Guetta"
    }
    #artist4 = Artist(artist4)
    artist5 = {
        "name": "Metalica"
    }
    #artist5 = Artist(artist5)
    song1 = {
        "name": "nothing else matter",
        "artists": [artist1],
        "duration_ms": 50000,
        "genres": "metal",
        "popularity": 10
    }

    song2 = {
        "name": "Thunder",
        "artists": [artist2],
        "duration_ms": 50000,
        "genres": "pop",
        "popularity": 10
    }
    song3 = {
        "name": "Cheap Thrills",
        "artists": [artist3],
        "duration_ms": 50000,
        "genres": "pop",
        "popularity": 10
    }
    song4 = {
        "name": "Titanium",
        "artists": [artist4],
        "duration_ms": 50000,
        "genres": "sol",
        "popularity": 10
    }
    song5 = {
        "name": "best",
        "artists": [artist5],
        "duration_ms": 150000,
        "genres": "metal",
        "popularity": 30
    }
    song1 = Song(song1)
    song2 = Song(song2)
    song3 = Song(song3)
    song4 = Song(song4)
    song5 = Song(song5)
    songs = [song1,song2,song3,song4,song5]
    opt = AvgRatingOptimizer(songs)
    opt.add_max_time_constraint(200)
    opt.add_min_time_constraint(100)
    # opt.add_genres_constraint("pop",1)
    # opt.add_genres_constraint("metal", 1)
    # opt.add_artists_constraint([artist1,artist2])
    opt.add_atleast_given_songs([song1,song2,song3,song4],3)
    sulotion = opt.solve()
    print('\n'.join([song.Name for song in sulotion]))
    assert True

test_optimizer()

