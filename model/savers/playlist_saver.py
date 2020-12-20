import json
from pathlib import Path

from model.savers.saver_interface import ISaver


class PlaylistSaver(ISaver):
    """
    A playlist saver for Song objects.
    Saves the playlist as a json file.
    """
    def __init__(self, name="playlist.json"):
        """
        :param name: name for the file that the playlist will be save to
        """
        if not name.endswith(".json"):
            name += ".json"
        self._name = name

    def save(self, songs):
        """
        Get a list of songs and save them to a json file.

        :param songs: list of Songs
        """
        playlists_path = Path(__file__).parent.parent.parent / "playlists"
        playlist_result_path = playlists_path / self._name
        if not playlists_path.is_dir():
            playlists_path.mkdir()
        result_dict = {}
        total_time_in_ms = 0
        for song in songs:
            result_dict[song.ID] = {
                "artists": song.Artists,
                "name": song.Name,
                "link": song.LinkToSong,
                "popularity": song.Popularity
            }
            total_time_in_ms += song.Duration
        result_dict["total_time_in_ms"] = total_time_in_ms
        result_json = json.dumps(result_dict)
        playlist_result_path.write_text(result_json)
