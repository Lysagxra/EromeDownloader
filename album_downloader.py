"""
This module provides a command-line tool for downloading media file from an
Erome album URL. The script validates the provided album URL, collects links to
the media files, and downloads them to a specified local directory.
"""

import os
import sys
import argparse
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse

import requests
from requests.exceptions import HTTPError
from bs4 import BeautifulSoup
from rich.live import Live

from helpers.erome_utils import (
    validate_url, extract_profile_name, extract_hostname
)
from helpers.progress_utils import create_progress_bar, create_progress_table
from helpers.download_utils import save_file_with_progress

DOWNLOAD_FOLDER = "Downloads"

SESSION = requests.Session()
HEADERS = {"User-Agent": "Mozilla/5.0"}
TIMEOUT = 10

MAX_WORKERS = 5
TASK_COLOR = 'light_cyan3'

def extract_download_links(album_url):
    """
    Extracts download links for video and image sources from the specified 
    album URL.

    Args:
        album_url (str): The URL of the album from which to extract media links.

    Returns:
        List[str]: A list of unique download links (video and image URLs)
                   extracted from the album page.

    Raises:
        HTTPError: If the HTTP request to the album URL fails.
    """
    response = SESSION.get(album_url, headers=HEADERS, timeout=TIMEOUT)

    if response.status_code != 200:
        raise HTTPError(f"HTTP error {response.status_code}")

    soup = BeautifulSoup(response.content, "html.parser")
    videos = [video_source["src"] for video_source in soup.find_all("source")]
    images = [
        image["data-src"]
        for image in soup.find_all("img", {"class": "img-back"})
    ]
    return list(set([*videos, *images]))

def manage_running_tasks(futures, job_progress):
    """
    Monitors and manages the status of running tasks.

    Args:
        futures (dict): A dictionary where keys are futures representing 
                        asynchronous tasks and values are task information 
                        to be used for progress updates.
        job_progress: An object responsible for updating the progress of 
                      tasks based on their current status.
    """
    while futures:
        for future in list(futures.keys()):
            if future.running():
                task = futures.pop(future)
                job_progress.update(task, visible=True)

def collect_links(album_url, overall_progress, job_progress, profile=None):
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
    download_path = get_download_path(album_id) if profile is None \
        else get_download_path(os.path.join(profile, album_id))

    num_files = len(download_links)
    futures = {}

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        overall_task = overall_progress.add_task(
            f"[{TASK_COLOR}]{album_id}", total=num_files, visible=True
        )

        for (indx, download_link) in enumerate(download_links):
            task = job_progress.add_task(
                f"[{TASK_COLOR}]File {indx + 1}/{num_files}",
                total=100, visible=False
            )
            future = executor.submit(
                download_album,
                download_link, download_path, album_url,
                (job_progress, task, overall_progress, overall_task)
            )
            futures[future] = task
            manage_running_tasks(futures, job_progress)

def get_download_path(title):
    """
    Constructs a download path for the given title and ensures that the
    directory exists.

    Args:
        title (str): The title or album ID to use as the folder name.

    Returns:
        str: The full download path where files will be saved.
    """
    download_path = os.path.join(DOWNLOAD_FOLDER, title)

    try:
        os.makedirs(download_path, exist_ok=True)
        return download_path

    except OSError as os_err:
        print(f"Error creating directory: {os_err}")
        sys.exit(1)

def configure_session_request(url, hostname, album):
    """
    Configures and sends a GET request using the global SESSION object.

    Args:
        url (str): The URL to which the GET request will be sent.
        hostname (str): The hostname to be used in the Referer and Origin
                        headers.
        album (str, optional): An optional album URL to use as the Referer.
                               If None, the Referer will be set to the hostname.

    Returns:
        Response: The response object from the GET request, enabling
        streaming of the response content.
    """
    return SESSION.get(
        url,
        stream=True,
        headers={
            "Referer": f"https://{hostname}" if album is None else album,
            "Origin": f"https://{hostname}",
            "User-Agent": "Mozila/5.0",
        },
        timeout=TIMEOUT
    )

def download_album(url, download_path, album, task_info):
    """
    Downloads a file from the specified URL if it hasn't been downloaded
    already.

    Args:
        url (str): The URL from which the file will be downloaded.
        download_path (str): The local directory path where the file will be
                             saved.
        album (str, optional): An optional album URL to use as the Referer.
                               If None, the Referer will be set based on the
                               hostname.
    Returns:
        None: The function performs the download and does not return a value.
    """
    parsed_url = urlparse(url)
    file_name = os.path.basename(parsed_url.path)

    hostname = extract_hostname(url)
    final_path = os.path.join(download_path, file_name)

    with configure_session_request(url, hostname, album) as response:
        save_file_with_progress(response, final_path, task_info)

def main():
    """
    Main function that parses command-line arguments and initiates the
    download process by calling collect_links().
    """
    parser = argparse.ArgumentParser(sys.argv[1:])
    parser.add_argument("-u", help="URL to download", type=str, required=True)
    parser.add_argument(
        "-p", help="Profile to download (optional)", type=str, required=False
    )

    args = parser.parse_args()

    validated_url = validate_url(args.u)
    profile_name = extract_profile_name(args.p) if args.p else None

    overall_progress = create_progress_bar()
    job_progress = create_progress_bar()
    progress_table = create_progress_table(overall_progress, job_progress)

    with Live(progress_table, refresh_per_second=10):
        collect_links(
            validated_url, overall_progress, job_progress, profile_name
        )

if __name__ == "__main__":
    main()
