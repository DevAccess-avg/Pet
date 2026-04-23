import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

def resolve_data_path(*parts) -> Path:
    base = Path(getattr(sys, "_MEIPASS", ROOT_DIR))
    return base.joinpath(*parts)

ASSETS_DIR = resolve_data_path("assets", "cat")
ICON_PATH_PNG = resolve_data_path("assets", "app_icon.png")
ICON_PATH_ICO = resolve_data_path("assets", "app_icon.ico")
ICON_PATH = ICON_PATH_PNG if ICON_PATH_PNG.exists() else ICON_PATH_ICO

FRAME_DURATION_MS = 120
WALK_SPEED = 150.0
ARRIVAL_RADIUS = 1.0
STOP_RADIUS = 0.5
IDLE_BEHAVIOR_DELAY = 4.2
BLINK_INTERVAL_MIN = 3.8
BLINK_INTERVAL_MAX = 6.4
BOUNCE_DURATION = 0.28
BOUNCE_MAGNITUDE = 0.08

ANIMATION_SETS = {
    "idle": "idle",
    "walk": "walk",
    "sit": "sit",
}
