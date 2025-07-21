from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGraphicsDropShadowEffect, QMessageBox
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPen, QColor

import os
import rasterio
import numpy as np
import shapefile  # pyshp

from ..styles.component_styles import (
    OUTPUT_HEADER_STYLE, TAB_WIDGET_STYLE, PREVIEW_LABEL_STYLE,
    INPUT_PREVIEW_LABEL_STYLE, INFO_LABEL_STYLE
)
from ..styles.base_styles import PANEL_STYLE
from config.settings import SENTINEL2_BANDS


class OutputPanelComponent(QtWidgets.QFrame):
    def __init__(self):
        super().__init__()
        self._lastInputImagePath = None
        self._lastOutputImagePath = None
        self.setupUi()

    def setupUi(self):
        self.setStyleSheet(PANEL_STYLE)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QtGui.QColor(0, 0, 0, 30))
        shadow.setOffset(0, 3)
        self.setGraphicsEffect(shadow)

        self.rightLayout = QtWidgets.QVBoxLayout(self)
        self.rightLayout.setContentsMargins(25, 25, 25, 25)
        self.rightLayout.setSpacing(15)

        self.outputHeader = QtWidgets.QLabel("💾 Preview")
        self.outputHeader.setFont(QtGui.QFont("Segoe UI", 14, QtGui.QFont.Bold))
        self.outputHeader.setStyleSheet(OUTPUT_HEADER_STYLE)
        self.outputHeader.setAlignment(Qt.AlignCenter)
        self.rightLayout.addWidget(self.outputHeader)

        self.tabWidget = QtWidgets.QTabWidget()
        self.tabWidget.setStyleSheet(TAB_WIDGET_STYLE)

        self.inputTab = QtWidgets.QWidget()
        self.inputTabLayout = QtWidgets.QVBoxLayout(self.inputTab)
        self.inputTabLayout.setContentsMargins(10, 10, 10, 10)

        self.inputPreviewLabel = QtWidgets.QLabel(
            "📥 Input TIFF akan ditampilkan di sini setelah file dipilih"
        )
        self.inputPreviewLabel.setAlignment(Qt.AlignCenter)
        self.inputPreviewLabel.setStyleSheet(INPUT_PREVIEW_LABEL_STYLE)
        self.inputPreviewLabel.setMinimumHeight(300)
        self.inputTabLayout.addWidget(self.inputPreviewLabel)

        self.tiffTab = QtWidgets.QWidget()
        self.tiffTabLayout = QtWidgets.QVBoxLayout(self.tiffTab)
        self.tiffTabLayout.setContentsMargins(10, 10, 10, 10)

        self.outputImageLabel = QtWidgets.QLabel("🖼️ Hasil deteksi akan tampil di sini")
        self.outputImageLabel.setAlignment(Qt.AlignCenter)
        self.outputImageLabel.setMinimumHeight(300)
        self.outputImageLabel.setStyleSheet(PREVIEW_LABEL_STYLE)
        self.tiffTabLayout.addWidget(self.outputImageLabel)

        self.outputPathLabel = QtWidgets.QLabel("")
        self.outputPathLabel.setAlignment(Qt.AlignLeft)
        self.outputPathLabel.setStyleSheet("font-size: 9pt; color: #888;")
        self.tiffTabLayout.addWidget(self.outputPathLabel)

        self.tabWidget.addTab(self.inputTab, "📥 Input TIFF")
        self.tabWidget.addTab(self.tiffTab, "🖼️ Output Preview")

        self.shpTab = QtWidgets.QWidget()
        self.shpTabLayout = QtWidgets.QVBoxLayout(self.shpTab)
        self.shpTabLayout.setContentsMargins(10, 10, 10, 10)

        self.outputShapefile = QtWidgets.QLabel("🗺️ Shapefile garis pantai akan ditampilkan di sini")
        self.outputShapefile.setAlignment(Qt.AlignCenter)
        self.outputShapefile.setMinimumHeight(300)
        self.outputShapefile.setStyleSheet(PREVIEW_LABEL_STYLE)
        self.shpTabLayout.addWidget(self.outputShapefile)

        self.tabWidget.addTab(self.inputTab, "📥 Input TIFF")
        self.tabWidget.addTab(self.tiffTab, "🖼️ Output Preview")
        self.tabWidget.addTab(self.shpTab, "🗺️ Shapefile Info")
        self.rightLayout.addWidget(self.tabWidget)

        self.outputInfoLabel = QtWidgets.QLabel(
            "📊 Hasil akan otomatis ditampilkan setelah proses deteksi selesai\n"
            "📁 File output tersimpan di direktori: ./output/"
        )
        self.outputInfoLabel.setFont(QtGui.QFont("Segoe UI", 9))
        self.outputInfoLabel.setAlignment(Qt.AlignCenter)
        self.outputInfoLabel.setWordWrap(True)
        self.outputInfoLabel.setStyleSheet(INFO_LABEL_STYLE)
        self.rightLayout.addWidget(self.outputInfoLabel)
        

    def updateInputPreview(self, image_path):
        try:
            print(f"[DEBUG] Membuka file: {image_path}")
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
                    QMessageBox.warning(
                        self,
                        "Kombinasi Band Tidak Valid",
                        f"File memiliki {band_count} band, tidak bisa memuat kombinasi band {bands_to_read}."
                    )
                    return

                bands = [src.read(b) for b in bands_to_read]
                array = np.stack(bands, axis=-1)

                array = array.astype(np.float32)

                if is_uav:
                    array -= array.min()
                    if array.max() > 0:
                        array /= array.max()
                    array *= 255
                    array = array.astype(np.uint8)
                    
                elif is_sentinel:
                    array = np.clip(array, 0, 10000)
                    
                    p2, p98 = np.percentile(array, (2, 98))
                    array = np.clip((array - p2) / (p98 - p2) * 255, 0, 255)
                    array = array.astype(np.uint8)

                height, width, channel = array.shape
                bytes_per_line = channel * width

                qimg = QtGui.QImage(
                    array.data, width, height, bytes_per_line, QtGui.QImage.Format_RGB888
                )

                pixmap = QtGui.QPixmap.fromImage(qimg)

                scaled_pixmap = pixmap.scaled(
                    self.inputPreviewLabel.width(), 
                    self.inputPreviewLabel.height(), 
                    Qt.KeepAspectRatio, 
                    Qt.SmoothTransformation
                )
                self.inputPreviewLabel.setPixmap(scaled_pixmap)
                self.inputPreviewLabel.setAlignment(Qt.AlignCenter)
                self._lastInputImagePath = image_path
                print("[DEBUG] Gambar berhasil ditampilkan.")

        except Exception as e:
            QMessageBox.critical(self, "Gagal Menampilkan Preview", str(e))
            print(f"[ERROR] updateInputPreview: {e}")
        
    def updateOutputPreview(self, output_path):
        if not os.path.exists(output_path):
            print(f"File tidak ditemukan: {output_path}")
            return

        try:
            with rasterio.open(output_path) as src:
                mask = src.read(1)

                height, width = mask.shape
                rgb_image = np.zeros((height, width, 3), dtype=np.uint8)

                rgb_image[mask == 0] = [160, 160, 160]  # abu-abu
                rgb_image[mask == 1] = [0, 102, 204]    # biru laut

                qimage = QImage(rgb_image.data, width, height, width * 3, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(qimage)

                self.outputImageLabel.setPixmap(pixmap.scaled(
                    self.outputImageLabel.size(),
                    aspectRatioMode=QtCore.Qt.KeepAspectRatio,
                    transformMode=QtCore.Qt.SmoothTransformation
                ))

                self.outputPathLabel.setText(f"Hasil disimpan di:\n{output_path}")

        except Exception as e:
            print(f"Gagal menampilkan output: {e}")

    def updateShapefilePreview(self, shapefile_path):
        try:
            # Baca shapefile dengan pyshp
            sf = shapefile.Reader(shapefile_path)
            shapes = sf.shapes()

            # Tentukan ukuran pixmap (misal 400x300)
            w, h = 400, 300
            pixmap = QPixmap(w, h)
            pixmap.fill(Qt.white)  # background putih

            painter = QPainter(pixmap)
            pen = QPen(QColor(0, 102, 204), 2)  # garis biru tebal 2 px
            painter.setPen(pen)

            # Cari bounding box dari semua shape untuk scaling
            all_points = [pt for shape in shapes for pt in shape.points]
            xs = [pt[0] for pt in all_points]
            ys = [pt[1] for pt in all_points]
            min_x, max_x = min(xs), max(xs)
            min_y, max_y = min(ys), max(ys)

            def scale_point(x, y):
                sx = (x - min_x) / (max_x - min_x) * (w - 20) + 10
                sy = (max_y - y) / (max_y - min_y) * (h - 20) + 10  # invert y-axis
                return int(sx), int(sy)

            for shape in shapes:
                points = [scale_point(x, y) for x, y in shape.points]
                if len(points) > 1:
                    for i in range(len(points) - 1):
                        painter.drawLine(points[i][0], points[i][1], points[i+1][0], points[i+1][1])
                else:
                    # titik tunggal (jika ada)
                    painter.drawPoint(points[0][0], points[0][1])

            painter.end()

            self.outputShapefile.setPixmap(pixmap)
            self.outputShapefile.setAlignment(Qt.AlignCenter)
        except Exception as e:
            self.outputShapefile.setText("Gagal menampilkan shapefile")
            print(f"[ERROR] updateShapefilePreview: {e}")
        
        