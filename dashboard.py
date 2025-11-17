import streamlit as st
import altair as alt
import shapely
import numpy as np
import pandas as pd
import json
from datetime import datetime

import constants as c
from utils import *


import plotly.graph_objects as go
import plotly.express as px
import altair as alt


st.set_page_config(layout="wide")
st.title("AAAQ HRH Deficit Explorer")

EXCEL_FILE = "Documents/14_07_22_VW_AAAQ_mastersheet__26_NOV_23.xlsx"
GEOJSON_PATH = "Documents/india_states.geojson"
PROCESSED_GEOJSON_CDN_PATH = "https://raw.githubusercontent.com/asarforindia/aaaq-hrh-deficit/refs/heads/main/india-states.geojson"


def print_with_timestamp(message):
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} - {message}")


# Static color mapping for cadres to ensure consistency across variables
# Define consistent domain for cadre colors (sorted for consistency)
CADRE_DOMAIN = sorted(set(c.CADRE_LABEL_MAPPING.values()))

# Category10 color palette (Altair's default categorical colors)
CATEGORY10_COLORS = [
    "#1f77b4",
    "#ff7f0e",
    "#2ca02c",
    "#d62728",
    "#9467bd",
    "#8c564b",
    "#e377c2",
    "#7f7f7f",
    "#bcbd22",
    "#17becf",
]


@st.cache_data
def load_line_gb(excel_file: str):
    data = load_raw_data(excel_file)
    cleaned_data = clean_data(data)
    line_gb = cleaned_data.groupby(["variable", "states"])

    index = {
        group: {v: [] for v in variables}
        for group, variables in c.VARIABLE_GROUPS.items()
    }

    variables = {v: index[group][v] for group in index for v in index[group]}

    for variable, state in line_gb.groups.keys():
        variables[variable].append(state)

    return line_gb, index


@st.cache_data
def load_map_geojson() -> dict:
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
def load_map_gb(excel_file: str):
    data = load_raw_data(excel_file)
    cleaned_data = clean_data(data)
    map_gb = cleaned_data.groupby(["variable", "cadres", "year"])

    index = {
        group: {v: {} for v in variables}
        for group, variables in c.VARIABLE_GROUPS.items()
    }

    variables = {v: index[group][v] for group in index for v in index[group]}

    for variable, cadre, year in map_gb.groups.keys():
        if cadre in variables[variable]:
            variables[variable][cadre].append(year)
        else:
            variables[variable][cadre] = [year]

    return map_gb, index


@st.cache_data
def load_variable_data(excel_file: str):
    data = load_raw_data(excel_file)
    cleaned_data = clean_data(data)
    variable_gb = cleaned_data.reset_index().groupby(["states", "cadres", "year"])

    index = {}
    for (state, cadre, year), data in variable_gb:
        if cadre == "all cadres":
            # The document mentions to exclude all cadres from the index
            continue

        if state not in index:
            index[state] = {}
        if cadre not in index[state]:
            index[state][cadre] = {}
        if year not in index[state][cadre]:
            index[state][cadre][year] = {}

        for threshold, threshold_variables in c.THRESHOLD_GROUPS.items():
            data_variables = data["variable"].tolist()
            threshold_var_list = list(threshold_variables.values())
            index[state][cadre][year][threshold] = [
                v for v in data_variables if v in threshold_var_list
            ]

    return variable_gb, index


def get_variable_value(cleaned_data, state, year, variable):
    """
    Utility function to get a single variable value from the MultiIndex structure.
    Returns None if the value is missing or NaN.
    """
    try:
        value = cleaned_data.loc[(state, year, variable)].iloc[0]
        return None if pd.isna(value) else value
    except (KeyError, IndexError):
        return None


