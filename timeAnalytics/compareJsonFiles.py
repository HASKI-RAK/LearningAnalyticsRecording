from deepdiff import DeepDiff
import json
import os
from sendUserData import send_user_data

def rename_old_user_data(old_file, output_name):
    """Renames the old user data file.

    Args:
        old_file (str): The filename of the old user data file.
        output_name (str): The new name to rename the old file to.
    """
    try:
        # Check if the old file exists
        if os.path.exists(old_file):
            # Rename the old file to the new name
            os.rename(old_file, output_name)
            print(f"Renamed old user data file from {old_file} to {output_name}.")
        else:
            print(f"No existing file to rename: {old_file}")
    except Exception as e:
        print(f"Error renaming old or new file: {e}")


def compare_json_files(old_file, new_file):
    """Compares two user_data.json files to detect changes in user-IDs.

    Args:
        old_file (str): The filename of the old user data file.
        new_file (str): The filename of the newly generated user_data.json.
    """
    try:
        # Load existing user data from JSON file
        with open(old_file, 'r') as json_file:
            existing_user_data = json.load(json_file)

        # Load new user data from the exported JSON file
        with open(new_file, 'r') as json_file:
            new_user_data = json.load(json_file)

        # Compare existing and new user data
        diff = DeepDiff(existing_user_data, new_user_data, ignore_order=True)
        user_ids = set()
        if len(diff) > 0:
            for user_id in diff.affected_root_keys:
                user_ids.add(user_id)
        return user_ids
    except Exception as e:
        print(f"Error when comparing json file: {e}")

if __name__ == '__main__':
    ## debugging example
    changed_ids = compare_json_files('timeAnalytics/data/old_user_data.json', 'timeAnalytics/data/user_data_WiSe_2425.json')
    print(f"change detected in {len(changed_ids)} users")
    send_user_data('timeAnalytics/data/user_data_WiSe_2425.json', changed_ids)
