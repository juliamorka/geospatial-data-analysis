import re
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from bs4.element import ResultSet

from constants import RAW_DATA_URL


def get_html_contents(url: str, html_tag: str, timeout: int = 10, **soup_kwargs) -> ResultSet:
    """
    TODO: Add docstring
    """
    resp = requests.get(url, timeout=timeout)
    soup = BeautifulSoup(resp.text, "html.parser")
    return soup.find_all(html_tag, **soup_kwargs)


links = get_html_contents(RAW_DATA_URL, "a", href=True)
files_to_download = []

for link in links:
    link = link["href"]
    if re.search(r"\d{4}", link):
        full_url = urljoin(RAW_DATA_URL, link)
        links = get_html_contents(full_url, "a", href=True)
        zip_files = [
            urljoin(full_url, link["href"])
            for link in links
            if link["href"].lower().endswith("zip")
        ]
        files_to_download.extend(zip_files)

print(*files_to_download, sep="\n")
