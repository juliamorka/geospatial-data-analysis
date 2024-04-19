import geopandas as gpd
import pandas as pd


def transform_coords(
    merged: pd.DataFrame, coord_cols: list, crs: str = "EPSG:4326"
) -> gpd.GeoDataFrame:
    """
    Transforms coordinates from
    degrees, minutes, and seconds to decimal degrees.

    Parameters:
        merged (pd.DataFrame): DataFrame containing coordinates columns.
        coord_cols (list): List of columns containing
            coordinates to be transformed.
        crs (str, optional): Coordinate reference system.
            Defaults to "EPSG:4326".

    Returns:
        gpd.GeoDataFrame: A GeoDataFrame containing
           proper coordinates and geometries.
    """

    def parse_coordinates_to_degrees(encoded: str) -> float:
        """
        Parse encoded coordinates to degrees.

        Args:
        encoded (str): Encoded coordinates in the format 'DD MM SS'.

        Returns:
        float: Degrees representation of the coordinates.
        """
        return (
            int(encoded[0:2])
            + int(encoded[3:5]) / 60
            + int(encoded[6:]) / 3600
        )

    for coord_col in coord_cols:
        merged = merged[merged[coord_col].str.match(r"((\d){2}\s*){3}")]
        merged[coord_col] = merged[coord_col].apply(
            parse_coordinates_to_degrees
        )
    return gpd.GeoDataFrame(
        merged,
        geometry=gpd.points_from_xy(merged["lon"], merged["lat"]),
        crs=crs,
    )


def get_chosen_voivodeship_stations(
    df: pd.DataFrame, stations_mapping: dict, voivodeship: str
) -> pd.DataFrame:
    """
    Filter DataFrame to get stations located in a specific voivodeship.

    Parameters:
        df (pd.DataFrame): The DataFrame containing stations data.
        stations_mapping (dict): A dictionary mapping voivodeships to
            lists of station names.
        voivodeship (str): The name of the voivodeship to filter by.

    Returns:
        pd.DataFrame: A DataFrame containing only the stations within
            specified voivodeship.
    """
    return df[df["name"].isin(stations_mapping[voivodeship])]


def convert_date_info_to_timestamp(
    df: pd.DataFrame, date_cols: list
) -> pd.DataFrame:
    """
    Converts specified date columns
    in the DataFrame to timestamps.

    Parameters:
        df (pd.DataFrame): The DataFrame containing the data.
        date_cols (list): A list of column names containing
           date information to be converted.

    Returns:
        pd.DataFrame: A new DataFrame with the specified
           date columns converted to timestamps.
    """
    df_with_timestamp = df.copy()
    df_with_timestamp["date"] = pd.to_datetime(df_with_timestamp[date_cols])
    return df_with_timestamp.drop(date_cols, axis=1)


def drop_stations_below_threshold(
    df: pd.DataFrame, threshold: int
) -> pd.DataFrame:
    """
    Drops stations from the DataFrame where the number
    of records is below the specified threshold.

    Parameters:
        df (pd.DataFrame): The DataFrame containing station data.
        threshold (int): The minimum number of records required
           for a station to be retained.

    Returns:
        pd.DataFrame: A DataFrame with stations dropped for which
           the number of records is below the threshold.
    """
    grouped_df = df.groupby("name")

    stations_records_count = grouped_df["date"].agg([len])
    stations_above_threshold = stations_records_count.index[
        stations_records_count["len"] >= threshold
    ]
    analyzed_subset_subset = df[
        df["name"].isin(stations_above_threshold)
    ].reset_index(drop=True)
    return analyzed_subset_subset


def fill_missing_dates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Fill missing dates for each station in the DataFrame and
    enter the data where it's possible.

    Parameters:
        df (pd.DataFrame): The DataFrame containing the data.

    Returns:
        pd.DataFrame: The DataFrame with missing dates filled for each station.
    """
    unindexed_df = df.copy()

    unindexed_df = unindexed_df.set_index(["date", "station_code"])

    stations = unindexed_df.index.get_level_values("station_code").unique()
    date_range = pd.date_range(
        start=unindexed_df.index.get_level_values("date").min(),
        end=unindexed_df.index.get_level_values("date").max(),
        freq="D",
    )
    complete_index = pd.MultiIndex.from_product(
        [stations, date_range], names=["station_code", "date"]
    )

    df_reindexed = unindexed_df.reindex(complete_index).reset_index()[
        ["station_code", "date"]
    ]

    full_dates = df_reindexed.merge(
        unindexed_df.reset_index(), on=["station_code", "date"], how="left"
    )

    full_dates = full_dates.set_index(["station_code"])

    filling_info = (
        unindexed_df.reset_index()
        .set_index(["station_code"])[
            ["station_name", "name", "lat", "lon", "geometry"]
        ]
        .drop_duplicates()
    )
    full_dates = full_dates.combine_first(filling_info)

    return full_dates


def interpolate_total_precip(df: pd.DataFrame) -> pd.DataFrame:
    """
    Interpolates missing values in the 'total_precip' column
    of the DataFrame using time-based interpolation.

    Parameters:
        df (pd.DataFrame): The DataFrame containing precipitation data.

    Returns:
        pd.DataFrame: A DataFrame with missing values
            in the 'total_precip' column interpolated.
    """
    interpolated = (
        df.drop("precip_type", axis=1).reset_index().set_index("date")
    )
    for station in interpolated["station_code"].unique():
        idx = interpolated.station_code == station
        interpolated.loc[idx, "total_precip"] = interpolated[idx][
            "total_precip"
        ].interpolate(method="time", limit_direction="both")
    return interpolated.reset_index()


def calculate_stations_rolling_precipitation_sum(
    df: pd.DataFrame, window: int
) -> pd.DataFrame:
    """
    Calculates the rolling sum of precipitation
    for each station over a specified window.

    Parameters:
        df (pd.DataFrame): The DataFrame containing precipitation data.
        window (int): The size of the rolling window.

    Returns:
        pd.DataFrame: A DataFrame containing the rolling sum
           of precipitation for each station.
    """
    df_sum = df.groupby(["station_code", df.date.dt.year, df.date.dt.month])[
        "total_precip"
    ].sum()
    idx = df_sum.index
    df_sum.index.names = ["station_code", "year", "month"]
    df_sum = df_sum.reset_index()
    rolling_sum = (
        df_sum.groupby(df_sum["station_code"])
        .rolling(window)["total_precip"]
        .sum()
    )
    rolling_sum.index = idx
    rolling_sum = rolling_sum.dropna()
    return pd.DataFrame(rolling_sum).reset_index()
