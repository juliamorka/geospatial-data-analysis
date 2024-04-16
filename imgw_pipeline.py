import argparse
import os
from datetime import datetime

from src.constants import (
    CHOSEN_VOIVODESHIP,
    DEFAULT_END_YEAR,
    DEFAULT_START_YEAR,
    IMGW_PRECIP_DATA_READ_OPTIONS,
    IMGW_STATIONS_INFO_READ_OPTIONS,
    NUMBER_OF_TASKS,
    OUTPUTS_PATH,
    PERCENT_OF_DATES_THRESHOLD,
    WINDOWS_TO_CALCULATE,
)
from src.inspection import (
    create_stations_voivodeship_mapping,
    get_missing_stations_info,
)
from src.plotting import plot_spi_and_total_precip_time_series, plot_stations
from src.preprocessing import append_stations_info, merge_unzipped_data
from src.scrapping import obtain_data
from src.spi import calculate_stations_spi
from src.transformations import (
    calculate_stations_rolling_precipitation_sum,
    convert_date_info_to_timestamp,
    drop_stations_below_threshold,
    fill_missing_dates,
    get_chosen_voivodeship_stations,
    interpolate_total_precip,
    transform_coords,
)


def main(start_year: int, end_year: int, download_data: bool) -> None:
    """
    Process the data - retrieve, download, and extract ZIP files
    from IMGW webpage.
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
    download_data : bool
        Boolean indicating whether to download and unzip the data or
        operate on the default data directory.

    Returns
    -------
    None
    """
    start_time = datetime.now()
    if download_data:
        obtain_data(start_year, end_year)
        print(f"Download and unzip data: DONE (1/{NUMBER_OF_TASKS})")
    else:
        print(f"Download and unzip data: SKIPPED (1/{NUMBER_OF_TASKS})")

    merged_df = merge_unzipped_data(
        "data/interim", start_year, end_year, **IMGW_PRECIP_DATA_READ_OPTIONS
    )
    print(f"Merge unzipped data: DONE (2/{NUMBER_OF_TASKS})")

    get_missing_stations_info(merged_df, **IMGW_STATIONS_INFO_READ_OPTIONS)
    print(f"Generate missing stations report: DONE (3/{NUMBER_OF_TASKS})")

    df_with_stations_info = append_stations_info(
        merged_df, **IMGW_STATIONS_INFO_READ_OPTIONS
    )
    print(f"Add stations info: DONE (4/{NUMBER_OF_TASKS})")

    df_with_stations_info = transform_coords(
        df_with_stations_info, ["lat", "lon"]
    )
    print(f"Transform coords: DONE (5/{NUMBER_OF_TASKS})")

    plot_stations(df_with_stations_info)
    print(f"Generate stations plot: DONE (6/{NUMBER_OF_TASKS})")

    voivodeships_mapping = create_stations_voivodeship_mapping(
        df_with_stations_info
    )
    print(f"Generate stations voivodeship mapping: DONE (7/{NUMBER_OF_TASKS})")

    analyzed_subset = get_chosen_voivodeship_stations(
        df_with_stations_info, voivodeships_mapping, CHOSEN_VOIVODESHIP
    )
    print(f"Get chosen voivodeship stations: DONE (8/{NUMBER_OF_TASKS})")

    analyzed_subset_tst = convert_date_info_to_timestamp(
        analyzed_subset, ["year", "month", "day"]
    )
    print(f"Convert date to timestamp: DONE (9/{NUMBER_OF_TASKS})")

    analyzed_subset_subset = drop_stations_below_threshold(
        analyzed_subset_tst, PERCENT_OF_DATES_THRESHOLD
    )
    print(f"Drop stations with too little data: DONE (10/{NUMBER_OF_TASKS})")

    full_dates = fill_missing_dates(analyzed_subset_subset)
    print(f"Fill missing dates: DONE (11/{NUMBER_OF_TASKS})")

    interpolated = interpolate_total_precip(full_dates)
    print(f"Interpolate missing dates values: DONE (12/{NUMBER_OF_TASKS})")

    output_files = []
    for idx, window in enumerate(WINDOWS_TO_CALCULATE):
        rolling_precip_sum = calculate_stations_rolling_precipitation_sum(
            interpolated, window
        )
        output_filename = os.path.join(OUTPUTS_PATH, f"spi_{window}.csv")
        spi = calculate_stations_spi(
            rolling_precip_sum,
            save_to_csv=True,
            output_csv_path=output_filename,
        )
        output_files.append(output_filename)
        plot_spi_and_total_precip_time_series(
            rolling_precip_sum,
            spi,
            output_plot_path=os.path.join(
                OUTPUTS_PATH, f"spi_rolling_total_precip_ts_w{window}.png"
            ),
        )

        print(
            f"Calculated SPI and generated SPI time series plot, "
            f"window = {window}: DONE ({12+idx}/{NUMBER_OF_TASKS})"
        )

    print(f"SPI output files: {output_files}")
    print(f"Execution time: {datetime.now()-start_time}")


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
    parser.add_argument(
        "--download-data",
        action="store_true",
        help="Whether to download the data or use the"
        "already downloaded and unzipped files.",
    )
    args = parser.parse_args()

    main(
        start_year=args.start_year,
        end_year=args.end_year,
        download_data=args.download_data,
    )
