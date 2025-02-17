import os
import argparse
import csv
import re
import json
import processLogfiles
import updateLPath
import updateLECompleted
from datetime import datetime
from compareJsonFiles import compare_json_files, rename_old_user_data
from sendUserData import send_user_data


def load_module_types(csv_file):
    """function to load every module type and their module ids from a csv file.

    Args:
        csv_file (str): path to the csv file containing the module types data

    Returns:
        dict: dictionary for every module-id with module-type as key and module-ids as value
    """
    module_types = {}
    with open(csv_file, mode='r', encoding='cp1252') as infile:
        reader = csv.reader(infile)
        for rows in reader:
            module_type = rows[0]
            module_ids = [int(id) for id in rows[1:]]
            module_types[module_type] = module_ids
    
    return module_types


def load_mark_as_done_events(csv_file):
    """fetches all the mark as done (MAD) events from a csv. Originally exported from the moodle DB. 
    Filters out accidental clicks or MAD if they were removed afterwards again.

    Args:
        csv_file (str): path to the csv file containing the moodle MAD events

    Returns:
        list: list of key-value pairs for user_id, module_id and timestamp for each MAD event
    """
    last_completion_state = {}
    mark_as_done_events = []

    with open(csv_file, mode='r', encoding='cp1252') as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            user_id = int(row['userid'])
            module_id = int(row['contextinstanceid'])
            timestamp = int(row['timecreated']) *1000
            # only works for SoSe24
            #other = row['other'] # both completionstates are kept in here so we need to filter them

            #other_data = json.loads(other)
            #completionstate = other_data.get('completionstate') # make sure that this is 1 and not changed later

            completionstate = int(row['completionstate'])
            key = (user_id, module_id)

            if completionstate == 1:
                last_completion_state[key] = (timestamp, completionstate)

            elif completionstate == 0 and key in last_completion_state: # if changed back from 1 to 0
                del last_completion_state[key]
        
        for key, (timestamp, completionstate) in last_completion_state.items():
            user_id, module_id = key 
            mark_as_done_events.append({
                'user_id' : user_id,
                'module_id': module_id,
                'timestamp': timestamp # might be string, have to check
            })
        return mark_as_done_events


def update_LA_state(user_data, filtered_module_ids, module_type, filtered_recordings):  
    """iterate over all the module_ids for a given module_type and update LE_completed state.
    If no recording for a given module_id is found, will return None and skip this module_id.

    Args:
        user_data (dict): dict that contains the user data and the LA data
        filtered_module_ids (__type__): __description__
        module_type (str): a given module type
        filtered_recordings (list): list of recording filepaths filtered by a certain module type
    Returns:
        dict: updated user_data dictionary with updated LE_completed events
    """
    for filtered_module_id in filtered_module_ids:
        # update user_data with LE_completed
        updated_user_data = updateLECompleted.update_LE_completed(filtered_module_id, user_data, module_type, filtered_recordings)
        if updated_user_data is not None:
            user_data.update(updated_user_data)
        else:
            continue
    return user_data


def find_missing_module_ids(module_type_dict, module_type):
    """Finds module IDs of a specified module type that are missing from the pdf-word-count-CSV. Used for debugging.

    Args:
        module_type_dict (dict): A dictionary mapping module IDs to their types.
        module_type (str): The desired module type (e.g., 'Zusammenfassung').

    Returns:
        list: a list of the missing module IDs from the csv file
    """
    missing_ids = []

    # Get all module IDs of the specified type
    module_ids_of_type = [id for id, type in module_type_dict.items() if type == module_type]
    
    pdf_csv_file = 'timeAnalytics/data/pdf_word_count.csv'

    # Get a set of module IDs from the CSV
    csv_module_ids = set()
    with open(pdf_csv_file, 'r') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header row
        
        for row in reader:
            # Extract the module ID from the filename, assuming it's the number before ".pdf"
            filename = row[0]
            match = re.search(r'_(\d+)\.pdf$', filename)
            if match:
                module_id = int(match.group(1))
                csv_module_ids.add(module_id)

    # Find the missing module IDs
    missing_ids = set(module_ids_of_type) - csv_module_ids

    return list(missing_ids)


def sort_user_data_by_le_type(user_data, module_type_list):   
    """sorts user data dictionary by module types for easier reading

    Args:
        user_data (dict): dictionary with the user data and the LA data
        module_type_list (list): list of all module types

    Returns:
        dict: sorted user data dictionary
    """
    # Create a dictionary to map LE types to their index in the sorted order
    le_type_index = {le_type: index for index, le_type in enumerate(module_type_list)}
    
    # Iterate through each user's data in user_data
    for user_id, user_info in user_data.items():
        # only sort by LE_type for the user_ids entries that have rrweb recordings
        # todo: might not be necesary, but just saves some operations potentially
        if user_info['recording_files']: 
            # Extract the modules and their LE types
            modules = user_info['modules']
            
            # Sort the modules based on LE type using the predefined order
            sorted_modules = dict(
                sorted(
                    modules.items(),
                    key=lambda x: le_type_index.get(modules[x[0]]['LE_type'][0], float('inf'))
                )
            )
            
            # Update the user's modules with the sorted order
            user_data[user_id]['modules'] = sorted_modules
    
    return user_data


