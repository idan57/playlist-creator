import os
from datetime import datetime
from pathlib import Path
from threading import Lock
from time import time

from model.logger import singleton


@singleton
class Logger(object):
    """
    A logger object to save logs into a file
    """

    def __init__(self):
        logs_path = Path(__file__).parent.parent.parent / "logs"
        if not logs_path.is_dir():
            logs_path.mkdir()
        timed_logs_path = logs_path / datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        if not logs_path.is_dir():
            logs_path.mkdir()
        timed_logs_path.mkdir()
        self._save_to = timed_logs_path / "log.txt"
        self._done_file = timed_logs_path / "done.txt"
        self._valid_chars = [" ", "-", ":", "\n", "\r", "\\", "."]
        self._save_to.touch()
        self._lock = Lock()
        self._b = "-" * 100
        self._start = time()

    def _write_to_log(self, msg):
        """
        Message to write to log file.

        :param msg: message
        """
        self._lock.acquire()

        self._write_to_file(msg)

        self._lock.release()

    def info(self, msg, add_start=True):
        """
        Write an info message to screen and log file.

        :param msg: message
        """
        msg = "".join(e for e in msg if e.isalnum() or e in self._valid_chars)
        if add_start:
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
        log_file.close()

    def done(self):
        """
        Creating a file to mark the playlist creation as done
        """
        self.beautiful_info(f"Finished in {(time() - self._start) / 60} minutes ({datetime.now().strftime('%Y-%m-%d_%H-%M-%S')})")
        self._done_file.touch()

    def beautiful_info(self, msg):
        """
        Beautiful print for log in format:
        -----------------------
        -----------------------
                  msg
        -----------------------
        -----------------------
        :param msg: message to print
        """
        self.info(self._b, add_start=False)
        self.info(self._b, add_start=False)
        self.info(msg, add_start=False)
        self.info(self._b, add_start=False)
        self.info(self._b, add_start=False)
