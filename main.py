"""
This module facilitates the downloading of albums by processing profile URLs and 
validating album URLs. It provides functionalities for reading and writing 
URL lists, handling command-line arguments, and organizing the download
workflow.

Key Features:
    - Read and write URL lists to/from files.
    - Validate and process profile URLs to generate profile dumps.
    - Collect links associated with valid album URLs.
    - Command-line interface for user interaction.

Usage:
To run the application, execute the module from the command line, providing 
optional arguments for profile or album URLs.
"""

import argparse

from helpers.profile_crawler import process_profile_url
from helpers.album_downloader import (
    extract_profile_name,
    validate_url,
    collect_links
)

DEFAULT_FILE = 'URLs.txt'
DUMP_FILE = 'profile_dump.txt'

def read_file(filename):
    """
    Reads the contents of a file and returns a list of its lines.

    Args:
        filename (str): The path to the file to be read.

    Returns:
        list: A list of lines from the file, with newline characters removed.
    """
    with open(filename, 'r', encoding='utf-8') as file:
        return file.read().splitlines()

def write_file(filename, content=''):
    """
    Writes content to a specified file. If content is not provided, the file is
    cleared.

    Args:
        filename (str): The path to the file to be written to.
        content (str, optional): The content to write to the file. Defaults to
                                 an empty string.
    """
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(content)

def process_urls(urls, profile_name):
    """
    Validates and processes a list of URLs to download items.

    Args:
        urls (list): A list of URLs to process.
        profile_name (str): The name of the profile associated with the URLs.

    Raises:
        ValueError: If any URL is invalid during validation.
    """
    for url in urls:
        validated_url = validate_url(url)
        collect_links(validated_url, profile_name)

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

    Raises:
        FileNotFoundError: If the specified files cannot be read or written.
        ValueError: If processing the profile or URLs encounters an error.
    """
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
