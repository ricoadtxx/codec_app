import numpy as np
import rasterio

from typing import Tuple
from config.settings import SENTINEL2_BANDS

def preprocess_image_uav(image_path):
    with rasterio.open(image_path) as src:
        image = src.read([1, 2, 3])
        image = np.transpose(image, (1, 2, 0))
        profile = src.profile
        transform = src.transform
        crs = src.crs

    if image is None or image.size == 0:
        raise ValueError(f"Gagal membaca gambar dari: {image_path}")

    image = image.astype(np.float32)

    min_vals = np.percentile(image, 0.0, axis=(0, 1))
    max_vals = np.percentile(image, 100.0, axis=(0, 1))
    stretched = (image - min_vals) / (max_vals - min_vals + 1e-6)
    image = np.clip(stretched, 0, 1)

    gamma = 1.0
    image = np.power(image, gamma)

    brightness = 0.0
    image = image + brightness
    image = np.clip(image, 0, 1)

    contrast = 0.0
    mean = np.mean(image, axis=(0, 1), keepdims=True)
    image = (image - mean) * (1 + contrast) + mean
    image = np.clip(image, 0, 1)

    saturation = 1.68
    gray = np.dot(image, [0.299, 0.587, 0.114])[..., np.newaxis]
    image = gray + (image - gray) * saturation
    image = np.clip(image, 0, 1)

    return image, profile, transform, crs
  
def preprocess_sentinel2(image_path, ndwi_threshold=0.5):
    with rasterio.open(image_path) as src:
        all_bands = src.read()
        profile = src.profile
        transform = src.transform
        crs = src.crs

    num_bands = all_bands.shape[0]
    bands = np.zeros((13, *all_bands.shape[1:]), dtype=np.float32)

    for i in range(min(13, num_bands)):
        bands[i] = all_bands[i].astype(np.float32)

    try:
        band_green = bands[SENTINEL2_BANDS['B3']]
        band_nir = bands[SENTINEL2_BANDS['B8']]
    except IndexError:
        raise ValueError("Citra tidak memiliki band B3 atau B8 yang diperlukan untuk NDWI.")

    ndwi = compute_ndwi(band_green, band_nir, threshold=ndwi_threshold)
    ndwi_stack = np.expand_dims(ndwi, axis=0)

    return ndwi_stack, profile, transform, crs, bands
  
def compute_ndwi(band_green, band_nir, threshold=0.2):
    denominator = band_green + band_nir
    denominator = np.where(denominator == 0, 1e-8, denominator)
    
    ndwi = (band_green - band_nir) / denominator
    
    ndwi = np.nan_to_num(ndwi, nan=0.0, posinf=1.0, neginf=-1.0)
    
    ndwi_normalized = (ndwi + 1) / 2
    
    ndwi_normalized = np.where(ndwi_normalized < threshold, 0.0, ndwi_normalized)
    
    return ndwi_normalized