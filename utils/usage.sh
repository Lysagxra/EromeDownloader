#!/bin/bash

function usage()
{
    local progname=$0

    echo "Usage: $progname [-p]"
    echo "    -p: Downloads all album from a profile page provided from the command-line"
    printf "\nNote: If no argument is provided, the script downloads from an URLs file containing a list of album URLs.\n"
    exit 1
}
