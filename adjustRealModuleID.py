import os
import json
import re


def update_module_ids(directory_path):
    """renames the recording files so they reflect the real module IDs.

    Args:
        directory_path (str): _descriptipath to the recordings
    """
    # Regular expression to capture the full filename pattern with randomString, userID, moduleID, and timestamp
    filename_pattern = re.compile(r"(.*)_(\d+)_(\d+)_(\d+)\.log$")
    counter = 0

    # Iterate over every file in the directory
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        
        # Match only log files with the expected structure
        match = filename_pattern.match(filename)
        if match and filename.endswith(".log"):
            random_string, user_id, current_module_id, timestamp = match.groups()
            
            # Open the file and read the first line
            try:
                with open(file_path, 'r') as file:
                    first_line = file.readline().strip()
                    
                    # Parse JSON data from the first line
                    log_data = json.loads(first_line)
                    if log_data.get("type") == 4:
                        href = log_data["data"].get("href", "")
                        
                        # Extract the real module_id from the href URL
                        real_module_id_match = re.search(r"id=(\d+)", href)
                        if real_module_id_match:
                            real_module_id = real_module_id_match.group(1)
                            
                            # Check if the module ID in the filename matches the real module ID
                            if real_module_id != current_module_id:
                                # Generate new filename with the corrected module ID and preserved userID
                                new_filename = f"{random_string}_{user_id}_{real_module_id}_{timestamp}.log"
                                new_file_path = os.path.join(directory_path, new_filename)
                                
                                # Rename the file to the corrected filename
                                os.rename(file_path, new_file_path)
                                counter += 1
                                print(f"Renamed: {filename} -> {new_filename}")
            except (IOError, json.JSONDecodeError) as e:
                print(f"Error reading file {filename}: {e}")
    
    return counter

# Usage
directory_path = "utils/app/recordings"
counter = 0
counter = update_module_ids(directory_path)
print(f"adjusted {counter} recordings")