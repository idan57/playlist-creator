class Song(object):
    """
    A class to represent an song object
    """

    def __init__(self, obj):
        self._obj = obj
        self._file = None
        self._weight = 0
        self._num_of_similar = 0

    @property
    def Name(self):
        return self._obj["name"]

    @property
    def Href(self):
        return self._obj["href"]

    @property
    def Popularity(self):
        return self._obj["popularity"]

    @property
    def Genres(self):
        return self._obj["genres"]

    @property
    def Duration(self):
        if not self._file:
            return self._obj["duration_ms"] / 1000
        return self._file["duration"]

    @property
    def ID(self):
        return self._obj["id"]

    @property
    def Artists(self):
        res = []
        for artist in self._obj["artists"]:
            res += [artist["name"]]
        return res

    @property
    def Weight(self):
        return self._weight

    @property
    def LinkToSong(self):
        return self._obj["external_urls"]["spotify"]

    def set_weight(self, w):
        self._weight = w

    @property
    def Similarity(self):
        return self._num_of_similar

    def set_similarity(self, sim):
        self._num_of_similar = sim

    def set_file(self, file):
        self._file = file
