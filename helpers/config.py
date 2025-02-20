"""Configuration module for managing constants and settings used across the project.

These configurations aim to improve modularity and readability by consolidating settings
into a single location.
"""

HOST_NETLOC = "www.erome.com"         # Host name of the site.
HOST_PAGE = f"https://{HOST_NETLOC}"  # Full URL of the homepage.
MAX_WORKERS = 3                       # The maximum number of threads for
                                      # concurrent downloads.
DOWNLOAD_FOLDER = "Downloads"         # The folder where downloaded files
                                      # will be stored.
FILE = "URLs.txt"                     # The name of the file containing the
                                      # list of URLs to process.
SESSION_LOG = "session_log.txt"       # The file used to log session errors.
DUMP_FILE = "profile_dump.txt"        # The name of the file where the profile
                                      # data will be dumped.

KB = 1024
MB = 1024 * KB

THRESHOLDS = [
    (1 * MB, 4 * KB),     # Less than 1 MB
    (10 * MB, 8 * KB),    # 1 MB to 10 MB
    (100 * MB, 16 * KB),  # 10 MB to 100 MB
]

LARGE_FILE_CHUNK_SIZE = 64 * KB

# Dictionary containing ANSI escape sequences for text styles and colors.
COLORS = {
    "PURPLE": "\033[95m",
    "CYAN": "\033[96m",
    "DARKCYAN": "\033[36m",
    "BLUE": "\033[94m",
    "GREEN": "\033[92m",
    "YELLOW": "\033[93m",
    "RED": "\033[91m",
    "BOLD": "\033[1m",       # Bold text style
    "UNDERLINE": "\033[4m",  # Underlined text style
    "END": "\033[0m",        # Reset to default terminal styling
}
