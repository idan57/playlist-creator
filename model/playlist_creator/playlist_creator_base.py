from model.playlist_creator.playlist_creator_interface import IPlaylistCreator


class PlaylistCreatorBase(IPlaylistCreator):
    def create_playlist(self, data):
        pass

