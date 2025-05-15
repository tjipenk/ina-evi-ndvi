import os
import requests
from pymodis import downmodis
import rasterio
from rasterio.merge import merge
import glob
import numpy as np

MODIS_USER = os.environ['MODIS_USER']
MODIS_PASS = os.environ['MODIS_PASS']

def download_modis(destination_folder, tiles, dates):
    url = 'https://e4ftl01.cr.usgs.gov/MOLT/MOD13Q1.061/'
    modis = downmodis.downModis(destination_folder, password=MODIS_PASS, user=MODIS_USER, url=url, tiles=tiles, today=dates, delta=1)
    modis.connect()
    modis.downloadsAllDay()

def extract_band(hdf_path, band_number, output_path):
    with rasterio.open(f'HDF4_EOS:EOS_GRID:"{hdf_path}":MODIS_Grid_16DAY_250m_500m_VI:250m 16 days NDVI') as dataset:
        band_data = dataset.read(band_number)
        profile = dataset.profile
        profile.update(driver='GTiff', count=1, compress='lzw')

        with rasterio.open(output_path, 'w', **profile) as dst:
            dst.write(band_data, 1)

def merge_images(image_paths, output_path):
    sources = [rasterio.open(img) for img in image_paths]
    mosaic, out_trans = merge(sources)

    out_meta = sources[0].meta.copy()
    out_meta.update({
        "driver": "GTiff",
        "height": mosaic.shape[1],
        "width": mosaic.shape[2],
        "transform": out_trans,
        "count": 1,
        "compress": "lzw"
    })

    with rasterio.open(output_path, "w", **out_meta) as dest:
        dest.write(mosaic)

def stack_images(ndvi_path, evi_path, output_path):
    with rasterio.open(ndvi_path) as ndvi, rasterio.open(evi_path) as evi:
        profile = ndvi.profile
        profile.update(count=2, compress='lzw')

        with rasterio.open(output_path, 'w', **profile) as dst:
            dst.write(ndvi.read(1), 1)
            dst.write(evi.read(1), 2)

if __name__ == "__main__":
    download_folder = './modis_data'
    os.makedirs(download_folder, exist_ok=True)
    tiles = 'h28v09'  # Ubah sesuai kebutuhan
    dates = '2024-01-01'  # Ubah sesuai kebutuhan

    # Download MODIS Data
    download_modis(download_folder, tiles, dates)

    hdf_files = glob.glob(os.path.join(download_folder, '*.hdf'))

    ndvi_files = []
    evi_files = []

    for hdf in hdf_files:
        basename = os.path.splitext(os.path.basename(hdf))[0]
        ndvi_path = os.path.join(download_folder, f'{basename}_ndvi.tif')
        evi_path = os.path.join(download_folder, f'{basename}_evi.tif')

        # Band 1: NDVI, Band 2: EVI pada MOD13Q1
        extract_band(hdf, 1, ndvi_path)
        extract_band(hdf, 2, evi_path)

        ndvi_files.append(ndvi_path)
        evi_files.append(evi_path)

    merged_ndvi = os.path.join(download_folder, 'merged_ndvi.tif')
    merged_evi = os.path.join(download_folder, 'merged_evi.tif')

    merge_images(ndvi_files, merged_ndvi)
    merge_images(evi_files, merged_evi)

    stacked_output = os.path.join(download_folder, 'stacked_ndvi_evi.tif')
    stack_images(merged_ndvi, merged_evi, stacked_output)

    print("Processing completed successfully!")