def create_radar_chart(categories, state_values, india_values):
    """Create radar chart comparing state vs India"""

    # Create radar chart
    fig = go.Figure()

    # Add state trace
    fig.add_trace(
        go.Scatterpolar(
            r=state_values,
            theta=categories,
            fill="toself",
            name=chosen_state.title(),
            line=dict(color="blue", width=2),
            fillcolor="rgba(0, 0, 255, 0.1)",
        )
    )

    # Add India trace
    fig.add_trace(
        go.Scatterpolar(
            r=india_values,
            theta=categories,
            fill="toself",
            name="India",
            line=dict(color="red", width=2),
            fillcolor="rgba(255, 0, 0, 0.1)",
        )
    )

    fig.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",  # Transparent polar background
            radialaxis=dict(
                visible=True,
                range=[-1, 1],
                gridwidth=0.3,  # Thinner radial grid lines
                linewidth=0.3,  # Thinner radial axis line
                gridcolor="rgba(128,128,128,0.3)",  # Lighter grid color
            ),
            angularaxis=dict(
                tickfont=dict(size=10),  # Smaller font size
                rotation=0,
                direction="clockwise",
                gridwidth=0.3,  # Thinner angular grid lines
                linewidth=0.3,  # Thinner angular axis lines
                gridcolor="rgba(128,128,128,0.3)",  # Lighter grid color
            ),
        ),
        showlegend=True,
        legend=dict(
            orientation="h",  # Horizontal legend
            yanchor="bottom",
            y=-0.25,  # Position above the chart
            xanchor="center",
            x=0.5,
        ),
        font=dict(size=12),
        margin=dict(
            l=80, r=80, t=80, b=80
        ),  # Adjusted margins - more space at top for legend
        paper_bgcolor="rgba(0,0,0,0)",  # Transparent paper background
        plot_bgcolor="rgba(0,0,0,0)",  # Transparent plot background
    )

    return fig


def create_number_comparison(cleaned_data, chosen_state, chosen_year, variable):
    """Create number comparison between state and India for AsD or QD"""
    print_with_timestamp(
        f"Creating number comparison for {chosen_state}, {chosen_year}, {variable}"
    )

    try:
        # Get scalar values using utility function
        state_value = get_variable_value(
            cleaned_data, chosen_state, chosen_year, variable
        )
        india_value = get_variable_value(cleaned_data, "india", chosen_year, variable)

        if state_value is None or india_value is None:
            return None, None, f"No {variable} data available for {chosen_year}"

        return state_value, india_value, None

    except Exception as e:
        print_with_timestamp(f"Error in number comparison: {e}")
        return None, None, f"Error retrieving {variable} data: {str(e)}"


def display_metric_comparison(cleaned_data, chosen_state, chosen_year, metric_type):
    metric_name = c.VARIABLE_GROUP_LABELS[metric_type]
    st.markdown(f"### {metric_name}")
    state_value, india_value, error = create_number_comparison(
        cleaned_data, chosen_state, chosen_year, metric_type
    )
    if error:
        st.error(error)
    else:
        col_left, col_right = st.columns(2)
        with col_left:
            st.metric(
                label=f"{chosen_state.title()}",
                value=f"{state_value:.3f}" if state_value is not None else "N/A",
                delta=(
                    f"{state_value - india_value:.3f}"
                    if state_value is not None and india_value is not None
                    else None
                ),
                delta_color="inverse",
            )
        with col_right:
            st.metric(
                label="India",
                value=f"{india_value:.3f}" if india_value is not None else "N/A",
            )


