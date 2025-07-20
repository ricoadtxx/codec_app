"""Image processing core functionality"""
import numpy as np
import cv2
from typing import Optional, Tuple
import logging
import rasterio

logger = logging.getLogger(__name__)

class ImageProcessor:
    def __init__(self):
        self.current_image = None
        self.processed_image = None
        self.image_info = {}
    
    def load_image(self, file_path: str) -> bool:
        """Load multi-band TIFF image using rasterio"""
        try:
            with rasterio.open(file_path) as src:
                self.current_image = src.read().astype(np.float32)  # pastikan float32 untuk processing
                self.image_info = {
                    'height': src.height,
                    'width': src.width,
                    'channels': src.count,
                    'dtype': str(src.dtypes[0]),
                    'crs': src.crs,
                    'transform': src.transform,
                    'file_path': file_path
                }
            logger.info(f"Image loaded successfully with rasterio: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error loading image with rasterio: {str(e)}")
            return False
    
    def extract_image_info(self):
        """Extract information about the loaded image"""
        if self.current_image is not None:
            shape = self.current_image.shape
            self.image_info = {
                'height': shape[0],
                'width': shape[1],
                'channels': shape[2] if len(shape) > 2 else 1,
                'dtype': str(self.current_image.dtype)
            }
    
    def get_band_info(self) -> str:
        """Get band information string for display"""
        if self.image_info:
            return f"Channels: {self.image_info['channels']}, Size: {self.image_info['width']}x{self.image_info['height']}"
        return ""
    
    def preprocess_for_uav(self) -> bool:
        try:
            logger.info("Preprocessing for UAV model")
            return True
        except Exception as e:
            logger.error(f"UAV preprocessing error: {str(e)}")
            return False
    
    def preprocess_for_sentinel(self) -> bool:
        """Preprocess image for Sentinel-2 model"""
        try:
            # TODO: Implement Sentinel-2 specific preprocessing
            logger.info("Preprocessing for Sentinel-2 model")
            return True
        except Exception as e:
            logger.error(f"Sentinel-2 preprocessing error: {str(e)}")
            return False
    
    def detect_coastline(self, model_type: str) -> bool:
        """Perform coastline detection"""
        try:
            if model_type == "🚁 UAV":
                return self.detect_coastline_uav()
            elif model_type == "🛰️ Sentinel-2":
                return self.detect_coastline_sentinel()
            else:
                logger.error(f"Unknown model type: {model_type}")
                return False
        except Exception as e:
            logger.error(f"Coastline detection error: {str(e)}")
            return False
    
    def detect_coastline_uav(self) -> bool:
        """UAV-specific coastline detection"""
        # TODO: Implement UAV coastline detection algorithm
        logger.info("Running UAV coastline detection")
        return True
    
    def detect_coastline_sentinel(self) -> bool:
        """Sentinel-2 specific coastline detection"""
        # TODO: Implement Sentinel-2 coastline detection algorithm
        logger.info("Running Sentinel-2 coastline detection")
        return True
    
    def get_preview_image(self, max_size: Tuple[int, int] = (400, 400)) -> Optional[np.ndarray]:
        """Get a preview-sized version of the current image"""
        if self.current_image is None:
            return None
        
        try:
            # Calculate scaling factor
            h, w = self.current_image.shape[:2]
            max_h, max_w = max_size
            scale = min(max_w / w, max_h / h)
            
            if scale < 1:
                new_w = int(w * scale)
                new_h = int(h * scale)
                preview = cv2.resize(self.current_image, (new_w, new_h))
            else:
                preview = self.current_image.copy()
            
            return preview
        except Exception as e:
            logger.error(f"Error creating preview: {str(e)}")
            return None