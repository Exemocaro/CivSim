"""Simple elapsed-time helper used to regulate turn speed."""

from __future__ import annotations

import time


class Timer:
    def __init__(self) -> None:
        self._begin: float = 0.0
        self.restart()

    def restart(self) -> None:
        self._begin = time.time()

    def get_time_passed(self) -> float:
        return time.time() - self._begin
