class Artist(object):
    """
    A class to represent an artist object
    """
    def __init__(self, obj):
        self._obj = obj
        self._num_of_similar = 0

    @property
    def Name(self):
        return self._obj["name"]

    @property
    def Href(self):
        return self._obj["href"]

    @property
    def Genres(self):
        return self._obj["genres"]

    @property
    def ID(self):
        return self._obj["id"]

    @property
    def Popularity(self):
        return self._obj["popularity"]

    @property
    def NumOfFollowers(self):
        return self._obj["followers"]["total"]

    @property
    def ExternalUrl(self):
        return self._obj["external_urls"]["spotify"]

    @property
    def Similarity(self):
        return self._num_of_similar

    def set_similarity(self, sim):
        self._num_of_similar = sim
