"""
This module provides functions for validating and processing Erome album URLs,
as well as extracting relevant information such as profile names and hostnames.
"""

import sys
from urllib.parse import urlparse

from .config import HOST_NETLOC

def validate_url(album_url):
    """
    Validate and normalize an Erome album URL.

    Args:
        album_url (str): The Erome album URL to be validated.

    Returns:
        str: The normalized URL using the global domain (`HOST_NETLOC`).
    """
    parsed_url = urlparse(album_url)
    regions = [
        "cn", "cz", "de", "es", "fr", "it", "nl", "jp", "pt", "pl", "rt"
    ]

    if parsed_url.netloc == HOST_NETLOC:
        return album_url

    for region in regions:
        if parsed_url.netloc == region + ".erome.com":
            return f"https://{HOST_NETLOC}{parsed_url.path}"

    print("Provide a valid Erome URL.")
    return None

def extract_profile_name(profile_url):
    """
    Extracts the profile name from the given profile URL.

    Args:
        profile_url (str): The URL from which to extract the profile name.

    Returns:
        str: The extracted profile name.

    Raises:
        SystemExit: If the provided URL is invalid, the function prints an
                    error message and exits the program.
    """
    try:
        return profile_url.split('/')[-1]

    except IndexError:
        print("Invalid profile URL.")
        sys.exit(1)

    return None

def extract_hostname(url):
    """
    Extracts the hostname from the given URL.

    Args:
        url (str): The URL from which to extract the hostname.

    Returns:
        str: The extracted hostname.
    """
#    extracted = tldextract.extract(url)
#    return f"{extracted.domain}.{extracted.suffix}"
    parsed_url = urlparse(url)
    return parsed_url.netloc
