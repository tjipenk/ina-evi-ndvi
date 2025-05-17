import pystac
from datetime import datetime
from pathlib import Path
import json

item = pystac.Item(
    id="modis_20240501_band1",
    geometry={
        "type": "Polygon",
        "coordinates": [[[100.0, -5.0], [105.0, -5.0], [105.0, -10.0], [100.0, -10.0], [100.0, -5.0]]]
    },
    bbox=[100.0, -10.0, 105.0, -5.0],
    datetime=datetime(2024, 5, 1),
    properties={}
)

item.add_asset("data", pystac.Asset(
    href="https://tjipenk.github.io/modis-stac/data/MODIS_20240501_Band1.tif",
    media_type=pystac.MediaType.COG,
    roles=["data"]
))

catalog = pystac.Catalog(id="modis-catalog", description="MODIS daily data")
catalog.add_item(item)

catalog.normalize_hrefs("stac")
catalog.save(catalog_type=pystac.CatalogType.SELF_CONTAINED)
