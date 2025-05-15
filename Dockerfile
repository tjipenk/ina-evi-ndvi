FROM choochootrain/python-gdal:python-3.12-gdal-3.9

RUN apt-get update && \
    apt-get install -y gdal-bin libgdal-dev gcc && \
    pip install --upgrade pip && \
    pip install numpy rasterio pymodis geopandas requests

WORKDIR /app

COPY . /app

CMD ["python", "process_modis_indonesia.py"]
