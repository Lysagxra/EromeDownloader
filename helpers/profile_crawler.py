"""
This module provides functionality to extract album links from user profile
pages on erome. It utilizes the BeautifulSoup library for HTML parsing and
requests for handling HTTP requests.

Dependencies:
- requests: To handle HTTP requests and responses.
- BeautifulSoup (from bs4): For parsing HTML and extracting data.

Usage:
Run the script from the command line, providing the profile page URL as an
argument:
    python profile_crawler.py <profile_page_url>

Example:
    python profile_crawler.py https://www.erome.com/marieanita
"""

import sys
import re
import requests
from bs4 import BeautifulSoup

DUMP_FILE = "profile_dump.txt"
HOST_PAGE = "https://www.erome.com"

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

def fetch_profile_page(url):
    """
    Fetches the profile page and returns its BeautifulSoup object.

    Args:
        url (str): The URL of the profile page.

    Returns:
        BeautifulSoup: The BeautifulSoup object containing the HTML.

    Raises:
        requests.RequestException: If there is an error with the HTTP request.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')

    except requests.RequestException as req_err:
        print(f"Error fetching the page: {req_err}")
        sys.exit(1)

def get_profile_page_links(soup, profile, next_page_tag="?page="):
    """
    Extracts and formats profile page links from a BeautifulSoup object.

    Parameters:
    soup (BeautifulSoup): The BeautifulSoup object representing the HTML content
                          to search through.
    profile (str): The profile identifier to match in the URL path.

    Returns:
    list: A list of formatted profile page links as strings.
          If no links are found, an empty list is returned.
    """
    try:
        # Regular expression to find all 'a' tags with href that match
        # "?page=" followed by a number
        page_links = soup.find_all(
            'a', {'href': re.compile(f"/{profile}\\{next_page_tag}\\d+")}
        )

        page_numbers = []
        for page_link in page_links:
            try:
                # Extract page number using regex and convert to integer
                page_number = int(
                    re.search(r'page=(\d+)', page_link['href']).group(1)
                )
                page_numbers.append(page_number)

            except (AttributeError, ValueError, TypeError) as err:
                print(f"Error extracting page index from: {page_link['href']}.")
                print(f"Error: {err}")

        max_page_number = max(page_numbers) if page_numbers else None

        formatted_page_links = []
        if max_page_number is not None:
            # The last item of the page_links list isn't useful, so it is
            # discarded
            formatted_page_links = [
                HOST_PAGE + page_link['href'] for page_link in page_links[:-1]
            ]

        return formatted_page_links

    except (AttributeError, TypeError, KeyError) as exc:
        print(f"An error occurred while processing the soup: {exc}")
        return []

def extract_album_links_in_page(soup):
    """
    Extracts album links from a BeautifulSoup object representing a webpage.

    Parameters:
    soup (BeautifulSoup): The BeautifulSoup object representing the HTML content
                          to search through.

    Returns:
    list: A list of strings, where each string is a link to an album. If no
          album links are found, an empty list is returned.
    """
    album_links_items = soup.find_all(
        'a', {'class': "album-link", 'href': True}
    )
    album_links = [item['href'] for item in album_links_items]
    return album_links

def get_profile_album_links(page_links):
    """
    Retrieves album links from a list of profile page links.

    Parameters:
    page_links (list): A list of strings representing URLs of profile pages from
                       which to extract album links.

    Returns:
    list: A list of strings, where each string is a link to an album found on
          the profile pages. If no album links are found, an empty list is
          returned.
    """
    profile_album_links = []

    for page_link in page_links:
        soup = fetch_profile_page(page_link)
        album_links = extract_album_links_in_page(soup)
        profile_album_links.extend(album_links)

    return profile_album_links

def generate_profile_dump(profile, profile_album_links):
    """
    Generates a text file containing album links for a specified profile.

    Parameters:
    profile (str): The profile identifier used to name the output file.
    profile_album_links (list): A list of strings, where each string is a link
                                to an album associated with the specified
                                profile.

    Returns:
    None: This function does not return any value. It creates a file in the
          current working directory.
    """
    print(f"\nDumping content for: {COLORS['BOLD']}{profile}{COLORS['END']}")

    with open(DUMP_FILE, 'w', encoding='utf-8') as file:
        file.writelines(album_link + '\n' for album_link in profile_album_links)

    print("[\u2713] Dump file correctly generated.")

def process_profile_url(url):
    """
    Processes a profile URL to fetch and generate a profile dump.

    Args:
        url (str): The URL of the profile to process.

    Raises:
        ValueError: If an error occurs during the extraction of links from the
                    profile page.

    Prints:
        An error message if a ValueError occurs during processing.
    """
    profile = url.split('/')[-1]
    soup = fetch_profile_page(url)

    try:
        page_links = get_profile_page_links(soup, profile)
        page_links.insert(0, url)

        profile_album_links = get_profile_album_links(page_links)
        generate_profile_dump(profile, profile_album_links)

    except ValueError as val_err:
        print(f"Value error: {val_err}")

def main():
    """
    Main function to execute the profile album extraction process.

    This function serves as the entry point for the script. It fetches the
    profile page from a specified URL, extracts all profile page links,
    retrieves album links from those pages, and generates a text file
    containing the album links.
    """
    if len(sys.argv) != 2:
        print("Usage: python profile_crawler.py <profile_page_url>")
        sys.exit(1)

    url = sys.argv[1]
    process_profile_url(url)

if __name__ == '__main__':
    main()
