import os
import numpy as np
import rasterio
from abc import ABC, abstractmethod
from typing import Optional, Tuple, Dict, Any
from keras.models import load_model
from PyQt5.QtCore import QThread, pyqtSignal
from datetime import datetime

import logging

from config.settings import SENTINEL2_BANDS
from core.predict import preprocess_image, morphological_smooth, predict, save_tiff, mask_to_polygons, extract_coastline
from core.file_handler import FileHandler

logger = logging.getLogger(__name__)

class BaseCoastlineDetector(ABC):
    def __init__(self):
        self.model_name = "BaseDetector"
        self.is_loaded = False
        self.parameters = {}
    
    @abstractmethod
    def load_model(self) -> bool:
        pass
    
    @abstractmethod
    def preprocess(self, image: np.ndarray) -> np.ndarray:
        pass
    
    @abstractmethod
    def detect(self, image: np.ndarray) -> Tuple[np.ndarray, Dict[str, Any]]:
        pass
    
    @abstractmethod
    def postprocess(self, detection_result: np.ndarray) -> np.ndarray:
        pass

class UAVCoastlineDetector(BaseCoastlineDetector):
    def __init__(self, model_path: Optional[str] = None):
        super().__init__()
        self.model_name = "UAV_CoastlineDetector"
        self.parameters = {
            'threshold': 0.5,
            'min_area': 100,
            'gaussian_blur': (5, 5)
        }
        self.model_path = model_path or "models/uav_model.h5"
        self.model = None
        self.metadata = {}

    def load_model(self) -> bool:
        try:
            self.model = load_model(self.model_path, compile=False)
            self.is_loaded = True
            logger.info("UAV model loaded successfully")
            return True
        except Exception as e:
            logger.error(f"Error loading UAV model: {str(e)}")
            return False

    def preprocess(self, image_path: str) -> Tuple[np.ndarray, dict, Any, Any]:
        try:
            rgb_image, profile, transform, crs = preprocess_image(image_path)
            logger.info("UAV image preprocessing completed")
            return rgb_image, profile, transform, crs
        except Exception as e:
            logger.error(f"UAV preprocessing error: {str(e)}")
            raise

    def detect(self, rgb_image: np.ndarray, tile_size: int = 256) -> Tuple[np.ndarray, Dict[str, Any]]:
        try:
            mask = predict(self.model, rgb_image, tile_size)
            self.metadata = {
                'method': 'uav_model_segmentation',
                'tile_size': tile_size
            }
            logger.info("UAV coastline detection completed")
            return mask, self.metadata
        except Exception as e:
            logger.error(f"UAV detection error: {str(e)}")
            return np.zeros(rgb_image.shape[:2], dtype=np.uint8), {}
            
    def postprocess(self, detection_result: np.ndarray) -> np.ndarray:
        try:
            smoothed = morphological_smooth(detection_result, kernel_size=7, iterations=1)
            logger.info("UAV postprocessing completed")
            return smoothed
        except Exception as e:
            logger.error(f"UAV postprocessing error: {str(e)}")
            return detection_result
        
    def convert_to_polygons(self, mask: np.ndarray, transform, crs):
        try:
            return mask_to_polygons(mask, transform, crs)
        except Exception as e:
            logger.error(f"Error converting to polygons: {str(e)}")
            return None
        
    def get_coastline(self, polygons_gdf, water_class: int = 1):
        try:
            return extract_coastline(polygons_gdf, water_class)
        except Exception as e:
            logger.error(f"Error extracting coastline: {str(e)}")
            return None

