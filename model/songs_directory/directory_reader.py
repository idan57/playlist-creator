from pathlib import Path
from mutagen.mp3 import MP3
from mutagen.wave import WAVE


class DerictoryReader:
    def get_files(self, p):
        files = []
        for x in p.iterdir():
            if x.is_dir():
                print(x)
                files.extend(self.get_files(x))
            elif x.suffix == '.mp3' or x.suffix == '.wav':
                files.append(x)
        return files

    def get_songs(self, path):
        p = Path(path)
        files = self.get_files(p)
        songs = []
        for file in files:
            songs.append(self.get_song_attr(file))
        return songs

    def get_song_attr(self, file):
        song = {}
        if file.suffix == '.mp3':
            audio = MP3(file)
        else:
            audio = WAVE(file)
        desc = file.name.rsplit('.', 1)[0]
        split = desc.rsplit('-',1)
        artist, name = split[0] if len(split) > 1 else '', split[1] if len(split) > 1 else split[0]
        if artist == '':
            artist = str(audio.tags['TPE1'])
        name = name.split("ft")[0].strip()
        name = name.split("feat")[0].strip()
        song['name'], song['artist'], song['duration'] = name, artist.strip(), audio.info.length
        return song
