from pathlib import Path
from PySide6.QtGui import QImage, QPainter, QColor, QPen, QFont
from PySide6.QtCore import Qt

ROOT_DIR = Path(__file__).resolve().parent
ASSETS_DIR = ROOT_DIR / "assets"
ICON_PNG = ASSETS_DIR / "app_icon.png"
ICON_ICO = ASSETS_DIR / "app_icon.ico"
CAT_DIR = ASSETS_DIR / "cat"

ASSETS_DIR.mkdir(exist_ok=True)
CAT_DIR.mkdir(parents=True, exist_ok=True)

if not (CAT_DIR / "placeholder.txt").exists():
    (CAT_DIR / "placeholder.txt").write_text("This folder contains generated cat animation frames.")

size = 256
image = QImage(size, size, QImage.Format_ARGB32)
image.fill(Qt.transparent)

painter = QPainter(image)
painter.setRenderHint(QPainter.Antialiasing)

# draw a simple friendly cat icon
painter.setBrush(QColor(240, 200, 160))
painter.setPen(Qt.NoPen)
painter.drawEllipse(34, 40, 188, 180)

painter.setBrush(QColor(240, 160, 120))
painter.drawEllipse(74, 24, 42, 64)
painter.drawEllipse(140, 24, 42, 64)

painter.setBrush(QColor(255, 255, 255))
painter.drawEllipse(88, 86, 34, 42)
painter.drawEllipse(134, 86, 34, 42)

painter.setBrush(QColor(40, 30, 20))
painter.drawEllipse(104, 110, 10, 16)
painter.drawEllipse(150, 110, 10, 16)

painter.setBrush(QColor(220, 80, 60))
painter.drawEllipse(124, 126, 16, 12)

painter.setPen(QPen(QColor(120, 60, 30), 8, Qt.SolidLine, Qt.RoundCap))
painter.drawLine(92, 150, 82, 170)
painter.drawLine(156, 150, 166, 170)

painter.setPen(QPen(QColor(120, 60, 30), 12, Qt.SolidLine, Qt.RoundCap))
painter.drawLine(106, 44, 66, 28)
painter.drawLine(150, 44, 196, 32)

painter.setPen(QPen(QColor(10, 10, 10), 8))
painter.drawArc(88, 138, 80, 50, 0, -120 * 16)

font = QFont("Segoe UI", 26, QFont.Bold)
painter.setFont(font)
painter.setPen(QColor(255, 255, 255))
painter.drawText(60, 228, "Pet")

painter.end()

image.save(str(ICON_PNG))
image.save(str(ICON_ICO))

print(f"Generated icon assets: {ICON_PNG} and {ICON_ICO}")
