import streamlit as st
import pandas as pd
import altair as alt

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


@st.cache_data
def load_line_gb(excel_file: str):
    data = load_raw_data(excel_file)
    cleaned_data = clean_data(data)
    return cleaned_data.groupby(["states", "variable"])


line_gb = load_line_gb(EXCEL_FILE)

state_opts, varname_opts = set(), set()
for s, v in line_gb.groups.keys():
    state_opts.add(s)
    varname_opts.add(v)

with st.sidebar:
    st.title("Configure plot")
    chosen_state = st.selectbox("State", state_opts)
    chosen_var = st.selectbox("Variable", varname_opts)

st.title("Deficit over time")

series = line_gb.get_group((chosen_state, chosen_var))

intersection = determine_cadre_intersection(chosen_var, series, c.CADRES_OF_INTEREST)
if not intersection:
    st.text("No Data Available")
else:
    # Prepare the DataFrame for plotting
    y_col = "deficit"
    df = series.rename(y_col).reset_index().copy()
    df = df[df["cadres"].isin(intersection)]

    # Use label mapping if available
    if hasattr(c, "CADRE_LABEL_MAPPING"):
        df["Cadre Label"] = df["cadres"].map(lambda x: c.CADRE_LABEL_MAPPING.get(x, x))
    else:
        df["Cadre Label"] = df["cadres"]

    st.dataframe(df)

    # Clip deficit column at -1, 1 for readable charts
    df[y_col] = np.clip(df[y_col], a_min=-1, a_max=1)

    # Set y-axis limits with a margin of 0.125
    y_min_margin = df[y_col].min() - 1
    y_max_margin = df[y_col].max() + 1

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
            y=alt.Y(y_col, title="Deficit", scale=alt.Scale(domain=[y_min_margin, y_max_margin])),
            color=alt.Color("Cadre Label:N", title="Cadre"),
            opacity=alt.condition(cadre_selection, alt.value(0.75), alt.value(0.1)),
            tooltip=["year", "Cadre Label", y_col],
        )
    )

    # Create the point chart with conditional marker shape
    point_chart = (
        alt.Chart(df)
        .mark_point(filled=True, size=80)
        .encode(
            x=alt.X("year:O"),
            y=alt.Y(y_col),
            color=alt.Color("Cadre Label:N"),
            opacity=alt.condition(cadre_selection, alt.value(1), alt.value(0.1)),
            shape=alt.Shape(
                "is_proj:N",
                scale=alt.Scale(domain=[False, True], range=["circle", "triangle"]),
                legend=alt.Legend(title=f"Projection", symbolType="stroke", symbolFillColor="gray"),
            ),
            tooltip=["year", "Cadre Label", y_col],
        )
    )

    # Add a rule at y=0 to highlight the zero line
    horizontal_line = alt.Chart().mark_rule(
        color='gray',
        opacity=0.7
    ).encode(
        y=alt.datum(0)  # line at y=100
    )


    chart = (
        (line_chart + point_chart + horizontal_line)
        .properties(
            width=600,
            height=400,
            title=f"{c.VARNAME_MAPPING.get(chosen_var, chosen_var)} in {chosen_state}",
        )
        .add_params(
            cadre_selection
        )
        .interactive()
    )

    st.altair_chart(chart, use_container_width=True)
