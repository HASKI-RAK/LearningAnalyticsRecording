#!/bin/bash

# Define base directory for the project
BASE_DIR=~/learninganalytics

# Step 1: Navigate to the project directory
cd $BASE_DIR

# Step 2: Activate the virtual environment
source venv/bin/activate

# Step 3: Go to the Moodle utilities directory
cd utils/moodle

# Step 4: Fetch the latest Moodle database dump
bash get-db.sh

# Step 5: Fix the Moodle dump file by commenting out the first line to avoid errors
bash fix-moodle-line.sh

# Step 6: Run the cron job to import the Moodle dump and generate necessary output files
bash cron-job.sh

# Step 7: Move back up one level in the utils directory
cd ..

# Step 8: Unpack the latest recording tar file
bash unpack-latest-tar.sh

# Step 9: Go back to the learninganalytics root directory
cd $BASE_DIR

# Step 10: Run Python scripts for data cleanup and ID adjustment
python3 filterLessThanFiveLines.py
python3 adjustRealModuleID.py

# Step 11: Navigate to the timeAnalytics directory
cd timeAnalytics

# Step 12: Build user data and send changes to the Moodle database
python3 buildUserData.py

# Step 13: Deactivate the virtual environment
deactivate

# Step 14: Print current date for clearer cron-log content
echo "Script completed successfully on: $(date)"
