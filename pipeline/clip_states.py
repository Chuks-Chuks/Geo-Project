import os
from database.pg_conn import DatabaseConnect
import geopandas as gpd
from utils.log import get_logger
import rasterio
import rasterio.mask

from shapely.geometry import box 
from .mosaic_tiles import MosaicTiles

log = get_logger()

class ClipStates:
    def __init__(self):
        self.mosaic_tiles = MosaicTiles()
        self.raster_files = self.mosaic_tiles.find_tiles()
        self.db = DatabaseConnect()
        self.out_dir = "data/clipped_rasters"
        self.mosaic_path = os.path.join(self.mosaic_tiles.raster_dir, "nigeria_lossyear_2024.tif")
        os.makedirs(self.out_dir, exist_ok=True)

    def _build_mosaic_if_needed(self):
        if not os.path.exists(self.mosaic_path):
            log.info("Mosaic file not found, creating mosaic...")
            self.mosaic_tiles.create_mosaic(self.raster_files)
        else:
            log.info("Mosaic file already exists.")

    def _check_if_states_clipped(self):
        existing_files = [f for f in os.listdir(self.out_dir) if f.endswith("_lossyear.tif")]
        if existing_files:
            log.info(f"Found {len(existing_files)} already clipped state rasters.")
            return True
        return False

    def load_state_boundaries(self):
         # Connect to PostGIS and load state boundaries
        try:
            log.info('Getting the raster files ready')
            engine = self.db.get_engine()

            query = """
                    SELECT name_1, geom
                    FROM nigeria_states;
                    """
            log.info('Loading the GeodataFrame') 
            states_gdf = gpd.read_postgis(query, engine, geom_col="geom")
            log.info('Locating the Hansen raster file to clip state boundaries')
            return states_gdf
        except Exception as e:
            log.info(f'Error loading state boundaries: {e}')
            return None
    
    def clip_rasters_to_states(self):
        try:
            self._build_mosaic_if_needed()
            log.info(f'Using mosaic file at {self.mosaic_path}')

            if self._check_if_states_clipped():
                log.info('States already clipped. Exiting.')
                return
            with rasterio.open(self.mosaic_path) as raster:
                states_gdf = self.load_state_boundaries()
                if states_gdf is None or states_gdf.empty:
                    log.info("No state boundaries loaded. Exiting.")
                    return

                # Ensure CRS match
                raster_crs = raster.crs
                log.info(f"Raster CRS: {raster_crs}")
                log.info(f"States CRS before: {states_gdf.crs}")
                states_gdf = states_gdf.to_crs(raster_crs)
                log.info(f"States CRS after: {states_gdf.crs}")

                raster_bounds = raster.bounds
                out_dir = self.out_dir

                log.info('Iterating through the states...')
                for idx, row in states_gdf.iterrows():
                    state_name = row['name_1'].replace(" ", "_")
                    geom = [row["geom"].__geo_interface__]

                    # Quick bounding box check
                    raster_box = box(*raster_bounds)
                    if not row["geom"].intersects(raster_box):
                        log.info(f"Skipping {state_name}: No overlap with raster tile")
                        continue

                    try:
                        log.info(f'Clipping raster to state boundary: {state_name}')
                        out_image, out_transform = rasterio.mask.mask(raster, geom, crop=True)
                        out_meta = raster.meta.copy()
                        out_meta.update({
                            "driver": "GTiff",
                            "height": out_image.shape[1],
                            "width": out_image.shape[2],
                            "transform": out_transform
                        })

                        out_fp = os.path.join(out_dir, f"{state_name}_lossyear.tif")
                        with rasterio.open(out_fp, "w", **out_meta) as dest:
                            dest.write(out_image)

                        log.info(f'Saved clipped raster for {state_name} at {out_fp}')

                    except Exception as e:
                        log.info(f"Error clipping {state_name}: {e}")

            self.db.get_engine().dispose()

        except Exception as e:
            log.info(f'Error in clipping rasters: {e}')

                    

        