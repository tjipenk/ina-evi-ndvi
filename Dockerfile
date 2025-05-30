# FROM choochootrain/python-gdal:python-3.12-gdal-3.9
FROM ghcr.io/osgeo/gdal:ubuntu-full-3.11.0

RUN apt update && apt install python3-full python3-pip -y \
    && pip3 install numpy rasterio pymodis slugify geopandas requests dotenv --break-system-packages \
    && rm -rf /var/lib/apt/lists/* \
    && apt clean

WORKDIR /app

COPY . /app

CMD ["python", "process_modis_indonesia.py"]
