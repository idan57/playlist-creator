from lyrics_extractor import SongLyrics


class LyricsGetter(object):
    def get(self, artist, song):
        songs_lyrics = SongLyrics("AIzaSyAxFaUFClQjKEXwpzGM7mor9-Nl2OqabH8", "ceb5297d59ef47ff8")
        res = songs_lyrics.get_lyrics(f"{artist} - {song}")
        return res["lyrics"]

    def _remove_symbols_n_spaces(self, artist):
        res = artist.replace("&", "")
        res = res.replace("x", "")
        res = res.replace(",", "")
        res = res.replace("\\", "")
        return res
