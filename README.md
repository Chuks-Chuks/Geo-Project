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
 
⚙️ Pipeline Architecture        +---------------------+
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
           +------------------+
           | CSV / GeoJSON    |
           +------------------+
                   |
                   v
         +---------------------+
         |  Visualization Map  |
         +---------------------+

Tech Stack
 	•	Python: geopandas, rasterio, shapely, numpy, pandas, matplotlib
 	•	Database (optional): PostGIS for storage and querying
 	•	Visualization: Matplotlib / GeoPandas choropleth

Why This Matters
 
 Nigeria has one of the highest deforestation rates globally. By building scalable pipelines like this, we can help:
 	•	Monitor forest loss trends at the state level.
 	•	Support policymakers and NGOs with actionable data.
 	•	Provide transparency for biodiversity and climate initiatives.

Repository Structure

nigeria-forest-loss-pipeline/
 │── data/                # Shapefiles, sample rasters
 │── pipeline.py          # Main script
 │── requirements.txt     # Dependencies
 │── README.md            # Documentation
 │── outputs/
 │     ├── nigeria_forest_loss.csv
 │     ├── forest_loss_map.png

