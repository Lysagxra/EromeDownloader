"""
This module provides a command-line tool for downloading media file from an
Erome album URL. The script validates the provided album URL, collects links to
the media files, and downloads them to a specified local directory.
"""

import os
import argparse
from urllib.parse import urlparse

import requests
from rich.live import Live

from helpers.progress_utils import create_progress_bar, create_progress_table
from helpers.download_utils import save_file_with_progress, run_in_parallel
from helpers.general_utils import (
    fetch_page, create_download_directory, clear_terminal
)
from helpers.erome_utils import (
    validate_url, extract_profile_name, extract_hostname
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

def download_album(album_url, overall_progress, job_progress, profile=None):
    """
    Collects video and image links from the given album URL and downloads them
    to a local directory.

    Args:
        album_url (str): The URL of the album containing video and image links
                         to be collected and downloaded.
        overall_progress (Progress): A `rich.progress.Progress` object used to
                                      track the overall download progress.
        job_progress (Progress): A `rich.progress.Progress` object used to
                                  track the progress of individual downloads.
        profile (str, optional): The profile identifier. If not provided, the
                                 media is downloaded to a default directory.
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

def download(download_link, download_path, album_url, task_info):
    """
    Downloads a file from the specified URL if it hasn't been downloaded
    already.

    Args:
        download_link (str): The URL from which the file will be downloaded.
        download_path (str): The local directory path where the file will be
                             saved.
        album_url (str, optional): An optional album URL to use as the Referer.
                                   If None, the Referer will be set based on
                                   the hostname.
        task_info (tuple): A tuple containing the progress tracking
                           information:
                           - `job_progress`: The progress bar object.
                           - `task`: The specific task being tracked.
                           - `overall_progress`: The overall progress task 
                             being updated.
    """
    parsed_url = urlparse(download_link)
    file_name = os.path.basename(parsed_url.path)

    hostname = extract_hostname(download_link)
    final_path = os.path.join(download_path, file_name)

    with configure_session(download_link, hostname, album_url) as response:
        save_file_with_progress(response, final_path, task_info)

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

    validated_url = validate_url(args.url)
    profile_name = extract_profile_name(args.profile) if args.profile else None

    overall_progress = create_progress_bar()
    job_progress = create_progress_bar()
    progress_table = create_progress_table(overall_progress, job_progress)

    with Live(progress_table, refresh_per_second=10):
        download_album(
            validated_url, overall_progress, job_progress, profile_name
        )

if __name__ == "__main__":
    main()
