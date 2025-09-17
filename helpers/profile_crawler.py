"""Profile crawler module.

This module provides functionality to extract album links from user profile pages on
erome. It utilizes the BeautifulSoup library for HTML parsing and requests for handling
HTTP requests.

Usage:
    Run the script from the command line, providing the profile page URL as an
    argument:
        python profile_crawler.py <profile_page_url>

Example:
    python profile_crawler.py https://www.erome.com/marieanita

"""

from __future__ import annotations

import logging
import re
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from rich.console import Console

from .config import DUMP_FILE, HOST_PAGE
from .general_utils import fetch_page
from .managers.progress_manager import create_progress_bar

if TYPE_CHECKING:
    from bs4 import BeautifulSoup


def extract_page_number(page_link: dict[str, str]) -> int | None:
    """Extract the page number from a URL."""
    page_pattern = r"page=(\d+)"

    try:
        match = re.search(page_pattern, page_link["href"])
        return int(match.group(1))

    except (AttributeError, ValueError, TypeError) as err:
        message = f"Error extracting page index from {page_link['href']}: {err}"
        logging.exception(message)
        return None


def get_profile_page_links(
    soup: BeautifulSoup,
    profile: str,
) -> list[str]:
    """Extract and  profile page links from a BeautifulSoup object."""
    try:
        # Regular expression to find all 'a' tags with href that match "?page="
        # followed by a number
        page_links = soup.find_all(
            "a",
            {"href": re.compile(f"/{profile}\\?page=\\d+")},
        )

    except (AttributeError, TypeError, KeyError) as err:
        message = f"An error occurred while processing the soup: {err}"
        logging.exception(message)
        return []

    page_numbers = [extract_page_number(page_link) for page_link in page_links]
    max_page_number = max(page_numbers) if page_numbers else None

    formatted_page_links = []
    if max_page_number is not None:
        # The last item of the page_links list isn't useful, so it is discarded
        formatted_page_links = [
            HOST_PAGE + page_link.get("href") for page_link in page_links[:-1]
        ]

    return formatted_page_links


def extract_album_links_in_page(soup: BeautifulSoup) -> list[str]:
    """Extract album links from a BeautifulSoup object representing a webpage."""
    album_links_items = soup.find_all("a", {"class": "album-link", "href": True})
    return [item.get("href") for item in album_links_items]


def get_profile_album_links(pages: list[str]) -> list[str]:
    """Retrieve album links from a list of profile page links."""
    profile_album_links = []
    num_pages = len(pages)

    with create_progress_bar() as progress_bar:
        task = progress_bar.add_task("[cyan]Progress", total=num_pages)
        for page in pages:
            soup = fetch_page(page)
            album_links = extract_album_links_in_page(soup)
            profile_album_links.extend(album_links)
            progress_bar.advance(task)

    return profile_album_links


def generate_profile_dump(profile_album_links: list[str]) -> None:
    """Generate a text file containing album links for a specified profile."""
    with Path(DUMP_FILE).open("w", encoding="utf-8") as file:
        file.writelines(f"{album_link}\n" for album_link in profile_album_links)


def process_profile_url(url: str) -> None:
    """Process a profile URL to fetch and generate a profile dump."""
    profile = url.rstrip("/").split("/")[-1]
    console = Console()
    console.print(f"Dumping profile: [bold]{profile}[/bold]")
    soup = fetch_page(url)

    try:
        page_links = get_profile_page_links(soup, profile)
        page_links.insert(0, url)

        profile_album_links = get_profile_album_links(page_links)
        generate_profile_dump(profile_album_links)

    except ValueError as val_err:
        message = f"Error occurred processing profile URL: {val_err}"
        logging.exception(message)

    else:
        console.print("[green]✓[/green] Dump file successfully generated.\n")


def main() -> None:
    """Execute the profile album extraction process."""
    url = sys.argv[1]
    process_profile_url(url)


if __name__ == "__main__":
    main()
