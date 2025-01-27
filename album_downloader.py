"""
This module provides a command-line tool for downloading media file from an
Erome album URL. The script validates the provided album URL, collects links to
the media files, and downloads them to a specified local directory.
"""

import os
import argparse
from urllib.parse import urlparse

import requests

from helpers.managers.live_manager import LiveManager
from helpers.managers.log_manager import LoggerTable
from helpers.managers.progress_manager import ProgressManager

from helpers.download_utils import (
    save_file_with_progress,
    run_in_parallel
)
from helpers.general_utils import (
    fetch_page,
    create_download_directory,
    clear_terminal
)
from helpers.erome_utils import (
    validate_url,
    extract_profile_name,
    extract_hostname
)

def extract_download_links(album_url):
    """
    Extracts download links for video and image sources from the specified 
    album URL.

    Args:
        album_url (str): The URL of the album from which to extract media
                         links.

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

def download_album(album_url, live_manager, profile=None):
    """
    Downloads an album from the given URL.

    Args:
        album_url (str): The URL of the album to be downloaded.
        live_manager (LiveManager): A manager for handling live download
                                    operations, such as progress tracking or
                                    concurrent downloads.
        profile (str): A path to a user-specific profile directory where the
                       album should be saved. If None, the album is saved in
                       the default location.
    """
    download_links = extract_download_links(album_url)

    album_id = album_url.split('/')[-1]
    album_path = album_id if not profile else os.path.join(profile, album_id)
    download_path = create_download_directory(album_path)

    run_in_parallel(
        download,
        download_links, live_manager,
        album_id, download_path, album_url
    )

def configure_session(
    url, hostname, album_url=None, timeout=10, read_timeout=20
):
    """
    Configures a GET request with custom headers and timeouts using a global
    SESSION object, and sends the request to the specified URL.

    Args:
        url (str): The URL to which the GET request will be sent.
        hostname (str): The hostname to be used in the `Referer` and `Origin`
                        headers.
        album_url (str, optional): An optional URL of the album to use as the
                                   `Referer` header. If not provided, the 
                                   `Referer` will default to the base URL 
                                   formed from the `hostname`.
        timeout (int, optional): The connection timeout value in seconds
                                 (default is 10).
        read_timeout (int, optional): The timeout value for the read operation
                                      in seconds (default is 20).

    Returns:
        Response: The response object from the GET request, which contains the
                  server's response to the HTTP request.
    """
    return requests.Session().get(
        url,
        stream=True,
        headers={
            "Referer": f"https://{hostname}" if not album_url else album_url,
            "Origin": f"https://{hostname}",
            "User-Agent": "Mozila/5.0",
            "Connection": "keep-alive"
        },
        timeout=(timeout, read_timeout)
    )

def download(download_link, task, live_manager, download_path, album_url):
    """
    Downloads a file from the specified download link and saves it to the given
    path.

    Args:
        download_link (str): The URL of the file to be downloaded.
        task (int): The ID of the current download task, used to track progress
                    and completion.
        live_manager (LiveManager): A manager responsible for handling live
                                    updates, such as download progress.
        download_path (str): The local path where the downloaded file should be
                             saved.
        album_url (str): The URL of the album, used to configure the session or
                         for additional context.
    """
    parsed_url = urlparse(download_link)
    file_name = os.path.basename(parsed_url.path)

    hostname = extract_hostname(download_link)
    final_path = os.path.join(download_path, file_name)

    with configure_session(download_link, hostname, album_url) as response:
        save_file_with_progress(response, final_path, task, live_manager)

def initialize_managers():
    """
    Initializes and returns the managers for progress tracking and logging.

    Returns:
        LiveManager: Handles the live display of progress and logs.
    """
    progress_manager = ProgressManager(
        task_name = "Album",
        item_description="File"
    )
    logger_table = LoggerTable()
    return LiveManager(progress_manager, logger_table)

def setup_parser():
    """
    Sets up the command-line argument parser for album download processing.

    Returns:
        argparse.ArgumentParser: The configured argument parser instance.
    """
    parser = argparse.ArgumentParser(description='Process album downloads.')
    parser.add_argument(
        '-p', '--profile', dest='profile', type=str, metavar='profile_url',
        help='Generate the profile dump file from the specified profile URL'
    )
    parser.add_argument(
        '-u', '--url', dest='url', type=str, metavar='album_url',
        help='Album URL to process'
    )
    return parser

def main():
    """
    Main function that parses command-line arguments and initiates the
    download process.
    """
    clear_terminal()
    parser = setup_parser()
    args = parser.parse_args()

    live_manager = initialize_managers()
    validated_url = validate_url(args.url)
    profile_name = extract_profile_name(args.profile) if args.profile else None

    with live_manager.live:
        download_album(validated_url, live_manager, profile_name)
        live_manager.stop()

if __name__ == "__main__":
    main()
