from typing import List
from PySide6.QtGui import QPixmap


class Animation:
    def __init__(self, frames: List[QPixmap], frame_duration_ms: int = 120, loop: bool = True):
        self.frames = frames
        self.frame_duration_ms = frame_duration_ms
        self.loop = loop
        self.elapsed_ms = 0.0
        self.current_index = 0

    def advance(self, elapsed_seconds: float) -> None:
        if not self.frames:
            return

        self.elapsed_ms += elapsed_seconds * 1000.0
        while self.elapsed_ms >= self.frame_duration_ms:
            self.elapsed_ms -= self.frame_duration_ms
            self.current_index += 1
            if self.current_index >= len(self.frames):
                if self.loop:
                    self.current_index = 0
                else:
                    self.current_index = len(self.frames) - 1

    def current_frame(self) -> QPixmap | None:
        if not self.frames:
            return None
        return self.frames[self.current_index]

    def restart(self) -> None:
        self.elapsed_ms = 0.0
        self.current_index = 0
