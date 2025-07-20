"""File handling operations"""
import os
import shutil
from pathlib import Path
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class FileHandler:
    """Handle file operations for the application"""
    
    def __init__(self, output_dir: str = "./output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.current_file_path = None
    
    def validate_file(self, file_path: str) -> bool:
        """Validate if the file is a supported format"""
        try:
            path = Path(file_path)
            if not path.exists():
                logger.error(f"File does not exist: {file_path}")
                return False
            
            # Check file extension
            supported_extensions = ['.tif', '.tiff']
            if path.suffix.lower() not in supported_extensions:
                logger.error(f"Unsupported file format: {path.suffix}")
                return False
            
            # Check file size (optional)
            file_size = path.stat().st_size
            if file_size > 500 * 1024 * 1024:  # 500MB limit
                logger.warning(f"Large file size: {file_size / (1024*1024):.1f} MB")
            
            return True
        except Exception as e:
            logger.error(f"File validation error: {str(e)}")
            return False
    
    def set_current_file(self, file_path: str) -> bool:
        """Set the current working file"""
        if self.validate_file(file_path):
            self.current_file_path = file_path
            return True
        return False
    
    def get_file_info(self, file_path: Optional[str] = None) -> Dict[str, Any]:
        """Get information about a file"""
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
        """Generate output filename based on input file"""
        if self.current_file_path is None:
            return f"output_{suffix}{extension}"
        
        input_path = Path(self.current_file_path)
        base_name = input_path.stem
        return f"{base_name}_{suffix}{extension}"
    
    def save_output_tiff(self, data, filename: Optional[str] = None) -> Optional[str]:
        """Save output TIFF file"""
        try:
            if filename is None:
                filename = self.generate_output_filename("result", ".tif")
            
            output_path = self.output_dir / filename
            
            # TODO: Implement TIFF saving with rasterio
            # This is a placeholder
            logger.info(f"Would save TIFF to: {output_path}")
            
            return str(output_path)
        except Exception as e:
            logger.error(f"Error saving TIFF: {str(e)}")
            return None
    
    def save_output_shapefile(self, data, filename: Optional[str] = None) -> Optional[str]:
        """Save output shapefile"""
        try:
            if filename is None:
                filename = self.generate_output_filename("coastline", ".shp")
            
            output_path = self.output_dir / filename
            
            # TODO: Implement shapefile saving with geopandas
            # This is a placeholder
            logger.info(f"Would save shapefile to: {output_path}")
            
            return str(output_path)
        except Exception as e:
            logger.error(f"Error saving shapefile: {str(e)}")
            return None
    
    def cleanup_temp_files(self):
        """Clean up temporary files"""
        try:
            temp_dir = self.output_dir / "temp"
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
                logger.info("Temporary files cleaned up")
        except Exception as e:
            logger.error(f"Error cleaning up temp files: {str(e)}")
    
    def get_output_files(self) -> Dict[str, list]:
        """Get list of output files by type"""
        try:
            tiff_files = list(self.output_dir.glob("*.tif")) + list(self.output_dir.glob("*.tiff"))
            shp_files = list(self.output_dir.glob("*.shp"))
            
            return {
                'tiff': [str(f) for f in tiff_files],
                'shapefile': [str(f) for f in shp_files]
            }
        except Exception as e:
            logger.error(f"Error getting output files: {str(e)}")
            return {'tiff': [], 'shapefile': []}