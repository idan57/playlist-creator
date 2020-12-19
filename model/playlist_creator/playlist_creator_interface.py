from abc import ABC, abstractmethod


class IPlaylistCreator(ABC):
    """
    Interface for creating playlists
    """
    @abstractmethod
    def create_playlist(self, data):
        """
        Create a playlist from data
        :param data: data to create playlist from
        :return: playlist
        """
        pass
