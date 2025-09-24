import rasterio
from rasterio.merge import merge
from rasterio.plot import show
import glob
import os

class MosaicTiles:
    def __init__(self):

    # Directory where you stored the tiles
        self.raster_dir = "data/rasters"
        self.src_files_to_mosaic = []

    def find_tiles(self):
        # Find all tif files in that directory
        search_path = os.path.join(self.raster_dir, "Hansen_GFC-2024-v1.12_lossyear_*.tif")
        raster_files = glob.glob(search_path)
        if not raster_files:
            raise FileNotFoundError(f"No Hansen raster files found in {self.raster_dir}")
        return raster_files


    def create_mosaic(self, raster_files):
        # Open all rasters

        for fp in raster_files:
            src = rasterio.open(fp)
            self.src_files_to_mosaic.append(src)

        # Merge them into one raster
        mosaic, out_trans = merge(self.src_files_to_mosaic)

        # Copy metadata of one file and update for the mosaic
        out_meta = src.meta.copy()
        out_meta.update({
            "driver": "GTiff",
            "height": mosaic.shape[1],
            "width": mosaic.shape[2],
            "transform": out_trans,
            "crs": src.crs
        })

        # Save the mosaic
        out_fp = os.path.join(self.raster_dir, "nigeria_lossyear_2024.tif")
        with rasterio.open(out_fp, "w", **out_meta) as dest:
            dest.write(mosaic)

        print(f"Mosaic saved to {out_fp}")
        return out_fp
    

    def visualize_mosaic(self, mosaic):
        # Optional: visualize (if running on Jupyter or local env)
        show(mosaic, cmap="viridis")
# 
