from abc import ABC, abstractmethod


class IMusicSearcher(ABC):
    @abstractmethod
    def get_artist_info(self, artist):
        pass

    @abstractmethod
    def get_song_info(self, song, artist):
        pass

    @abstractmethod
    def get_album_info(self, album, artist):
        pass
