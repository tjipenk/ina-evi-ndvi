from json import load
import os
import glob
import requests
import tempfile
from pymodis import downmodis
import rasterio
from rasterio.merge import merge
from rasterio.mask import mask
import geopandas as gpd

from dotenv import load_dotenv
load_dotenv()

MODIS_USER = os.environ.get['MODIS_USER']
MODIS_PASS = os.environ.get['MODIS_PASS']

print("User MODIS:", modis_user)
print("Pass MODIS:", '*' * len(modis_pass))  

def download_modis(destination_folder, tiles, dates):
    url = 'https://e4ftl01.cr.usgs.gov/MOLT/MOD13Q1.061/'
    modis = downmodis.downModis(destination_folder, password=MODIS_PASS, user=MODIS_USER, url=url, tiles=tiles, today=dates, delta=1)
    modis.connect()
    modis.downloadsAllDay()

def extract_band(hdf_path, band_name, output_path):
    dataset_path = f'HDF4_EOS:EOS_GRID:"{hdf_path}":MODIS_Grid_16DAY_250m_500m_VI:{band_name}'
    with rasterio.open(dataset_path) as dataset:
        band_data = dataset.read(1)
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

def stack_and_clip(ndvi_path, evi_path, boundary_url, output_path):
    # Unduh GeoJSON langsung dari URL
    response = requests.get(boundary_url)
    response.raise_for_status()

    with tempfile.NamedTemporaryFile(suffix='.geojson') as tmp_geojson:
        tmp_geojson.write(response.content)
        tmp_geojson.flush()

        boundary = gpd.read_file(tmp_geojson.name)
        boundary_geom = boundary.geometry.values

        with rasterio.open(ndvi_path) as ndvi, rasterio.open(evi_path) as evi:
            # Masking
            ndvi_array, ndvi_transform = mask(ndvi, boundary_geom, crop=True, filled=True, nodata=0, indexes=1)
            evi_array, evi_transform = mask(evi, boundary_geom, crop=True, filled=True, nodata=0, indexes=1)

            profile = ndvi.profile
            profile.update({
                'height': ndvi_array.shape[1],
                'width': ndvi_array.shape[2],
                'transform': ndvi_transform,
                'count': 2,
                'compress': 'lzw'
            })

            with rasterio.open(output_path, 'w', **profile) as dst:
                dst.write(ndvi_array, 1)
                dst.write(evi_array, 2)

if __name__ == "__main__":
    download_folder = './modis_data'
    boundary_geojson_url = 'https://geodata.ucdavis.edu/gadm/gadm4.1/json/gadm41_IDN_0.json'
    os.makedirs(download_folder, exist_ok=True)

    tiles = ['h27v08', 'h28v08', 'h28v09', 'h29v08', 'h29v09']  # Cakupan wilayah Indonesia
    dates = '2025-01-01'  # Sesuaikan tanggal

    # Unduh MODIS Data
    download_modis(download_folder, ','.join(tiles), dates)

    hdf_files = glob.glob(os.path.join(download_folder, '*.hdf'))

    ndvi_files = []
    evi_files = []

    for hdf in hdf_files:
        basename = os.path.splitext(os.path.basename(hdf))[0]
        ndvi_path = os.path.join(download_folder, f'{basename}_ndvi.tif')
        evi_path = os.path.join(download_folder, f'{basename}_evi.tif')

        # Ekstraksi band NDVI & EVI dari MOD13Q1
        extract_band(hdf, '250m 16 days NDVI', ndvi_path)
        extract_band(hdf, '250m 16 days EVI', evi_path)

        ndvi_files.append(ndvi_path)
        evi_files.append(evi_path)

    merged_ndvi = os.path.join(download_folder, 'merged_ndvi.tif')
    merged_evi = os.path.join(download_folder, 'merged_evi.tif')

    merge_images(ndvi_files, merged_ndvi)
    merge_images(evi_files, merged_evi)

    stacked_output = os.path.join(download_folder, 'stacked_ndvi_evi_indonesia.tif')
    stack_and_clip(merged_ndvi, merged_evi, boundary_geojson_url, stacked_output)

    print("✅ Proses selesai. Output:", stacked_output)