def display_line_chart(line_gb, chosen_state, chosen_variable):
    print_with_timestamp(f"Displaying line chart for {chosen_state}, {chosen_variable}")

    series = line_gb.get_group((chosen_variable, chosen_state))
    intersection = determine_cadre_intersection(
        chosen_variable, series, c.CADRES_OF_INTEREST
    )

    if not intersection:
        st.text("No Data Available")
    else:
        # Prepare the DataFrame for plotting
        deficit_col = "deficit"
        df = series.rename(deficit_col).reset_index().copy()
        df_origin = df.copy()

        df = df[df["cadres"].isin(intersection)]
        df["Cadre Label"] = df["cadres"].map(lambda x: c.CADRE_LABEL_MAPPING.get(x, x))
        df[deficit_col] = np.clip(df[deficit_col], a_min=-1, a_max=1)

        y_min_margin = df[deficit_col].min() - 1
        y_max_margin = df[deficit_col].max() + 1
        df["is_proj"] = df["year"].astype(int) >= c.PROJECTION_YEAR

        cadre_selection = alt.selection_point(fields=["Cadre Label"], bind="legend")
        default_opacity = 0.8

        line_chart = (
            alt.Chart(df)
            .mark_line(strokeOpacity=default_opacity)
            .encode(
                x=alt.X("year:O", title="Year", axis=alt.Axis(labelAngle=0)),
                y=alt.Y(
                    deficit_col,
                    title="Deficit",
                    scale=alt.Scale(domain=[y_min_margin, y_max_margin]),
                ),
                color=alt.Color(
                    "Cadre Label:N",
                    title="Cadres",
                    scale=alt.Scale(domain=CADRE_DOMAIN),
                    legend=alt.Legend(
                        symbolLimit=10,
                        values=sorted(df["Cadre Label"].unique()),
                    ),
                ),
                opacity=alt.condition(
                    cadre_selection, alt.value(default_opacity), alt.value(0.1)
                ),
                tooltip=["year", "Cadre Label", deficit_col],
            )
        )

        # Create the point chart with conditional marker shape and x-axis labels horizontal
        point_chart = (
            alt.Chart(df)
            .mark_point(filled=True, size=300, fillOpacity=default_opacity)
            .encode(
                x=alt.X("year:O", axis=alt.Axis(labelAngle=0)),
                y=alt.Y(deficit_col),
                color=alt.Color(
                    "Cadre Label:N",
                    scale=alt.Scale(domain=CADRE_DOMAIN),
                ),
                opacity=alt.condition(
                    cadre_selection, alt.value(default_opacity), alt.value(0.1)
                ),
                shape=alt.Shape(
                    "is_proj:N",
                    scale=alt.Scale(domain=[False, True], range=["circle", "triangle"]),
                    legend=alt.Legend(
                        title="Projected Value",
                        symbolType="stroke",
                        symbolFillColor="gray",
                        labelExpr="datum.value === true ? 'Yes' : 'No'",
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
                title=f"{c.VARNAME_MAPPING.get(chosen_variable, chosen_variable)} in {chosen_state.title()}",
            )
            .add_params(cadre_selection)
            .interactive()
        )

        st.altair_chart(chart, use_container_width=True)
        st.caption(
            "**Disclaimer:** All surplus, i.e., negative values, are capped at -1 in this plot since the focus is on positive values of deficit needing policy attention."
        )
        st.markdown("---")
        df_origin = df_origin.assign(states=df_origin["states"].str.title())
        df_origin.columns = [
            "State/UT/National",
            "Years",
            "Variable",
            "Cadres",
            "Deficit Value",
        ]
        st.dataframe(df_origin, height=300, hide_index=True)
        print_with_timestamp(
            f"Displayed line chart for {chosen_state}, {chosen_variable}"
        )


@st.cache_data(max_entries=300)
def load_map_data_multiyear(chosen_variable, chosen_years, chosen_cadre):
    map_gb, _ = load_map_gb(EXCEL_FILE)

    frames_data = {}
    for year in chosen_years:
        series = map_gb.get_group((chosen_variable, chosen_cadre, year)).rename(
            "deficit"
        )
        df = series.reset_index().copy()
        deficit_dict = df.set_index("states")["deficit"].to_dict()

        # Separate states with data and without data
        locations_with_data = []
        deficits_with_data = []
        state_names_with_data = []
        locations_without_data = []
        state_names_without_data = []

        for state_id in c.STATE_IDS:
            if state_id in deficit_dict:
                locations_with_data.append(state_id)
                deficits_with_data.append(deficit_dict[state_id])
                state_names_with_data.append(state_id.title())
            else:
                locations_without_data.append(state_id)
                state_names_without_data.append(state_id.title())

        frames_data[year] = {
            "locations_with_data": locations_with_data,
            "deficits": deficits_with_data,
            "state_names_with_data": state_names_with_data,
            "locations_without_data": locations_without_data,
            "state_names_without_data": state_names_without_data,
        }

    return frames_data


def display_map_chart(
    chosen_variable: str,
    chosen_cadre: str,
    chosen_years: list[str],
):
    print_with_timestamp(
        f"Requested map chart for {chosen_variable}, {chosen_cadre}, {chosen_years}"
    )

    frames_data = load_map_data_multiyear(
        chosen_variable, tuple(chosen_years), chosen_cadre
    )

    print_with_timestamp(
        f"Loaded map data for {chosen_variable}, {chosen_years}, {chosen_cadre}"
    )

    # Create initial frame (first year)
    first_year = chosen_years[0]
    initial_data = frames_data[first_year]

    fig = go.Figure()
    # Layer 1: Gray background for missing data
    fig.add_trace(
        go.Choroplethmap(
            geojson=PROCESSED_GEOJSON_CDN_PATH,
            locations=initial_data["locations_without_data"],
            z=[0] * len(initial_data["locations_without_data"]),
            featureidkey="id",
            colorscale=[[0, "#d3d3d3"], [1, "#d3d3d3"]],
            showscale=False,
            marker_line_width=0.2,
            marker_line_color="black",
            hovertemplate="<b>%{customdata}</b><br>No data<extra></extra>",
            customdata=initial_data["state_names_without_data"],
        )
    )

    # Layer 2: Actual data with color scale
    fig.add_trace(
        go.Choroplethmap(
            geojson=PROCESSED_GEOJSON_CDN_PATH,
            locations=initial_data["locations_with_data"],
            z=initial_data["deficits"],
            featureidkey="id",
            colorscale=[[0, "#91cf60"], [0.5, "#ffffbf"], [1, "#fc8d59"]],
            zmin=-1,
            zmax=1,
            marker_line_width=0.2,
            marker_line_color="black",
            colorbar_title="Deficit Level",
            hovertemplate="<b>%{customdata}</b><br>Deficit: %{z:.2f}<extra></extra>",
            customdata=initial_data["state_names_with_data"],
        )
    )

    # Create frames for slider
    frames = []
    for year in chosen_years:
        year_data = frames_data[year]
        frames.append(
            go.Frame(
                data=[
                    go.Choroplethmap(
                        geojson=PROCESSED_GEOJSON_CDN_PATH,
                        locations=year_data["locations_without_data"],
                        z=[0] * len(year_data["locations_without_data"]),
                        featureidkey="id",
                        colorscale=[[0, "#d3d3d3"], [1, "#d3d3d3"]],
                        showscale=False,
                        marker_line_width=0.2,
                        marker_line_color="black",
                        hovertemplate="<b>%{customdata}</b><br>No data<extra></extra>",
                        customdata=year_data["state_names_without_data"],
                    ),
                    go.Choroplethmap(
                        geojson=PROCESSED_GEOJSON_CDN_PATH,
                        locations=year_data["locations_with_data"],
                        z=year_data["deficits"],
                        featureidkey="id",
                        colorscale=[[0, "#91cf60"], [0.5, "#ffffbf"], [1, "#fc8d59"]],
                        zmin=-1,
                        zmax=1,
                        marker_line_width=0.2,
                        marker_line_color="black",
                        colorbar_title="Deficit Level",
                        hovertemplate="<b>%{customdata}</b><br>Deficit: %{z:.2f}<extra></extra>",
                        customdata=year_data["state_names_with_data"],
                    ),
                ],
                name=year,
            )
        )

    title_varname = c.VARNAME_MAPPING.get(chosen_variable, chosen_variable)
    title_cadre = c.CADRE_LABEL_MAPPING.get(chosen_cadre, chosen_cadre)
    fig.frames = frames
    fig.update_layout(
        map=dict(
            style="white-bg",
            center=dict(lat=22.5, lon=82),
            zoom=3.6,
        ),
        height=800,
        title=f"{title_varname} for {title_cadre}",
        sliders=[
            {
                "active": 0,
                "steps": [
                    {
                        "args": [
                            [year],
                            {
                                "frame": {"duration": 0, "redraw": True},
                                "mode": "immediate",
                            },
                        ],
                        "method": "animate",
                        "label": year,
                    }
                    for year in chosen_years
                ],
            }
        ],
    )

    print_with_timestamp(
        f"Displaying map chart for {chosen_variable}, {chosen_cadre}, {chosen_years}"
    )

    st.plotly_chart(fig, use_container_width=True, config={"scrollZoom": False})
    st.caption(
        "**Disclaimer:** The map scale is restricted from +1 to -1 since the policy interest is in the positive deficit values. Grey represents missing/non-calculable values."
    )
    st.markdown("---")

    frame = pd.DataFrame(
        [
            (state.title(), year, chosen_variable, chosen_cadre, deficit)
            for year, variables in frames_data.items()
            for state, deficit in zip(
                variables["locations_with_data"], variables["deficits"]
            )
        ],
        columns=["State/UT/National", "Years", "Variable", "Cadre", "Deficit Values"],
    )
    st.dataframe(frame, height=300, hide_index=True)

    print_with_timestamp(
        f"Displayed map chart for {chosen_variable}, {chosen_years}, {chosen_cadre}"
    )


def display_variable_view(
    variable_gb,
    chosen_state,
    chosen_cadre,
    chosen_year,
    chosen_threshold,
    chosen_threshold_variables,
):
    print_with_timestamp(
        f"Displaying variable view for {chosen_state}, {chosen_cadre}, {chosen_year}, {chosen_threshold}, {chosen_threshold_variables}"
    )

    def make_radar_series(series: pd.Series) -> pd.Series:
        df = series.reset_index().drop(columns=["index"])
        df = df[df["variable"].isin(chosen_threshold_variables)]
        return df.set_index("variable")["default"].rename("value")

    state_series = variable_gb.get_group((chosen_state, chosen_cadre, chosen_year))
    india_series = variable_gb.get_group(("india", chosen_cadre, chosen_year))
    state_radar_series = make_radar_series(state_series)
    india_radar_series = make_radar_series(india_series)

    radar_df = pd.merge(
        state_radar_series,
        india_radar_series,
        left_index=True,
        right_index=True,
        suffixes=("_state", "_india"),
    ).sort_index()

    fig = create_radar_chart(
        radar_df.index.tolist(),
        radar_df["value_state"].tolist(),
        radar_df["value_india"].tolist(),
    )
    st.plotly_chart(fig, use_container_width=True, config={"scrollZoom": False})
    st.caption(
        "**Disclaimer:** The chart scale is restricted from +1 to -1 since the policy interest is in the positive deficit values. Grey represents missing/non-calculable values."
    )
    st.markdown("---")

    df_state = state_series.reset_index().drop(columns=["index"]).copy()
    df_state = df_state[df_state["variable"].isin(chosen_threshold_variables)]
    df_state = df_state.rename(
        columns={
            "variable": "Variable",
            "default": "Value",
            "states": "State/UT/National",
            "cadres": "Cadre",
            "year": "Year",
        }
    )
    df_india = india_series.reset_index().drop(columns=["index"]).copy()
    df_india = df_india[df_india["variable"].isin(chosen_threshold_variables)]
    df_india = df_india.rename(
        columns={
            "variable": "Variable",
            "default": "Value",
            "states": "State/UT/National",
            "cadres": "Cadre",
            "year": "Year",
        }
    )
    st.dataframe(pd.concat([df_state, df_india]), hide_index=True)

    print_with_timestamp(
        f"Displayed variable view for {chosen_state}, {chosen_cadre}, {chosen_year}, {chosen_threshold}, {chosen_threshold_variables}"
    )


def select_map_parameters(index: dict):
    chosen_variable, chosen_cadre, chosen_year = None, None, None
    chosen_group = st.radio(
        "Deficit Index",
        c.VARIABLE_GROUP_LABELS.keys(),
        index=0,
        format_func=lambda x: c.VARIABLE_GROUP_LABELS[x],
    )

    if chosen_group is not None:
        choice_dict = index[chosen_group]
        chosen_variable = st.selectbox("Threshold", sorted(choice_dict.keys()), index=0)

        if chosen_variable is not None:
            choice_dict = choice_dict[chosen_variable]
            chosen_cadre = st.selectbox(
                "Cadre",
                sorted(choice_dict.keys()),
                index=0,
                format_func=lambda x: c.CADRE_LABEL_MAPPING.get(x, x),
            )

            if chosen_cadre is not None:
                chosen_year = choice_dict[chosen_cadre]

    return chosen_variable, chosen_cadre, chosen_year


def select_line_parameters(index):
    chosen_state, chosen_variable = None, None

    chosen_group = st.radio(
        "Choose Group of Variables",
        c.VARIABLE_GROUP_LABELS.keys(),
        index=0,
        format_func=lambda x: c.VARIABLE_GROUP_LABELS[x],
    )

    if chosen_group is not None:
        choice_dict = index[chosen_group]
        chosen_variable = st.selectbox("Threshold", sorted(choice_dict.keys()), index=0)

        if chosen_variable is not None:
            state_choices = choice_dict[chosen_variable]
            chosen_state = st.selectbox(
                "State/UT/National",
                sorted(state_choices),
                format_func=lambda x: x.title(),
                index=0,
            )

    return chosen_state, chosen_variable


def select_variable_parameters(index):
    chosen_state, chosen_cadre, chosen_year, chosen_threshold, available_variables = (
        None,
        None,
        None,
        None,
        None,
    )

    chosen_state = st.selectbox(
        "State/UT/National",
        sorted(index.keys()),
        format_func=lambda x: x.title(),
        index=0,
    )

    if chosen_state is not None:
        state_dict = index[chosen_state]
        cadres = sorted(state_dict.keys())

        if cadres:
            chosen_cadre = st.selectbox(
                "Cadre",
                cadres,
                index=0,
                format_func=lambda x: c.CADRE_LABEL_MAPPING.get(x, x),
            )

            if chosen_cadre is not None:
                cadre_dict = state_dict[chosen_cadre]
                years = sorted(cadre_dict.keys())

                if years:
                    chosen_year = st.selectbox("Year", years, index=0)

                    if chosen_year is not None:
                        year_dict = cadre_dict[chosen_year]
                        thresholds = sorted(year_dict.keys())

                        if thresholds:
                            chosen_threshold = st.selectbox(
                                "Threshold", thresholds, index=0
                            )
                            available_variables = year_dict[chosen_threshold]

    return (
        chosen_state,
        chosen_cadre,
        chosen_year,
        chosen_threshold,
        available_variables,
    )


# tab_lines, tab_maps = st.tabs(["Deficit over time", "Deficit over geography"])

with st.sidebar:
    tab_choice = st.radio(
        label="Dashboard View",
        options=["Temporal", "Spatial", "Variable"],
        index=0,
    )

if tab_choice == "Temporal":
    st.subheader("Deficit over time")
    line_gb, index = load_line_gb(EXCEL_FILE)

    # sidebar_col, _, main_col = st.columns([4, 1, 12])
    with st.sidebar:
        chosen_state, chosen_variable = select_line_parameters(index)

    display_line_chart(line_gb, chosen_state, chosen_variable)

elif tab_choice == "Spatial":
    st.subheader("Deficit over geography")
    map_gb, index = load_map_gb(EXCEL_FILE)

    with st.sidebar:
        chosen_variable, chosen_cadre, chosen_year = select_map_parameters(index)

    if chosen_variable is None or chosen_cadre is None or chosen_year is None:
        st.text("Please select ALL required parameters using the sidebar")
    else:
        display_map_chart(chosen_variable, chosen_cadre, chosen_year)

elif tab_choice == "Variable":
    st.subheader("Variable View - State vs India comparison")
    variable_gb, index = load_variable_data(EXCEL_FILE)

    with st.sidebar:
        (
            chosen_state,
            chosen_cadre,
            chosen_year,
            chosen_threshold,
            chosen_threshold_variables,
        ) = select_variable_parameters(index)

    if chosen_state is None:
        st.text("Please select a state using the sidebar")
    else:
        display_variable_view(
            variable_gb,
            chosen_state,
            chosen_cadre,
            chosen_year,
            chosen_threshold,
            chosen_threshold_variables,
        )

with st.sidebar:
    st.markdown(
        """
---
**General Notes:** 

1. Lower deficit values are better.
2. Deficit values for 2021 and 2031 are projections.
"""
    )
