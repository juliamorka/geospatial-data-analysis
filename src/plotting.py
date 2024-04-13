import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd

from src.constants import VOIVODESHIPS_URL


def plot_stations(
    merged: pd.DataFrame,
    crs: str = "EPSG:4326",
    voivodeship_boundaries_url: str = VOIVODESHIPS_URL,
    output_plot_path: str = "stations_map.png",
):
    """
    Plots stations on top of Polish voivodeships map and saves the plot as an image.

    Parameters:
        merged (pd.DataFrame): DataFrame containing stations data.
        crs (str, optional): Coordinate reference system. Defaults to "EPSG:4326".
        voivodeship_boundaries_url (str, optional): URL to the file containing
            voivodeships boundaries data. Defaults to VOIVODESHIPS_URL.
        output_plot_path (str, optional): Path to save the plot image.
            Defaults to "stations_map.png".
    """
    gdf = gpd.GeoDataFrame(
        merged, geometry=gpd.points_from_xy(merged["lon"], merged["lat"]), crs=crs
    )
    woj = gpd.read_file(voivodeship_boundaries_url, crs=crs)
    woj.columns = ["id", "name", "geometry"]
    stacje = gdf[["name", "lat", "lon", "geometry"]].drop_duplicates("geometry")
    fig, ax = plt.subplots(1, 1, figsize=(15, 10))
    plt.tight_layout()
    woj.plot(ax=ax, color="dodgerblue", zorder=1)
    woj.boundary.plot(ax=ax, color="blue", zorder=2)
    stacje.plot(ax=ax, color="red", zorder=3)
    ax.set_title("Measurement stations on top of Polish voivodeships", fontsize=18)
    ax.set_xlabel("Longitude [degrees]", fontsize=12)
    ax.set_ylabel("Latitude [degrees]", fontsize=12)
    fig.savefig(output_plot_path, bbox_inches="tight")
    plt.close()
