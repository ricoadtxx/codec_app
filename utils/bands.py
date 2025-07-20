import rasterio

def get_band_count(image_path):
    try:
        with rasterio.open(image_path) as src:
            return src.count
    except Exception as e:
        raise RuntimeError(f"Gagal membaca citra: {e}")
