from pathlib import Path

from mutagen.mp3 import MP3
from mutagen.wave import WAVE

from model.logger.spotify_logger import Logger


class DirectoryReader:
    """
    Class to read the contents of a songs directory
    """
    def __init__(self):
        self._logger = Logger()

    def get_files(self, p):
        """
        Get file from songs folder
        :param p: path to directory
        :return: files in the directory
        """
        files = []
        self._logger.info(f"Getting data from songs files from folder {str(p)}")
        for x in p.iterdir():
            self._logger.info(f"Current file or dir: {x}")
            if x.is_dir():
                files.extend(self.get_files(x))
            elif x.suffix == '.mp3' or x.suffix == '.wav':
                files.append(x)
        self._logger.info(f"Finished getting data from songs folder: {str(p)}")
        return files

    def get_songs(self, path):
        """
        Get songs from path.

        :param path: path for songs directory
        :return: songs in path
        """
        self._logger.info(f"Getting songs from path: {path}")
        p = Path(path)
        files = self.get_files(p)
        songs = []
        for file in files:
            songs.append(self.get_song_attr(file))
        self._logger.info(f"FINISHED GETTING SONGS")
        return songs

    def get_song_attr(self, file):
        """
        Gets the attributes needed from the songs.

        :param file: the path to the file
        :return: attributes of the file
        """
        song = {}
        self._logger.info(f"Getting attributes for the file: {file}")
        if file.suffix == '.mp3':
            audio = MP3(file)
        else:
            audio = WAVE(file)
        desc = file.name.rsplit('.', 1)[0]
        split = desc.rsplit('-', 1)
        artist, name = split[0] if len(split) > 1 else '', split[1] if len(split) > 1 else split[0]
        if artist == '':
            artist = str(audio.tags['TPE1'])
        name = name.split("ft")[0].strip()
        name = name.split("feat")[0].strip()
        song['name'], song['artist'], song['duration'] = name, artist.strip(), audio.info.length
        return song
