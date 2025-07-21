import argparse
import os
import cv2
import numpy as np
import rasterio
from rasterio.features import shapes
import geopandas as gpd
from shapely.geometry import shape, LineString
import tensorflow as tf
from keras.models import load_model
from keras import backend as K
from tqdm import tqdm
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from rasterio.transform import rowcol
import matplotlib.patches as mpatches


def preprocess_image(image_path):
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

def predict(model, rgb_image, tile_size=256):
    height, width, _ = rgb_image.shape
    output_mask = np.zeros((height, width), dtype=np.uint8)

    rows = list(range(0, height, tile_size))
    cols = list(range(0, width, tile_size))

    with tqdm(total=len(rows) * len(cols), desc="Prediksi patches") as pbar:
        for row in rows:
            for col in cols:
                patch = rgb_image[row:row+tile_size, col:col+tile_size]
                
                patch_h, patch_w, _ = patch.shape
                padded_patch = np.zeros((tile_size, tile_size, 3), dtype=np.float32)
                padded_patch[:patch_h, :patch_w, :] = patch

                input_patch = np.expand_dims(padded_patch, axis=0)

                pred = model.predict(input_patch, verbose=0)
                pred_mask_patch = np.argmax(pred[0], axis=-1).astype(np.uint8)
                pred_mask_patch = pred_mask_patch[:patch_h, :patch_w]

                output_mask[row:row+patch_h, col:col+patch_w] = pred_mask_patch
                pbar.update(1)

    return output_mask

def save_tiff(mask, profile, output_path):
    profile.update(dtype=rasterio.uint8, count=1)
    with rasterio.open(output_path, 'w', **profile) as dst:
        dst.write(mask.astype(rasterio.uint8), 1)

def morphological_smooth(mask, kernel_size=3, iterations=1):
    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    opened = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=iterations)
    closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, kernel, iterations=iterations)
    return closed

def mask_to_polygons(mask, transform, crs):
    shapes_gen = shapes(mask.astype(np.uint8), mask > 0, transform=transform)
    geoms = []
    classes = []
    for geom, val in shapes_gen:
        if val == 1:
            geoms.append(shape(geom))
            classes.append(val)
    gdf = gpd.GeoDataFrame({'geometry': geoms, 'class_id': classes}, crs=crs)
    return gdf

def extract_coastline(polygons_gdf, water_class=1):
    coastlines = []
    water_polygons = polygons_gdf[polygons_gdf['class_id'] == water_class]
    for poly in water_polygons.geometry:
        if poly.geom_type == 'Polygon':
            coastlines.append(LineString(poly.exterior.coords))
        elif poly.geom_type == 'MultiPolygon':
            for subpoly in poly.geoms:
                coastlines.append(LineString(subpoly.exterior.coords))
    coastline_gdf = gpd.GeoDataFrame({'geometry': coastlines}, crs=polygons_gdf.crs)
    return coastline_gdf
    
def parse_args():
    parser = argparse.ArgumentParser(description="Prediksi garis pantai dari citra Sentinel-2.")
    parser.add_argument('--image-path', type=str, required=True, help='Path ke citra TIFF input.')
    parser.add_argument('--model-path', type=str, required=True, help='Path ke model Keras (.h5).')
    parser.add_argument('--output-path', type=str, required=True, help='Path direktori output.')
    parser.add_argument('--threshold', type=float, default=0.6, 
                       help='Threshold NDWI untuk background (default: 0.2).')
    return parser.parse_args()

def main():
    args = parse_args()
    
    input_path = args.image_path
    output_dir = args.output_path
    os.makedirs(output_dir, exist_ok=True)
    base_name = os.path.splitext(os.path.basename(input_path))[0]

    rgb_image, profile, transform, crs = preprocess_image(input_path)

    model = load_model(
        args.model_path, 
        compile=False,
    )

    predicted_mask = predict(model, rgb_image, tile_size=256)

    tiff_output_path = os.path.join(output_dir, base_name + '_segmentation.tif')
    save_tiff(predicted_mask, profile, tiff_output_path)
    print(f"Segmentasi disimpan di: {tiff_output_path}")
    
    smoothed_mask = morphological_smooth(predicted_mask, kernel_size=7, iterations=1)

    polygons_gdf = mask_to_polygons(smoothed_mask, transform, crs)
    coastline_gdf = extract_coastline(polygons_gdf, water_class=1)

    shp_output_path = os.path.join(output_dir, base_name + '_coastline.shp')
    coastline_gdf.to_file(shp_output_path)
    print(f"Garis pantai disimpan di: {shp_output_path}")
    
