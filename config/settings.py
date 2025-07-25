import os

APP_NAME = "CoDec App - Coastline Detection & Extraction"
VERSION = "1.0.0"
AUTHOR = "CoDec Development Team"

SUPPORTED_FORMATS = [
    "TIFF Files (*.tif *.tiff)",
    "All Files (*)"
]

SENTINEL2_BANDS = {
    'B1': 0, 'B2': 1, 'B3': 2, 'B4': 3,
    'B5': 4, 'B6': 5, 'B7': 6, 'B8': 7,
    'B8A': 8, 'B9': 9, 'B10': 10, 'B11': 11, 'B12': 12
}

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 650
LEFT_PANEL_WIDTH = 450

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")
ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")

MODEL_TYPES = ["Pilih Model","✈️ UAV", "🛰️ Sentinel-2"]

os.makedirs(OUTPUT_DIR, exist_ok=True)