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
    def Genre(self):
        return self._obj["genre"]

    @property
    def ID(self):
        return self._obj["id"]
