"""Main module of the project.

This module facilitates the downloading of albums by processing profile URLs and
validating album URLs. It provides functionalities for reading and writing URL lists,
handling command-line arguments, and organizing the download workflow.

Usage:
    To run the application, execute the module from the command line, providing
    optional arguments for profile or album URLs.
"""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from downloader import download_album, extract_profile_name, validate_url
from helpers.config import DUMP_FILE, URLS_FILE, parse_arguments
from helpers.file_utils import read_file, write_file
from helpers.general_utils import clear_terminal
from helpers.managers.live_manager import initialize_managers
from helpers.profile_crawler import process_profile_url

if TYPE_CHECKING:
    from argparse import Namespace


def process_urls(urls: list[str], profile_name: str, args: Namespace) -> None:
    """Validate and processes a list of URLs to download items."""
    live_manager = initialize_managers()

    try:
        with live_manager.live:
            for url in urls:
                validated_url = validate_url(url)
                download_album(
                    validated_url,
                    live_manager,
                    profile=profile_name,
                    custom_path=args.custom_path,
                )

            live_manager.stop()

    except KeyboardInterrupt:
        sys.exit(1)


def handle_profile_processing(profile_url: str) -> str | None:
    """Process a profile URL and extracts the profile name."""
    if profile_url:
        process_profile_url(profile_url)
        return extract_profile_name(profile_url)

    return None


def main() -> None:
    """Run the script."""
    # Clear the terminal and profile dump file
    clear_terminal()
    write_file(DUMP_FILE)

    # Parse arguments, determine which file to read, and handle profile processing
    args = parse_arguments()
    file_to_read = DUMP_FILE if args.profile else URLS_FILE
    profile_name = handle_profile_processing(args.profile)

    # Read the content from the determined file, processes the URLs
    urls = [url.strip() for url in read_file(file_to_read) if url.strip()]
    process_urls(urls, profile_name, args)

    # Clear URLs file
    write_file(URLS_FILE)


if __name__ == "__main__":
    main()
