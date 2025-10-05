import streamlit as st
import altair as alt
import folium
from streamlit_folium import st_folium
import shapely
import numpy as np
import json
from datetime import datetime
import branca.colormap as cm

import constants as c
from utils import *


import geopandas as gpd
import altair as alt


st.set_page_config(layout="wide")

EXCEL_FILE = "Documents/14_07_22_VW_AAAQ_mastersheet__26_NOV_23.xlsx"
SHAPEFILE_PATH = "Documents/maps-master/States/Admin2"
GEOJSON_PATH = "Documents/india_states.geojson"
RESULTS_DIR = "Results/raw-value-based"


def print_with_timestamp(message):
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} - {message}")


cadre_colors = {
    cadre: f"C{i}"
    for i, cadre in enumerate(
        c.CADRES_OF_INTEREST + ("nursing cadres", "supporting cadres")
    )
}

st.title("AAAQ HRH Deficit Explorer")


@st.cache_data
def load_line_gb(excel_file: str):
    data = load_raw_data(excel_file)
    cleaned_data = clean_data(data)
    line_gb = cleaned_data.groupby(["states", "variable"])

    state_opts, varname_opts = set(), set()
    for s, v in line_gb.groups.keys():
        state_opts.add(s)
        varname_opts.add(v)

    return line_gb, sorted(state_opts), sorted(varname_opts)


@st.cache_data
def load_map_geojson() -> dict:
    # state_geoms = load_state_geometries(SHAPEFILE_PATH)
    state_geoms = load_state_geometries_geojson(GEOJSON_PATH)
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
def load_map_geom() -> dict:
    with open(GEOJSON_PATH, "r") as f:
        geojson = json.load(f)

    for feature in geojson["features"]:
        feature["id"] = feature["properties"]["ST_NM"].lower()
    return geojson


@st.cache_data
def load_map_gb(excel_file: str):
    data = load_raw_data(excel_file)
    cleaned_data = clean_data(data)
    map_gb = cleaned_data.groupby(["variable", "cadres", "year"])

    index = {
        group: {v: {} for v in variables}
        for group, variables in c.VARIABLE_GROUPS.items()
    }

    variables = {v: index[group][v] for group in index for v in index[group]}
    # year_opts, varname_opts, cadre_opts = set(), set(), set()

    for variable, cadre, year in map_gb.groups.keys():
        if cadre in variables[variable]:
            variables[variable][cadre].append(year)
        else:
            variables[variable][cadre] = [year]

    return map_gb, index


def display_line_chart(line_gb, chosen_state, chosen_var):
    print_with_timestamp(f"Displaying line chart for {chosen_state}, {chosen_var}")

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
        print_with_timestamp(f"Displayed line chart for {chosen_state}, {chosen_var}")


@st.cache_data(max_entries=300)
def load_map_data(chosen_var, chosen_year, chosen_cadre):
    geojson = load_map_geojson()
    map_gb, _ = load_map_gb(EXCEL_FILE)

    series = map_gb.get_group((chosen_var, chosen_cadre, chosen_year)).rename("deficit")
    df = series.reset_index().copy()
    deficit_dict = df.set_index("states")["deficit"].to_dict()

    print_with_timestamp(
        f"Displaying map chart for {chosen_var}, {chosen_year}, {chosen_cadre}"
    )

    new_features = []
    for feature in geojson["features"]:
        new_features.append(
            {
                "type": "Feature",
                "geometry": feature["geometry"],
                "properties": {
                    **feature["properties"],
                    "deficit": deficit_dict.get(feature["id"]),
                },
            }
        )

    geojson = {"type": "FeatureCollection", "features": new_features}
    return geojson


def display_map_chart(
    chosen_var: str,
    chosen_cadre: str,
    chosen_year: str,
):
    geojson = load_map_data(chosen_var, chosen_year, chosen_cadre)

    # st.dataframe(df, height=300)
    colormap = cm.LinearColormap(
        vmin=-1,
        vmax=1,
        colors=["#91cf60", "#ffffbf", "#fc8d59"],
        caption="Deficit Level",
    )

    m = folium.Map(
        location=[23, 81],
        zoom_start=5,
        zoom_control=False,
        scroll_wheel_zoom=False,
        dragging=False,
        extent=[-180, -90, 180, 90],
        tiles=None,
        no_touch=True,
        png_enabled=True,
    )

    tooltip = folium.GeoJsonTooltip(
        fields=["state", "deficit"],
        aliases=["State", "Deficit"],
        localize=True,
        sticky=False,
        labels=True,
        max_width=800,
    )

    folium.GeoJson(
        geojson,
        style_function=lambda x: {
            "fillColor": (
                colormap(x["properties"]["deficit"])
                if x["properties"]["deficit"] is not None
                else "white"
            ),
            "fillOpacity": 0.9,
            "color": "black",
            "weight": 0.2,
        },
        name="geojson",
        tooltip=tooltip,
        highlight=False,
    ).add_to(m)

    # folium.LayerControl().add_to(m)
    colormap.add_to(m)

    st_folium(m, width=None, height=800, key="folium_map")
    print_with_timestamp(
        f"Displayed map chart for {chosen_var}, {chosen_year}, {chosen_cadre}"
    )


def select_map_parameters(index: dict):
    chosen_variable, chosen_cadre, chosen_year = None, None, None
    chosen_group = st.segmented_control("Choose Group of Variables:", index.keys())

    if chosen_group is not None:
        choice_dict = index[chosen_group]
        chosen_variable = st.selectbox(
            "Map Variable", sorted(choice_dict.keys()), index=None
        )

        if chosen_variable is not None:
            choice_dict = choice_dict[chosen_variable]
            chosen_cadre = st.selectbox(
                "Map Cadre", sorted(choice_dict.keys()), index=None
            )

            if chosen_cadre is not None:
                choices = choice_dict[chosen_cadre]
                chosen_year = st.selectbox("Map Year", sorted(choices), index=None)

    return chosen_variable, chosen_cadre, chosen_year


tab_lines, tab_maps = st.tabs(["Deficit over time", "Deficit over geography"])

with tab_lines:
    st.title("Deficit over time")
    line_gb, line_state_opts, line_varname_opts = load_line_gb(EXCEL_FILE)

    sidebar_col, _, main_col = st.columns([4, 1, 12])
    with sidebar_col:
        chosen_state = st.selectbox("State", line_state_opts)
        chosen_var = st.selectbox("Variable", line_varname_opts)
        st.text(
            f"Showing {len(line_state_opts)} states, {len(line_varname_opts)} variables"
        )

    with main_col:
        display_line_chart(line_gb, chosen_state, chosen_var)


with tab_maps:
    st.title("Deficit over geography")
    map_gb, index = load_map_gb(EXCEL_FILE)

    sidebar_col, _, main_col = st.columns([4, 1, 12])

    with sidebar_col:
        chosen_variable, chosen_cadre, chosen_year = select_map_parameters(index)

    with main_col:
        if chosen_variable is None or chosen_cadre is None or chosen_year is None:
            st.markdown("## Please select required parameters using the sidebar")
        elif (chosen_variable, chosen_cadre, chosen_year) in map_gb.groups:
            display_map_chart(chosen_variable, chosen_cadre, chosen_year)
        else:
            st.markdown(
                """
## Something went wrong!

This is probably a bug. Kindly report [here](https://github.com/asarforindia/aaaq-hrh-deficit/issues) along with screenshot of the sidebar.

Thank you!
"""
            )
