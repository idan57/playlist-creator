from model.runners.runner_interface import IRunner


class PlaylistCreatorRunner(IRunner):
    def run(self, args):
        if args.songs_path:
            pass
        if args.artists_list:
            pass
        if args.albums_list:
            pass
        if args.genres_list:
            pass
