class Song(object):
    def __init__(self, obj):
        self._obj = obj
        self._file = None

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
        return self._file["duration"]

    @property
    def ID(self):
        return self._obj["id"]

    def set_file(self, file):
        self._file = file
