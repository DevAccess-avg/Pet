import math
import random
from pathlib import Path
from PySide6.QtCore import Qt, QTimer, QPointF
from PySide6.QtGui import QPixmap, QCursor, QPainter, QColor, QPen, QBrush, QImage, QPolygonF, QGuiApplication
from PySide6.QtWidgets import QWidget
from .config import ASSETS_DIR, ANIMATION_SETS, FRAME_DURATION_MS, WALK_SPEED, ARRIVAL_RADIUS, STOP_RADIUS, IDLE_BEHAVIOR_DELAY, BLINK_INTERVAL_MIN, BLINK_INTERVAL_MAX, BOUNCE_DURATION, BOUNCE_MAGNITUDE
from .animation import Animation


class DesktopPet(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setWindowFlag(Qt.WindowDoesNotAcceptFocus)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)

        self._position = QPointF(600.0, 360.0)
        self._target = QPointF(self._position)
        self._last_mouse_pos = QCursor.pos()
        self._last_tick = 0.0
        self._stopped_time = 0.0
        self._bounce_timer = 0.0
        self._bounce_value = 0.0
        self._idle_behavior_timer = random.uniform(BLINK_INTERVAL_MIN, BLINK_INTERVAL_MAX)
        self._state = "idle"

        self.screen_width = QGuiApplication.primaryScreen().size().width()

        self.animations = self._load_animations()
        self.current_animation = self.animations.get("idle")
        self._set_window_size()

        self._tick_timer = QTimer(self)
        self._tick_timer.timeout.connect(self._on_tick)
        self._tick_timer.start(16)

    def _on_tick(self) -> None:
        now = self._last_tick + 0.016
        elapsed = 0.016
        self._last_tick = now

        self._update_target()
        self._update_state(elapsed)
        self._update_animation(elapsed)
        self._update_position()
        self.update()

    def _update_target(self) -> None:
        mouse = QCursor.pos()
        offset_x = 22
        self._target = QPointF(mouse.x() + offset_x, mouse.y())

    def _update_state(self, elapsed: float) -> None:
        distance = self._distance(self._position, self._target)
        mouse_moved = self._distance(self._target, QPointF(self._last_mouse_pos)) > 8.0
        self._last_mouse_pos = QPointF(self._target)

        if distance <= ARRIVAL_RADIUS and not mouse_moved:
            if self._state not in ("sit", "idle"):
                self._switch_state("sit")
                self._bounce_timer = BOUNCE_DURATION
                self._bounce_value = BOUNCE_MAGNITUDE
            self._stopped_time += elapsed
            if self._state == "sit" and self._stopped_time >= self._idle_behavior_timer:
                self._switch_state("idle")
                self._idle_behavior_timer = random.uniform(BLINK_INTERVAL_MIN, BLINK_INTERVAL_MAX)
                self._stopped_time = 0.0
        else:
            self._stopped_time = 0.0
            self._switch_state("walk")
            self._move_toward_target(elapsed)

        if self._bounce_timer > 0.0:
            self._bounce_timer -= elapsed
            if self._bounce_timer < 0.0:
                self._bounce_timer = 0.0
                self._bounce_value = 0.0

    def _update_animation(self, elapsed: float) -> None:
        if self.current_animation:
            self.current_animation.advance(elapsed)

    def _update_position(self) -> None:
        if self.current_animation is None:
            return

        frame = self.current_animation.current_frame()
        if frame is None:
            return

        self.move(int(self._position.x() - frame.width() / 2), int(self._position.y() - frame.height() / 2))

    def _move_toward_target(self, elapsed: float) -> None:
        direction = QPointF(self._target - self._position)
        distance = self._distance(self._position, self._target)
        if distance < 1.0:
            return

        step = WALK_SPEED * elapsed
        fraction = min(1.0, step / distance)
        eased = 1.0 - pow(1.0 - fraction, 3.0)
        self._position += direction * eased

    def _trigger_idle_behavior(self) -> None:
        if self._state != "sit":
            return
        self._switch_state("idle")
        self._stopped_time = 0.0

    def _switch_state(self, state: str) -> None:
        if self._state == state:
            return
        self._state = state
        self.current_animation = self.animations.get(state, self.current_animation)
        if self.current_animation:
            self.current_animation.restart()

    def _distance(self, a: QPointF, b: QPointF) -> float:
        dx = a.x() - b.x()
        dy = a.y() - b.y()
        return math.hypot(dx, dy)

    def paintEvent(self, event):
        frame = self.current_animation.current_frame() if self.current_animation else None
        if frame is None:
            return
        
        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.transparent)
        
        scale = 1.0 + self._bounce_value * (self._bounce_timer / max(BOUNCE_DURATION, 0.001))
        
        x = (self.width() - frame.width()) / 2.0
        y = (self.height() - frame.height()) / 2.0
        
        painter.translate(x + frame.width() / 2.0, y + frame.height() / 2.0)
        painter.scale(scale, scale)
        painter.translate(-frame.width() / 2.0, -frame.height() / 2.0)
        painter.drawPixmap(0, 0, frame)
        painter.end()
        
        self.setMask(frame.mask())

    def _set_window_size(self) -> None:
        maximum = self._max_frame_size()
        self.setFixedSize(maximum[0], maximum[1])
        self._update_position()

    def _max_frame_size(self) -> tuple[int, int]:
        max_width = max((frame.width() for animation in self.animations.values() for frame in animation.frames), default=40)
        max_height = max((frame.height() for animation in self.animations.values() for frame in animation.frames), default=40)
        return max_width, max_height

    def _load_animations(self) -> dict[str, Animation]:
        self._prepare_asset_folders()

        animations: dict[str, Animation] = {}
        for state, folder_name in ANIMATION_SETS.items():
            folder = ASSETS_DIR / folder_name
            frames = self._load_frames(folder)
            if not frames:
                self._generate_animation_frames(state, folder)
                frames = self._load_frames(folder)
            animations[state] = Animation(frames, FRAME_DURATION_MS, loop=True)
        return animations

    def _prepare_asset_folders(self) -> None:
        for folder_name in ANIMATION_SETS.values():
            folder = ASSETS_DIR / folder_name
            folder.mkdir(parents=True, exist_ok=True)

    def _load_frames(self, folder: Path) -> list[QPixmap]:
        frames = []
        for image_path in sorted(folder.glob("*.png")):
            pixmap = QPixmap(str(image_path))
            if pixmap.isNull():
                continue
            frames.append(pixmap)
        return frames

    def _generate_animation_frames(self, state: str, folder: Path) -> None:
        frame_count = 6 if state == "walk" else 4
        for index in range(frame_count):
            image = QImage(40, 40, QImage.Format.Format_ARGB32)
            image.fill(Qt.transparent)
            painter = QPainter(image)
            painter.setRenderHint(QPainter.Antialiasing, False)
            painter.setRenderHint(QPainter.SmoothPixmapTransform, False)

            self._draw_cat(painter, state, index)
            painter.end()

            image.save(str(folder / f"frame_{index:02d}.png"), "PNG")

    def _draw_cat(self, painter: QPainter, state: str, frame_index: int) -> None:
        body = QColor(255, 180, 100)
        dark = QColor(100, 60, 20)
        eye_color = QColor(50, 50, 50)
        white = QColor(255, 255, 255)

        center = QPointF(20.0, 20.0)
        painter.setPen(Qt.NoPen)

        if state == "walk":
            step = (frame_index / 6.0) * math.pi * 2.0
            leg_offset = math.sin(step * 2.0) * 1.2
            tail_angle = math.sin(step) * 20.0
            self._paint_cat_body(painter, center, body, dark, eye_color, white, leg_offset, tail_angle, blink=False)
        elif state == "sit":
            breath = math.sin(frame_index * math.pi / 4.0) * 0.4
            self._paint_cat_body(painter, center + QPointF(0, breath), body, dark, eye_color, white, 0.0, -15.0, blink=False, sitting=True)
        else:
            blink = (frame_index % 4) == 0
            tail_angle = -12.0 + (frame_index % 2) * 3.0
            self._paint_cat_body(painter, center, body, dark, eye_color, white, 0.0, tail_angle, blink=blink)

    def _paint_cat_body(self, painter: QPainter, center: QPointF, body: QColor, dark: QColor, eye_color: QColor, white: QColor, leg_offset: float, tail_angle: float, blink: bool, sitting: bool = False) -> None:
        painter.setPen(Qt.NoPen)
        
        # Body - filled circle for rounded look
        painter.setBrush(QBrush(body))
        painter.drawEllipse(center + QPointF(0, 1.5), 5.5, 7)
        
        # Head - filled circle
        painter.drawEllipse(center + QPointF(0, -4), 5.5, 5.5)
        
        # Left ear
        painter.setBrush(QBrush(dark))
        painter.drawRect(int(center.x() - 2.5), int(center.y() - 7), 1, 2)
        painter.drawRect(int(center.x() - 3.5), int(center.y() - 6), 1, 1)
        
        # Right ear
        painter.drawRect(int(center.x() + 1.5), int(center.y() - 7), 1, 2)
        painter.drawRect(int(center.x() + 2.5), int(center.y() - 6), 1, 1)
        
        # Eyes
        painter.setBrush(QBrush(eye_color))
        if blink:
            painter.drawRect(int(center.x() - 1), int(center.y() - 4.5), 1, 1)
            painter.drawRect(int(center.x() + 1), int(center.y() - 4.5), 1, 1)
        else:
            painter.drawRect(int(center.x() - 1), int(center.y() - 4.5), 1, 1)
            painter.setBrush(QBrush(white))
            painter.drawPoint(int(center.x() - 1), int(center.y() - 4.5))
            
            painter.setBrush(QBrush(eye_color))
            painter.drawRect(int(center.x() + 1), int(center.y() - 4.5), 1, 1)
            painter.setBrush(QBrush(white))
            painter.drawPoint(int(center.x() + 1), int(center.y() - 4.5))
        
        # Nose
        painter.setBrush(QBrush(QColor(255, 100, 100)))
        painter.drawRect(int(center.x()), int(center.y() - 2), 1, 1)
        
        # Left front leg
        painter.setBrush(QBrush(body))
        painter.drawRect(int(center.x() - 2.5), int(center.y() + 6 + leg_offset), 1, 2)
        
        # Right front leg
        painter.drawRect(int(center.x() + 1.5), int(center.y() + 6 - leg_offset), 1, 2)
        
        # Tail - draw as rectangles for pixelated look
        if tail_angle > 0:
            # Tail going right
            painter.setBrush(QBrush(body))
            painter.drawRect(int(center.x() + 5), int(center.y()), 2, 1)
        else:
            # Tail going left
            painter.setBrush(QBrush(body))
            painter.drawRect(int(center.x() - 7), int(center.y()), 2, 1)
