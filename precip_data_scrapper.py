import argparse
import os
import re
import zipfile
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from bs4.element import ResultSet

from constants import (
    RAW_DATA_URL,
    DEFAULT_START_YEAR,
    DEFAULT_END_YEAR,
    HTTP_REQUEST_TIMEOUT,
    INPUT_DATA_PATH,
    INTERIM_DATA_PATH,
)


def get_html_contents(
    url: str, html_tag: str, timeout: int = 10, **soup_kwargs
) -> ResultSet:
    """
    Retrieve contents from a webpage and return elements specified by HTML tag.

    Parameters
    ----------
    url : str
        The URL of the webpage to retrieve contents from.
    html_tag : str
        The HTML tag to search for in the webpage.
    timeout : int, optional
        Timeout value for the HTTP request in seconds. Defaults to 10.
    **soup_kwargs
        Additional keyword arguments to be passed to BeautifulSoup.

    Returns
    -------
    ResultSet
        A result set containing elements matching the specified HTML tag.

    Example
    -------
    >>> get_html_contents("https://example.com", "a", timeout=5)
    """
    resp = requests.get(url, timeout=timeout)
    soup = BeautifulSoup(resp.text, "html.parser")
    return soup.find_all(html_tag, **soup_kwargs)


def validate_zip(name: str, start_year: int, end_year: int) -> bool:
    """
    Validate if a given href corresponds to a ZIP file and falls within
    the specified range of years, according to IMGW file naming convention.

    Parameters
    ----------
    name : str
        The URL or filename to validate.
    start_year : int
        The start year of the range (inclusive).
    end_year : int
        The end year of the range (inclusive).

    Returns
    -------
    bool
        True if the href corresponds to a ZIP file and its year falls within the specified range,
        False otherwise.

    Example
    -------
    >>> validate_zip("example_2023.zip", 2020, 2025)
    True
    >>> validate_zip("example_2019.zip", 2020, 2025)
    False
    """
    return name.lower().endswith("zip") and int(name.split("_")[0]) in range(
        start_year, end_year + 1
    )


def download_zip(zip_file_url: str, save_path: str = INPUT_DATA_PATH) -> str:
    """
    Download a ZIP file from a given URL and extract its contents.

    Parameters
    ----------
    zip_file_url : str
        The URL of the ZIP file to download.

    save_path : str, optional
        The directory path where the downloaded ZIP file will be saved.
        Defaults to INPUT_DATA_PATH.

    Returns
    -------
    str
        The path where the downloaded ZIP file is saved.

    Example
    -------
    >>> download_zip("https://example.com/data_2023.zip")
    """
    os.makedirs(save_path, exist_ok=True)
    zip_file_name = zip_file_url.split("/")[-1]
    zip_save_path = os.path.join(save_path, zip_file_name)

    resp = requests.get(zip_file_url, timeout=HTTP_REQUEST_TIMEOUT)

    with open(zip_save_path, "wb") as file:
        for chunk in resp.iter_content(chunk_size=8192):
            file.write(chunk)

    return zip_save_path


def unzip_file(zip_save_path: str, unzip_save_path: str = INTERIM_DATA_PATH) -> str:
    """
    Unzip a ZIP file to a specified directory.

    Parameters
    ----------
    zip_save_path : str
        The path to the ZIP file to be extracted.
    unzip_save_path : str, optional
        The directory path where the contents of the ZIP file will be extracted.
        Defaults to INTERIM_DATA_PATH.

    Returns
    -------
    str
        The path where the unzipped ZIP archive is saved.

    Example
    -------
    >>> unzip_file("/path/to/your/zipfile.zip")
    """
    data_year = os.path.basename(zip_save_path).split("_")[0] + "/"
    unzipped_save_path = os.path.join(unzip_save_path, data_year)
    os.makedirs(unzipped_save_path, exist_ok=True)
    with zipfile.ZipFile(zip_save_path, "r") as zip_ref:
        try:
            zip_ref.extractall(unzipped_save_path)
        except:
            print(unzipped_save_path)
    return os.path.join(unzipped_save_path, os.path.basename(zip_save_path))


def main(start_year: int, end_year: int):
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
