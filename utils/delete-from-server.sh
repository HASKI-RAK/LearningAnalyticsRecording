#!/bin/bash

# Check for success marker before deleting recordings
if [ ! -f ~/recordings/export_success.marker ]; then
    echo "Error: Export not verified. Skipping deletion of recordings on server."
    exit 1
fi

# Delete recordings on the server
ssh -i ~/.ssh/id_rsa root@XX.XXXX.XXXXX "cd /srv/moodle/learninganalytics/utils && bash delete-recordings.sh"
if [ $? -ne 0 ]; then
    echo "Error: Failed to delete recordings from server."
    exit 1
fi

# Remove the success marker after successful deletion
rm -f ~/recordings/export_success.marker
echo "Deletion successful."
exit 0
