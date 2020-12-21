import argparse

from model.logger.spotify_logger import Logger
from model.runners.playlist_creator_runner import PlaylistCreatorRunner

if __name__ == '__main__':
    runner = PlaylistCreatorRunner()
    argparser = argparse.ArgumentParser()
    argparser.add_argument("-s", "--songs_path",
                           default=None,
                           type=str,
                           help="Path to songs in a directory")
    argparser.add_argument("-r", "--artists_list",
                           type=str,
                           default=None,
                           help="Path to artists file list")
    argparser.add_argument("-l", "--albums_list",
                           type=str,
                           help="Path to albums file list")
    argparser.add_argument("-g", "--genres_list",
                           type=str,
                           help="Path to genres file list")
    argparser.add_argument("-d", "--down",
                           type=int,
                           required=True,
                           default=0,
                           help="Minimum time for playlist")
    argparser.add_argument("-u", "--up",
                           type=int,
                           required=True,
                           default=180,
                           help="Maximum time for playlist")
    argparser.add_argument("-m", "--minimum_songs",
                           type=int,
                           default=0,
                           help="Minimum songs required from input")
    runner.run(argparser.parse_args())
    Logger().done()
