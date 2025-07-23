from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen, QColor
from PyQt5.QtCore import Qt
import rasterio
import numpy as np
import shapefile
from config.settings import SENTINEL2_BANDS

def generate_input_preview(image_path: str, label_width: int, label_height: int) -> QPixmap:
    with rasterio.open(image_path) as src:
        band_count = src.count
        is_uav = band_count <= 4
        is_sentinel = band_count > 4

        if is_uav:
            bands_to_read = [1, 2, 3]
        else:
            bands_to_read = [
                SENTINEL2_BANDS['B4'] + 1,
                SENTINEL2_BANDS['B3'] + 1,
                SENTINEL2_BANDS['B2'] + 1
            ]

        if max(bands_to_read) > band_count:
            raise ValueError(
                f"File memiliki {band_count} band, tidak bisa memuat kombinasi band {bands_to_read}."
            )

        bands = [src.read(b) for b in bands_to_read]
        array = np.stack(bands, axis=-1).astype(np.float32)

        if is_uav:
            array -= array.min()
            if array.max() > 0:
                array /= array.max()
            array *= 255
        else:
            array = np.clip(array, 0, 10000)
            p2, p98 = np.percentile(array, (2, 98))
            array = np.clip((array - p2) / (p98 - p2) * 255, 0, 255)

        array = array.astype(np.uint8)
        h, w, ch = array.shape
        qimage = QImage(array.data, w, h, ch * w, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimage)
        return pixmap.scaled(label_width, label_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)

def generate_output_mask_preview(output_path: str, label_width: int, label_height: int) -> QPixmap:
    with rasterio.open(output_path) as src:
        mask = src.read(1)
        h, w = mask.shape
        rgb = np.zeros((h, w, 3), dtype=np.uint8)
        rgb[mask == 0] = [160, 160, 160]
        rgb[mask == 1] = [0, 102, 204]

        qimage = QImage(rgb.data, w, h, w * 3, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimage)
        return pixmap.scaled(label_width, label_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)

def generate_shapefile_preview(shapefile_path: str, width: int = 400, height: int = 300) -> QPixmap:
    sf = shapefile.Reader(shapefile_path)
    shapes = sf.shapes()

    pixmap = QPixmap(width, height)
    pixmap.fill(Qt.white)
    painter = QPainter(pixmap)
    pen = QPen(QColor(0, 102, 204), 2)
    painter.setPen(pen)

    all_points = [pt for shape in shapes for pt in shape.points]
    xs = [pt[0] for pt in all_points]
    ys = [pt[1] for pt in all_points]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    def scale_point(x, y):
        sx = (x - min_x) / (max_x - min_x) * (width - 20) + 10
        sy = (max_y - y) / (max_y - min_y) * (height - 20) + 10
        return int(sx), int(sy)

    for shape in shapes:
        points = [scale_point(x, y) for x, y in shape.points]
        if len(points) > 1:
            for i in range(len(points) - 1):
                painter.drawLine(points[i][0], points[i][1], points[i+1][0], points[i+1][1])
        else:
            painter.drawPoint(points[0][0], points[0][1])

    painter.end()
    return pixmap
