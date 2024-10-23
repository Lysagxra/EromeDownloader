# Erome Downloader for Linux

A command-line tool for downloading media files from Erome albums using Python and Bash scripts. This project includes functionality to extract album links from user profiles and download them efficiently.

## Features

- Extracts album links from user profiles.
- Downloads media files (images and videos) from Erome albums.
- Supports batch downloading via a list of URLs.

## Directory Structure
```
/project-root
│ ├── start.sh          # Main Bash script to run the downloader
├── album_downloader.py # Python script for downloading albums
├── profile_crawler.py  # Python script to crawl profiles for album links
└── URLs.txt            # Text file containing album URLs
```

## Dependencies

- Python 3
- `requests` - for HTTP requests
- `BeautifulSoup` (bs4) - for HTML parsing
- `argparse` - for command-line argument parsing
- `tldextract` - for extracting domains
- `rich` - for progress display in terminal

## Usage

### Step 1: Prepare URLs

Create a `URLs.txt` file in the project root and list the album URLs you want to download.

### Step 2: Run the Downloader

To start the process, execute the main script via the command line:

```
chmod +x start.sh  # Make the script executable
./start.sh [-p <profile_page_url>]
    Use the `-p` option if you want to extract album links from a specific profile.
```

Example

```bash
./start.sh -p https://www.erome.com/marieanita
```

The downloaded files will be saved in the `Downloads` directory.
