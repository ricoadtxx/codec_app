"""Utility helper functions"""
import os
import time
from pathlib import Path
from typing import Union, Optional, Dict, Any
import logging

def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None) -> logging.Logger:
    """Setup application logging"""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file) if log_file else logging.NullHandler()
        ]
    )
    return logging.getLogger(__name__)

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024.0 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    return f"{size_bytes:.1f} {size_names[i]}"

def format_processing_time(start_time: float) -> str:
    """Format processing time duration"""
    duration = time.time() - start_time
    if duration < 60:
        return f"{duration:.1f} seconds"
    elif duration < 3600:
        return f"{duration/60:.1f} minutes"
    else:
        return f"{duration/3600:.1f} hours"

def create_directory_structure(base_path: Union[str, Path]) -> bool:
    """Create required directory structure"""
    try:
        base_path = Path(base_path)
        directories = [
            base_path / "output",
            base_path / "output" / "tiff",
            base_path / "output" / "shapefile",
            base_path / "output" / "temp",
            base_path / "logs"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
        
        return True
    except Exception as e:
        logging.error(f"Error creating directory structure: {str(e)}")
        return False

def validate_image_path(file_path: Union[str, Path]) -> Dict[str, Any]:
    """Validate image file path and return info"""
    try:
        path = Path(file_path)
        result = {
            'valid': False,
            'exists': path.exists(),
            'readable': False,
            'size': 0,
            'extension': path.suffix.lower(),
            'error': None
        }
        
        if not result['exists']:
            result['error'] = "File does not exist"
            return result
        
        # Check if file is readable
        try:
            with open(path, 'rb') as f:
                f.read(1)
            result['readable'] = True
        except:
            result['error'] = "File is not readable"
            return result
        
        # Get file size
        result['size'] = path.stat().st_size
        
        # Check extension
        supported_extensions = ['.tif', '.tiff']
        if result['extension'] not in supported_extensions:
            result['error'] = f"Unsupported file format: {result['extension']}"
            return result
        
        result['valid'] = True
        return result
        
    except Exception as e:
        return {
            'valid': False,
            'error': f"Validation error: {str(e)}"
        }

def get_system_info() -> Dict[str, str]:
    """Get system information for debugging"""
    import platform
    import sys
    
    return {
        'platform': platform.platform(),
        'python_version': sys.version,
        'architecture': platform.architecture()[0],
        'processor': platform.processor(),
        'memory_available': "N/A"  # Could add psutil for memory info
    }

def truncate_path(file_path: str, max_length: int = 50) -> str:
    """Truncate file path for display"""
    if len(file_path) <= max_length:
        return file_path
    
    # Try to keep the filename and some of the path
    path = Path(file_path)
    filename = path.name
    
    if len(filename) >= max_length - 3:
        return f"...{filename[-(max_length-3):]}"
    
    remaining_length = max_length - len(filename) - 4  # 4 for ".../"
    truncated_dir = str(path.parent)
    
    if len(truncated_dir) > remaining_length:
        truncated_dir = truncated_dir[:remaining_length]
    
    return f".../{truncated_dir}/{filename}"

def choose_model_by_band_count(band_count: int) -> str | None:
    """
    Pilih tipe model berdasarkan jumlah band pada citra input.
    
    Args:
        band_count (int): Jumlah band pada citra.
    
    Returns:
        str|None: Model type string sesuai dengan pilihan di UI atau None kalau tidak valid.
    """
    if band_count in [3, 4]:
        return "🚁 UAV"
    elif band_count > 4:
        return "🛰️ Sentinel-2"
    else:
        return None