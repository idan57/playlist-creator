import os
from datetime import datetime
from pathlib import Path
from threading import Lock

from model.logger import singleton


@singleton
class Logger(object):
    """
    A logger object to save logs into a file
    """
    def __init__(self):
        logs_path = Path(__file__).parent.parent.parent / "logs"
        timed_logs_path = logs_path / datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        curr_logs_path = logs_path / "current"
        logs = [str(log_dir) for log_dir in logs_path.iterdir()]
        if str(curr_logs_path) in logs:
            curr_logs_path.rmdir()
        os.symlink(str(timed_logs_path), str(curr_logs_path), target_is_directory=True)
        if not logs_path.is_dir():
            logs_path.mkdir()
        timed_logs_path.mkdir()
        self._save_to = timed_logs_path / "log.txt"
        self._valid_chars = [" ", "-", ":"]
        self._save_to.touch()
        self._lock = Lock()

    def _write_to_log(self, msg):
        """
        Message to write to log file.

        :param msg: message
        """
        self._lock.acquire()

        self._write_to_file(msg)

        self._lock.release()

    def info(self, msg):
        """
        Write an info message to screen and log file.

        :param msg: message
        """
        msg = "".join(e for e in msg if e.isalnum() or e in self._valid_chars)
        msg = f"Playlist Creator - {datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}: {msg}"
        self._write_to_log(msg)
        print(msg)

    def error(self, msg):
        """
        Write an error message to screen and log file.

        :param msg: message
        """
        msg = "".join(e for e in msg if e.isalnum() or e in self._valid_chars)
        msg = f"Playlist Creator - {datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}: -------- Exception -------- {msg}"
        self._write_to_log(msg)
        print(msg)

    def _write_to_file(self, msg):
        """
        Write a message to log file char by char to get all chars that can be written to the file.

        :param msg: message
        """
        log_file = self._save_to.open("a")
        for c in msg:
            try:
                log_file.write(c)
            except Exception:
                continue
        log_file.write("\n")
