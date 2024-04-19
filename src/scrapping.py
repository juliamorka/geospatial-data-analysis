import os
import re
import zipfile
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from bs4.element import ResultSet

from src.constants import (
    HTTP_REQUEST_TIMEOUT,
    INPUT_DATA_PATH,
    INTERIM_DATA_PATH,
    RAW_DATA_URL,
)


def get_html_contents(
    url: str, html_tag: str, timeout: int = 10, **soup_kwargs
) -> ResultSet:
    """
    Retrieve contents from a webpage and return
    elements specified by HTML tag.

    Parameters
    ----------
    url (str): The URL of the webpage to
        retrieve contents from.
    html_tag (str): The HTML tag to search for
        in the webpage.
    timeout (int, optional): Timeout value for the HTTP
        request in seconds.
        Defaults to 10.
    **soup_kwargs: Additional keyword arguments
        to be passed to BeautifulSoup.

    Returns
    -------
    ResultSet: A result set containing elements
        matching the specified HTML tag.
    """
    resp = requests.get(url, timeout=timeout)
    soup = BeautifulSoup(resp.text, "html.parser")
    return soup.find_all(html_tag, **soup_kwargs)


def validate_zip(name: str, start_year: int, end_year: int) -> bool:
    """
    Validate if a given href corresponds to a ZIP file
    and falls within the specified range of years,
    according to IMGW file naming convention.

    Parameters
    ----------
    name (str): The URL or filename to validate.
    start_year (int): The start year of the range (inclusive).
    end_year (int): The end year of the range (inclusive).

    Returns
    -------
    bool: True if the href corresponds to a ZIP file
        and its year falls within the specified range,
        False otherwise.
    """
    return name.lower().endswith("zip") and int(name.split("_")[0]) in range(
        start_year, end_year + 1
    )


def download_zip(zip_file_url: str, save_path: str = INPUT_DATA_PATH) -> str:
    """
    Download a ZIP file from a given URL and extract its contents.

    Parameters
    ----------
    zip_file_url (str): The URL of the ZIP file
        to download.

    save_path (str, optional): The directory path
        where the downloaded ZIP file will be saved.
        Defaults to INPUT_DATA_PATH.

    Returns
    -------
    str: The path where the downloaded ZIP file is saved.
    """
    os.makedirs(save_path, exist_ok=True)
    zip_file_name = zip_file_url.split("/")[-1]
    zip_save_path = os.path.join(save_path, zip_file_name)

    resp = requests.get(zip_file_url, timeout=HTTP_REQUEST_TIMEOUT)

    with open(zip_save_path, "wb") as file:
        for chunk in resp.iter_content(chunk_size=8192):
            file.write(chunk)

    return zip_save_path


def create_interim_dir(
    zip_save_path: str, unzip_save_path: str = INTERIM_DATA_PATH
) -> str:
    """
    Create an interim directory for storing
    the contents of a ZIP file after extraction.

    Parameters
    ----------
    zip_save_path (str): The path to the ZIP file.
    unzip_save_path (str, optional): The parent directory
        path where the contents of the ZIP file
        will be extracted. Defaults to INTERIM_DATA_PATH.

    Returns
    -------
    str: The path of the created interim directory.
    """
    data_year = os.path.basename(zip_save_path).split("_")[0] + "/"
    unzipped_save_path = os.path.join(unzip_save_path, data_year)
    os.makedirs(unzipped_save_path, exist_ok=True)
    return unzipped_save_path


def unzip_file(
    zip_save_path: str, unzip_save_path: str = INTERIM_DATA_PATH
) -> list[str]:
    """
    Unzip a ZIP file to a specified directory.

    Parameters
    ----------
    zip_save_path (str): The path to the ZIP
        file to be extracted.
    unzip_save_path (str, optional) The directory
        path where the contents of the ZIP file
        will be extracted. Defaults to INTERIM_DATA_PATH.

    Returns
    -------
    list[str]: List of files extracted from the ZIP archive.
    """
    unzipped_save_path = create_interim_dir(zip_save_path, unzip_save_path)
    with zipfile.ZipFile(zip_save_path, "r") as zip_ref:
        try:
            zip_ref.extractall(unzipped_save_path)
            extracted_files = zip_ref.namelist()
        except:
            print(f"Could not unzip archive: {zip_save_path}")
            return []
    return [
        os.path.join(unzipped_save_path, extracted_file)
        for extracted_file in extracted_files
    ]


def obtain_data(start_year: int, end_year: int) -> list[str]:
    """
    Retrieve, download, and extract ZIP files from IMGW webpage.

    Parameters
    ----------
    start_year (int): The start year of the range
        (inclusive) for validating ZIP files.
    end_year (int): The end year of the range
        (inclusive) for validating ZIP files.

    Returns
    -------
    list[str]: List of downloaded and extracted files.
    """
    unzipped_data = []
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
                unzipped_files = unzip_file(zipped_file)
                unzipped_data.extend(unzipped_files)
    return unzipped_data
