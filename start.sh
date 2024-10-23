#!/bin/bash

# Constants
readonly FILE='URLs.txt'
readonly DUMP_FILE='profile_dump.txt'
readonly SCRIPTS_DIR='utils'

# Default values for options
file_to_read="$FILE"
profile_option=""

# Import all functions in utils directory
for script in "$SCRIPTS_DIR"/*.sh; do
    source "$script"
done

# Parse command-line options
while getopts ":p" option; do
    case $option in
        # Generate the profile dump file and set it as file to read
        p) python3 profile_crawler.py "$2"
           profile_option="-p"
           file_to_read="$DUMP_FILE" ;;
        \?) usage ;;
    esac
done

while read -r line; do
    # Download Erome album
    if [ "$profile_option" ]; then
        profile_name=$(extract_profile_name "$2")
        python3 album_downloader.py -u "$line" $profile_option "$profile_name"
    else
        python3 album_downloader.py -u "$line"
    fi
done < "$file_to_read"

# Clear the URLs file
: > "$file_to_read"
