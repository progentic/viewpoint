import os
from pathlib import Path


class LocalContentStore:
    def __init__(self, root: Path) -> None:
        self._root = root
        self._ready = False

    def start(self) -> None:
        self._root.mkdir(parents=True, exist_ok=True, mode=0o700)
        os.chmod(self._root, 0o700)
        self._ready = self._root.is_dir()

    def stop(self) -> None:
        self._ready = False

    def is_ready(self) -> bool:
        return self._ready

    @property
    def root(self) -> Path:
        return self._root
