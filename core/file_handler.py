from pathlib import Path
from typing import Optional, Dict, Any
import logging
import numpy as np
import rasterio
import geopandas as gpd

from core.predict import extract_coastline


logger = logging.getLogger(__name__)

class FileHandler:
    def __init__(self, output_dir: str = "./output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.current_file_path = None
    
    def validate_file(self, file_path: str) -> bool:
        try:
            path = Path(file_path)
            if not path.exists():
                logger.error(f"File does not exist: {file_path}")
                return False
            
            supported_extensions = ['.tif', '.tiff']
            if path.suffix.lower() not in supported_extensions:
                logger.error(f"Unsupported file format: {path.suffix}")
                return False
            
            file_size = path.stat().st_size
            if file_size > 500 * 1024 * 1024:
                logger.warning(f"Large file size: {file_size / (1024*1024):.1f} MB")
            
            return True
        except Exception as e:
            logger.error(f"File validation error: {str(e)}")
            return False
    
    def set_current_file(self, file_path: str) -> bool:
        if self.validate_file(file_path):
            self.current_file_path = file_path
            return True
        return False
    
    def get_file_info(self, file_path: Optional[str] = None) -> Dict[str, Any]:
        if file_path is None:
            file_path = self.current_file_path
        
        if file_path is None:
            return {}
        
        try:
            path = Path(file_path)
            stat = path.stat()
            
            return {
                'name': path.name,
                'size': stat.st_size,
                'size_mb': stat.st_size / (1024 * 1024),
                'extension': path.suffix,
                'absolute_path': str(path.absolute())
            }
        except Exception as e:
            logger.error(f"Error getting file info: {str(e)}")
            return {}
    
    def generate_output_filename(self, suffix: str = "coastline", extension: str = ".tif") -> str:
        if self.current_file_path is None:
            return f"output_{suffix}{extension}"
        
        input_path = Path(self.current_file_path)
        base_name = input_path.stem
        return f"{base_name}_{suffix}{extension}"
    
    def save_tiff(self, data: np.ndarray, profile: dict, filename: Optional[str] = None) -> Optional[str]:
        try:
            if filename is None:
                filename = self.generate_output_filename("result", ".tif")

            output_path = self.output_dir / filename

            profile_copy = profile.copy()
            profile_copy.update({
                "count": 1,
                "dtype": "uint8",
                "compress": "lzw"
            })

            with rasterio.open(output_path, "w", **profile_copy) as dst:
                dst.write(data.astype("uint8"), 1)

            logger.info(f"TIFF saved to: {output_path}")
            return str(output_path)
        except Exception as e:
            logger.error(f"Error saving TIFF: {str(e)}")
            return None
    
    def save_coastline_shapefile(self, polygons_gdf: gpd.GeoDataFrame, water_class: int = 1, filename: Optional[str] = None) -> Optional[str]:
        try:
            coastline_gdf = extract_coastline(polygons_gdf, water_class)
            if coastline_gdf is None or coastline_gdf.empty:
                logger.warning("No coastline extracted from polygons.")
                return None

            if filename is None:
                filename = self.generate_output_filename("coastline", ".shp")

            output_path = self.output_dir / filename
            coastline_gdf.to_file(output_path)
            logger.info(f"Coastline shapefile saved to: {output_path}")
            return str(output_path)
        except Exception as e:
            logger.error(f"Error saving coastline shapefile: {str(e)}")
            return None
