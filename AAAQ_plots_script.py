import os
import sys
from typing import cast

from matplotlib import pyplot as plt
import matplotlib.cm as cm
from matplotlib.colors import Normalize

from cartopy.feature import ShapelyFeature
from cartopy.mpl.geoaxes import GeoAxes
import cartopy.crs as ccrs

import pandas as pd
import numpy as np
from tqdm.auto import tqdm

import constants as c
from utils import *


# -------------------------------------------------------------------
# HELPER FUNCTIONS FOR LINE PLOTS
# -------------------------------------------------------------------


def plot_line_figure(
    frame,
    state: str,
    varname: str,
    varname_mapping: dict,
    cadre_label_mapping: dict,
    cadre_colors: dict,
    proj_year: int,
) -> plt.Figure:  # type: ignore
    """
    Given the “frame” (as returned by build_line_frame), produce a matplotlib Figure
    with the actual vs. projected lines drawn. Returns the Figure object (unsaved).
    Pure: it creates a small Figure in memory but does not call plt.savefig().
    """
    fig, ax = plt.subplots(figsize=(7, 4), facecolor="white")
    ax.set_position((0.15, 0.1, 0.5, 0.8))
    ax.axhline(0, color="gray", lw=0.5)

    # Determine x‐ticks (all years present)
    xticks = sorted(frame.index.get_level_values("year").unique())
    ax.set_xticks(xticks)

    # Track min/max for consistent y‐limits
    ymax, ymin = -np.inf, np.inf

    for cadre, subser in frame.groupby("cadres"):
        color = cadre_colors.get(cadre, "C0")
        series = subser.droplevel(["states", "variable", "cadres"])
        series = np.clip(series, a_min=-1, a_max=1)

        ymax = max(ymax, series.max())
        ymin = min(ymin, series.min())

        real = series[series.index <= proj_year]
        proj = series[series.index >= proj_year]

        props = dict(ax=ax, marker="o", ls="--", c=color, ms=10)
        real.plot(label=cadre_label_mapping.get(cadre, cadre), **props)
        proj.plot(
            label="_nolegend_", markerfacecolor="none", markeredgewidth=2, **props
        )

    # Labels and titles
    var_full_name = varname_mapping[varname]
    ax.set_ylabel(var_full_name)
    if state != "india":
        ax.set_title(state.title(), size="x-large")
    ax.set_xlabel("Year")

    # Adjust y‐limits
    ymax = min(ymax + 0.125, 1.25)
    ymin = max(ymin - 0.125, -1.25)
    ax.set_ylim((ymin, ymax))
    ax.legend(loc="center left", bbox_to_anchor=[1, 0.5])

    return fig


def get_line_output_path(results_dir: str, varname: str, state: str) -> str:
    """
    Constructs the path where the line‐plot PDF should be saved, e.g.:
      {results_dir}/lines/{varname}/{state}.pdf
    Pure: just returns a string, does not create directories.
    """
    return os.path.join(results_dir, "lines", varname, f"{state}.pdf")


# -------------------------------------------------------------------
# HELPER FUNCTIONS FOR MAP PLOTS
# -------------------------------------------------------------------


def digitize_values_for_map(
    varname: str, group: pd.Series
) -> tuple[pd.Series, float, float]:
    """
    Digitize raw values into bins, based on varname. Returns a Series or array
    of integer “buckets” (0..7). Pure: no I/O.
    """
    if varname == "QD":
        a_min, a_max, a_step, base = 0.125, 0.875, 0.125, 0
    else:
        a_min, a_max, a_step, base = -0.75, 0.75, 0.25, -4

    bins = np.arange(a_min, a_max + a_step, a_step)
    digitized = group.where(np.isnan(group), np.digitize(group, bins))
    return digitized, a_step, base


def prepare_color_mapper(vmin: int = 0, vmax: int = 7):
    """
    Returns a (mapper, cticks, cticklabels) tuple that can be reused each time:
    - mapper: a ScalarMappable configured for RdYlGn_r with discrete buckets
    - cticks: list of tick positions
    - cticklabels: human‐readable labels for colorbar
    Pure: no I/O.
    """
    norm = Normalize(vmin=vmin - 0.5, vmax=vmax + 0.5)
    mapper = cm.ScalarMappable(norm=norm, cmap=cm.get_cmap("RdYlGn_r", vmax - vmin + 1))
    return mapper


