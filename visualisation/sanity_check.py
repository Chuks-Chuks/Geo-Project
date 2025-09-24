import matplotlib.pyplot as plt
import rasterio
from rasterio.plot import show
import geopandas as gpd
from database.pg_conn import DatabaseConnect

db_engine = DatabaseConnect().get_engine()

raster = rasterio.open("data/clipped_rasters/Delta_lossyear.tif")
states = gpd.read_postgis("SELECT name_1, geom FROM nigeria_states;", db_engine, geom_col="geom")

fig, ax = plt.subplots(figsize=(10, 10))
show(raster, ax=ax, cmap="viridis")  # or 'YlOrRd' for a deforestation heatmap feel
states.boundary.plot(ax=ax, color="black", linewidth=0.5)
plt.savefig("visualisation/delta_forest_loss.png", dpi=300, bbox_inches="tight")  # Save the figure
plt.show()
