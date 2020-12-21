class Album(object):
    """
    A class to represent an album object
    """

    def __init__(self, obj):
        self._obj = obj
        self._num_of_similar = 0

    @property
    def Name(self):
        return self._obj["name"]

    @property
    def ID(self):
        return self._obj["id"]

    @property
    def Href(self):
        return self._obj["href"]

    @property
    def ReleaseDate(self):
        return self._obj["release_date"]

    @property
    def Genres(self):
        return self._obj["genres"]

    @property
    def Tracks(self):
        return self._obj["tracks"]["items"]

    @property
    def NumOfTracks(self):
        return self._obj["total_tracks"]

    @property
    def LinkToAlbum(self):
        return self._obj["external_urls"]["spotify"]

    @property
    def Popularity(self):
        return self._obj["popularity"]

    @property
    def AvgTracksPopularity(self):
        return sum([track.Popularity for track in self.Tracks]) / self.NumOfTracks

    @property
    def Similarity(self):
        return self._num_of_similar

    def set_similarity(self, sim):
        self._num_of_similar = sim
