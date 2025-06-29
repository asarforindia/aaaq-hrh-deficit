import streamlit as st
import altair as alt
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import shapely
import json

import constants as c
from utils import *

EXCEL_FILE = "Documents/14_07_22_VW_AAAQ_mastersheet__26_NOV_23.xlsx"
SHAPEFILE_PATH = "Documents/maps-master/States/Admin2"
RESULTS_DIR = "Results/raw-value-based"

cadre_colors = {
    cadre: f"C{i}"
    for i, cadre in enumerate(
        c.CADRES_OF_INTEREST + ("nursing cadres", "supporting cadres")
    )
}

st.title("AAAQ HRH Deficit Explorer")
st.set_page_config(layout="wide")


@st.cache_data
def load_line_gb(excel_file: str):
    data = load_raw_data(excel_file)
    cleaned_data = clean_data(data)
    return cleaned_data.groupby(["states", "variable"])


@st.cache_data
def load_map_geom() -> gpd.GeoDataFrame:
    state_geoms = load_state_geometries(SHAPEFILE_PATH)
    return gpd.GeoDataFrame(
        [(k, v) for k, v in state_geoms.items()], columns=["state", "geometry"]
    )


@st.cache_data
def load_map_geojson() -> dict:
    state_geoms = load_state_geometries(SHAPEFILE_PATH)
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "id": k,
                "geometry": json.loads(shapely.to_geojson(v)),
                "properties": {"state": k},
            }
            for k, v in state_geoms.items()
        ],
    }


@st.cache_data
def load_map_gb(excel_file: str):
    data = load_raw_data(excel_file)
    cleaned_data = clean_data(data)
    return cleaned_data.groupby(["variable", "year", "cadres"])


def display_line_chart(line_gb, chosen_state, chosen_var):
    series = line_gb.get_group((chosen_state, chosen_var))
    intersection = determine_cadre_intersection(
        chosen_var, series, c.CADRES_OF_INTEREST
    )

    if not intersection:
        st.text("No Data Available")
    else:
        # Prepare the DataFrame for plotting
        deficit_col = "deficit"
        df = series.rename(deficit_col).reset_index().copy()
        st.dataframe(df, height=300)

        st.text(f"Showing deficit for {len(intersection)} cadres")

        df = df[df["cadres"].isin(intersection)]

        # Use label mapping if available
        if hasattr(c, "CADRE_LABEL_MAPPING"):
            df["Cadre Label"] = df["cadres"].map(
                lambda x: c.CADRE_LABEL_MAPPING.get(x, x)
            )
        else:
            df["Cadre Label"] = df["cadres"]

        # Clip deficit column at -1, 1 for readable charts
        df[deficit_col] = np.clip(df[deficit_col], a_min=-1, a_max=1)
        # Set y-axis limits with a margin of 0.125
        y_min_margin = df[deficit_col].min() - 1
        y_max_margin = df[deficit_col].max() + 1
        # Add a column to indicate if year > PROJ_YEAR
        df["is_proj"] = df["year"].astype(int) >= c.PROJECTION_YEAR
        # Use the new altair selection API for interactive legend (show/hide by clicking legend)
        cadre_selection = alt.selection_point(fields=["Cadre Label"], bind="legend")

        # Create the line chart
        line_chart = (
            alt.Chart(df)
            .mark_line()
            .encode(
                x=alt.X("year:O", title="Year"),
                y=alt.Y(
                    deficit_col,
                    title="Deficit",
                    scale=alt.Scale(domain=[y_min_margin, y_max_margin]),
                ),
                color=alt.Color("Cadre Label:N", title="Cadre"),
                opacity=alt.condition(cadre_selection, alt.value(0.75), alt.value(0.1)),
                tooltip=["year", "Cadre Label", deficit_col],
            )
        )

        # Create the point chart with conditional marker shape
        point_chart = (
            alt.Chart(df)
            .mark_point(filled=True, size=80)
            .encode(
                x=alt.X("year:O"),
                y=alt.Y(deficit_col),
                color=alt.Color("Cadre Label:N"),
                opacity=alt.condition(cadre_selection, alt.value(1), alt.value(0.1)),
                shape=alt.Shape(
                    "is_proj:N",
                    scale=alt.Scale(domain=[False, True], range=["circle", "triangle"]),
                    legend=alt.Legend(
                        title=f"Is projection",
                        symbolType="stroke",
                        symbolFillColor="gray",
                    ),
                ),
                tooltip=["year", "Cadre Label", deficit_col],
            )
        )

        # Add a rule at y=0 to highlight the zero line
        horizontal_line = (
            alt.Chart().mark_rule(color="gray", opacity=0.4).encode(y=alt.datum(0))
        )

        chart = (
            (line_chart + point_chart + horizontal_line)
            .properties(
                width=600,
                height=400,
                title=f"{c.VARNAME_MAPPING.get(chosen_var, chosen_var)} in {chosen_state}",
            )
            .add_params(cadre_selection)
            .interactive()
        )

        st.altair_chart(chart, use_container_width=True)


def display_map_chart(map_gb, chosen_var, chosen_year, chosen_cadre, geojson):
    series = map_gb.get_group((chosen_var, chosen_year, chosen_cadre)).rename("deficit")
    df = series.reset_index().copy()
    # st.dataframe(df, height=300)

    m = folium.Map(
        location=[23, 81],
        zoom_start=5,
        zoom_control=False,
        scroll_wheel_zoom=False,
        dragging=False,
        extent=[-180, -90, 180, 90],
    )

    folium.Choropleth(
        geo_data=geojson,
        name="choropleth",
        data=df,
        columns=["states", "deficit"],
        key_on="feature.id",
        fill_color="RdYlGn",
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name="Deficit",
        highlight=True,
    ).add_to(m)

    folium.LayerControl().add_to(m)

    st_folium(m, width=800, height=800)


tab_lines, tab_maps = st.tabs(["Deficit over time", "Deficit over geography"])

with tab_lines:
    st.title("Deficit over time")
    line_gb = load_line_gb(EXCEL_FILE)

    state_opts, varname_opts = set(), set()
    for s, v in line_gb.groups.keys():
        state_opts.add(s)
        varname_opts.add(v)

    sidebar_col, _, main_col = st.columns([4, 1, 12])
    with sidebar_col:
        chosen_state = st.selectbox("State", state_opts)
        chosen_var = st.selectbox("Variable", varname_opts)
        st.text(f"Showing {len(state_opts)} states, {len(varname_opts)} variables")

    with main_col:
        display_line_chart(line_gb, chosen_state, chosen_var)


with tab_maps:
    st.title("Deficit over geography")
    map_gb = load_map_gb(EXCEL_FILE)
    geojson = load_map_geojson()

    sidebar_col, _, main_col = st.columns([4, 1, 12])

    year_opts, varname_opts, cadre_opts = set(), set(), set()
    for v, y, c in map_gb.groups.keys():
        year_opts.add(y)
        varname_opts.add(v)
        cadre_opts.add(c)

    with sidebar_col:
        chosen_var = st.selectbox("Map Variable", varname_opts)
        chosen_year = st.selectbox("Map Year", year_opts)
        chosen_cadre = st.selectbox("Map Cadre", cadre_opts)
        st.text(
            f"Showing {len(year_opts)} years, {len(varname_opts)} variables, {len(cadre_opts)} cadres"
        )

    with main_col:
        display_map_chart(map_gb, chosen_var, chosen_year, chosen_cadre, geojson)
