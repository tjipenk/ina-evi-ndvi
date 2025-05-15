# FROM choochootrain/python-gdal:python-3.12-gdal-3.9
FROM ghcr.io/osgeo/gdal:ubuntu-small-3.11.0

RUN apt update && apt install python3-pip && \
    && pip install numpy rasterio pymodis geopandas requests dotenv \
    && rm -rf /var/lib/apt/lists/* \
    && apt clean

WORKDIR /app

COPY . /app

CMD ["python", "process_modis_indonesia.py"]