def plot_map_figure(
    state_geoms: dict,
    digitized_series: pd.Series,
    varname: str,
    year: int,
    cadre: str,
    cadre_label_mapping: dict,
    varname_mapping: dict,
    state_abbr: dict,
    mapper,
    a_step,
    base,
    vmin,
    vmax,
) -> plt.Figure:  # type: ignore
    """
    Given the digitized series (indexed by state name), returns a matplotlib Figure
    that draws each state polygon, colors it, and adds text labels. Pure in the sense
    that it only creates a Figure and returns it (does not save to disk).
    """
    proj_crs = ccrs.PlateCarree()

    fig = plt.figure(figsize=(7, 7), facecolor="white")
    ax = cast(GeoAxes, fig.add_subplot(projection=proj_crs))
    ax.set_extent([67, 98, 6, 38])

    cticks = np.arange(vmin - 0.5, vmax + 1.5, 1)
    # cticklabels correspond to actual value ranges, e.g. [-1, -0.75, …, 1]
    # but here we keep them as simple integers or bins for demonstration
    cticklabels = np.arange(
        a_step * (vmin + base), a_step * (vmax + base) + 2 * a_step, a_step
    )

    # Track which states are filled
    filled = {s: False for s in state_geoms.keys()}

    # Drop top‐levels
    series = digitized_series.droplevel(["variable", "year", "cadres"])

    for state, value in series.items():
        if state == "india":
            continue
        record = state_geoms[state]
        color = mapper.to_rgba(value)
        feature = ShapelyFeature(
            [record], proj_crs, edgecolor="black", lw=0.5, facecolor=color
        )
        centroid = record.centroid
        abbr = state_abbr[state]
        ax.add_feature(feature, rasterized=True)
        ax.text(centroid.x, centroid.y, abbr, va="center", ha="center")
        filled[state] = True

    # Outline states without data
    for state, is_filled in filled.items():
        if not is_filled:
            record = state_geoms[state]
            feature = ShapelyFeature(
                [record], proj_crs, edgecolor="black", facecolor="none", lw=0.5
            )
            ax.add_feature(feature, rasterized=True)

    # Add colorbar
    cbar = plt.colorbar(mapper, shrink=0.8, ax=ax)
    cbar.set_ticks(cticks)
    cbar.set_ticklabels(cticklabels)

    # Title
    var_full_name = varname_mapping[varname]
    cadre_label = cadre_label_mapping.get(
        cadre, " ".join([w.capitalize() for w in cadre.split()])
    )
    line1 = f"{var_full_name}:"
    line2 = f"{cadre_label} ({year})"
    if len(line1 + " " + line2) <= 60:
        title = f"{line1} {line2}"
    else:
        title = f"{line1}\n{line2}"
    ax.set_title(title, size="x-large", loc="left")
    fig.tight_layout()

    return fig


def get_map_output_path(
    results_dir: str, varname: str, year: int, cadre: str, cadre_label_mapping: dict
) -> str:
    """
    Returns the path where the map PDF should be saved:
      {results_dir}/maps/{varname}/{year}/{CadreLabel}.pdf
    Pure: string construction only.
    """
    cadre_label = cadre_label_mapping.get(
        cadre, " ".join([w.capitalize() for w in cadre.split()])
    )
    return os.path.join(results_dir, "maps", varname, str(year), f"{cadre_label}.pdf")


# -------------------------------------------------------------------
# MAIN GENERATORS (use the pure helpers inside)
# -------------------------------------------------------------------


