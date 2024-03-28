import argparse

from constants import DEFAULT_END_YEAR, DEFAULT_START_YEAR
from scrapping import obtain_data


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
    obtained_files = obtain_data(start_year, end_year)
    print(obtained_files)


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
