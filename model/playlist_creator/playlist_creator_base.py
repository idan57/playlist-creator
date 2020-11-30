from model.playlist_creator.playlist_creator_interface import IPlaylistCreator
from model.playlist_creator.playlist_modes import PlaylistModes


class PlaylistCreatorBase(IPlaylistCreator):
    def __init__(self, constaints, mode=PlaylistModes.TIME):
        self._constraints = constaints
        self._mode = mode

    def create_playlist(self, songs):
        if self._mode == PlaylistModes.TIME:
            return self._time_creator(songs)
        elif self._mode == PlaylistModes.WORDS:
            return self._words_creator(songs)

    def _time_creator(self, songs):
        pass

    def _words_creator(self, songs):
        pass
