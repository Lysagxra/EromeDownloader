# Erome Downloader for Linux

A Python-based tool for downloading albums from Erome albums. This project includes functionality to extract album links from user profiles and download them efficiently.

## Features

- Extracts album links from user profiles.
- Downloads media files (images and videos) from Erome albums.
- Supports batch downloading via a list of URLs.

## Dependencies

- Python 3
- `requests` - for HTTP requests
- `BeautifulSoup` (bs4) - for HTML parsing
- `argparse` - for command-line argument parsing
- `tldextract` - for extracting domains
- `rich` - for progress display in terminal

## Directory Structure

```
project-root/
├── helpers/
│ ├── album_downloader.py # Python script for downloading albums
│ └── profile_crawler.py  # Python script to crawl profiles for album links
├── main.py               # Main Python script to run the downloader
├── URLs.txt              # Text file containing album URLs
└── profile_dump.txt      # File for temporary data storage
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
