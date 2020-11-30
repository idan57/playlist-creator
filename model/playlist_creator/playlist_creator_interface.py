from abc import ABC, abstractmethod


class IPlaylistCreator(ABC):
    @abstractmethod
    def create_playlist(self, data):
        pass
