import os
import shutil
import csv

#takes a module_type name and a directory as input and picks the first recording for each module_id of that module type and copies the recording to a target directory
#grouping the recordings like that makes it easier to fetch the word count later on when comparing the time budget 

# returns all module ids for a given module type string
def get_module_ids_for_type(csv_file, module_type):
    module_ids = []
    with open(csv_file, 'r', encoding='cp1252') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0].strip() == module_type:
                module_ids = [int(module_id.strip()) for module_id in row[1:]]
                break
    return module_ids


def copy_unique_logfiles(source_dir, target_dir, module_ids):
    seen_module_ids = set()

    # Ensure the target directory exists
    os.makedirs(target_dir, exist_ok=True)

    for root, _, files in os.walk(source_dir):
        for file in files:
            if file.endswith(".log"):
                parts = file.split('_')
                if len(parts) == 4 and parts[2] != 'unknown' and parts[2] != 'null' and parts[1] != '2':
                    module_id = int(parts[2])  # Get the module_id from the filename

                    # Check if the module_id is in the desired module_ids list and hasn't been copied yet
                    if module_id in module_ids and module_id not in seen_module_ids:
                        # Copy the file to the target directory
                        shutil.copy(os.path.join(root, file), os.path.join(target_dir, file))
                        seen_module_ids.add(module_id)  # Mark this module_id as processed

    print(f"Copied {len(seen_module_ids)} unique log files to {target_dir}")

# Example usage
csv_file = 'timeAnalytics/data/grouped_module_numbers.csv'  # Path to CSV file
source_directory = 'utils/app/recordings'  # Path to the directory containing the log files
target_directory = 'timeAnalytics/logs/Lernziel'  # Path to the target directory
module_type = 'Lernziel'  # The module type you want to process

# Get the list of module_ids for the specified module_type
module_ids = get_module_ids_for_type(csv_file, module_type)

# Copy unique log files for the given module_ids
copy_unique_logfiles(source_directory, target_directory, module_ids)