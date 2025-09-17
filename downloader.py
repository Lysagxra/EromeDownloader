"""Module that provides a command-line tool for downloading from an Erome album URL.

The script validates the provided album URL, collects links to the media files, and
downloads them to a specified local directory.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING
from urllib.parse import urlparse

import requests

from helpers.config import HOST_PAGE, USER_AGENT
from helpers.download_utils import run_in_parallel, save_file_with_progress
from helpers.erome_utils import extract_hostname
from helpers.file_utils import create_download_directory
from helpers.general_utils import fetch_page

if TYPE_CHECKING:
    from bs4 import BeautifulSoup
    from requests.models import Response

    from helpers.managers.live_manager import LiveManager


def get_cookies_header() -> dict[str, str]:
    """Build a cookies header dict from a request object."""
    response = requests.get(HOST_PAGE, timeout=10)
    laravel_session = response.cookies.get("laravel_session")
    xsrf_token = response.cookies.get("XSRF-TOKEN")
    cookies_value = f'XSRF-TOKEN="{xsrf_token}"; laravel_session="{laravel_session}"'
    return {"Cookies": cookies_value}


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
            "User-Agent": USER_AGENT,
            "Referer": album_url if album_url else origin_url,
            "Origin": origin_url,
            "Connection": "keep-alive",
        },
        timeout=(timeout, read_timeout),
    )


def extract_and_format_album_title(soup: BeautifulSoup, album_id: str) -> str:
    """Extract and format the album title, appending the album ID."""
    title_container = soup.find("meta", {"property": "og:title", "content": True})
    album_title = title_container.get("content").strip()
    return f"{album_title} ({album_id})"


def extract_download_links(soup: BeautifulSoup) -> list[str]:
    """Extract download links for image and video sources from the album URL."""
    image_items = soup.find_all("img", {"class": "img-back"})
    video_items = soup.find_all("source")

    image_download_links = [image_item.get("data-src") for image_item in image_items]
    video_download_links = [video_item.get("src") for video_item in video_items]
    return list({*image_download_links, *video_download_links})


def download_item(
    download_link: str,
    task_id: int,
    live_manager: LiveManager,
    download_path: str,
    album_url: str,
) -> None:
    """Download a file from the specified download link."""
    parsed_url = urlparse(download_link)
    filename = Path(parsed_url.path).name

    hostname = extract_hostname(download_link)
    final_path = Path(download_path) / filename

    with configure_session(download_link, hostname, album_url) as response:
        save_file_with_progress(response, final_path, task_id, live_manager)


def download_album(
    album_url: str,
    live_manager: LiveManager,
    profile: str | None = None,
    custom_path: str | None = None,
) -> None:
    """Download an album from the given URL."""
    # Cookies used only to fetch soup for download links
    cookies = get_cookies_header()
    soup = fetch_page(album_url, cookies=cookies)
    if soup is None:
        return

    album_id = album_url.rstrip("/").split("/")[-1]
    album_title = extract_and_format_album_title(soup, album_id)
    album_path = album_title if not profile else Path(profile) / album_title
    download_path = create_download_directory(album_path, custom_path=custom_path)

    download_links = extract_download_links(soup)
    if download_links is None:
        return

    run_in_parallel(
        download_item, download_links, live_manager, album_id, download_path, album_url,
    )


#def main() -> None:
#    """Initiate the download process."""
#    clear_terminal()
#    args = parse_arguments()

#    live_manager = initialize_managers()
#    validated_url = validate_url(args.url)
#    profile_name = extract_profile_name(args.profile) if args.profile else None

#    with live_manager.live:
#        download_album(
#            validated_url,
#            live_manager,
#            profile=profile_name,
#            custom_path=args.custom_path,
#        )
#        live_manager.stop()


#if __name__ == "__main__":
#    main()
