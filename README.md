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

## 🚀 Reproducible Setup With Docker

The easiest way to run this pipeline is with Docker, which ensures all dependencies are installed and configured correctly.

### 🐳 Step 1: Build the Docker Image

Make sure you have [Docker installed](https://docs.docker.com/get-docker/).  
In your project root, run:

```sh
docker build -t nigeria-forest-loss-pipeline .
```

### 🐳 Step 2: Prepare Data

- Download the Nigeria states shapefile and Hansen raster files as described below.
- Place the shapefile in `data/` and the raster `.tif` files in `data/rasters/`.

### 🐳 Step 3: Run the Pipeline

```sh
docker run --rm -it nigeria-forest-loss-pipeline
```

You can also mount your local data directory if you want to persist outputs or use external data:

```sh
docker run --rm -it -v "$PWD/data:/app/data" -v "$PWD/outputs:/app/outputs" nigeria-forest-loss-pipeline
```

---

## 🗺️ Prepare Your Database and Nigeria States Data

### 🔑 Step 1: Confirm PostGIS on RDS

If you are using AWS RDS for PostgreSQL, enable the PostGIS extension by running:

```sql
CREATE EXTENSION postgis;
```

Or, use the provided `create_extension.sql` file with `psql`:

```sh
psql -h <your-rds-endpoint> -U <dbuser> -d <dbname> -p 5432 -f create_extension.sql
```

👉 If you get an error, check that your PostgreSQL version is 13 or higher.

---

### 📂 Step 2: Get the Nigeria States Shapefile

Download the Nigeria Level 1 (state boundaries) shapefile from GADM:

```sh
wget https://geodata.ucdavis.edu/gadm/gadm4.1/shp/gadm41_NGA_shp.zip
unzip gadm41_NGA_shp.zip -d data/
```

This will extract files including `gadm41_NGA_1.shp` (Nigeria states).

---

### 🛠️ Step 3: Load Shapefile into RDS

If you’re on Ubuntu, install GDAL tools:

```sh
sudo apt-get update
sudo apt-get install gdal-bin
```

On **Windows**, use [OSGeo4W](https://trac.osgeo.org/osgeo4w/) or [GDAL binaries](https://gdal.org/download.html) to install GDAL/OGR tools.  
Use [wget for Windows](https://eternallybored.org/misc/wget/) and [unzip](https://gnuwin32.sourceforge.net/packages/unzip.htm) if needed, or extract ZIP files with Windows Explorer.

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

## 📥 Download Required Data

Before running the pipeline, download the following Hansen Global Forest Change raster files and place them in the `data/rasters/` directory:

- [Hansen_GFC-2024-v1.12_lossyear_10N_000E.tif](https://storage.googleapis.com/earthenginepartners-hansen/GFC-2024-v1.12/Hansen_GFC-2024-v1.12_lossyear_10N_000E.tif)
- [Hansen_GFC-2024-v1.12_lossyear_10N_010E.tif](https://storage.googleapis.com/earthenginepartners-hansen/GFC-2024-v1.12/Hansen_GFC-2024-v1.12_lossyear_10N_010E.tif)
- [Hansen_GFC-2024-v1.12_lossyear_20N_000E.tif](https://storage.googleapis.com/earthenginepartners-hansen/GFC-2024-v1.12/Hansen_GFC-2024-v1.12_lossyear_20N_000E.tif)
- [Hansen_GFC-2024-v1.12_lossyear_20N_010E.tif](https://storage.googleapis.com/earthenginepartners-hansen/GFC-2024-v1.12/Hansen_GFC-2024-v1.12_lossyear_20N_010E.tif)

**After cloning this repository, place the downloaded `.tif` files in `data/rasters/`.**

---

## ⚡️ Before Running the Streamlit App

**Update your `.env` file:**  
Make sure your `.env` file includes the following line to set the center coordinates for Nigeria:

```
NIGERIA_CENTER=9.0820,8.6753
```

This ensures the map centers correctly in the Streamlit dashboard.

---

## ▶️ Run the Streamlit App

After updating your `.env` file, start the dashboard with:

```sh
streamlit run app.py
```
---

> **Note:**  
> You can run the pipeline either locally (with Python and all dependencies installed) or inside Docker for maximum reproducibility.  
> Docker is recommended for new users and for sharing your work across different systems.