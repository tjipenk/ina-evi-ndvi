# FROM choochootrain/python-gdal:python-3.12-gdal-3.9
FROM ghcr.io/osgeo/gdal:alpine-small-3.11.0

RUN pip install numpy rasterio pymodis geopandas requests dotenv

WORKDIR /app

COPY . /app

CMD ["python", "process_modis_indonesia.py"]
