import json
from pathlib import Path
from threading import Thread

import pylab as plt
import matplotlib as mpl

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
        result_dict = {
            "songs": {}
        }
        cols = ["ID", "Popularity", "Link"]
        y = []
        x = []
        rows = []
        table = []
        total_time_in_ms = 0
        n = 0
        for song in songs:
            table += [[n, song.Popularity, song.LinkToSong]]
            y += [song.Popularity]
            n += 1
            x += [n]
            rows += [f"{song.Artists[0]} {song.Name}"]
            result_dict["songs"][song.ID] = {
                "artists": song.Artists,
                "name": song.Name,
                "link": song.LinkToSong,
                "popularity": song.Popularity
            }
            total_time_in_ms += song.Duration

        result_dict["total_time_in_ms"] = total_time_in_ms
        result_json = json.dumps(result_dict)
        playlist_result_path.write_text(result_json)

        self._show_table_graph(table, rows, cols, x, y)

    def _show_table_graph(self, table, rows, cols, x, y):
        """
        Show the table and graph of the playlist created.
        The graph is the id of the song to its popularity
        :param table: table contents
        :param rows: songs as row labels of the table
        :param cols: cols labels of the table
        :param x: ids of the songs
        :param y: popularities
        """
        f = plt.figure(1)
        the_table = plt.table(cellText=table,
                              colWidths=[0.4] * 3,
                              rowLabels=rows,
                              colLabels=cols,
                              loc='center')
        the_table.auto_set_font_size(False)
        mng = plt.get_current_fig_manager()
        mng.resize(*mng.window.maxsize())
        plt.axis('off')
        f.show()

        g = plt.figure(2)
        plt.plot(x, y)
        g.show()
        plt.show()
