"""Configuration module for managing constants and settings used across the project.

These configurations aim to improve modularity and readability by consolidating settings
into a single location.
"""

from enum import IntEnum

# ============================
# Paths and Files
# ============================
DOWNLOAD_FOLDER = "Downloads"    # The folder where downloaded files will be stored.
URLS_FILE = "URLs.txt"           # The file containing the list of URLs to process.
SESSION_LOG = "session_log.txt"  # The file used to log session errors.
DUMP_FILE = "profile_dump.txt"   # The file where the profile data will be dumped.

# ============================
# UI & Table Settings
# ============================
COLUMNS_SEPARATOR = "•"  # Visual separator used between progress bar columns.

# Constant defining the minimum width for each column
MIN_COLUMN_WIDTHS = {
    "Timestamp": 10,
    "Event": 15,
    "Details": 30,
}

# ============================
# Host Configuration
# ============================
HOST_NETLOC = "www.erome.com"         # Host name of the site.
HOST_PAGE = f"https://{HOST_NETLOC}"  # Full URL of the homepage.

# Country codes representing different regions.
REGIONS = [
    "cn", "cz", "de", "es", "fr", "gr", "it",
    "nl", "jp", "pt", "pl", "rt", "ru", "se",
]

# ============================
# Download Settings
# ============================
MAX_WORKERS = 2          # The maximum number of threads for concurrent downloads.

# Constants for file sizes, expressed in bytes.
KB = 1024
MB = 1024 * KB

# Thresholds for file sizes and corresponding chunk sizes used during download.
THRESHOLDS = [
    (1 * MB, 2 * KB),    # Less than 1 MB
    (10 * MB, 4 * KB),   # 1 MB to 10 MB
    (100 * MB, 8 * KB),  # 10 MB to 100 MB
]

# Default chunk size for files larger than the largest threshold.
LARGE_FILE_CHUNK_SIZE = 16 * KB

# ============================
# HTTP / Network
# ============================
class HTTPStatus(IntEnum):
    """Enumeration of common HTTP status codes used in the project."""

    OK = 200
    FORBIDDEN = 403
    NOT_FOUND = 404
    GONE = 410
    TOO_MANY_REQUESTS = 429
    INTERNAL_ERROR = 500
    BAD_GATEWAY = 502
    SERVICE_UNAVAILABLE = 503
    SERVER_DOWN = 521

# User-Agent string to mimic a Firefox browser
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0"
)
