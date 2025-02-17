#!/bin/bash

# Set the source and destination directories
SOURCE_DIR=~/recordings
DEST_DIR=~/learninganalytics/utils/app/recordings

# Create the target directory if it doesn't exist
mkdir -p "$DEST_DIR"

# Find the latest tar file in the source directory
latest_tar_file=$(ls -t "$SOURCE_DIR"/recordings_*.tar | head -n 1)

if [[ -n "$latest_tar_file" ]]; then
    echo "Processing latest file: $latest_tar_file"
    # Extract the contents directly into the destination, removing the first two components
    tar -xf "$latest_tar_file" -C "$DEST_DIR" --strip-components=2 app/recordings
else
    echo "No recordings tar file found in $SOURCE_DIR."
fi
