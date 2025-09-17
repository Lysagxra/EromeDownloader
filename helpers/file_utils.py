"""Module that provides utility functions for file input and output operations.

It includes methods to read the contents of a file and to write content to a file, with
optional support for clearing the file.
"""

from __future__ import annotations

import logging
import os
import re
import sys
from pathlib import Path

from .config import DOWNLOAD_FOLDER


def read_file(filename: str) -> list[str]:
    """Read the contents of a file and returns a list of its lines."""
    with Path(filename).open("r", encoding="utf-8") as file:
        return file.read().splitlines()


def write_file(filename: str, content: str = "") -> None:
    """Write content to a specified file.

    If content is not provided, the file is cleared.
    """
    with Path(filename).open("w", encoding="utf-8") as file:
        file.write(content)


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


def create_download_directory(
    directory_name: str,
    custom_path: str | None = None,
) -> str:
    """Create a directory for downloads if it doesn't exist."""
    # Sanitizing the directory name (album ID), if provided
    sanitized_directory_name = (
        sanitize_directory_name(directory_name) if directory_name else None
    )

    # Determine the base download path.
    base_path = (
        Path(custom_path) / DOWNLOAD_FOLDER if custom_path else Path(DOWNLOAD_FOLDER)
    )

    # Albums containing a single file will be directly downloaded into the 'Downloads'
    # folder, without creating a subfolder for the album ID.
    download_path = (
        base_path / sanitized_directory_name if sanitized_directory_name else base_path
    )

    # Create the directory if it doesn't exist
    try:
        download_path.mkdir(parents=True, exist_ok=True)

    except OSError as os_err:
        log_message = f"Error creating 'Downloads' directory: {os_err}"
        logging.exception(log_message)
        sys.exit(1)

    return str(download_path)
