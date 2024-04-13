import json
from collections import defaultdict

import geopandas as gpd
import pandas as pd

from src.constants import VOIVODESHIPS_URL


def get_missing_stations_info(
    merged_stations_data: pd.DataFrame,
    stations_info_path: str,
    stations_info_columns_labels: list,
    primary_key_col: str,
    **read_csv_kwargs
) -> None:
    """
    Retrieves missing stations and saves them to a JSON file in a form of {station_code: station_name}.

    Parameters:
        merged_stations_data (pd.DataFrame): Merged stations data DataFrame.
        stations_info_path (str): Path to the file containing stations information.
        stations_info_columns_labels (list): List of column labels for the stations information DataFrame.
        primary_key_col (str): Primary key column to perform the merge on.
        **read_csv_kwargs: Additional keyword arguments to be passed to pandas read_csv function.
    """
    stations_info = pd.read_csv(stations_info_path, **read_csv_kwargs)
    stations_info.columns = stations_info_columns_labels
    merged = merged_stations_data.merge(stations_info, how="left", on=primary_key_col)
    missing = merged[merged["name"].isna()][
        ["station_code", "station_name"]
    ].drop_duplicates()
    with open("outputs/missing_stations_test.json", "w") as file:
        json.dump(dict(zip(missing.station_code, missing.station_name)), file, indent=4)


def create_stations_voivodeship_mapping(
    merged: pd.DataFrame,
    crs: str = "EPSG:4326",
    voivodeship_boundaries_url: str = VOIVODESHIPS_URL,
):
    """
    Creates a mapping between stations and voivodeships and saves it to a JSON file.

    Parameters:
        merged (pd.DataFrame): DataFrame containing stations data.
        crs (str, optional): Coordinate reference system. Defaults to "EPSG:4326".
        voivodeship_boundaries_url (str, optional): URL to the file containing voivodeships
            boundaries data. Defaults to VOIVODESHIPS_URL.
    """
    mapping = defaultdict(list)
    gdf = gpd.GeoDataFrame(
        merged, geometry=gpd.points_from_xy(merged["lon"], merged["lat"]), crs=crs
    )
    woj = gpd.read_file(voivodeship_boundaries_url, crs=crs)
    woj.columns = ["id", "name", "geometry"]
    stacje = gdf[["name", "lat", "lon", "geometry"]].drop_duplicates("geometry")
    for _, wojewodztwo in woj.iterrows():
        mapping[wojewodztwo["name"]].extend(
            stacje[stacje.within(wojewodztwo["geometry"])]["name"].tolist()
        )
    with open("outputs/stations_mapping.json", "w") as file:
        json.dump(dict(mapping), file, indent=4)
    return dict(mapping)
