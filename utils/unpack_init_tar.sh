#!/bin/bash

# Create the target directory if it doesn't exist
mkdir -p ~/learninganalytics/utils/app/recordings

# Ensure the user provides a semester parameter
if [[ -z $1 ]]; then
    echo "Usage: $0 [winter|summer]"
    exit 1
fi

# Get the parameter and current year/month
SEMESTER=$1
CURRENT_YEAR=$(date +"%Y")
CURRENT_MONTH=$(date +"%m")

# Initialize date range variables
START_YEAR=$CURRENT_YEAR
START_MONTH=03
END_YEAR=$CURRENT_YEAR
END_MONTH=$CURRENT_MONTH

# Determine the date range based on the semester
if [[ $SEMESTER == "winter" ]]; then
    START_MONTH=10
    # Adjust year for winter semester if the current month is before October
    if [[ $CURRENT_MONTH -lt 10 ]]; then
        START_YEAR=$((CURRENT_YEAR - 1))
    fi
    # Winter semester ends in February of the following year
    if [[ $CURRENT_MONTH -lt 3 ]]; then
        END_YEAR=$((CURRENT_YEAR))
    fi
elif [[ $SEMESTER == "summer" ]]; then
    START_MONTH=03
else
    echo "Invalid semester. Please choose 'winter' or 'summer'."
    exit 1
fi

# Debug: Show the calculated date range
echo "Processing files from ${START_YEAR}-${START_MONTH} to ${END_YEAR}-${END_MONTH}..."

# Loop through the relevant months and unpack tar files
for YEAR in $(seq $START_YEAR $END_YEAR); do
    for MONTH in $(seq -w 1 12); do
        # Skip months outside the semester range
        if [[ $YEAR -eq $START_YEAR && $MONTH -lt $START_MONTH ]]; then
            continue
        fi
        if [[ $YEAR -eq $END_YEAR && $MONTH -gt $END_MONTH ]]; then
            continue
        fi

        # Process all tar files for the given year and month
        for tar_file in ~/recordings/recordings_${YEAR}${MONTH}*.tar; do
            if [[ -f "$tar_file" ]]; then
                echo "Processing $tar_file..."
                tar -xf "$tar_file" -C ~/learninganalytics/utils/app/recordings --strip-components=2 app/recordings
            else
                echo "No tar files found for ${YEAR}-${MONTH}."
            fi
        done
    done
done
