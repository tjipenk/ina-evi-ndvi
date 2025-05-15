#!/usr/bin/env python3
import os
from datetime import datetime, timedelta
from pymodis import downmodis
import argparse
import math

def lat_lon_to_tile(lat, lon):
    """
    Convert latitude/longitude to MODIS tile coordinates.
    
    Args:
        lat (float): Latitude in decimal degrees
        lon (float): Longitude in decimal degrees
    
    Returns:
        tuple: (h, v) tile coordinates
    """
    h = math.floor((lon + 180) / 10)
    v = math.floor((90 - lat) / 10)
    return h, v

def get_tiles_from_bbox(min_lon, min_lat, max_lon, max_lat):
    """
    Get list of MODIS tiles that cover the given bounding box.
    
    Args:
        min_lon (float): Minimum longitude
        min_lat (float): Minimum latitude
        max_lon (float): Maximum longitude
        max_lat (float): Maximum latitude
    
    Returns:
        list: List of MODIS tiles in 'hXXvYY' format
    """
    # Get corner tiles
    h1, v1 = lat_lon_to_tile(max_lat, min_lon)  # Northwest corner
    h2, v2 = lat_lon_to_tile(min_lat, max_lon)  # Southeast corner
    
    tiles = []
    for h in range(h1, h2 + 1):
        for v in range(v1, v2 + 1):
            tiles.append(f"h{h:02d}v{v:02d}")
    
    return tiles

def download_modis_data(username, password, start_date, end_date, tiles=None, bbox=None, output_dir="modis_data"):
    """
    Download MODIS MOD13Q1 data (NDVI, EVI, and composite day of the year)
    
    Args:
        username (str): NASA Earthdata username
        password (str): NASA Earthdata password
        start_date (str): Start date in format YYYY-MM-DD
        end_date (str): End date in format YYYY-MM-DD
        tiles (list): List of MODIS tiles (e.g., ['h27v08', 'h28v08'])
        bbox (tuple): Bounding box coordinates (min_lon, min_lat, max_lon, max_lat)
        output_dir (str): Directory to save downloaded files
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # If bbox is provided, get tiles from bbox
    if bbox and not tiles:
        tiles = get_tiles_from_bbox(*bbox)
        print(f"Using tiles from bounding box: {tiles}")
    elif not tiles:
        raise ValueError("Either tiles or bbox must be provided")
    
    # Convert dates to datetime objects
    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')
    
    # Initialize downloader
    modis_down = downmodis.downModis(
        user=username,
        password=password,
        destinationFolder=output_dir,
        tiles=tiles,
        today=end_date,
        delta=int((end - start).days),
        product="MOD13Q1.061"
    )
    
    # Download data
    modis_down.connect()
    print(f"Downloading MODIS MOD13Q1 data from {start_date} to {end_date}")
    modis_down.downloadsAllDay()
    print("Download completed!")

def main():
    parser = argparse.ArgumentParser(description='Download MODIS MOD13Q1 data')
    parser.add_argument('--username', required=True, help='NASA Earthdata username')
    parser.add_argument('--password', required=True, help='NASA Earthdata password')
    parser.add_argument('--start-date', required=True, help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end-date', required=True, help='End date (YYYY-MM-DD)')
    parser.add_argument('--tiles', nargs='+', help='MODIS tiles (e.g., h27v08 h28v08)')
    parser.add_argument('--bbox', nargs=4, type=float, 
                        help='Bounding box coordinates: min_lon min_lat max_lon max_lat')
    parser.add_argument('--output-dir', default='modis_data', help='Output directory')
    
    args = parser.parse_args()
    
    if not args.tiles and not args.bbox:
        parser.error("Either --tiles or --bbox must be provided")
    
    bbox = args.bbox if args.bbox else None
    
    download_modis_data(
        args.username,
        args.password,
        args.start_date,
        args.end_date,
        tiles=args.tiles,
        bbox=bbox,
        output_dir=args.output_dir
    )

if __name__ == '__main__':
    main() 
