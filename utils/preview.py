# utils/preview_utils.py

import numpy as np

def normalize_band(band):
    band = band.astype(float)
    p2, p98 = np.percentile(band[band > 0], (2, 98))
    band = np.clip(band, p2, p98)
    if p98 > p2:
        band = ((band - p2) / (p98 - p2) * 255)
    return band.astype(np.uint8)

def get_rgb_preview(src):
    red = src.read(1)
    green = src.read(2)
    blue = src.read(3)
    red_norm = normalize_band(red)
    green_norm = normalize_band(green)
    blue_norm = normalize_band(blue)
    return np.dstack((red_norm, green_norm, blue_norm))
