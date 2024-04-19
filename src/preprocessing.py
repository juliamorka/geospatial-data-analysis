import os

import pandas as pd

from src.constants import (
    COLUMNS_LABELS,
    STATIONS_INFO_COLUMNS_LABELS,
    STATIONS_INFO_PATH,
    STATIONS_INFO_PK,
)


def merge_unzipped_data(
    interim_data_path: str,
    start_year: int,
    end_year: int,
    output_columns_labels: list = COLUMNS_LABELS,
    **read_csv_kwargs
) -> pd.DataFrame:
    """
    Merges unzipped data from multiple years into a single DataFrame.

    Parameters:
        interim_data_path (str): Path to the directory
            which contains unzipped data.
        start_year (int, optional): Starting year for
            merging data (inclusive). Defaults to 1990.
        end_year (int, optional): Ending year for
            merging data (inclusive). Defaults to 2020.
        output_columns_labels (list): List of column labels
            for the merged DataFrame. Defaults to COLUMNS_LABELS.
        **read_csv_kwargs: Additional keyword arguments to
            be passed to pandas read_csv function.

    Returns:
        pd.DataFrame: Merged DataFrame containing data from specified years.
    """
    stations_data = pd.DataFrame()
    for yr in os.listdir(interim_data_path):
        if int(yr) not in range(start_year, end_year + 1):
            continue
        yr_path = os.path.join(interim_data_path, yr)
        for file in os.listdir(yr_path):
            temp = pd.read_csv(os.path.join(yr_path, file), **read_csv_kwargs)
            stations_data = pd.concat([stations_data, temp])
    stations_data.columns = output_columns_labels
    return stations_data


def append_stations_info(
    merged_stations_data: pd.DataFrame,
    stations_info_path: str = STATIONS_INFO_PATH,
    stations_info_columns_labels: list = STATIONS_INFO_COLUMNS_LABELS,
    primary_key_col: str = STATIONS_INFO_PK,
    **read_csv_kwargs
) -> pd.DataFrame:
    """
    Appends stations information to the merged stations data.

    Parameters:
        merged_stations_data (pd.DataFrame): Merged stations data DataFrame.
        stations_info_path (str): Path/URL of the file containing
            stations information. Defaults to STATIONS_INFO_PATH.
        stations_info_columns_labels (list): List of column labels
            for the stations information DataFrame.
            Defaults to STATIONS_INFO_COLUMNS_LABELS.
        primary_key_col (str): Primary key column to perform the merge on.
            Defaults to STATIONS_INFO_PK.
        **read_csv_kwargs: Additional keyword arguments
            to be passed to pandas read_csv function.

    Returns:
        pd.DataFrame: Merged DataFrame containing
            stations data with appended stations information.
    """
    stations_info = pd.read_csv(stations_info_path, **read_csv_kwargs)
    stations_info.columns = stations_info_columns_labels
    return merged_stations_data.merge(
        stations_info, how="inner", on=primary_key_col
    )
