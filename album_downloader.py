"""
This module provides a command-line tool for downloading media file from an
Erome album URL. The script validates the provided album URL, collects links to
the media files, and downloads them to a specified local directory.
"""

import os
import sys
import argparse
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from rich.live import Live

from helpers.erome_utils import (
    validate_url, extract_profile_name, extract_hostname
)
from helpers.progress_utils import create_progress_bar, create_progress_table
from helpers.download_utils import save_file_with_progress, run_in_parallel

DOWNLOAD_FOLDER = "Downloads"

SESSION = requests.Session()
HEADERS = {"User-Agent": "Mozilla/5.0"}
TIMEOUT = 10

def fetch_page(url):
    """
    Fetches the HTML content of a page at the given URL.

    Args:
        url (str): The URL to fetch.

    Returns:
        BeautifulSoup: Parsed HTML content of the page.

    Raises:
        requests.RequestException: If there are issues with the request.
    """
    try:
        response = SESSION.get(url, headers=HEADERS, timeout=TIMEOUT)
        response.raise_for_status()
        return BeautifulSoup(response.content, "html.parser")

    except requests.RequestException as req_err:
        print(f"Request error: {req_err}")
        return None

def extract_download_links(album_url):
    """
    Extracts download links for video and image sources from the specified 
    album URL.

    Args:
        album_url (str): The URL of the album from which to extract media links.

    Returns:
        List[str]: A list of unique download links (video and image URLs)
                   extracted from the album page.
    """
    soup = fetch_page(album_url)
    videos = [video_source["src"] for video_source in soup.find_all("source")]
    images = [
        image["data-src"]
        for image in soup.find_all("img", {"class": "img-back"})
    ]
    return list(set([*videos, *images]))

def download_album(album_url, overall_progress, job_progress, profile=None):
    """
    Collects video and image links from the given album URL and downloads them
    to a local directory.

    Args:
        album_url (str): The URL of the album from which video and image links
                         are to be collected.
        profile (str, optional): The profile identifier to use for additional
                                 context.

    Returns:
        int: The number of media files successfully downloaded.
    """
    download_links = extract_download_links(album_url)

    album_id = album_url.split('/')[-1]
    album_path = album_id if not profile else os.path.join(profile, album_id)
    download_path = create_download_directory(album_path)

    run_in_parallel(
        download, download_links,
        (job_progress, overall_progress),
        album_id, download_path, album_url
    )

def create_download_directory(album_path):
    """
    Constructs a download path for the given title and ensures that the
    directory exists.

    Args:
        album_path (str): The title or album ID to use as the folder name.

    Returns:
        str: The full download path where files will be saved.
    """
    download_path = os.path.join(DOWNLOAD_FOLDER, album_path)

    try:
        os.makedirs(download_path, exist_ok=True)
        return download_path

    except OSError as os_err:
        print(f"Error creating directory: {os_err}")
        sys.exit(1)

def configure_session(url, hostname, album_url, read_timeout=20):
    """
    Configures and sends a GET request using the global SESSION object.

    Args:
        url (str): The URL to which the GET request will be sent.
        hostname (str): The hostname to be used in the Referer and Origin
                        headers.
        album_url (str, optional): An optional album URL to use as the Referer.
                                   If None, the Referer will be set to the 
                                   hostname.

    Returns:
        Response: The response object from the GET request, enabling
        streaming of the response content.
    """
    return SESSION.get(
        url,
        stream=True,
        headers={
            "Referer": f"https://{hostname}" if not album_url else album_url,
            "Origin": f"https://{hostname}",
            "User-Agent": "Mozila/5.0",
        },
        timeout=(TIMEOUT, read_timeout)
    )

def download(download_link, download_path, album_url, task_info):
    """
    Downloads a file from the specified URL if it hasn't been downloaded
    already.

    Args:
        download_link (str): The URL from which the file will be downloaded.
        download_path (str): The local directory path where the file will be
                             saved.
        album_url (str, optional): An optional album URL to use as the Referer.
                                   If None, the Referer will be set based on the
                                   hostname.
    """
    parsed_url = urlparse(download_link)
    file_name = os.path.basename(parsed_url.path)

    hostname = extract_hostname(download_link)
    final_path = os.path.join(download_path, file_name)

    with configure_session(download_link, hostname, album_url) as response:
        save_file_with_progress(response, final_path, task_info)

def clear_terminal():
    """
    Clears the terminal screen based on the operating system.
    """
    options = {
        'nt': 'cls',      # Windows
        'posix': 'clear'  # macOS and Linux
    }

    command = options.get(os.name)
    if command:
        os.system(command)

def main():
    """
    Main function that parses command-line arguments and initiates the
    download process.
    """
    parser = argparse.ArgumentParser(sys.argv[1:])
    parser.add_argument("-u", help="URL to download", type=str, required=True)
    parser.add_argument(
        "-p", help="Profile to download (optional)", type=str, required=False
    )

    clear_terminal()
    args = parser.parse_args()

    validated_url = validate_url(args.u)
    profile_name = extract_profile_name(args.p) if args.p else None

    overall_progress = create_progress_bar()
    job_progress = create_progress_bar()
    progress_table = create_progress_table(overall_progress, job_progress)

    with Live(progress_table, refresh_per_second=10):
        download_album(
            validated_url, overall_progress, job_progress, profile_name
        )

if __name__ == "__main__":
    main()
