import os
import sys
from PyQt5.QtWidgets import QMessageBox
import rasterio
import numpy as np

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
