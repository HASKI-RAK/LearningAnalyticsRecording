import os
import json
import re
from datetime import datetime


# used to rename the recoridng filenames to a uniform format of randomString_userID_moduleID_timestamp
# if no timestamp given, will take the first one in the logfile
# sets userID or moduleID to unknown/null if it cannot be found
# a tiny bit buggy still in that after going through around 4.7k files it will leave a few open.

def extract_module_id_and_timestamp_from_line(first_line):
    try:
        data = json.loads(first_line)
        href = data['data']['href']
        timestamp = data['timestamp']
        module_id_match = re.search(r'id=(\d+)', href)
        if module_id_match:
            module_id = module_id_match.group(1)
        else:
            module_id = 'unknown'
        return module_id, timestamp
    except (json.JSONDecodeError, KeyError):
        return 'unknown', None

def standardize_filename(root, filename):
    parts = filename.split('_')
    random_string = parts[0]
    user_id = parts[1] if len(parts) > 1 else 'null'
    module_id = 'unknown'
    timestamp = 'unknown'

    with open(os.path.join(root, filename), 'r') as file:
        first_line = file.readline().strip()
        module_id, timestamp = extract_module_id_and_timestamp_from_line(first_line)
        if not timestamp:
            timestamp = int(datetime.now().timestamp() * 1000)  # Current timestamp if not found

    new_filename = f"{random_string}_{user_id}_{module_id}_{timestamp}.log"
    return new_filename

def rename_log_files(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".log"):
                original_path = os.path.join(root, file)
                parts = file.split('_')
                if len(parts) < 3:  # Check if the filename doesn't already follow the correct format
                    new_filename = standardize_filename(root, file)
                    new_path = os.path.join(root, new_filename)
                    if not os.path.exists(new_path):  # Ensure we don't overwrite existing files
                        os.rename(original_path, new_path)
                        print(f"Renamed {original_path} to {new_path}")
                else:
                    print("skipped file")


# clean up broken filenames after accidentally creating .log.log ending because of missing split call when renaming them
def cleanup_filenames(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.count('.log') > 1:
                base_name = file.replace('.log', '', file.count('.log') - 1)
                new_name = f"{base_name}"
                original_path = os.path.join(root, file)
                new_path = os.path.join(root, new_name)
                if not os.path.exists(new_path):  # Ensure we don't overwrite existing files
                    os.rename(original_path, new_path)
                    print(f"Cleaned {original_path} to {new_path}")


if __name__ == "__main__":
    log_directory = 'utils/app/recordings'
    rename_log_files(log_directory)
    #cleanup_filenames(log_directory)
