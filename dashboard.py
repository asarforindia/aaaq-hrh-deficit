import streamlit as st
import pandas as pd

from constants import *
from utils import *

EXCEL_FILE = "Documents/14_07_22_VW_AAAQ_mastersheet__26_NOV_23.xlsx"
SHAPEFILE_PATH = "Documents/maps-master/States/Admin2"
RESULTS_DIR = "Results/raw-value-based"
PROJ_YEAR = 2011

cadre_colors = {
    cadre: f"C{i}"
    for i, cadre in enumerate(
        CADRES_OF_INTEREST + ("nursing cadres", "supporting cadres")
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

st.title("Line Plots")

series = line_gb.get_group((chosen_state, chosen_var))

intersection = determine_cadre_intersection(chosen_var, series, CADRES_OF_INTEREST)
if not intersection:
    st.text("No Data Available")
else:
    st.dataframe(series)
