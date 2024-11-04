# Erome Downloader

> A Python-based tool for downloading Erome albums. This project includes functionality to extract album links from user profiles and download them efficiently.

![Demo](https://github.com/Lysagxra/EromeDownloader/blob/a9c7e7d262a5bbd317e5fe9266bb01f3069a28e8/misc/Demo.gif)

## Features

- Extracts album links from user profiles.
- Downloads multiple media files (images and videos) concurrently from Erome albums.
- Supports batch downloading via a list of URLs.
- Tracks download progress with a progress bar.
- Automatically creates a directory structure for organized storage.

## Dependencies

- Python 3
- `requests` - for HTTP requests
- `BeautifulSoup` (bs4) - for HTML parsing
- `tldextract` - for extracting domains
- `rich` - for progress display in terminal

## Directory Structure

```
project-root/
├── helpers/
│ ├── download_utils.py   # Script containing utilities for managing the download process
│ ├── erome_utils.py      # Script containing Erome utilities
│ ├── profile_crawler.py  # Script to crawl profiles for album links
│ └── progress_utils.py   # Script with functions to create and manage progress indicators
├── album_downloader.py   # Module for downloading albums
├── main.py               # Main script to run the downloader
├── URLs.txt              # Text file containing album URLs
└── profile_dump.txt      # Log file for recording session details
```

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Lysagxra/EromeDownloader.git

2. Navigate to the project directory:
   ```bash
   cd EromeDownloader

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt

## Batch Download

To batch download from multiple album URLs, you can use the `main.py` script. This script reads URLs from a file named `URLs.txt` and downloads each one using the album downloader.

### Usage

1. Create a `URLs.txt` file in the project root and list the album URLs you want to download.

2. Run the main script via the command line:

```
python3 main.py
```

The downloaded files will be saved in the `Downloads` directory.

## Profile Crawler and Downloader

To download all the albums from a profile page, you can use the `-p` option.

### Usage

Use the `-p` option if you want to extract album links from a specific profile:

```bash
python3 main.py [-p <profile_page_url>]
```

Example

```
python3 main.py -p https://www.erome.com/marieanita
```

The downloaded files will be saved in `Downloads/<profile_name>` directory, where `<profile_name>` is the profile name extracted from the page.
