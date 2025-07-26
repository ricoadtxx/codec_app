import os
import sys
import rasterio
import numpy as np
from typing import Union
from keras.models import Model
from PyQt5.QtWidgets import QMessageBox

def show_warning_dialog(parent, title: str, message: str):
    warning_box = QMessageBox(parent)
    warning_box.setIcon(QMessageBox.Warning)
    warning_box.setWindowTitle(title)
    warning_box.setText(message)
    warning_box.setStandardButtons(QMessageBox.Ok)
    warning_box.exec_()

def load_raster_image(file_path):
    try:
        with rasterio.open(file_path) as dataset:
            image_array = dataset.read()
            image_array = np.transpose(image_array, (1, 2, 0))
            band_count = dataset.count
            return image_array, band_count, None
    except Exception as e:
        return None, 0, str(e)

def validate_model_selection(model_type, band_count):
    if model_type == "✈️ UAV" and band_count not in [3, 4]:
        return False, "Model UAV memerlukan citra dengan 3 atau 4 band. Mohon pilih file yang sesuai."
    elif model_type == "🛰️ Sentinel-2" and band_count <= 4:
        return False, "Model Sentinel-2 memerlukan citra dengan lebih dari 4 band. Mohon pilih file yang sesuai."
    return True, None

def choose_model_by_band_count(band_count: int) -> str | None:
    if band_count in [3, 4]:
        return "✈️ UAV"
    elif band_count > 4:
        return "🛰️ Sentinel-2"
    else:
        return None

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
        print("📦 Running from bundle. _MEIPASS =", base_path)
    except Exception:
        base_path = os.path.abspath(".")
        print("🛠️ Running from script. base_path =", base_path)
    return os.path.join(base_path, relative_path)

def run_patch_prediction(model: Model, image: Union[np.ndarray], tile_size: int = 256, channels_last: bool = True, is_multichannel: bool = True) -> np.ndarray:
    if model is None:
        raise ValueError("Model tidak boleh None.")
    if image is None:
        raise ValueError("Input image tidak boleh None.")

    if not is_multichannel:
        if image.ndim == 3 and image.shape[0] == 1:
            image = image[0]
        elif image.ndim == 3 and image.shape[2] == 1:
            image = image[:, :, 0]
        elif image.ndim != 2:
            raise ValueError(f"Input image shape tidak valid untuk single-channel: {image.shape}")
        h, w = image.shape
        c = 1
    else:
        if image.ndim != 3:
            raise ValueError(f"Input image shape tidak valid untuk multichannel: {image.shape}")
        if channels_last:
            h, w, c = image.shape
        else:
            c, h, w = image.shape
            image = np.transpose(image, (1, 2, 0))

    mask = np.zeros((h, w), dtype=np.uint8)

    for row in range(0, h, tile_size):
        for col in range(0, w, tile_size):
            patch_h = min(tile_size, h - row)
            patch_w = min(tile_size, w - col)
            patch = image[row:row + patch_h, col:col + patch_w]

            padded = np.zeros((tile_size, tile_size, c), dtype=np.float32)
            if is_multichannel:
                padded[:patch_h, :patch_w, :] = patch
            else:
                padded[:patch_h, :patch_w, 0] = patch

            input_patch = np.expand_dims(padded, axis=0)
            pred = model.predict(input_patch, verbose=0)

            pred_mask = np.argmax(pred[0], axis=-1).astype(np.uint8)
            mask[row:row + patch_h, col:col + patch_w] = pred_mask[:patch_h, :patch_w]

    return mask
