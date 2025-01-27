# Erome Downloader

> A Python-based tool for downloading Erome albums. This project includes functionality to extract album links from user profiles and download them efficiently.

![Demo](https://github.com/Lysagxra/EromeDownloader/blob/f272207ad92373e2a7b48c12a2c093cf7ae175aa/misc/DemoV2.gif)

## Features

- Downloads multiple files concurrently from albums.
- Supports [batch downloading](https://github.com/Lysagxra/EromeDownloader?tab=readme-ov-file#batch-download) via a list of URLs.
- Supports [downloading of user profile](https://github.com/Lysagxra/EromeDownloader?tab=readme-ov-file#profile-crawler-and-downloader) album links.
- Tracks download progress with a progress bar.
- Automatically creates a directory structure for organized storage.

## Dependencies

- Python 3
- `requests` - for HTTP requests
- `BeautifulSoup` (bs4) - for HTML parsing
- `rich` - for progress display in terminal

## Directory Structure

```
project-root/
├── helpers/
│ ├── managers/
│ │ ├── live_manager.py      # Manages a real-time live display
│ │ ├── log_manager.py       # Manages real-time log updates
│ │ └── progress_manager.py  # Manages progress bars
│ ├── config.py              # Manages constants and settings used across the project
│ ├── download_utils.py      # Utilities for managing the download process
│ ├── erome_utils.py         # Functions for validating and processing Erome album URLs.
│ ├── file_utils.py          # Utilities for managing file operations
│ ├── general_utils.py       # Miscellaneous utility functions
│ └── profile_crawler.py     # Module to crawl profiles for album links
├── album_downloader.py      # Module for downloading albums
├── main.py                  # Main script to run the downloader
├── profile_dump.txt         # Log file for recording session details
└── URLs.txt                 # Text file containing album URLs
```

## Installation

1. Clone the repository:

```bash
git clone https://github.com/Lysagxra/EromeDownloader.git
```

2. Navigate to the project directory:

```bash
cd EromeDownloader
```

3. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Batch Download

To batch download from multiple album URLs, you can use the `main.py` script. This script reads URLs from a file named `URLs.txt` and downloads each one using the album downloader.

### Usage

1. Create a `URLs.txt` file in the project root and list the album URLs you want to download.

- Example of `URLs.txt`:

```
https://www.erome.com/a/cef1Rmyr
https://www.erome.com/a/1A3vgEBR
https://www.erome.com/a/IBFlQcQH
```

- Ensure that each URL is on its own line without any extra spaces.
- You can add as many URLs as you need, following the same format.

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

### Example

```
python3 main.py -p https://www.erome.com/marieanita
```

The downloaded files will be saved in `Downloads/<profile_name>` directory, where `<profile_name>` is the profile name extracted from the page.
