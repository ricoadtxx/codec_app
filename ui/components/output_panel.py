from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGraphicsDropShadowEffect, QMessageBox
import os

from ..styles.component_styles import (
    OUTPUT_HEADER_STYLE, TAB_WIDGET_STYLE, PREVIEW_LABEL_STYLE,
    INPUT_PREVIEW_LABEL_STYLE
)
from ..styles.base_styles import PANEL_STYLE
from utils.image_processor import (
    generate_input_preview,
    generate_output_mask_preview,
    generate_shapefile_preview
)

class OutputPanelComponent(QtWidgets.QFrame):
    def __init__(self):
        super().__init__()
        self._lastInputImagePath = None
        self._lastOutputImagePath = None
        self.file_handler = None
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

        # Input TIFF Tab
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

        # Output Preview Tab
        self.tiffTab = QtWidgets.QWidget()
        self.tiffTabLayout = QtWidgets.QVBoxLayout(self.tiffTab)
        self.tiffTabLayout.setContentsMargins(10, 10, 10, 10)

        self.outputImageLabel = QtWidgets.QLabel("🖼️ Hasil deteksi akan tampil di sini")
        self.outputImageLabel.setAlignment(Qt.AlignCenter)
        self.outputImageLabel.setMinimumHeight(300)
        self.outputImageLabel.setStyleSheet(PREVIEW_LABEL_STYLE)
        self.tiffTabLayout.addWidget(self.outputImageLabel)

        # Shapefile Tab
        self.shpTab = QtWidgets.QWidget()
        self.shpTabLayout = QtWidgets.QVBoxLayout(self.shpTab)
        self.shpTabLayout.setContentsMargins(10, 10, 10, 10)

        self.outputShapefile = QtWidgets.QLabel("🗺️ Shapefile garis pantai akan ditampilkan di sini")
        self.outputShapefile.setAlignment(Qt.AlignCenter)
        self.outputShapefile.setMinimumHeight(300)
        self.outputShapefile.setStyleSheet(PREVIEW_LABEL_STYLE)
        self.shpTabLayout.addWidget(self.outputShapefile)

        # Add Tabs
        self.tabWidget.addTab(self.inputTab, "📥 Input TIFF")
        self.tabWidget.addTab(self.tiffTab, "🖼️ Output Preview")
        self.tabWidget.addTab(self.shpTab, "🗺️ Shapefile Info")
        self.rightLayout.addWidget(self.tabWidget)

        # Download Button
        self.downloadButton = QtWidgets.QPushButton("📥 Download Output")
        self.downloadButton.setCursor(Qt.PointingHandCursor)
        self.downloadButton.setEnabled(True)
        self.downloadButton.setStyleSheet("padding: 6px 12px;")
        self.layout().addWidget(self.downloadButton)

    def updateInputPreview(self, image_path):
        try:
            print(f"[DEBUG] Membuka file: {image_path}")
            pixmap = generate_input_preview(
                image_path,
                self.inputPreviewLabel.width(),
                self.inputPreviewLabel.height()
            )
            self.inputPreviewLabel.setPixmap(pixmap)
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
            pixmap = generate_output_mask_preview(
                output_path,
                self.outputImageLabel.width(),
                self.outputImageLabel.height()
            )
            self.outputImageLabel.setPixmap(pixmap)
        except Exception as e:
            QMessageBox.critical(self, "Gagal Menampilkan Output", str(e))
            print(f"[ERROR] updateOutputPreview: {e}")

    def updateShapefilePreview(self, shapefile_path):
        try:
            pixmap = generate_shapefile_preview(shapefile_path)
            self.outputShapefile.setPixmap(pixmap)
            self.outputShapefile.setAlignment(Qt.AlignCenter)
        except Exception as e:
            self.outputShapefile.setText("Gagal menampilkan shapefile")
            print(f"[ERROR] updateShapefilePreview: {e}")

    def set_file_handler(self, file_handler):
        self.file_handler = file_handler
        self.downloadButton.clicked.connect(self.handle_download)

    def handle_download(self):
        if not self.file_handler:
            QMessageBox.warning(self, "Error", "FileHandler belum tersedia.")
            return

        zip_path = self.file_handler.download_and_clear_outputs(parent_widget=self)

        if not zip_path:
            QMessageBox.warning(self, "Gagal", "Tidak ada file output untuk dikompres.")
            return

        QMessageBox.information(self, "Berhasil", f"Hasil disimpan ke:\n{zip_path}")
