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
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
import tldextract
from rich.progress import (
    Progress,
    SpinnerColumn,
    BarColumn,
    DownloadColumn,
    TextColumn,
    TransferSpeedColumn,
    TimeRemainingColumn
)

DOWNLOAD_FOLDER = "Downloads"

HOST_NAME = "www.erome.com"
CHUNK_SIZE = 1024
SESSION = requests.Session()

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
            validated_url = f"https://{HOST_NAME}{parsed_url.path}"
            return validated_url

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

def collect_links(album_url, profile=None):
    """
    Collects video and image links from the given album URL and downloads them
    to a local directory.

    The function validates the provided URL, sends an HTTP GET request to
    retrieve the content, parses it to extract video and image URLs, and then
    downloads the media files if they are not already in the target download
    directory.

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
    response = SESSION.get(album_url, headers={"User-Agent": "Mozilla/5.0"})

    if response.status_code != 200:
        raise Exception(f"HTTP error {response.status_code}")

    soup = BeautifulSoup(response.content, "html.parser")
    videos = [video_source["src"] for video_source in soup.find_all("source")]
    images = [
        image["data-src"]
        for image in soup.find_all("img", {"class": "img-back"})
    ]
    urls = list(set([*videos, *images]))

    album_id = album_url.split('/')[-1]
    download_path = get_download_path(album_id) if profile is None \
        else get_download_path(os.path.join(profile, album_id))
    existing_files = get_files_in_dir(download_path)

    print(f"\nDownloading Album: {COLORS['BOLD']}{album_id}{COLORS['END']}")

    for file_url in urls:
        download(file_url, download_path, album_url, existing_files)

    print("\t[\u2713] Download complete.")

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

    if not os.path.isdir(download_path):
        os.makedirs(download_path)

    return download_path

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

def progress_bar():
    """
    Creates and returns a progress bar for tracking download progress.

    Returns:
        Progress: A Progress object configured with relevant columns.
    """
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        DownloadColumn(),
        "-",
        TransferSpeedColumn(),
        "-",
        TimeRemainingColumn(),
        transient=True
    )

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
        headers={
            "Referer": f"https://{hostname}" if album is None else album,
            "Origin": f"https://{hostname}",
            "User-Agent": "Mozila/5.0",
        },
        stream=True,
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
    return "{}.{}".format(extracted.domain, extracted.suffix)

def handle_response(url, response, download_path):
    """
    Handles the HTTP response for a file download.

    If the response indicates success (status code 200),
    the function reads the response content in chunks and writes
    it to the specified download path while displaying a progress bar.

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
        total_size = int(response.headers.get("content-length", 0))

        with progress_bar() as pbar:
            task = pbar.add_task("[cyan]Progress:", total=total_size)

            with open(download_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                    file.write(chunk)
                    pbar.update(task, advance=len(chunk))
    else:
        print(response)
        print(f'\t[#] Download of "{url}" failed.')
        return

def download(url, download_path, album, existing_files):
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
        existing_files (list): A list of filenames that have already been
                               downloaded.

    Returns:
        None: The function performs the download and does not return a value.
    """
    parsed_url = urlparse(url)
    file_name = os.path.basename(parsed_url.path)

    if file_name in existing_files:
        print(f'\t[#] Skipping {file_name} [already downloaded]')
        return

    print(f"\t[+] Downloading {file_name}...")

    hostname = extract_hostname(url)
    final_path = os.path.join(download_path, file_name)

    with configure_session_request(url, hostname, album) as response:
        handle_response(url, response, final_path)

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
    collect_links(validated_url, profile_name)

if __name__ == "__main__":
    main()
