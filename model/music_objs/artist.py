class Artist(object):
    def __init__(self, obj):
        self._obj = obj

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
