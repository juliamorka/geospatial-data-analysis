import io
import os
import re
import zipfile
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from bs4.element import ResultSet

from pathlib import Path

from constants import RAW_DATA_URL, START_YEAR, END_YEAR, INPUT_DATA_PATH, INTERIM_DATA_PATH


def get_html_contents(url: str, html_tag: str, timeout: int = 10, **soup_kwargs) -> ResultSet:
    """
    TODO: Add docstring
    """
    resp = requests.get(url, timeout=timeout)
    soup = BeautifulSoup(resp.text, "html.parser")
    return soup.find_all(html_tag, **soup_kwargs)


def validate_zip(href: str, start_year: int, end_year: int) -> bool:
    return href.lower().endswith("zip") and int(href.split("_")[0]) in range(start_year, end_year + 1)


def download_zip(zip_file_url: str):
    zip_file_name = zip_file_url.split("/")[-1]
    data_year = zip_file_name.split("_")[0] + "/"
    zip_save_path = os.path.join(INPUT_DATA_PATH, zip_file_name)
    r = requests.get(zip_file_url)  # TODO: Add Exception handling
    with open(zip_save_path, 'wb') as fd:
        for chunk in r.iter_content(chunk_size=8192):
            fd.write(chunk)
    unzipped_save_path = os.path.join(INTERIM_DATA_PATH, data_year)
    Path(unzipped_save_path).mkdir(exist_ok=True)
    with zipfile.ZipFile(zip_save_path, 'r') as zip_ref:
        try:
            zip_ref.extractall(unzipped_save_path)
        except:
            print(unzipped_save_path)


# TODO: CREATE MISSING DATA DIRECTORIES (INPUT, INTERIM), CLEANING DIRS
# TODO: MAKE INTO A LUIGI PIPELINE

links = get_html_contents(RAW_DATA_URL, "a", href=True)

for link in links:
    link = link["href"]
    if re.search(r"\d{4}", link):
        full_url = urljoin(RAW_DATA_URL, link)
        links = get_html_contents(full_url, "a", href=True)
        zip_files_urls = [
            urljoin(full_url, link["href"])
            for link in links
            if validate_zip(link["href"], START_YEAR, END_YEAR)
        ]
        for zip_file_url in zip_files_urls:
            download_zip(zip_file_url)
        if zip_files_urls:
            print(*zip_files_urls, sep="\n")
