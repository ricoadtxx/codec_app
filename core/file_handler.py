from pathlib import Path
from typing import Optional, Dict, Any
import numpy as np
import rasterio
import geopandas as gpd
import shutil, zipfile, logging

from PyQt5.QtWidgets import QFileDialog

from core.predict import extract_coastline

logger = logging.getLogger(__name__)

class FileHandler:
    def __init__(self, output_dir: str = "./output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.current_file_path = None
    
    def validate_file(self, file_path: str) -> tuple[bool, Optional[str]]:
        try:
            path = Path(file_path)
            if not path.exists():
                return False, f"File tidak ditemukan: {file_path}"
            
            supported_extensions = ['.tif', '.tiff']
            if path.suffix.lower() not in supported_extensions:
                return False, f"Format file tidak didukung: {path.suffix}"
            
            file_size_mb = path.stat().st_size / (1024 * 1024)

            if file_size_mb > 500:
                return False, f"Ukuran file terlalu besar ({file_size_mb:.2f} MB). Maksimal 500 MB. \nSilakan pilih file yang kurang dari 500 MB."
            elif file_size_mb >= 100:
                return True, f"Ukuran file besar ({file_size_mb:.2f} MB). Proses deteksi mungkin akan memakan waktu lebih lama."

            return True, None
        except Exception as e:
            return False, f"Terjadi kesalahan saat memvalidasi file: {str(e)}"

    def set_current_file(self, file_path: str) -> tuple[bool, Optional[str]]:
        is_valid, message = self.validate_file(file_path)
        if is_valid:
            self.current_file_path = file_path
        return is_valid, message
        
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
            print(f"[DEBUG] Menyimpan shapefile ke: {output_path}")
            print(f"[DEBUG] Folder output ada? {self.output_dir.exists()}")
            coastline_gdf.to_file(output_path)
            logger.info(f"Coastline shapefile saved to: {output_path}")
            return str(output_path)
        except Exception as e:
            logger.error(f"Error saving coastline shapefile: {str(e)}")
            return None
        
    def clean_files(self, parent_widget=None):
        try:
            output_files = list(self.output_dir.glob("*"))
            if not output_files:
                return

            for file in output_files:
                file.unlink()

            zip_path = self.output_dir / "hasil_output.zip"
            if zip_path.exists():
                zip_path.unlink()

            if hasattr(self, 'downloadButton'):
                self.downloadButton.setEnabled(False)

            if parent_widget:
                logger.info("Semua file output telah dihapus.")

        except Exception as e:
            if parent_widget:
                logger.error(f"Gagal membersihkan file output: {str(e)}")


    def download_and_clear_outputs(self, parent_widget=None) -> Optional[str]:
        try:
            output_files = list(self.output_dir.glob("*"))
            if not output_files:
                return None

            zip_filename = self.output_dir / "hasil_output.zip"
            with zipfile.ZipFile(zip_filename, 'w') as zipf:
                for file in output_files:
                    if file != zip_filename:
                        zipf.write(file, arcname=file.name)

            save_path, _ = QFileDialog.getSaveFileName(
                parent_widget,
                "Simpan File Output",
                str(zip_filename),
                "ZIP files (*.zip)"
            )
    
            if not save_path:
                zip_filename.unlink(missing_ok=True)
                return None

            shutil.copy(zip_filename, save_path)
            logger.info(f"Hasil output disimpan ke: {save_path}")

            for file in output_files:
                file.unlink()
            zip_filename.unlink()

            return save_path

        except Exception as e:
            logger.error(f"Gagal mendownload dan membersihkan output: {str(e)}")
            return None