class SentinelCoastlineDetector(BaseCoastlineDetector):
    def __init__(self, model_path=None):
        super().__init__()
        self.model_name = "Sentinel2_CoastlineDetector"
        self.model_path = model_path or "models/sentinel.h5"
        self.model = None
        self.ndwi_threshold = 0.5
        self.parameters = {
            'water_index_threshold': self.ndwi_threshold,
            'bands': ['B3', 'B8', 'B11'],
            'resolution': 10
        }
        self.metadata = {}

    def load_model(self) -> bool:
        try:
            if not self.model_path:
                raise ValueError("Model path is not set.")
            self.model = load_model(self.model_path, compile=False)
            self.is_loaded = True
            logger.info("Sentinel-2 coastline detection model loaded successfully")
            return True
        except Exception as e:
            logger.error(f"Error loading Sentinel-2 model: {str(e)}")
            return False

    def preprocess(self, image_array: np.ndarray) -> np.ndarray:
        bands = np.zeros((13, image_array.shape[0], image_array.shape[1]), dtype=np.float32)
        for i in range(min(image_array.shape[2], 13)):
            bands[i] = image_array[:, :, i].astype(np.float32)

        green = bands[SENTINEL2_BANDS['B3']]
        nir = bands[SENTINEL2_BANDS['B8']]

        denom = green + nir
        denom = np.where(denom == 0, 1e-8, denom)
        ndwi = (green - nir) / denom
        ndwi = np.nan_to_num(ndwi, nan=0.0, posinf=1.0, neginf=-1.0)
        ndwi_norm = (ndwi + 1) / 2
        ndwi_norm = np.where(ndwi_norm < self.ndwi_threshold, 0.0, ndwi_norm)

        self.bands = bands
        self.ndwi = ndwi
        return np.expand_dims(ndwi_norm, axis=0)

    def detect(self, ndwi_stack: np.ndarray, tile_size: int = 256) -> Tuple[np.ndarray, Dict[str, Any]]:
        ndwi = ndwi_stack[0]
        h, w = ndwi.shape
        mask = np.zeros((h, w), dtype=np.uint8)
        rows = list(range(0, h, tile_size))
        cols = list(range(0, w, tile_size))

        for row in rows:
            for col in cols:
                patch_h = min(tile_size, h - row)
                patch_w = min(tile_size, w - col)
                patch = ndwi[row:row + patch_h, col:col + patch_w]

                padded = np.zeros((tile_size, tile_size), dtype=np.float32)
                padded[:patch_h, :patch_w] = patch

                input_patch = np.expand_dims(padded, axis=(0, -1))
                pred = self.model.predict(input_patch, verbose=0)
                pred_mask = np.argmax(pred[0], axis=-1).astype(np.uint8)
                mask[row:row + patch_h, col:col + patch_w] = pred_mask[:patch_h, :patch_w]

        self.metadata = {
            'tile_size': tile_size,
            'confidence': 0.85,
            'processing_time': 0.0
        }
        return mask, self.metadata

    def postprocess(self, mask: np.ndarray) -> np.ndarray:
        return mask

    def convert_to_polygons(self, mask: np.ndarray, transform, crs):
        try:
            return mask_to_polygons(mask, transform, crs)
        except Exception as e:
            logger.error(f"Error converting to polygons: {str(e)}")
            return None
        
    def get_coastline(self, polygons_gdf, water_class: int = 1):
        try:
            return extract_coastline(polygons_gdf, water_class)
        except Exception as e:
            logger.error(f"Error extracting coastline: {str(e)}")
            return None

class CoastlineDetectorFactory:
    @staticmethod
    def create_detector(model_type: str) -> Optional[BaseCoastlineDetector]:
        if model_type == "🚁 UAV":
            return UAVCoastlineDetector(model_path="models/uav.h5")
        elif model_type == "🛰️ Sentinel-2":
            return SentinelCoastlineDetector(model_path="models/sentinel.h5")
        else:
            logger.error(f"Unknown model type: {model_type}")
            return None

class DetectionThread(QThread):
    detectionFinished = pyqtSignal(str, dict)
    detectionFailed = pyqtSignal(str)

    def __init__(self, detector, input_image_path, input_image_array):
        super().__init__()
        self.detector = detector
        self.input_image_path = input_image_path
        self.input_image_array = input_image_array
        self.file_handler = FileHandler()

    def run(self):
        try:
            os.makedirs(self.file_handler.output_dir, exist_ok=True)

            base_name = os.path.basename(self.input_image_path).replace('.tif', '')
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"{base_name}_deteksi_{timestamp}.tif"
            output_path = os.path.join(self.file_handler.output_dir, output_filename)

            if self.detector.model_name == "UAV_CoastlineDetector":
                preprocessed, profile, transform, crs = self.detector.preprocess(self.input_image_path)
                mask, meta = self.detector.detect(preprocessed)
            elif self.detector.model_name == "Sentinel2_CoastlineDetector":
                preprocessed = self.detector.preprocess(self.input_image_array)
                mask, meta = self.detector.detect(preprocessed)
                with rasterio.open(self.input_image_path) as src:
                    profile = src.profile
                    transform = src.transform
                    crs = src.crs
            else:
                self.detectionFailed.emit("Model tidak dikenali")
                return

            result = self.detector.postprocess(mask)

            tiff_path = self.file_handler.save_tiff(result, profile, filename=output_filename)
            
            polygons_gdf = self.detector.convert_to_polygons(result, transform, crs)
            if polygons_gdf is None or polygons_gdf.empty:
                logger.warning("Polygons GeoDataFrame is empty or None")
                shp_path = None
            else:
                shp_path = self.file_handler.save_coastline_shapefile(polygons_gdf, water_class=1)

            meta.update({
                'tiff_path': tiff_path,
                'shapefile_path': shp_path
            })

            self.detectionFinished.emit(tiff_path or "", meta)

        except Exception as e:
            logger.error(f"Error during detection: {str(e)}")
            self.detectionFailed.emit(str(e))