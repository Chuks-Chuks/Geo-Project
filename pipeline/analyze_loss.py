from sqlalchemy import Table, Column, Integer, String, Float, MetaData, insert, UniqueConstraint
from sqlalchemy.dialects.postgresql import insert
import numpy as np
from database.pg_conn import DatabaseConnect
import rasterio
import os
from utils.log import get_logger

log = get_logger()

class AnalyzeLoss:
    def __init__(self):
        self.db = DatabaseConnect()
        self.engine = self.db.get_engine()
        self.metadata = MetaData()

        self.state_forest_loss = Table(
            'state_forest_loss', self.metadata,
            Column('id', Integer, primary_key=True, autoincrement=True),
            Column('state_name', String(100), nullable=False),
            Column('year', Integer, nullable=False),
            Column('loss_ha', Float),
            UniqueConstraint('state_name', 'year', name='uix_state_year')
        )

        # Create table if it doesn't exist
        self.metadata.create_all(self.engine)

        self.clipped_dir = "data/clipped_rasters"

    def analyze_loss_by_state(self):
        with self.engine.begin() as conn:  # handles commit/rollback
            for fp in os.listdir(self.clipped_dir):
                if not fp.endswith(".tif"):
                    continue

                state_name = fp.replace("_lossyear.tif", "").replace("_", " ")
                raster_path = os.path.join(self.clipped_dir, fp)

                with rasterio.open(raster_path) as src:
                    arr = src.read(1)
                    pixel_size = abs(src.transform[0]) * abs(src.transform[4])
                    pixel_area_ha = pixel_size * (111000**2) / 10000

                    unique, counts = np.unique(arr, return_counts=True)
                    year_counts = dict(zip(unique, counts))
                    year_counts.pop(0, None)

                    for val, count in year_counts.items():
                        year = 2000 + int(val)  # Ensured val was converted to int to prevent overflow
                        loss_ha = float(count * pixel_area_ha) # converted to float to prevent np.float64 issues

                        stmt = insert(self.state_forest_loss).values(
                            state_name=state_name,
                            year=year,
                            loss_ha=loss_ha
                        ).on_conflict_do_update(
                            index_elements=['state_name', 'year'],
                            set_=dict(loss_ha=loss_ha)
                        )
                        conn.execute(stmt)

                log.info(f"Inserted forest loss data for {state_name}")