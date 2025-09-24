Nigeria Forest Loss Pipeline
 
 🌍 Project Overview
 
 This project demonstrates a geospatial data pipeline that calculates forest loss across Nigerian states using Hansen Global Forest Change data. The pipeline ingests raster forest loss datasets, clips them to Nigeria’s state boundaries, aggregates results, and produces both tabular and visual outputs.
 
 The aim is to showcase data engineering applied to climate and biodiversity monitoring, with a focus on Nigeria as a case study.
 
 ⸻
 
 🗂️ Datasets
 	1.	Forest Loss Raster:
 	•	Source: Hansen Global Forest Change
 	•	Data: Annual forest loss since 2000 (raster, GeoTIFF).
 	2.	Nigeria Administrative Boundaries:
 	•	Source: GADM
 	•	Level 1 shapefile (state boundaries).
 
⚙️ Pipeline Architecture

```text
+---------------------+
|  Forest Loss Raster |
+---------------------+
          |
          v
+---------------------+
| Nigeria Boundaries  |
+---------------------+
          |
          v
+---------------------+
|   Raster Clip       |
+---------------------+
          |
          v
+---------------------+
| Aggregate by State  |
+---------------------+
          |
          v
+--------------------+
|     GeoJSON        |
+--------------------+
          |
          v
+---------------------+
|  Visualization Map  |
+---------------------+
```

Tech Stack
 	•	Python: geopandas, rasterio, shapely, numpy, pandas, matplotlib
 	•	Database: PostGIS for storage and querying
 	•	Visualization: Matplotlib / GeoPandas choropleth

Why This Matters
 
 Nigeria has one of the highest deforestation rates globally. By building scalable pipelines like this, we can help:
 	•	Monitor forest loss trends at the state level.
 	•	Support policymakers and NGOs with actionable data.
 	•	Provide transparency for biodiversity and climate initiatives.

Repository Structure
```text
nigeria-forest-loss-pipeline/
 │── data/                # Shapefiles, sample rasters
 │── pipeline.py          # Main script
 │── requirements.txt     # Dependencies
 │── README.md            # Documentation
 │── outputs/
 │     ├── nigeria_forest_loss.csv
 │     ├── forest_loss_map.png
```
# INSTRUCTIONS
## Once you clone the repo:
## 🗺️ Prepare Your Database and Nigeria States Data

### IMPORTANT NOTE:
The initial setup was done on an Ubuntu Virtual Machine. If any of the commands are not clear consider using your system's equivalent. 

### 🔑 Step 1: Confirm PostGIS on RDS

If you are using AWS RDS for PostgreSQL, enable the PostGIS extension by running on DBeaver, pgAdmin or DataGrip. I used Postgres for the project

```sql
CREATE EXTENSION postgis;
```
Or for ease, I already created a `create_extension.sql` file. If you have psql installed you can simply run:

```sh
psql -h <your-rds-endpoint> -U <dbuser> -d <dbname> -p 5432 -f create_extension.sql
```

👉 If you get an error, check that your PostgreSQL version is 13 or higher.

---

### 📂 Step 2: Get the Nigeria States Shapefile
Download the Nigeria Level 1 (state boundaries) shapefile from GADM:

```sh
curl -O https://geodata.ucdavis.edu/gadm/gadm4.1/shp/gadm41_NGA_shp.zip
unzip gadm41_NGA_shp.zip -d data/
```

This will extract files including `gadm41_NGA_1.shp` (Nigeria states).

---

### 🛠️ Step 3: Load Shapefile into RDS

If you’re on Ubuntu, install GDAL tools if not already: (I created a EC2 instance and created the needed setup)

```sh
sudo apt-get update
sudo apt-get install gdal-bin
```

Then load the shapefile into your RDS/PostGIS database (replace placeholders with your actual credentials):

```sh
ogr2ogr -f "PostgreSQL" \
  PG:"host=<your-rds-endpoint> user=<dbuser> dbname=<dbname> password=<dbpass> port=5432" \
  data/gadm41_NGA_1.shp \
  -nln nigeria_states \
  -nlt MULTIPOLYGON \
  -lco GEOMETRY_NAME=geom
```

✅ This will create a table `nigeria_states` with all 36 states plus FCT.

---
However, if you can't go throgh the stress of creating a VM then research on how to ensure you have gdal up and running.

## 📥 Download Required Data

Before running the pipeline, download the following Hansen Global Forest Change raster files and place them in the `data/rasters/` directory:

- [Hansen_GFC-2024-v1.12_lossyear_10N_000E.tif](https://storage.googleapis.com/earthenginepartners-hansen/GFC-2024-v1.12/Hansen_GFC-2024-v1.12_lossyear_10N_000E.tif)
- [Hansen_GFC-2024-v1.12_lossyear_10N_010E.tif](https://storage.googleapis.com/earthenginepartners-hansen/GFC-2024-v1.12/Hansen_GFC-2024-v1.12_lossyear_10N_010E.tif)
- [Hansen_GFC-2024-v1.12_lossyear_20N_000E.tif](https://storage.googleapis.com/earthenginepartners-hansen/GFC-2024-v1.12/Hansen_GFC-2024-v1.12_lossyear_20N_000E.tif)
- [Hansen_GFC-2024-v1.12_lossyear_20N_010E.tif](https://storage.googleapis.com/earthenginepartners-hansen/GFC-2024-v1.12/Hansen_GFC-2024-v1.12_lossyear_20N_010E.tif)

**After cloning this repository, place the downloaded `.tif` files in `data/rasters/`.**