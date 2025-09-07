"""Module that provides utilities to the project.

It includes functions to handle common tasks such as sending HTTP requests, parsing
HTML, creating download directories, and clearing the terminal, making it reusable
across projects.
"""

from __future__ import annotations

import logging
import os
import re
import sys
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from .config import DOWNLOAD_FOLDER, HTTPStatus


def fetch_page(
    url: str,
    cookies: dict[str, str] | None = None,
    timeout: int = 10,
) -> BeautifulSoup | None:
    """Fetch the HTML content of a webpage."""
    # Create a new session per worker
    session = requests.Session()

    try:
        response = session.get(url, cookies=cookies, timeout=timeout)
        if response.status_code in (HTTPStatus.NOT_FOUND, HTTPStatus.GONE):
            log_message = f"Page not found or permanently removed: {url}"
            logging.warning(log_message)
            return None

        response.raise_for_status()

    except requests.RequestException as req_err:
        message = f"Error fetching page {url}: {req_err}"
        logging.exception(message)
        sys.exit(1)

    return BeautifulSoup(response.text, "html.parser")

def sanitize_directory_name(directory_name: str) -> str:
    """Sanitize a given directory name by removing invalid characters.

    Handles the invalid characters specific to Windows, macOS, and Linux.
    """
    invalid_chars_dict = {
        "nt": r'[\\/:*?"<>|]',  # Windows
        "posix": r"[/:]",       # macOS and Linux
    }
    invalid_chars = invalid_chars_dict.get(os.name)
    return re.sub(invalid_chars, "", directory_name)


def create_download_directory(directory_path: str) -> str:
    """Construct a download path for the given title."""
    download_path = Path(DOWNLOAD_FOLDER) / sanitize_directory_name(directory_path)

    try:
        Path(download_path).mkdir(parents=True, exist_ok=True)

    except OSError:
        logging.exception("Error creating 'Downloads' directory")
        sys.exit(1)

    return download_path


def clear_terminal() -> None:
    """Clear the terminal screen based on the operating system."""
    commands = {
        "nt": "cls",       # Windows
        "posix": "clear",  # macOS and Linux
    }

    command = commands.get(os.name)
    if command:
        os.system(command)  # noqa: S605
