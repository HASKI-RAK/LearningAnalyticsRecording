import os
import csv
import shutil
import json

with open('timeAnalytics/data/config_WiSe_2425.json', 'r') as f:
    config = json.load(f)
    submission_exercises = config['SUBMISSION_EXERCISES']
    download_exercises = config['DOWNLOAD_EXERCISES']
    pdf_exercises = config['PDF_EXERCISES']
    broken_exercises = config['BROKEN_EXERCISES']
    non_html_exercises = submission_exercises + download_exercises + pdf_exercises + broken_exercises

    plain_text_modules = config['PLAIN_TEXT_MODULES']

'''
submission_exercises = [22,26,30,53,54,55,56,89,311]
download_exercises = [702,703,706,708,710]
pdf_exercises = [57]
broken_exercises = [336,345,354,363,372,381,390,400]
'''


#used to fill a directory with sample recoding files that can be used to access the word count for them

def load_module_types(csv_file):
    module_types = {}
    with open(csv_file, mode='r', encoding='cp1252') as infile:
        reader = csv.reader(infile)
        for rows in reader:
            module_type = rows[0]
            module_ids = [int(id) for id in rows[1:]]
            module_types[module_type] = module_ids
    
    return module_types

def fill_sample_directory(module_types, module_type, directory, target_directory = 'utils/sample_recordings_WiSe_2425'):
    
    specified_modules = module_types[module_type]
    seen_module_ids = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".log"):
                parts = file.split('_')
                if len(parts) == 4 and parts[1] != 'null' and parts[2] != 'unknown' and parts[2] != 'null':
                    logfile_module_id = parts[2]
                    if int(logfile_module_id) in non_html_exercises:
                        continue
                    if int(logfile_module_id) not in plain_text_modules:
                        continue
                    # skip reocrdings of admin / teachers that can access old, hidden course
                    # skip recordings before a certain time
                    if int(parts[3].split('.')[0]) < 1730557525773:
                        continue
                    # copy logfile if it matches a given module_type and the module-id has not yet been seen
                    if int(logfile_module_id) in specified_modules and logfile_module_id not in seen_module_ids:
                        new_filename = f"{module_type}_{logfile_module_id}.log"
                        new_path = os.path.join(target_directory, new_filename)
                        seen_module_ids.append(logfile_module_id)
                        shutil.copy(os.path.join(root, file), new_path)
                        print(f"Copied {file} to {new_path}")
    print("done. debug me!")


def copy_module_type_recordings(module_types, module_type, source_dir, target_dir):
    """
    Copies all recordings of a specified module type from the source directory to the target directory.

    Args:
        module_types (dict): A dictionary mapping module types to their corresponding module IDs.
        module_type (str): The module type to copy recordings for.
        source_dir (str): The directory containing the recordings.
        target_dir (str): The directory to copy the recordings to.
    """

    specified_modules = {module_id: value for module_id, value in module_types.items() if value == module_type}

    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    for root, _, files in os.walk(source_dir):
        for file in files:
            if file.endswith(".log"):
                parts = file.split('_')
                if len(parts) == 4 and parts[1] != 'null' and parts[2] != 'unknown' and parts[2] != 'null':
                    logfile_module_id = parts[2]
                    if int(logfile_module_id) in non_html_exercises:
                        continue
                    if int(logfile_module_id) in specified_modules:
                        new_path = os.path.join(target_dir, file)
                        shutil.copy(os.path.join(root, file), new_path)
                        print(f"Copied {file} to {new_path}")



def filter_log_files(directory, target_string):
    """
    Filters log files in a given directory, deleting files that don't contain the specified target string.

    Args:
        directory (str): The directory containing the log files.
        target_string (str): The string to search for within the log files.
    """

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".log"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r") as f:
                        for line in f:
                            if target_string in line:
                                break
                        else:  # If the loop completes without a break, the string wasn't found
                            os.remove(file_path)
                            print(f"Deleted {file} because it doesn't contain '{target_string}'.")
                except Exception as e:
                    print(f"Error processing {file}: {e}")


def search_logs_for_patterns(logs_dir):
    """Search all log files in a directory for specific patterns and return matching filenames."""
    
    # Patterns to search for
    source7_pattern = '"source":7'
    
    # Lists to hold files that match each pattern
    source7_files = []

    # Walk through all files in the directory
    for root, dirs, files in os.walk(logs_dir):
        for file in files:
            # Only process .log or .txt files, or you can customize file extensions
            if file.endswith('.log') or file.endswith('.txt'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        
                        # Check if the file contains the '"source":7' pattern
                        if any(source7_pattern in line for line in lines):
                            source7_files.append(file_path)
               
                except Exception as e:
                    print(f"Error reading file {file}: {e}")
    
    return source7_files

def find_youtube_logs(directory):
    """Find all log files with YouTube-related events and return a list."""
    youtube_logs = []

    # Loop through all files in the directory
    for filename in os.listdir(directory):
        if filename.endswith(".log"):  # Assuming log files have a .log extension
            file_path = os.path.join(directory, filename)
            
            with open(file_path, 'r') as logfile:
                for line in logfile:
                    # Check if both 'type":"custom"' and one of the YouTube events ('play', 'pause', 'ended') appear
                    if '"type":"play"' in line or '"type":"pause"' in line or '"type":"ended"' in line:
                        youtube_logs.append(filename)
                        break  # No need to check further in this file, we found the event
    
    return youtube_logs


module_csv = 'timeAnalytics/data/grouped_module_numbers_WiSe_2425.csv'
module_type = 'Zusatzmaterial Textuell'
directory = 'utils/recordings_buggy_moduleID'
target_dir = 'utils/app/uebung'
module_types = load_module_types(module_csv)
#copy_module_type_recordings(module_types, module_type, directory, target_dir)
fill_sample_directory(module_types, module_type, directory)
