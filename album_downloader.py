"""
This module provides a command-line tool for downloading media file from an
Erome album URL. The script validates the provided album URL, collects links to
the media files, and downloads them to a specified local directory.

Dependencies:
    - argparse: For parsing command-line arguments.
    - requests: For making HTTP requests.
    - bs4 (BeautifulSoup): For parsing HTML content.
    - tldextract: For extracting the domain and subdomain from URLs.
    - rich: For creating rich progress bar.
"""

import os
import sys
import re
import argparse
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse
import requests
from requests.exceptions import HTTPError
from bs4 import BeautifulSoup
import tldextract
from rich.live import Live

from helpers.progress_utils import create_progress_bar, create_progress_table

HOST_NAME = "www.erome.com"
DOWNLOAD_FOLDER = "Downloads"
SESSION = requests.Session()
HEADERS = {"User-Agent": "Mozilla/5.0"}

MAX_WORKERS = 5
CHUNK_SIZE = 4096
TASK_COLOR = 'light_cyan3'

COLORS = {
    'PURPLE': '\033[95m',
    'CYAN': '\033[96m',
    'DARKCYAN': '\033[36m',
    'BLUE': '\033[94m',
    'GREEN': '\033[92m',
    'YELLOW': '\033[93m',
    'RED': '\033[91m',
    'BOLD': '\033[1m',
    'UNDERLINE': '\033[4m',
    'END': '\033[0m'
}

def validate_url(album_url):
    """
    Validate and normalize an Erome album URL.

    Args:
        album_url (str): The Erome album URL to be validated.

    Returns:
        str: The normalized URL using the global domain (`HOST_NAME`).

    Raises:
        SystemExit: If the provided URL is not a valid Erome domain.
    """
    parsed_url = urlparse(album_url)

    regions = [
        "cn", "cz", "de", "es", "fr", "it", "nl", "jp", "pt", "pl", "rt"
    ]

    if parsed_url.netloc == HOST_NAME:
        return album_url

    for region in regions:
        if parsed_url.netloc == region + ".erome.com":
            return f"https://{HOST_NAME}{parsed_url.path}"

    print("Provide a valid Erome URL.")
    sys.exit(1)

def extract_profile_name(profile_url):
    """
    Extracts the profile name from the given profile URL.

    Args:
        profile_url (str): The URL from which to extract the profile name.

    Returns:
        str: The extracted profile name.

    Raises:
        SystemExit: If the provided URL is invalid, the function prints an error
                    message and exits the program.
    """
    try:
        return profile_url.split('/')[-1]
    except IndexError:
        print("Invalid profile URL.")
        sys.exit(1)

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
    response = SESSION.get(album_url, headers=HEADERS)

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

    Raises:
        Exception: If the hostname of the album URL does not match the
                   expected `HOST_NAME`.
        Exception: If the HTTP request to the album URL fails.
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

def clean_title(title, default_title="temp"):
    """
    Cleans the given title by replacing illegal characters with underscores and
    stripping trailing dots or spaces.

    Args:
        title (str): The original title to be cleaned.
        default_title (str, optional): The default title to return if the
                                       cleaned title is empty.

    Returns:
        str: The cleaned title, or the default title if the cleaned title is
             empty.
    """
    illegal_chars = r'[\\/:*?"<>|]'
    title = re.sub(illegal_chars, '_', title)
    title = title.strip('. ')
    return title if title else default_title

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

def get_files_in_dir(directory):
    """
    Retrieves a list of all files in the given directory.

    Args:
        directory (str): The path to the directory from which to list files.

    Returns:
        List[str]: A list of filenames in the directory.
    """
    return [
        file for file in os.listdir(directory)
        if os.path.isfile(os.path.join(directory, file))
    ]

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
        timeout=10
    )

def extract_hostname(url):
    """
    Extracts the hostname from the given URL.

    Args:
        url (str): The URL from which to extract the hostname.

    Returns:
        str: The extracted hostname in the format 'domain.suffix'.
    """
    extracted = tldextract.extract(url)
    return f"{extracted.domain}.{extracted.suffix}"

def handle_response(url, response, download_path, task_info):
    """
    Handles the HTTP response for a file download.

    Args:
        response (Response): The HTTP response object containing the file data.
        download_path (str): The local file path where the content should be
                             saved.

    Returns:
        None: The function performs file writing and does not return a value.

    Raises:
        IOError: If there is an issue writing to the specified download path.
    """
    if response.ok:
        (job_progress, task, overall_progress, overall_task) = task_info
        file_size = int(response.headers.get("content-length", -1))
        total_downloaded = 0

        with open(download_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                if chunk:
                    file.write(chunk)
                    total_downloaded += len(chunk)
                    progress_percentage = (total_downloaded / file_size) * 100
                    job_progress.update(task, completed=progress_percentage)

        job_progress.update(task, completed=100, visible=False)
        overall_progress.advance(overall_task)

    else:
        print(f'\t[#] Download of "{url}" failed.')

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

#    if file_name in existing_files:
#        print(f'\t[#] Skipping {file_name} [already downloaded]')
#        return

    hostname = extract_hostname(url)
    final_path = os.path.join(download_path, file_name)

    with configure_session_request(url, hostname, album) as response:
        handle_response(url, response, final_path, task_info)

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
