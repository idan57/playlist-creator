from datetime import datetime
from pathlib import Path
from threading import Lock

from model.logger import singleton


@singleton
class Logger(object):
    def __init__(self):
        logs_path = Path(__file__).parent.parent.parent / "logs"
        self._save_to = logs_path / (datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".txt")
        self._valid_chars = [" ", "-", ":"]
        self._save_to.touch()
        self._lock = Lock()

    def info(self, msg):
        msg = "".join(e for e in msg if e.isalnum() or e in self._valid_chars)
        msg = f"Playlist Creator - {datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}: {msg}"

        self._lock.acquire()
        self._write_to_file(msg)
        self._lock.release()

        print(msg)

    def error(self, msg):
        msg = "".join(e for e in msg if e.isalnum() or e in self._valid_chars)
        msg = f"Playlist Creator - {datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}: -------- Exception -------- {msg}"

        self._lock.acquire()
        self._write_to_file(msg)
        self._lock.release()

        print(msg)

    def _write_to_file(self, msg):
        log_file = self._save_to.open("a")
        for c in msg:
            try:
                log_file.write(c)
            except Exception:
                continue
        log_file.write("\n")
