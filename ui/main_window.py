from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGraphicsDropShadowEffect, QFileDialog, QMessageBox
from config.settings import SUPPORTED_FORMATS
import rasterio
import numpy as np

from models.coastline_detector import DetectionThread
from config.settings import WINDOW_WIDTH, WINDOW_HEIGHT, LEFT_PANEL_WIDTH, APP_NAME
from .styles.base_styles import MAIN_WINDOW_STYLE, PANEL_STYLE
from .components.headers import HeaderComponent
from .components.file_section import FileSectionComponent
from .components.model_section import ModelSectionComponent
from .components.process_section import ProcessSectionComponent
from .components.output_panel import OutputPanelComponent
from models.coastline_detector import CoastlineDetectorFactory
from utils.helper import choose_model_by_band_count

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi()
        self.connectSignals()
        self.current_detector = None
        self.input_image_path = None
        self.input_image_array = None
        self.detection_thread = None

    def setupUi(self):
        self.setObjectName("MainWindow")
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setWindowTitle(APP_NAME)
        self.setStyleSheet(MAIN_WINDOW_STYLE)

        self.centralwidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.centralwidget)

        self.mainLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.mainLayout.setContentsMargins(30, 30, 30, 30)
        self.mainLayout.setSpacing(25)

        self.headerComponent = HeaderComponent()
        self.mainLayout.addWidget(self.headerComponent)

        self.contentHorizontalLayout = QtWidgets.QHBoxLayout()
        self.contentHorizontalLayout.setSpacing(20)

        self.leftPanel = QtWidgets.QFrame()
        self.leftPanel.setFixedWidth(LEFT_PANEL_WIDTH)
        self.leftPanel.setStyleSheet(PANEL_STYLE)
        left_shadow = QGraphicsDropShadowEffect()
        left_shadow.setBlurRadius(15)
        left_shadow.setColor(QtGui.QColor(0, 0, 0, 30))
        left_shadow.setOffset(0, 3)
        self.leftPanel.setGraphicsEffect(left_shadow)

        self.leftLayout = QtWidgets.QVBoxLayout(self.leftPanel)
        self.leftLayout.setContentsMargins(30, 25, 30, 25)
        self.leftLayout.setSpacing(20)

        self.fileSectionComponent = FileSectionComponent()
        self.modelSectionComponent = ModelSectionComponent()
        self.processSectionComponent = ProcessSectionComponent()

        self.leftLayout.addWidget(self.fileSectionComponent)
        self.leftLayout.addWidget(self.modelSectionComponent)
        self.leftLayout.addWidget(self.processSectionComponent)
        self.leftLayout.addStretch()

        self.outputPanelComponent = OutputPanelComponent()

        self.contentHorizontalLayout.addWidget(self.leftPanel)
        self.contentHorizontalLayout.addWidget(self.outputPanelComponent, 1)

        self.mainLayout.addLayout(self.contentHorizontalLayout, 1)

        self.footerLabel = QtWidgets.QLabel("© 2024 CoDec App - Advanced Coastline Analysis Tool")
        self.footerLabel.setAlignment(Qt.AlignCenter)
        self.footerLabel.setFont(QtGui.QFont("Segoe UI", 9))
        self.mainLayout.addWidget(self.footerLabel)

        QtCore.QMetaObject.connectSlotsByName(self)

    def connectSignals(self):
        self.fileSectionComponent.btnBrowse.clicked.connect(self.browseFile)
        self.fileSectionComponent.btnClear.clicked.connect(self.clearFile)
        self.modelSectionComponent.btnSelectType.currentTextChanged.connect(self.onModelChanged)
        self.processSectionComponent.btnRun.clicked.connect(self.runDetection)

    def showWarning(self, title: str, message: str):
        warning_box = QMessageBox(self)
        warning_box.setIcon(QMessageBox.Warning)
        warning_box.setWindowTitle(title)
        warning_box.setText(message)
        warning_box.setStandardButtons(QMessageBox.Ok)
        warning_box.exec_()

    def browseFile(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Pilih File TIFF", "", ";;".join(SUPPORTED_FORMATS)
        )

        if file_path:
            self.input_image_path = file_path
            self.fileSectionComponent.setFilePath(file_path)

            try:
                with rasterio.open(file_path) as dataset:
                    image_array = dataset.read()  # (band, H, W)
                    image_array = np.transpose(image_array, (1, 2, 0))  # (H, W, band)
                    self.input_image_array = image_array

                    band_count = dataset.count
                    self.fileSectionComponent.setBandInfo(f"Jumlah band terdeteksi: {band_count}")

                    model_type = choose_model_by_band_count(band_count)

                    if model_type:
                        self.modelSectionComponent.btnSelectType.setCurrentText(model_type)
                        self.onModelChanged(model_type)
                    else:
                        print("Tidak ada model yang sesuai untuk jumlah band ini.")

                    self.outputPanelComponent.updateInputPreview(file_path)

            except Exception as e:
                self.input_image_array = None
                self.fileSectionComponent.setBandInfo("Gagal membaca citra")
                print(f"Error loading image: {e}")

    def clearFile(self):
        self.fileSectionComponent.clearFile()
        self.input_image_path = None
        self.input_image_array = None
        self.outputPanelComponent.inputPreviewLabel.clear()
        self.outputPanelComponent.outputImageLabel.clear()
        self.outputPanelComponent.outputShapefile.clear()
        self.outputPanelComponent.clear_output_files()

    def onModelChanged(self, model_type):
        band_count = self.input_image_array.shape[2] if self.input_image_array is not None else 0

        if band_count == 0:
            self.showWarning(
                "Peringatan Model Tidak Sesuai",
                "Tidak ada citra yang dimuat. Mohon pilih file TIFF terlebih dahulu."
            )
            return

        if model_type == "🚁 UAV" and band_count not in [3, 4]:
            self.showWarning(
                "Peringatan Model Tidak Sesuai",
                "Model UAV memerlukan citra dengan 3 atau 4 band. Mohon pilih file yang sesuai."
            )
            return
        elif model_type == "🛰️ Sentinel-2" and band_count <= 4:
            self.showWarning(
                "Peringatan Model Tidak Sesuai",
                "Model Sentinel-2 memerlukan citra dengan lebih dari 4 band. Mohon pilih file yang sesuai."
            )
            return

        self.current_detector = CoastlineDetectorFactory.create_detector(model_type)
        if self.current_detector:
            loaded = self.current_detector.load_model()
            if loaded:
                print(f"{self.current_detector.model_name} loaded successfully.")
            else:
                print(f"Failed to load {self.current_detector.model_name}.")
        else:
            print("Model tidak dikenali.")

    def runDetection(self):
        if not self.current_detector or not self.current_detector.is_loaded:
            print("Model belum dipilih atau gagal dimuat")
            return
        if self.input_image_array is None or self.input_image_path is None:
            print("Input image belum dipilih atau gagal dimuat")
            return

        self.processSectionComponent.setProcessingState(True)

        self.detection_thread = DetectionThread(
            self.current_detector,
            self.input_image_path,
            self.input_image_array
        )
        self.detection_thread.detectionFinished.connect(self.onDetectionFinished)
        self.detection_thread.detectionFailed.connect(self.onDetectionFailed)
        self.detection_thread.start()

    def onDetectionFinished(self, output_path, meta):
        self.processSectionComponent.setProcessingState(False)
        print("Deteksi selesai dengan metadata:", meta)
        print(f"Hasil deteksi disimpan di: {output_path}")
        self.outputPanelComponent.updateOutputPreview(output_path)
        shapefile_path = meta.get('shapefile_path', None) if meta else None
        if shapefile_path:
            self.outputPanelComponent.updateShapefilePreview(shapefile_path)

    def onDetectionFailed(self, error_msg):
        self.processSectionComponent.setProcessingState(False)
        print("Error saat proses deteksi:", error_msg)
        self.showWarning("Error Proses Deteksi", error_msg)
