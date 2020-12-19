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
        if not logs_path.is_dir():
            logs_path.mkdir()
        timed_logs_path.mkdir()
        self._save_to = timed_logs_path / "log.txt"
        self._lock_file = timed_logs_path / "lock"
        self._valid_chars = [" ", "-", ":"]
        self._save_to.touch()
        self._lock = Lock()

    def _write_to_log(self, msg):
        """
        Message to write to log file.

        :param msg: message
        """
        self._lock.acquire()

        # Create a lock file to let other programs know if the file is available
        self._lock_file.touch()
        self._write_to_file(msg)
        self._lock_file.unlink()

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
