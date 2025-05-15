FROM python:3.12-slim

RUN apt-get update && \
    apt-get install -y gdal-bin libgdal-dev gcc && \
    pip install --upgrade pip && \
    pip install numpy rasterio pymodis geopandas requests

WORKDIR /app

COPY . /app

CMD ["python", "process_modis_indonesia.py"]
