# Erome Downloader

> A Python-based tool for downloading Erome albums. This project includes functionality to extract album links from user profiles and download them efficiently.

![Demo](https://github.com/Lysagxra/EromeDownloader/blob/51784c7396e3809582ced6a1465459526b196784/assets/demo.gif)

## Features

- Downloads multiple files concurrently from albums.
- Supports [batch downloading](https://github.com/Lysagxra/EromeDownloader?tab=readme-ov-file#batch-download) via a list of URLs.
- Supports [downloading of user profile](https://github.com/Lysagxra/EromeDownloader?tab=readme-ov-file#profile-crawler-and-downloader) album links.
- Supports [custom download location](https://github.com/Lysagxra/EromeDownloader/?tab=readme-ov-file#file-download-location).
- Tracks download progress with a progress bar.
- Automatically creates a directory structure for organized storage.

## Dependencies

- Python 3
- `requests` - for HTTP requests
- `BeautifulSoup` (bs4) - for HTML parsing
- `rich` - for progress display in terminal

<details>

<summary>Show directory structure</summary>

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

</details>

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
https://www.erome.com/a/fNpP7r11
https://www.erome.com/a/o0I2Smt1
https://www.erome.com/a/cef1Rmyr
```

- Ensure that each URL is on its own line without any extra spaces.
- You can add as many URLs as you need, following the same format.

2. Run the main script via the command line:

```
python3 main.py
```

## File Download Location

If the `--custom-path <custom_path>` argument is used, the downloaded files will be saved in `<custom_path>/Downloads`. Otherwise, the files will be saved in a `Downloads` folder created within the script's directory

### Usage

```bash
python3 main.py --custom-path <custom_path>
```

### Example

```bash
python3 main.py --custom-path /path/to/external/drive
```

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