def dict_merge(total_user_data, user_data):
    """merges dict entries wihtout overwriting other fields. Used to accumulate all the module type data in one dict.

    Args:
        total_user_data (dict): dict containing every user data
        user_data (dict): current user data that should be merged into total_user_data

    Returns:
        dict: the merged total_user_data dictionary
    """
    for user_id, current_user_data in user_data.items():
        if user_id not in total_user_data:
            total_user_data[user_id] = current_user_data
        else:
            # Merge total_overall_time
            total_user_data[user_id]['total_overall_time'] = round(
                total_user_data[user_id]['total_overall_time'] + round(current_user_data['total_overall_time'], 2), 2
            )
            
            # Handle floating-point precision errors
            if abs(user_data[user_id]['total_overall_time']) < 1e-6:
                user_data[user_id]['total_overall_time'] = 0.0
            
            # Merge modules
            for module_id, module_data in current_user_data['modules'].items():
                if module_id not in total_user_data[user_id]['modules']:
                    # If the module_id is not yet in total_user_data, add it
                    total_user_data[user_id]['modules'][module_id] = module_data
                else:
                    total_user_data[user_id]['total_overall_time'] = round(total_user_data[user_id]['total_overall_time'] - round(current_user_data['total_overall_time'], 2), 2)
                    if abs(total_user_data[user_id]['total_overall_time']) < 1e-6:
                        total_user_data[user_id]['total_overall_time'] = 0.0
                    break
    return total_user_data
     

def export_total_user_data(total_user_data, filename):
    """Exports the user_data dict to a json file

    Args:
        total_user_data (dict): the dictionary structure containing the accumulated user_data
        filename (str): the output filename; defaults to 'timeAnalytics/data/user_data.csv'.
    """
    try:
        # Custom function to handle non-serializable data (like Enums and datetime)
        def default_serializer(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()  # Convert datetime objects to string
            if hasattr(obj, 'name'):  # For Enums or similar objects
                return obj.name  # Serialize Enum name
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

        # Ensure all data types are JSON-serializable
        for user_id, user_info in total_user_data.items():
            for module_id, module_info in user_info.get('modules', {}).items():
                if 'time_entries' in module_info:
                    # Convert time_entries (if it's a dictionary) to a list of dictionaries
                    serialized_entries = []
                    for time_entry_id, time_entry in module_info['time_entries'].items():
                        # Handle Enum-like objects for 'semester_quantile_categorical'
                        if 'semester_quantile_categorical' in time_entry:
                            time_entry['semester_quantile_categorical'] = time_entry['semester_quantile_categorical'].name
                        # Append the time_entry to a list
                        serialized_entries.append(time_entry)

                    # Replace the original time_entries with the serialized version
                    module_info['time_entries'] = serialized_entries

        # Export the data to a JSON file with the custom serializer
        with open(filename, 'w') as json_file:
            json.dump(total_user_data, json_file, indent=4, default=default_serializer)

        print(f"User data exported successfully to {filename}.")
    except Exception as e:
        print(f"Error exporting user data: {e}")


# checks logfiles for each specified module type and compares the time every user_id spent for each module_id against the time budget
def main():  
   
    with open('timeAnalytics/data/config_WiSe_2425.json', 'r') as f:
        config = json.load(f)

        log_directory = config['log_directory']
        module_csv = config['module_csv']
        export_filename = config['export_filename']
        MAD_csv = config['MAD_csv']
        old_user_data_file = config['OLD_FILE_PATH']
 
    
    total_user_data = {}
    
    if os.path.isdir(log_directory) and os.path.exists(module_csv): # make sure that only valid file and directory inputs are considered
        module_types = load_module_types(module_csv)
        # set of values to iterate over every unique LE_type
        module_type_list = sorted(list(module_types.keys()))
        # fetches every mark as done event from the logfile
        MAD_events = load_mark_as_done_events(MAD_csv)
        
        for module_type in module_type_list:
            recordings, filtered_module_ids = processLogfiles.filter_recordings_by_module_type_or_user_id(module_types, log_directory, module_type)
            user_data = processLogfiles.process_log_files(recordings, module_types)
            user_data = update_LA_state(user_data, filtered_module_ids, module_type, recordings)
            # only do recursive merges if total_user_data is not empty
            if bool(total_user_data) is True: 
                dict_merge(total_user_data, user_data)
            else:
                    total_user_data.update(user_data)
            

        updateLPath.update_cur_student_LPath(total_user_data, MAD_events)
        updateLPath.update_cur_la_lpath(total_user_data)
        updateLPath.update_LE_Consumption_reliable(total_user_data)
        updateLPath.update_LA_LPath_improved(total_user_data)
        updateLPath.update_Student_LPath_improved(total_user_data)

        sort_user_data_by_le_type(total_user_data, module_type_list)
        
        rename_old_user_data(export_filename, old_user_data_file)
        export_total_user_data(total_user_data, export_filename)
        updated_user_ids = compare_json_files(old_user_data_file, export_filename)
        print(f"detected change in users(s) {updated_user_ids}")
        
        if len(updated_user_ids) > 0:
            send_user_data(export_filename, updated_user_ids)
        else:
            print("No updated data to send")
        print("Finished building and sending user data.")
        
            
    else:
        if not os.path.isdir(log_directory):
            print("Directory not found.")
        if not os.path.exists(module_csv):
            print("CSV file not found.")

if __name__ == "__main__":
    main()

