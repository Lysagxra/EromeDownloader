"""
This module facilitates the downloading of albums by processing profile URLs
and validating album URLs. It provides functionalities for reading and writing
URL lists, handling command-line arguments, and organizing the download
workflow.

Usage:
    To run the application, execute the module from the command line, providing
    optional arguments for profile or album URLs.
"""

from helpers.profile_crawler import process_profile_url
from helpers.file_utils import read_file, write_file
from helpers.general_utils import clear_terminal
from album_downloader import (
    extract_profile_name, validate_url, download_album,
    setup_parser, initialize_managers
)

DEFAULT_FILE = 'URLs.txt'
DUMP_FILE = 'profile_dump.txt'

def process_urls(urls, profile_name):
    """
    Validates and processes a list of URLs to download items.

    Args:
        urls (list): A list of URLs to process.
        profile_name (str): The name of the profile associated with the URLs.
    """
    live_manager = initialize_managers()
    with live_manager.live:
        for url in urls:
            validated_url = validate_url(url)
            download_album(validated_url, live_manager, profile=profile_name)

def handle_profile_processing(profile_url):
    """
    Processes a profile URL and extracts the profile name.

    Args:
        profile_url (str): The URL of the profile to process.

    Returns:
        str: The extracted profile name, or None if the profile URL is not
             provided.
    """
    if profile_url:
        process_profile_url(profile_url)
        return extract_profile_name(profile_url)

    return None

def main():
    """
    Main entry point for the album download processing application.
    """
    clear_terminal()
    write_file(DUMP_FILE)

    parser = setup_parser()
    args = parser.parse_args()

    file_to_read = DUMP_FILE if args.profile else DEFAULT_FILE
    profile_name = handle_profile_processing(args.profile)

    urls = read_file(file_to_read)
    process_urls(urls, profile_name)

    write_file(DEFAULT_FILE)

if __name__ == '__main__':
    main()
