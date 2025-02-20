"""Module that provides utilities to the project.

It includes functions to handle common tasks such as sending HTTP requests, parsing
HTML, creating download directories, and clearing the terminal, making it reusable
across projects.
"""

import logging
import os
import sys
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from .config import DOWNLOAD_FOLDER


def fetch_page(url: str, timeout: int = 10) -> BeautifulSoup:
    """Fetch the HTML content of a webpage."""
    # Create a new session per worker
    session = requests.Session()

    try:
        response = session.get(url, timeout=timeout)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")

    except requests.RequestException as req_err:
        message = f"Error fetching page {url}: {req_err}"
        logging.exception(message)
        sys.exit(1)

def create_download_directory(directory_path: str) -> str:
    """Construct a download path for the given title."""
    download_path = Path(DOWNLOAD_FOLDER) / Path(directory_path)

    try:
        Path(download_path).mkdir(parents=True, exist_ok=True)
        return download_path

    except OSError:
        logging.exception("Error creating directory")
        sys.exit(1)

def clear_terminal() -> None:
    """Clear the terminal screen based on the operating system."""
    commands = {
        "nt": "cls",      # Windows
        "posix": "clear",  # macOS and Linux
    }

    command = commands.get(os.name)
    if command:
        os.system(command)  # noqa: S605
