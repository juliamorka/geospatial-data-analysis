from math import ceil

import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from src.constants import (
    DEFAULT_SPI_PRECIP_TS_PLOT_PATH,
    DEFAULT_STATIONS_PLOT_PATH,
    VOIVODESHIPS_URL,
)


def plot_stations(
    merged: pd.DataFrame,
    crs: str = "EPSG:4326",
    voivodeship_boundaries_url: str = VOIVODESHIPS_URL,
    output_plot_path: str = DEFAULT_STATIONS_PLOT_PATH,
):
    """
    Plots stations on top of Polish voivodeships map
    and saves the plot as an image.

    Parameters:
        merged (gpd.GeoDataFrame): GeoDataFrame containing stations data.
        crs (str, optional): Coordinate reference system.
            Defaults to "EPSG:4326".
        voivodeship_boundaries_url (str, optional): URL to the file containing
            voivodeships boundaries data. Defaults to VOIVODESHIPS_URL.
        output_plot_path (str, optional): Path to save the plot image.
            Defaults to DEFAULT_STATIONS_PLOT_PATH.
    """
    voivodeships = gpd.read_file(voivodeship_boundaries_url, crs=crs)
    voivodeships.columns = ["id", "name", "geometry"]
    stations = merged[["name", "lat", "lon", "geometry"]].drop_duplicates("geometry")
    fig, ax = plt.subplots(1, 1, figsize=(15, 10))
    plt.tight_layout()
    voivodeships.plot(ax=ax, color="dodgerblue", zorder=1)
    voivodeships.boundary.plot(ax=ax, color="blue", zorder=2)
    stations.plot(ax=ax, color="red", zorder=3)
    ax.set_title("Measurement stations on top of Polish voivodeships", fontsize=18)
    ax.set_xlabel("Longitude [degrees]", fontsize=12)
    ax.set_ylabel("Latitude [degrees]", fontsize=12)
    fig.savefig(output_plot_path, bbox_inches="tight")
    plt.close()


def plot_spi_and_total_precip_time_series(
    rolling_total_precip: pd.DataFrame,
    spi: pd.DataFrame,
    output_plot_path: str = DEFAULT_SPI_PRECIP_TS_PLOT_PATH,
) -> None:
    """
    Plot time series of Standardized Precipitation Index (SPI)
    and total precipitation for each station.

    Parameters:
        rolling_total_precip (pd.DataFrame): A DataFrame containing
           rolling total precipitation data for stations.
        spi (pd.DataFrame): A DataFrame containing SPI data
          for stations.
        output_plot_path (str, optional): Path to save the plot.
          Defaults to DEFAULT_SPI_PRECIP_TS_PLOT_PATH.

    Returns:
        None
    """
    unique_stations = rolling_total_precip["station_code"].unique()

    for df in (rolling_total_precip, spi):
        df["date"] = pd.to_datetime(
            df["year"].astype(str) + "-" + df["month"].astype(str),
            format="%Y-%m",
        )

    fig, axes = plt.subplots(ceil(len(unique_stations) / 2), 2, figsize=(15, 20))
    fig.tight_layout()
    fig.subplots_adjust(hspace=0.5, wspace=0.2)
    for ax, station_code in zip(axes.flat, unique_stations):
        spi_subset = spi[spi["station_code"] == station_code].copy()
        rolling_total_precip_subset = rolling_total_precip[
            rolling_total_precip["station_code"] == station_code
        ].copy()
        rolling_total_precip_subset["total_precip"] = (
            rolling_total_precip_subset["total_precip"]
            - rolling_total_precip_subset["total_precip"].mean()
        ) / rolling_total_precip_subset["total_precip"].std()
        sns.lineplot(
            data=spi_subset,
            x="date",
            y="SPI",
            ax=ax,
            color="blue",
            label="SPI",
            legend=False,
        )
        sns.lineplot(
            data=rolling_total_precip_subset,
            x="date",
            y="total_precip",
            ax=ax,
            color="red",
            label="Total precipitation",
            legend=False,
        )
        ax.set_title(
            f"Time series of SPI and standardized total precipitation for station {station_code}"
        )
    handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles, labels, bbox_to_anchor=(0.6, 0), ncols=2)
    fig.savefig(output_plot_path, bbox_inches="tight")
    plt.close()
