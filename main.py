"""Main module of the project.

This module facilitates the downloading of albums by processing profile URLs
and validating album URLs. It provides functionalities for reading and writing
URL lists, handling command-line arguments, and organizing the download
workflow.

Usage:
    To run the application, execute the module from the command line, providing
    optional arguments for profile or album URLs.
"""

from __future__ import annotations

from album_downloader import (
    download_album,
    extract_profile_name,
    initialize_managers,
    setup_parser,
    validate_url,
)
from helpers.config import (
    DUMP_FILE,
)
from helpers.config import (
    FILE as DEFAULT_FILE,
)
from helpers.file_utils import read_file, write_file
from helpers.general_utils import clear_terminal
from helpers.profile_crawler import process_profile_url


def process_urls(urls: list[str], profile_name: str) -> None:
    """Validate and processes a list of URLs to download items."""
    live_manager = initialize_managers()
    with live_manager.live:
        for url in urls:
            validated_url = validate_url(url)
            download_album(validated_url, live_manager, profile=profile_name)

        live_manager.stop()


def handle_profile_processing(profile_url: str) -> str | None:
    """Process a profile URL and extracts the profile name."""
    if profile_url:
        process_profile_url(profile_url)
        return extract_profile_name(profile_url)

    return None


def main() -> None:
    """Run the script."""
    clear_terminal()
    write_file(DUMP_FILE)

    parser = setup_parser()
    args = parser.parse_args()

    file_to_read = DUMP_FILE if args.profile else DEFAULT_FILE
    profile_name = handle_profile_processing(args.profile)

    urls = read_file(file_to_read)
    process_urls(urls, profile_name)

    write_file(DEFAULT_FILE)


if __name__ == "__main__":
    main()
