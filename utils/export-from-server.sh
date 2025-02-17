#!/bin/bash

TIMESTAMP=$(date +"%Y%m%d%H%M%S")

# Export recordings from the server
ssh root@XXXXXXX "cd /srv/moodle/learninganalytics/utils && bash export-recordings.sh"
if [ $? -ne 0 ]; then
    echo "Error: Failed to export recordings from server."
    exit 1
fi

# Securely copy the recordings to the local machine
scp root@XXXXXXXXX:/srv/moodle/learninganalytics/utils/recordings.tar ~/recordings/recordings_$TIMESTAMP.tar
if [ $? -ne 0 ]; then
    echo "Error: Failed to copy recordings from server to local machine."
    exit 1
fi

# Create a success marker file
touch ~/recordings/export_success.marker
echo "Export successful: ~/recordings/recordings_$TIMESTAMP.tar"
exit 0