def generate_line_plots(
    cleaned: pd.Series,
    varname_mapping: dict,
    cadre_label_mapping: dict,
    cadres_of_interest: tuple,
    proj_year: int,
    results_dir: str,
) -> None:
    """
    Iterates over (state, variable) groups and:
      1. Determines which cadres to plot
      2. Builds the frame for plotting
      3. Calls `plot_line_figure(...)` to get a Figure
      4. Saves the figure to disk
    """
    cadre_colors = {
        cadre: f"C{i}"
        for i, cadre in enumerate(
            cadres_of_interest + ("nursing cadres", "supporting cadres")
        )
    }

    for (state, varname), group_series in tqdm(
        list(cleaned.groupby(["states", "variable"]))
    ):
        if varname not in varname_mapping:
            print(f"skipping {varname}, not in mapping", file=sys.stderr)
            continue

        intersection = determine_cadre_intersection(
            varname, group_series, cadres_of_interest
        )
        if not intersection:
            continue

        frame = group_series.loc[:, :, :, list(intersection)]
        fig = plot_line_figure(
            frame=frame,
            state=state,
            varname=varname,
            varname_mapping=varname_mapping,
            cadre_label_mapping=cadre_label_mapping,
            cadre_colors=cadre_colors,
            proj_year=proj_year,
        )

        out_path = get_line_output_path(results_dir, varname, state)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        if not os.path.exists(out_path):
            fig.savefig(out_path, dpi=450)
        plt.close(fig)


def generate_map_plots(
    cleaned: pd.Series,
    state_geoms: dict,
    varname_mapping: dict,
    cadre_label_mapping: dict,
    state_abbr: dict,
    results_dir: str,
) -> None:
    """
    Iterates over (variable, year, cadre) groups and:
      1. Digitizes the values
      2. Prepares the color mapper & ticks
      3. Calls `plot_map_figure(...)` to get a Figure
      4. Saves the figure to disk
    """

    vmin, vmax = 0, 7
    # (We can reuse the same mapper for all, since vmin/vmax don't change)
    mapper = prepare_color_mapper(vmin=vmin, vmax=vmax)

    for (varname, year, cadre), group_series in tqdm(
        cleaned.groupby(["variable", "year", "cadres"])
    ):
        if varname not in varname_mapping:
            print(f"skipping {varname}, not in mapping", file=sys.stderr)
            continue

        digitized, a_step, base = digitize_values_for_map(varname, group_series)
        fig = plot_map_figure(
            state_geoms=state_geoms,
            digitized_series=digitized,
            varname=varname,
            year=year,
            cadre=cadre,
            cadre_label_mapping=cadre_label_mapping,
            varname_mapping=varname_mapping,
            state_abbr=state_abbr,
            mapper=mapper,
            a_step=a_step,
            base=base,
            vmin=vmin,
            vmax=vmax,
        )

        out_path = get_map_output_path(
            results_dir, varname, year, cadre, cadre_label_mapping
        )
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        if not os.path.exists(out_path):
            fig.savefig(out_path, dpi=450)
        plt.close(fig)


if __name__ == "__main__":
    # Define file paths
    EXCEL_FILE = "Documents/14_07_22_VW_AAAQ_mastersheet__26_NOV_23.xlsx"
    SHAPEFILE_PATH = "Documents/maps-master/States/Admin2"
    RESULTS_DIR = "Results/raw-value-based"
    PROJ_YEAR = 2011

    # Load and preprocess data
    raw_data = load_raw_data(EXCEL_FILE)
    state_geometries = load_state_geometries(SHAPEFILE_PATH)
    cleaned_stacked = clean_data(raw_data)

    # Generate line plots
    generate_line_plots(
        cleaned=cleaned_stacked,
        varname_mapping=c.VARNAME_MAPPING,
        cadre_label_mapping=c.CADRE_LABEL_MAPPING,
        cadres_of_interest=c.CADRES_OF_INTEREST,
        proj_year=PROJ_YEAR,
        results_dir=RESULTS_DIR,
    )

    # Generate map plots
    generate_map_plots(
        cleaned=cleaned_stacked,
        state_geoms=state_geometries,
        varname_mapping=c.VARNAME_MAPPING,
        cadre_label_mapping=c.CADRE_LABEL_MAPPING,
        state_abbr=c.STATE_ABBR,
        results_dir=RESULTS_DIR,
    )
