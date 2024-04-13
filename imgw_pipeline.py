import argparse

from src.constants import (
    DEFAULT_END_YEAR,
    DEFAULT_START_YEAR,
    IMGW_PRECIP_DATA_READ_OPTIONS,
    IMGW_STATIONS_INFO_READ_OPTIONS,
    PERCENT_OF_DATES_THRESHOLD,
)
from src.inspection import create_stations_voivodeship_mapping
from src.plotting import plot_stations
from src.preprocessing import append_stations_info, merge_unzipped_data
from src.scrapping import obtain_data
from src.transformations import (
    calculate_stations_rolling_precipitation_sum,
    convert_date_info_to_timestamp,
    drop_stations_below_threshold,
    fill_missing_dates,
    get_chosen_voivodeship_stations,
    interpolate_total_precip,
    transform_coords,
)


def main(start_year: int, end_year: int) -> None:
    """
    Process the data - retrieve, download, and extract ZIP files from IMGW webpage.
    Subsequent stages of processing include:

    - feature engineering,
    - handling missing values,
    - cleaning the data
    and more.

    Parameters
    ----------
    start_year : int
        The start year of the range (inclusive) for validating ZIP files.
    end_year : int
        The end year of the range (inclusive) for validating ZIP files.

    Returns
    -------
    None
    """
    obtain_data(start_year, end_year)
    merged_df = merge_unzipped_data(
        "data/interim", start_year, end_year, **IMGW_PRECIP_DATA_READ_OPTIONS
    )
    df_with_stations_info = append_stations_info(merged_df, **IMGW_STATIONS_INFO_READ_OPTIONS)
    df_with_stations_info = transform_coords(df_with_stations_info, ["lat", "lon"])
    plot_stations(df_with_stations_info)

    # GET MISSING STATIONS INFO !!!

    voivodeships_mapping = create_stations_voivodeship_mapping(df_with_stations_info)
    analyzed_subset = get_chosen_voivodeship_stations(
        df_with_stations_info, voivodeships_mapping, "podlaskie"
    )
    analyzed_subset_tst = convert_date_info_to_timestamp(
        analyzed_subset, ["year", "month", "day"]
    )

    analyzed_subset_subset = drop_stations_below_threshold(
        analyzed_subset_tst, PERCENT_OF_DATES_THRESHOLD
    )
    full_dates = fill_missing_dates(analyzed_subset_subset)
    interpolated = interpolate_total_precip(full_dates)

    m1 = calculate_stations_rolling_precipitation_sum(interpolated, 1)
    m3 = calculate_stations_rolling_precipitation_sum(interpolated, 3)
    m12 = calculate_stations_rolling_precipitation_sum(interpolated, 12)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="IMGW data pipeline")
    parser.add_argument(
        "--start-year",
        type=int,
        default=DEFAULT_START_YEAR,
        help="First year for which the data should be obtained.",
    )
    parser.add_argument(
        "--end-year",
        type=int,
        default=DEFAULT_END_YEAR,
        help="Last year for which the data should be obtained.",
    )
    args = parser.parse_args()

    main(start_year=args.start_year, end_year=args.end_year)
