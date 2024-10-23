#!/bin/bash

# Function to extract the profile name from a given URL
extract_profile_name()
{
    local url="$1"
    local profile_name="${url##*/}"
    echo "$profile_name"
}
