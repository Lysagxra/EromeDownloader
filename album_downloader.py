"""Module that provides a command-line tool for downloading from an Erome album URL.

The script validates the provided album URL, collects links to the media files, and
downloads them to a specified local directory.
"""

from __future__ import annotations

import argparse
from argparse import ArgumentParser
from pathlib import Path
from typing import TYPE_CHECKING
from urllib.parse import urlparse

import requests

from helpers.download_utils import run_in_parallel, save_file_with_progress
from helpers.erome_utils import extract_hostname, extract_profile_name, validate_url
from helpers.general_utils import clear_terminal, create_download_directory, fetch_page
from helpers.managers.live_manager import LiveManager
from helpers.managers.log_manager import LoggerTable
from helpers.managers.progress_manager import ProgressManager

if TYPE_CHECKING:
    from requests.models import Response


def extract_download_links(album_url: str) -> list[str] | None:
    """Extract download links for video and image sources from the album URL."""
    soup = fetch_page(album_url)
    if soup is None:
        return None

    videos = [
        video_source["src"] for video_source in soup.find_all("source")
    ]
    images = [
        image["data-src"] for image in soup.find_all("img", {"class": "img-back"})
    ]
    return list({*videos, *images})


def download_album(
    album_url: str,
    live_manager: LiveManager,
    profile: str | None = None,
) -> None:
    """Download an album from the given URL."""
    album_id = album_url.rstrip("/").split("/")[-1]
    album_path = album_id if not profile else Path(profile) / album_id
    download_path = create_download_directory(album_path)

    download_links = extract_download_links(album_url)
    if download_links is None:
        return

    run_in_parallel(
        download, download_links, live_manager, album_id, download_path, album_url,
    )


def configure_session(
    url: str,
    hostname: str,
    album_url: str | None = None,
    timeout: int = 10,
    read_timeout: int = 20,
) -> Response:
    """Configure a request using a global session."""
    origin_url = f"https://{hostname}"
    return requests.Session().get(
        url,
        stream=True,
        headers={
            "Referer": album_url if album_url else origin_url,
            "Origin": origin_url,
            "User-Agent": "Mozila/5.0",
            "Connection": "keep-alive",
        },
        timeout=(timeout, read_timeout),
    )


def download(
    download_link: str,
    task: int,
    live_manager: LiveManager,
    download_path: str,
    album_url: str,
) -> None:
    """Download a file from the specified download link."""
    parsed_url = urlparse(download_link)
    file_name = Path(parsed_url.path).name

    hostname = extract_hostname(download_link)
    final_path = Path(download_path) / file_name

    with configure_session(download_link, hostname, album_url) as response:
        save_file_with_progress(response, final_path, task, live_manager)


def initialize_managers() -> LiveManager:
    """Initialize and returns the managers for progress tracking and logging."""
    progress_manager = ProgressManager(task_name="Album", item_description="File")
    logger_table = LoggerTable()
    return LiveManager(progress_manager, logger_table)


def setup_parser() -> ArgumentParser:
    """Set up the command-line argument parser for album download processing."""
    parser = argparse.ArgumentParser(description="Process album downloads.")
    parser.add_argument(
        "-p",
        "--profile",
        dest="profile",
        type=str,
        metavar="profile_url",
        help="Generate the profile dump file from the specified profile URL",
    )
    parser.add_argument(
        "-u",
        "--url",
        dest="url",
        type=str,
        metavar="album_url",
        help="Album URL to process",
    )
    return parser.parse_args()


def main() -> None:
    """Initiate the download process."""
    clear_terminal()
    args = setup_parser()

    live_manager = initialize_managers()
    validated_url = validate_url(args.url)
    profile_name = extract_profile_name(args.profile) if args.profile else None

    with live_manager.live:
        download_album(validated_url, live_manager, profile_name)
        live_manager.stop()


if __name__ == "__main__":
    main()
