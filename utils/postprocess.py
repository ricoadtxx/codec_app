import numpy as np
import cv2
import geopandas as gpd
from rasterio.features import shapes
from shapely.geometry import shape, LineString


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