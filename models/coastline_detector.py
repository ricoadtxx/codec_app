import os
import numpy as np
import rasterio
from abc import ABC, abstractmethod
from typing import Optional, Tuple, Dict, Any
from keras.models import load_model
from PyQt5.QtCore import QThread, pyqtSignal
from datetime import datetime

import logging

from utils.preprocess import preprocess_image_uav, preprocess_sentinel2
from utils.postprocess import  morphological_smooth, mask_to_polygons, extract_coastline
from core.file_handler import FileHandler
from utils.helper import resource_path, run_patch_prediction

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
    def postprocess(self, transform, crs, detection_result: np.ndarray) -> np.ndarray:
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
        self.model_path = model_path or "models/uav.h5"
        self.model = None
        self.metadata = {}

    def load_model(self) -> bool:
        try:
            full_path = resource_path(self.model_path)
            self.model = load_model(full_path, compile=False)
            self.is_loaded = True
            logger.info("UAV model loaded successfully")
            return True
        except Exception as e:
            logger.error(f"Error loading UAV model: {str(e)}")
            return False

    def preprocess(self, image_path: str) -> Tuple[np.ndarray, dict, Any, Any]:
        try:
            rgb_image, profile, transform, crs = preprocess_image_uav(image_path)
            logger.info("UAV image preprocessing completed")
            return rgb_image, profile, transform, crs
        except Exception as e:
            logger.error(f"UAV preprocessing error: {str(e)}")
            raise

    def detect(self, rgb_image: np.ndarray, tile_size: int = 256) -> Tuple[np.ndarray, Dict[str, Any]]:
        try:
            mask = run_patch_prediction(
                model=self.model,
                image=rgb_image,
                tile_size=256,
                channels_last=True,
                is_multichannel=True
            )
            self.metadata = {
                'method': 'uav_model_segmentation',
                'tile_size': tile_size,
                'input_shape': rgb_image.shape,
            }
            return mask, self.metadata

        except Exception as e:
            logger.exception(f"UAV detection error: {str(e)}")
            return np.zeros(rgb_image.shape[:2], dtype=np.uint8), {}

    def postprocess(self, detection_result: np.ndarray, transform, crs, water_class: int = 1) -> dict:
        try:
            smoothed_mask = morphological_smooth(detection_result, kernel_size=7, iterations=1)
            
            polygons_gdf = mask_to_polygons(smoothed_mask, transform, crs)
            
            coastline_gdf = None
            
            if polygons_gdf is not None and not polygons_gdf.empty:
                coastline_gdf = extract_coastline(polygons_gdf, water_class)
            else:
                logger.warning("Polygons Kosong")
                
            logger.info("Proses UAV Selesai")
            
            return {
                'mask': smoothed_mask,
                'polygons': polygons_gdf,
                'coastline': coastline_gdf
            }
        
        except Exception as e:
            logger.error(f"Proses UAV Error: {str(e)}")
            return{
                'mask': detection_result,
                'polygons': None,
                'coastline': None
            }

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
            full_path = resource_path(self.model_path)
            self.model = load_model(full_path, compile=False)
            self.is_loaded = True
            logger.info("Sentinel-2 coastline detection model loaded successfully")
            return True
        except Exception as e:
            logger.error(f"Error loading Sentinel-2 model: {str(e)}")
            return False

    def preprocess(self, image_path: str) -> Tuple[np.ndarray, dict]:
        try:
            ndwi_stack, profile, transform, crs, bands = preprocess_sentinel2(image_path, ndwi_threshold=self.ndwi_threshold)
            logger.info("Preprocess sentinel-2 berhasil")
            return ndwi_stack, profile, transform, crs, bands
        except Exception as e:
            logger.error(f"UAV preprocessing error: {str(e)}")
            raise

    def detect(self, ndwi_stack: np.ndarray, tile_size: int = 256) -> Tuple[np.ndarray, dict]:
        try:
            ndwi = ndwi_stack[0]
            mask = run_patch_prediction(
                model=self.model,
                image=ndwi,
                tile_size=256,
                channels_last=True,
                is_multichannel=False
            )
            self.metadata = {'method': 'sentinel_segmentation', 'tile_size': tile_size}
            return mask, self.metadata
        
        except Exception as e:
            logger.error(f"Sentinel detection error: {e}")
            return np.zeros(ndwi_stack.shape[1:3], dtype=np.uint8), {}
    
    def postprocess(self, detection_result: np.ndarray, transform, crs, water_class: int = 1) -> dict:
        try:
            binary_mask = (detection_result > 0.5).astype(np.uint8)
            
            polygons_gdf = mask_to_polygons(binary_mask, transform, crs)
            coastline_gdf = None
            
            if polygons_gdf is not None and not polygons_gdf.empty:
                coastline_gdf = extract_coastline(polygons_gdf, water_class)
            else:
                logger.warning("Polygons Kosong")
                
            logger.info("Proses Satelit Selesai")
            
            return {
                'mask': binary_mask,
                'polygons': polygons_gdf,
                'coastline': coastline_gdf
            }
            
        except Exception as e:
            logger.error(f"Proses Sentinel Error: {str(e)}")
            return{
                'mask': detection_result,
                'polygons': None,
                'coastline': None
            }

class CoastlineDetectorFactory:
    @staticmethod
    def create_detector(model_type: str) -> Optional[BaseCoastlineDetector]:
        if model_type == "✈️ UAV":
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

            if self.detector.model_name == "UAV_CoastlineDetector":
                preprocessed, profile, transform, crs = self.detector.preprocess(self.input_image_path)
                mask, meta = self.detector.detect(preprocessed)
                postprocess_result = self.detector.postprocess(mask, transform, crs, water_class=1)
            elif self.detector.model_name == "Sentinel2_CoastlineDetector":
                preprocessed, profile, transform, crs, bands = self.detector.preprocess(self.input_image_path)
                mask, meta = self.detector.detect(preprocessed)
                postprocess_result = self.detector.postprocess(mask, transform, crs, water_class=1)
            else:
                self.detectionFailed.emit("Model tidak dikenali")
                return
            
            result_mask = postprocess_result['mask']
            polygons_gdf = postprocess_result['polygons']
            coastline_gdf = postprocess_result['coastline']
            
            tiff_path = self.file_handler.save_tiff(result_mask, profile, filename=output_filename)
            shp_path = None
            
            if polygons_gdf is not None and not polygons_gdf.empty:
                shp_path = self.file_handler.save_coastline_shapefile(polygons_gdf, water_class=1)
            else:
                logger.warning("Polygons kosong")
                
            meta.update({
                'tiff_path': tiff_path,
                'shapefile_path': shp_path,
                'polygons_available': polygons_gdf is not None and not polygons_gdf.empty,
                'coastline_available': coastline_gdf is not None and not coastline_gdf.empty
            })
            
            self.detectionFinished.emit(tiff_path or "", meta)

        except Exception as e:
            logger.error(f"Error during detection: {str(e)}")
            self.detectionFailed.emit(str(e))