from models.coastline_detector import CoastlineDetectorFactory, DetectionThread
from utils.helper import choose_model_by_band_count, show_warning_dialog, load_raster_image, validate_model_selection
from config.settings import SUPPORTED_FORMATS
from models.coastline_detector import DetectionThread

from PyQt5.QtWidgets import QFileDialog, QMessageBox

class AppController:
    def __init__(self, main_window):
        self.main_window = main_window
        self.current_detector = None
        self.input_image_path = None
        self.input_image_array = None
        self.detection_thread = None
        self.file_handler = main_window.file_handler

    def browseFile(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self.main_window, "Pilih File TIFF", "", ";;".join(SUPPORTED_FORMATS)
        )

        if file_path:
            is_valid, message = self.file_handler.set_current_file(file_path)
            if not is_valid:
                show_warning_dialog(self.main_window, "File Tidak Valid", message or "File tidak sesuai.")
                return
            elif message:
                QMessageBox.information(self.main_window, "Peringatan Ukuran File", message)

            self.input_image_path = file_path
            self.main_window.fileSectionComponent.setFilePath(file_path)

            image_array, band_count, error = load_raster_image(file_path)
            if error:
                self.input_image_array = None
                self.main_window.fileSectionComponent.setBandInfo("Gagal membaca citra")
                print(f"Error loading image: {error}")
                return

            self.input_image_array = image_array
            self.main_window.fileSectionComponent.setBandInfo(f"Jumlah band terdeteksi: {band_count}")

            model_type = choose_model_by_band_count(band_count)
            if model_type:
                self.main_window.modelSectionComponent.btnSelectType.setCurrentText(model_type)
                self.onModelChanged(model_type)
            else:
                print("Tidak ada model yang sesuai untuk jumlah band ini.")

            self.main_window.outputPanelComponent.updateInputPreview(file_path)

    def clearFile(self):
        self.main_window.fileSectionComponent.clearFile()
        self.input_image_path = None
        self.input_image_array = None
        self.main_window.outputPanelComponent.inputPreviewLabel.clear()
        self.main_window.outputPanelComponent.outputImageLabel.clear()
        self.main_window.outputPanelComponent.outputShapefile.clear()
        self.file_handler.clean_files(parent_widget=self.main_window)

    def onModelChanged(self, model_type):
        band_count = self.input_image_array.shape[2] if self.input_image_array is not None else 0

        if band_count == 0:
            show_warning_dialog(
                self.main_window,
                "Peringatan Model Tidak Sesuai",
                "Tidak ada citra yang dimuat. Mohon pilih file TIFF terlebih dahulu."
            )
            return

        is_valid, warning_msg = validate_model_selection(model_type, band_count)
        if not is_valid:
            show_warning_dialog(self.main_window, "Peringatan Model Tidak Sesuai", warning_msg)
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

        self.main_window.processSectionComponent.setProcessingState(True)

        self.detection_thread = DetectionThread(
            self.current_detector,
            self.input_image_path,
            self.input_image_array
        )
        self.detection_thread.detectionFinished.connect(self.onDetectionFinished)
        self.detection_thread.detectionFailed.connect(self.onDetectionFailed)
        self.detection_thread.start()

    def onDetectionFinished(self, output_path, meta):
        self.main_window.processSectionComponent.setProcessingState(False)
        print("Deteksi selesai dengan metadata:", meta)
        print(f"Hasil deteksi disimpan di: {output_path}")
        self.main_window.outputPanelComponent.updateOutputPreview(output_path)
        shapefile_path = meta.get('shapefile_path', None) if meta else None
        if shapefile_path:
            self.main_window.outputPanelComponent.updateShapefilePreview(shapefile_path)

    def onDetectionFailed(self, error_msg):
        self.main_window.processSectionComponent.setProcessingState(False)
        print("Error saat proses deteksi:", error_msg)
        show_warning_dialog(self.main_window, "Error Proses Deteksi", error_msg)
