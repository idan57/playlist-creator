import json
from pathlib import Path

import pylab as plt
import xlwt

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
        self._playlist_folder = Path(__file__).parent.parent.parent / "playlists"

    def save(self, songs):
        """
        Get a list of songs and save them to a json file.

        :param songs: list of Songs
        """
        playlist_result_path = self._playlist_folder / self._name
        if not self._playlist_folder.is_dir():
            self._playlist_folder.mkdir()
        result_dict = {
            "songs": {}
        }
        cols = ["ID", "Popularity", "Link"]
        y = []
        x = []
        rows = []
        table = []
        total_time_in_minute = 0
        n = 0
        for song in songs:
            table += [[n, song.Popularity, song.LinkToSong]]
            y += [song.Popularity]
            n += 1
            x += [n]
            ar = song.Artists[0].replace("$", "")
            if f"{ar} - {song.Name}" not in rows:
                rows += [f"{ar} - {song.Name}"]
                result_dict["songs"][song.ID] = {
                    "artists": song.Artists,
                    "name": song.Name,
                    "link": song.LinkToSong,
                    "popularity": song.Popularity
                }
                total_time_in_minute += song.Duration

        result_dict["total_time_in_minute"] = total_time_in_minute / 60
        result_json = json.dumps(result_dict, indent=4, sort_keys=True)
        playlist_result_path.write_text(result_json)

        self._show_table_graph(x, y)
        self._save_to_excel(table, rows, cols)

    def _show_table_graph(self, x, y):
        """
        Show the table and graph of the playlist created.
        The graph is the id of the song to its popularity

        :param x: ids of the songs
        :param y: popularities
        """
        g = plt.figure(2)
        plt.plot(x, y)
        plt.ylabel("Songs Popularity")
        plt.xlabel("Songs IDs")
        g.savefig(str(self._playlist_folder / "playlist_graph.pdf"))

    def _save_to_excel(self, table, rows, cols):
        book = xlwt.Workbook(encoding='utf8')
        sheet = book.add_sheet("playlist")

        style = xlwt.easyxf('pattern: pattern solid, fore_colour light_blue;'
                            'font: colour white, bold True;')

        style_c = xlwt.easyxf('pattern: pattern solid, fore_colour light_yellow;'
                              'font: bold True;')
        max_widths = [0] * (len(cols) + 1)
        for i, col in zip(range(len(cols)), cols):
            max_widths[i + 1] = max(max_widths[i + 1], len(str(col)))
            sheet.col(i + 1).width = max_widths[i + 1] * 500
            sheet.write(0, i + 1, col, style)

        for i, row, t in zip(range(1, len(rows) + 2), rows, table):
            max_widths[0] = max(max_widths[0], len(str(row)))
            sheet.col(0).width = max_widths[0] * 500
            sheet.write(i, 0, row, style)
            for j, t_val in zip(range(1, len(t) + 1), t):
                max_widths[j] = max(max_widths[j], len(str(t_val)))
                sheet.col(j).width = max_widths[j] * 500
                sheet.write(i, j, t_val, style_c)

        book.save(str(self._playlist_folder / "playlist_table.xls"))
