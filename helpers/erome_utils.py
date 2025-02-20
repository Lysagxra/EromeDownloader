"""Module that provides functions for validating and processing Erome album URLs."""

from __future__ import annotations

import logging
import sys
from urllib.parse import urlparse

from .config import HOST_NETLOC


def validate_url(album_url: str) -> str:
    """Validate and normalize an Erome album URL."""
    parsed_url = urlparse(album_url)
    regions = [
        "cn", "cz", "de", "es", "fr", "it", "nl", "jp", "pt", "pl", "rt",
    ]

    if parsed_url.netloc == HOST_NETLOC:
        return album_url

    for region in regions:
        if parsed_url.netloc == region + ".erome.com":
            return f"https://{HOST_NETLOC}{parsed_url.path}"

    logging.error("Provide a valid Erome URL.")
    return None


def extract_profile_name(profile_url: str) -> str | None:
    """Extract the profile name from the given profile URL."""
    try:
        return profile_url.split("/")[-1]

    except IndexError:
        logging.exception("Invalid profile URL.")
        sys.exit(1)

    return None


def extract_hostname(url: str) -> str:
    """Extract the hostname from the given URL."""
    parsed_url = urlparse(url)
    return parsed_url.netloc
