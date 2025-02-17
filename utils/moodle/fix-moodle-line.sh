#!/bin/bash

# Path to the moodle.sql file
sql_file="moodle.sql"

# Check if the file exists
if [[ -f "$sql_file" ]]; then
    # Read the first line and trim any trailing whitespace
    first_line=$(head -n 1 "$sql_file" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')

    # Check if the first line matches the expected pattern
    if [[ "$first_line" == "/*M!999999\\- enable the sandbox mode */" ]]; then
        # Comment out the first line by adding "-- " at the beginning
        sed -i '1s/^/-- /' "$sql_file"
        echo "The first line was commented out successfully."
    else
        echo "The first line does not match the expected pattern. No changes made."
    fi
else
    echo "File '$sql_file' not found."
fi
