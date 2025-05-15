# MODIS MOD13Q1 Downloader

Aplikasi Python untuk mengunduh data MODIS MOD13Q1 (NDVI, EVI, dan composite day of the year).

## Persiapan

1. Pastikan Python 3.6 atau versi lebih baru sudah terinstal
2. Install dependensi yang diperlukan:
   ```bash
   pip install -r requirements.txt
   ```
3. Daftar akun NASA Earthdata di https://urs.earthdata.nasa.gov/

## Penggunaan

Ada dua cara untuk menentukan area yang akan diunduh:

### 1. Menggunakan Tile MODIS

```bash
python download_modis.py --username ${MODIS_USER}$ \
                        --password ${MODIS_PASS}$ \
                        --start-date 2023-01-01 \
                        --end-date 2023-12-31 \
                        --tiles h27v08 h28v08 \
                        --output-dir modis_data
```

### 2. Menggunakan Bounding Box

```bash
python download_modis.py --username YOUR_USERNAME \
                        --password YOUR_PASSWORD \
                        --start-date 2023-01-01 \
                        --end-date 2023-12-31 \
                        --bbox 105.0 -5.0 110.0 0.0 \
                        --output-dir modis_data
```

### Parameter

- `--username`: Username akun NASA Earthdata
- `--password`: Password akun NASA Earthdata
- `--start-date`: Tanggal awal dalam format YYYY-MM-DD
- `--end-date`: Tanggal akhir dalam format YYYY-MM-DD
- `--tiles`: Daftar tile MODIS yang akan diunduh (opsional jika menggunakan bbox)
- `--bbox`: Koordinat bounding box dalam format: min_lon min_lat max_lon max_lat (opsional jika menggunakan tiles)
- `--output-dir`: Direktori untuk menyimpan hasil unduhan (default: modis_data)

## Informasi Dataset

MOD13Q1 (Terra Vegetation Indices 16-Day L3 Global 250m) menyediakan data:
- NDVI (Normalized Difference Vegetation Index)
- EVI (Enhanced Vegetation Index)
- Composite day of the year
- Kualitas pixel dan informasi tambahan lainnya

Data tersedia dalam resolusi spasial 250 meter dengan periode temporal 16 hari.

## Catatan Penggunaan Bounding Box

- Format koordinat: decimal degrees (DD)
- Urutan koordinat: min_lon min_lat max_lon max_lat
- Contoh untuk wilayah Jawa Tengah: `--bbox 108.0 -8.0 111.0 -6.0`
- Script akan secara otomatis menentukan tile MODIS yang mencakup area yang diminta 