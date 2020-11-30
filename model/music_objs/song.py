class Song(object):
    def __init__(self, obj, file):
        self._obj = obj
        self._file = file

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
    def Genre(self):
        return self._obj["genre"]

    @property
    def Duration(self):
        return self._file["duration"]

    @property
    def Lyrics(self):
        return self._obj["lyrics"]
