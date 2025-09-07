"""Configuration module for managing constants and settings used across the project.

These configurations aim to improve modularity and readability by consolidating settings
into a single location.
"""

# ============================
# Host Configuration
# ============================
HOST_NETLOC = "www.erome.com"         # Host name of the site.
HOST_PAGE = f"https://{HOST_NETLOC}"  # Full URL of the homepage.

# ============================
# Paths and Files
# ============================
DOWNLOAD_FOLDER = "Downloads"    # The folder where downloaded files will be stored.
URLS_FILE = "URLs.txt"           # The file containing the list of URLs to process.
SESSION_LOG = "session_log.txt"  # The file used to log session errors.
DUMP_FILE = "profile_dump.txt"   # The file where the profile data will be dumped.

# ============================
# Download Settings
# ============================
MAX_WORKERS = 3          # The maximum number of threads for concurrent downloads.
COLUMNS_SEPARATOR = "•"  # Visual separator used between progress bar columns.

# Country codes representing different regions.
REGIONS = [
    "cn", "cz", "de", "es", "fr", "gr", "it",
    "nl", "jp", "pt", "pl", "rt", "ru", "se",
]

# Constants for file sizes, expressed in bytes.
KB = 1024
MB = 1024 * KB

# Thresholds for file sizes and corresponding chunk sizes used during download.
THRESHOLDS = [
    (1 * MB, 4 * KB),     # Less than 1 MB
    (10 * MB, 8 * KB),    # 1 MB to 10 MB
    (100 * MB, 16 * KB),  # 10 MB to 100 MB
]

# Default chunk size for files larger than the largest threshold.
LARGE_FILE_CHUNK_SIZE = 64 * KB

# ============================
# HTTP / Network
# ============================
# HTTP status codes
HTTP_STATUS_NOT_FOUND = 404
HTTP_STATUS_GONE = 410
