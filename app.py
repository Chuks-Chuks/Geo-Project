# app.py
import os
import json
# from functools import lru_cache
import pandas as pd
import geopandas as gpd
import folium
from folium.plugins import TimeSliderChoropleth
from database.pg_conn import DatabaseConnect
import streamlit as st
import branca.colormap as cm
import plotly.express as px
from utils.config import SETTINGS
from shapely.geometry import mapping

# --- CONFIG: set DB ---

db_engine = DatabaseConnect().get_engine()
# Center of Nigeria for map view
lat, lon = map(float, SETTINGS.nigeria_center.split(",")) 
nigeria_center = (lat, lon)
# Cache DB engine and queries
@st.cache_resource
def get_engine():
    return db_engine

@st.cache_data(ttl=300)
def load_state_boundaries():
    engine = get_engine()
    sql = "SELECT name_1, geom FROM nigeria_states;"
    gdf = gpd.read_postgis(sql, engine, geom_col="geom")
    gdf = gdf.to_crs(epsg=4326)
    return gdf

@st.cache_data(ttl=300)
def load_loss_data():
    engine = get_engine()
    sql = """
    SELECT state_name, year, SUM(loss_ha) AS total_loss
    FROM state_forest_loss
    GROUP BY state_name, year
    ORDER BY state_name, year;
    """
    df = pd.read_sql(sql, engine)
    return df

def build_year_choropleth(gdf_states, df_year, year, value_col="total_loss"):
    # Merge
    merged = gdf_states.merge(df_year[["state_name", "value"]],
                          left_on="name_1", right_on="state_name", how="left")
    merged["value"] = merged["value"].fillna(0)
    # Build a linear colormap
    vmax = merged["value"].max() if merged["value"].max() > 0 else 1
    colormap = cm.linear.YlOrRd_09.scale(0, vmax)
    colormap.caption = f"Forest loss (ha) in {year}"

    m = folium.Map(location=nigeria_center, zoom_start=6, tiles="cartodbpositron")

    folium.Choropleth(
        geo_data=merged.to_json(),
        data=merged,
        columns=["name_1", "value"],
        key_on="feature.properties.name_1",
        fill_color="YlOrRd",
        fill_opacity=0.8,
        line_opacity=0.2,
        highlight=True,
        legend_name=f"Forest loss (ha) in {year}",
    ).add_to(m)

    # Add tooltip
    folium.GeoJson(
        merged.to_json(),
        name="labels",
        tooltip=folium.GeoJsonTooltip(fields=["name_1", "value"],
                                      aliases=["State", "Loss (ha)"],
                                      localize=True)
    ).add_to(m)

    colormap.add_to(m)
    return m

def build_time_slider_map(gdf_states, df):
    # pivot data into year-by-state matrix
    years = sorted(df["year"].unique().tolist())
    max_val = df.groupby("state_name")["total_loss"].sum().max()
    if pd.isna(max_val) or max_val == 0:
        max_val = 1.0

    # Prepare features for TimeSliderChoropleth
    features = []
    for _, row in gdf_states.iterrows():
        state = row["name_1"]
        geom_json = mapping(row["geom"])
        # get series for state
        series = df[df["state_name"] == state].set_index("year")["total_loss"].reindex(years, fill_value=0)
        # TimeSliderChoropleth expects styledict keyed by feature id (we'll use state name)
        properties = {"state": state, "values": series.tolist(), "years": years}
        features.append({
            "type": "Feature",
            "geometry": geom_json,
            "properties": properties
        })

    geojson = {"type": "FeatureCollection", "features": features}

    # Build styledict
    styledict = {}
    for feat in geojson["features"]:
        sid = feat["properties"]["state"]
        styledict[sid] = {}
        vals = feat["properties"]["values"]
        for i, y in enumerate(years):
            # opacity proportional to value
            v = vals[i]
            # normalize
            norm = min(1.0, float(v) / float(max_val)) if max_val > 0 else 0
            color = cm.linear.YlOrRd_09(norm) if norm > 0 else "#ffffff00"
            styledict[sid][str(y)] = {"color": color, "opacity": norm}

    m = folium.Map(location=nigeria_center, zoom_start=6, tiles="cartodbpositron")
    TimeSliderChoropleth(
        data=json.dumps(geojson),
        styledict=styledict,
    ).add_to(m)

    return m

# --- Streamlit UI ---
st.set_page_config(page_title="Nigeria Deforestation — Federation Dashboard", layout="wide")
st.title("Nigeria Deforestation — Federation Dashboard")

# Load data
with st.spinner("Loading spatial data..."):
    gdf_states = load_state_boundaries()
with st.spinner("Loading loss data..."):
    df_loss = load_loss_data()

if df_loss.empty:
    st.warning("No forest loss data found in the database.")
    st.stop()

# Sidebar controls
st.sidebar.header("Filters")
years = sorted(df_loss["year"].unique().tolist())
selected_year = st.sidebar.selectbox("Select year to display (choropleth)", years[::-1], index=0)
view_type = st.sidebar.radio("Map view", ("Yearly (single year)", "Time slider (animated)"))
top_n = st.sidebar.slider("Show top N states (by total loss, all years)", min_value=5, max_value=37, value=10)

# Top-level KPIs
total_national = df_loss.groupby("year")["total_loss"].sum().sum()  # total across all years
latest_year = max(years)
latest_total = df_loss[df_loss["year"] == latest_year]["total_loss"].sum()
col1, col2, col3 = st.columns(3)
col1.metric("Years covered", f"{min(years)}–{max(years)}")
col2.metric("Total loss (all years)", f"{int(total_national):,} ha")
col3.metric(f"Loss in {latest_year}", f"{int(latest_total):,} ha")

# Main: map + charts
left, right = st.columns([2,1])

with left:
    st.subheader("Map")
    if view_type == "Yearly (single year)":
        df_year = df_loss[df_loss["year"] == selected_year].rename(columns={"total_loss":"value"})
        m = build_year_choropleth(gdf_states, df_year, selected_year)
        # Render folium map in Streamlit
        html = m._repr_html_()
        st.components.v1.html(html, width=900, height=700)
    else:
        st.info("Time-slider map: animate across years")
        m = build_time_slider_map(gdf_states, df_loss)
        html = m._repr_html_()
        st.components.v1.html(html, width=900, height=700)

with right:
    st.subheader("Top states")
    totals = df_loss.groupby("state_name")["total_loss"].sum().reset_index().sort_values("total_loss", ascending=False)
    st.dataframe(totals.head(top_n).reset_index(drop=True).rename(columns={"state_name":"State", "total_loss":"Total loss (ha)"}))

    st.subheader("National trend")
    national = df_loss.groupby("year")["total_loss"].sum().reset_index()
    fig = px.line(national, x="year", y="total_loss", title="National Annual Forest Loss (ha)")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("State time series")
    chosen_state = st.selectbox("Choose state", ["-- select --"] + sorted(df_loss["state_name"].unique().tolist()))
    if chosen_state != "-- select --":
        series = df_loss[df_loss["state_name"] == chosen_state]
        fig2 = px.bar(series, x="year", y="total_loss", title=f"{chosen_state} — annual loss (ha)")
        st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")
st.caption("Data source: Hansen Global Forest Change (aggregated). Processing: custom ETL pipeline → PostGIS")
