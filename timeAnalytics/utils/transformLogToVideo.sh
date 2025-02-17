#!/bin/bash
# uses rrweb's rrvideo tool to transfrom recordings into mp4 format
# had to clone and setup the entire rrweb project since the cli tool did not work in my setup

# Set the directory containing the log files
log_directory="timeAnalytics/powerpoint_videos"
output_directory="timeAnalytics/data/powerpoint_videos"

# Set the path to the cli.js
rrvideo_cli="/usr/local/lib/node_modules/rrvideo/build/cli.js"

# Loop over all log files in the specified directory
for log_file in "$log_directory"/*.log; do
    # Get the base name of the log file (without extension)
    base_name=$(basename "$log_file" .log)
    
    # Set the output video file name (replace .log with .mp4)
    output_file="$output_directory/$base_name.mp4"
    
    # Run the rrvideo CLI command to transform the log file into a video
    node "$rrvideo_cli" --input "$log_file" --output "$output_file"
    
    # Check if the transformation was successful
    if [ $? -eq 0 ]; then
        echo "Successfully transformed $log_file to $output_file"
    else
        echo "Failed to transform $log_file"
    fi
done
