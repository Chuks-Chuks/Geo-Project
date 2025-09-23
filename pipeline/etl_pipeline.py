from database.pg_conn import DatabaseConnect
import geopandas as gpd
from utils.log import get_logger
import rasterio
import rasterio.mask
import numpy as np
import pandas as pd
from shapely.geometry import mapping 

log = get_logger()

try:
    log.info('Establishing comnection to database')
    db = DatabaseConnect()
    engine = db.get_engine()
    query = """
            SELECT name_1, geom
            FROM nigeria_states;
            """
    log.info('Loading the GeodataFrame') 
    states_gdf = gpd.read_postgis(query, engine, geom_col="geom")
    log.info('Locating the Hansen raster file to clip state boundaries')
    raster_path = "data/Hansen_GFC-2024-v1.12_lossyear_10N_010E.tif"
    raster = rasterio.open(raster_path)
    results = []

    log.info('Iterating through the states')
    for idx, row in states_gdf.iterrows():
        state_name = row['name_1']
        geom = [mapping(row['geom'])]
        try:
            log.info('Clipping raster to state boundary')
            out_image, out_transform = rasterio.mask.mask(raster, geom, crop=True)
            out_data = out_image[0]

            log.info('Counting Forest Log Pixels')
            loss_pixels = int(np.sum(out_data > 0))
            results.append({'state': state_name, 'pixel_loss': loss_pixels})

        except Exception as e:
            log.info(f'Skipping {state_name} : {e}')
   
    log.info('Loading into Dataframe')
    df = pd.DataFrame(results)
    df.to_sql("forest_loss_by_state", engine, if_exists="replace", index=False)

except Exception as e:
    log.info(f'{e}')
