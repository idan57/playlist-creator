from pathlib import Path
from mutagen.mp3 import MP3
from mutagen.wave import WAVE

class Derictory_reader:
    def get_files(self,p):
        files = []
        #files = list(x for x in p.iterdir() if not x.is_dir())
        for x in p.iterdir():
            if x.is_dir():
                print(x)
                files.extend(self.get_files(x))
            elif x.suffix == '.mp3' or x.suffix == '.wav':
                files.append(x)
        return files

    def get_songs(self,path):
        p = Path(path)
        #files = list(p.glob('**/*.mp3'))
        #files = list(x for x in p.iterdir() if not x.is_dir())
        files = self.get_files(p)
        songs = []
        for file in files:
            songs.append(self.get_song_attr(file))
        songs = dict(enumerate(songs))
        return songs

    def get_song_attr(self,file):
        song = {}
        if file.suffix == '.mp3':
            audio = MP3(file)
        else:
            audio = WAVE(file)
        desc = file.name.rsplit('.', 1)[0]
        split = desc.split('-')
        artist, name = split[0] if len(split) > 1 else '', split[1] if len(split) > 1 else split[0]
        if artist == '':
            artist = str(audio.tags['TPE1'])
        song['name'], song['artist'], song['duration'] = name, artist, audio.info.length
        return song

# songs = Derictory_reader().get_songs('C:/Users/ADI-PC2/Downloads/Computer_sience/year_3/semester1/Intro to optimization/songs')
# print(songs)





