class Playlist(object):
    def __init__(self, obj):
        self._obj = obj

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
    def Genres(self):
        return self._obj["genres"]

    @property
    def Tracks(self):
        return self._obj["songs"]

    @property
    def NumOfTracks(self):
        return self._obj["tracks"]["total"]

    @property
    def LinkToAlbum(self):
        return self._obj["external_urls"]["spotify"]

    @property
    def NumOfFollowers(self):
        return self._obj["followers"]["total"]

    @property
    def AvgTracksPopularity(self):
        return sum([track.Popularity for track in self.Tracks]) / self.NumOfTracks
