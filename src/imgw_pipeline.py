import argparse
import re
from urllib.parse import urljoin

from constants import DEFAULT_END_YEAR, DEFAULT_START_YEAR, RAW_DATA_URL
from scrapping import download_zip, get_html_contents, unzip_file, validate_zip


def main(start_year: int, end_year: int) -> None:
    """
    Main function to retrieve, download, and extract ZIP files from IMGW webpage.

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
    links = get_html_contents(RAW_DATA_URL, "a", href=True)
    for link in links:
        link = link["href"]
        if re.search(r"\d{4}", link):
            full_url = urljoin(RAW_DATA_URL, link)
            links = get_html_contents(full_url, "a", href=True)
            zip_files_urls = [
                urljoin(full_url, link["href"])
                for link in links
                if validate_zip(link["href"], start_year, end_year)
            ]
            for zip_file_url in zip_files_urls:
                zipped_file = download_zip(zip_file_url)
                unzipped = unzip_file(zipped_file)
                print(unzipped)


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
