from abc import ABC, abstractmethod


class IMusicSearcher(ABC):
    """
    An interface for searching music
    """

    @abstractmethod
    def get_artist_info(self, artist):
        """
        Search artist info by name.

        :param artist: artist name
        :return: artist info
        """
        pass

    @abstractmethod
    def get_song_info(self, song, artist):
        """
        Search song info by name.

        :param song: song name
        :param artist: artist name
        :return: song info
        """
        pass

    @abstractmethod
    def get_album_info(self, album, artist):
        """
        Search album info by name.

        :param album: album name
        :param artist: artist name
        :return: album info
        """
        pass
