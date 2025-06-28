import numpy as np
import pandas as pd
import openpyxl
from cartopy.io.shapereader import Reader

import constants as c


def load_raw_data(excel_file: str) -> pd.DataFrame:
    """
    Loads the Excel file, removes hidden columns, drops specified change columns,
    and replaces error strings with NaN.
    Returns a pandas DataFrame ready for further cleaning.
    """
    wb = openpyxl.load_workbook(excel_file)
    ws = wb["Mastersheet_raw_values_based_de"]

    hidden_cols = []
    for i, (_, dimension) in enumerate(ws.column_dimensions.items()):
        if dimension.hidden and dimension.min is not None and dimension.max is not None:
            hidden_cols.extend(list(range(dimension.min - 1, dimension.max)))

    data = pd.read_excel(excel_file)
    unhidden = np.setdiff1d(np.arange(data.shape[1]), hidden_cols)
    data = data.iloc[:, unhidden].replace({"#DIV/0!": np.nan})
    data = data.drop(c.CHANGE_COLS, axis=1, errors="ignore")
    return data


def clean_data(data: pd.DataFrame) -> pd.Series:
    """
    Transforms the raw DataFrame into a cleaned, stacked DataFrame with a MultiIndex:
    (state, cadre, variable, year, method). Returns only the 'default' method slice.
    Drops Goa and Daman & Diu to avoid geometry conflicts.
    """
    states = data.iloc[:, 0].str.lower().str.strip()
    cadres = data.iloc[:, 1].str.lower()

    values = data.filter(
        regex=r"^((A(v|s|p)D)|QD)_((?P<thresh>[a-zA-Z0-9_]+)_)?[0-9]{4}"
    )
    replace_dict = {"#DIV/0!": np.nan, "ERROR": np.nan, "#VALUE!": np.nan}
    values = values.replace(replace_dict).astype(float)

    cleaned = values.set_index([states, cadres])  # type: ignore

    extracted = cleaned.columns.str.extract(
        r"^(?P<variable>.*)_(?P<year>[0-9]{4})(_using_(?P<method>[a-zA-Z_]+))?$"
    )

    is_year_nan = extracted["year"].isna()
    extracted = extracted[~is_year_nan]
    cleaned = cleaned.loc[:, ~is_year_nan.to_numpy()]

    extracted["year"] = extracted["year"].astype(int)
    extracted = extracted.drop(2, axis=1)  # drop the unnamed column
    extracted["method"] = extracted["method"].fillna("default")
    extracted["variable"] = extracted["variable"].replace(
        {"AvD_IHME_UHC_90": "AvD_IHME_UHC90"}
    )

    cleaned.columns = pd.MultiIndex.from_tuples(
        extracted.to_numpy().tolist(), names=extracted.columns
    )
    cleaned = cleaned.stack([0, 1]).swaplevel("cadres", "year").sort_index()
    cleaned = cleaned.drop(["goa", "daman & diu"], level="states")
    return cleaned["default"]


def load_state_geometries(shapefile_path: str) -> dict:
    """
    Reads the shapefile using cartopy.io.shapereader.Reader and returns a dictionary
    mapping state names (lowercased) to their geometries, with certain manual merges/renames.
    """
    reader = Reader(shapefile_path)
    state_geoms = {
        record.attributes["ST_NM"].lower(): record.geometry
        for record in reader.records()
        if record.geometry is not None
    }
    # Handle special cases / name merges
    state_geoms["n.c.t. of delhi"] = state_geoms.pop("delhi")
    state_geoms["andaman & nicobar islands"] = state_geoms.pop("andaman & nicobar")
    state_geoms["dadra & nagar haveli"] = state_geoms.pop(
        "dadra and nagar haveli and daman and diu"
    )
    # Merge Jammu & Kashmir with Ladakh
    state_geoms["jammu & kashmir"] = state_geoms["jammu & kashmir"].union(
        state_geoms.pop("ladakh")
    )
    # Merge Andhra Pradesh and Telangana
    state_geoms["andhra pradesh"] = state_geoms["andhra pradesh"].union(
        state_geoms.pop("telangana")
    )
    return state_geoms


def determine_cadre_intersection(
    varname: str, group: pd.Series, cadres_of_interest: tuple
) -> set:
    """
    Given a (state, varname) group, returns the set of cadres to plot.
    Applies the special rule for 'ApD_cadre_mix' and removes 'anm'
    when varname == 'ApD_sex_mix'.
    Pure: no I/O, no side effects.
    """
    all_cadres = set(group.index.get_level_values("cadres"))
    if varname.startswith("ApD_cadre_mix"):
        intersection = all_cadres & {"nursing cadres", "supporting cadres"}
    else:
        intersection = all_cadres & set(cadres_of_interest)

    if varname == "ApD_sex_mix" and "anm" in intersection:
        intersection.remove("anm")

    return intersection
