import requests
from bs4 import BeautifulSoup


class LyricsGetter(object):
    def get(self, artist, song):
        no_sym_art = self._remove_symbols_n_spaces(artist.lower())
        no_sym_song = self._remove_symbols_n_spaces(song.lower())

        response = requests.get(f"https://www.azlyrics.com/lyrics/{no_sym_art}/{no_sym_song}.html")
        parsed = BeautifulSoup(response.text)
        res = parsed.find("div", {"class": "main-page"}).text
        return res

    def _remove_symbols_n_spaces(self, artist):
        res = artist.replace(" & ", "")
        res = res.replace(" ", "")
        res = res.replace(" x ", "")
        res = res.replace(", ", "")
        return res
