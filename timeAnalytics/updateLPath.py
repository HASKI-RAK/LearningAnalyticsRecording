import statistics
import numpy as np
import processLogfiles


def update_cur_student_LPath(total_user_data, MAD_events):
    """updates user_data dict with the respective LPath value. Current student LPath is the order of 'Mark as Done' events the student triggered in Moodle

    Args:
        total_user_data (dict): accumulated user data
        MAD_events (list): list of events for Mark as Done by the student

    Returns:
        dict: updated total_user_data where the cur_student_LPath represents the order of MAD events for a user. In other words: the learning path the student
        actively chooses. 
    """
    # sort by timestamp to avoid wrong order of events
    sorted_MAD_events = sorted(MAD_events, key=lambda event: event['timestamp'])

    for event in sorted_MAD_events:
        user_id = int(event['user_id'])
        module_id = int(event['module_id'])
        timestamp = int(event['timestamp'])
        
        # create new user entry if it does not exist yet
        # dummy data for consistency of the user_data entries but modules will be empty since there are no known recordings
        # can only fill user_data with what is known via the moodle DB data
        if user_id not in total_user_data:
            processLogfiles.initialize_user(user_id, total_user_data, recording_exists=False)
            
        # append module_id to user's LPath if it's not already there
        if module_id not in total_user_data[user_id]['Cur_student_LPath']:
            total_user_data[user_id]['Cur_student_LPath'][module_id] = timestamp
    return total_user_data


def remove_outliers_modified_z_score(data, threshold=3.5):
    """Remove outliers using the modified Z-score method."""
    if len(data) < 2:
        return data  # Not enough data to determine outliers

    # Calculate median and MAD
    median = np.median(data)
    mad = np.median(np.abs(data - median))

    # Calculate modified Z-scores
    modified_z_scores = [(x - median) / (1.4826 * mad) for x in data]

    # Filter out outliers
    return [data[i] for i, z in enumerate(modified_z_scores) if abs(z) < threshold]


def remove_outliers_iqr(data):
    """Remove outliers using the IQR method (1.5 * IQR)."""
    if len(data) < 3:  # Not enough data to reliably calculate IQR
        return data

    # Convert to numpy array for easier percentile calculation
    data_array = np.array(data)

    # Calculate Q1 (25th percentile) and Q3 (75th percentile)
    Q1 = np.percentile(data_array, 25)
    Q3 = np.percentile(data_array, 75)
    IQR = Q3 - Q1

    # Define lower and upper bounds for outliers
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    # Return data with outliers removed
    return [x for x in data if lower_bound <= x <= upper_bound]


def calculate_median_and_stddev(times):
    """Helper function to calculate median and standard deviation from a list of times."""
    if len(times) < 2:
        return None, None  # Not enough data points for standard deviation
    median = round(statistics.median(times), 2)
    stddev = round(statistics.stdev(times), 2)
    return median, stddev

def update_LE_Consumption_reliable(total_user_data):
    """Updates LE_Consumption_reliable for each user's module consumption based on cohort comparison."""
    # Collect LE consumption times for all users for each module
    cohort_data = {}

    # Step 1: Gather cohort times for each module
    for user_id, user_info in total_user_data.items():
        for module_id, module_data in user_info['modules'].items():
            if module_data.get('total_LE_time') is not None and module_data.get('total_LE_time') > 0:
                # Initialize the list if this module hasn't been encountered
                if module_id not in cohort_data:
                    cohort_data[module_id] = []
                # Append the total time spent on the module
                cohort_data[module_id].append(module_data['total_LE_time'])

    # Step 2: Remove outliers and calculate median and standard deviation for each module
    cohort_stats = {}
    for module_id, times in cohort_data.items():
        # Remove outliers using IQR
        filtered_times = remove_outliers_iqr(times)
        # Calculate median and standard deviation on the filtered data
        median, stddev = calculate_median_and_stddev(filtered_times)
        cohort_stats[module_id] = {
            'median': median,
            'stddev': stddev
        }

    # Step 3: Update each user's `LE_Consumption_reliable` field
    for user_id, user_info in total_user_data.items():
        for module_id, module_data in user_info['modules'].items():
            total_time = module_data.get('total_LE_time')

            if total_time is not None and module_id in cohort_stats:
                median = cohort_stats[module_id]['median']
                stddev = cohort_stats[module_id]['stddev']

                if median is not None and stddev is not None:
                    # Check if the user's time is within 1 standard deviation of the cohort's median
                    if median - stddev <= total_time <= median + stddev:
                        module_data['LE_consumption_reliable'] = True
                    else:
                        module_data['LE_consumption_reliable'] = False
                else:
                    # Not enough data to compute standard deviation
                    module_data['LE_consumption_reliable'] = None


def update_cur_la_lpath(total_user_data):
    """Updates the 'Cur_LA_LPath' for each user based on their completed modules.

    Args:
        total_user_data (dict): A dictionary containing user data.
    """

    for user_id, user_data in total_user_data.items():
        # Filter only completed modules and sort them by completion timestamp
        sorted_completed_modules = sorted(
            filter(lambda item: item[1]['LE_completed'], user_data['modules'].items()),
            key=lambda item: item[1]['LE_completed_timestamp']
        )

        # Create a dict  of completed module IDs and their timestamps in order
        user_data['Cur_LA_LPath'] = {
            module_id: module_data['LE_completed_timestamp'] for module_id, module_data in sorted_completed_modules
        }

    
def update_lpath_improved(total_user_data, base_path_key, recent_path_key, result_key):
    """
    Generalized function to update learning paths based on recent timestamps from a comparison path.

    Args:
        total_user_data (dict): A dictionary containing user data.
        base_path_key (str): The key for the base path to use as a reference (e.g., 'MAD_LPath').
        recent_path_key (str): The key for the path to check for recent updates (e.g., 'Cur_LA_LPath').
        result_key (str): The key to store the improved path (e.g., 'Student_LPath_improved').
    """

    for user_id, user_data in total_user_data.items():
        # Get the base and recent paths for this user
        base_path = user_data.get(base_path_key, {})
        recent_path = user_data.get(recent_path_key, {})

        # Create a list to store the final order for the improved path
        improved_lpath = []

        # Go through the modules in the base path order
        for module_id, base_timestamp in sorted(base_path.items(), key=lambda item: item[1]):
            # If this module is also in the recent path, use the recent timestamp
            if module_id in recent_path:
                # Add the module with the recent timestamp to prioritize recent study actions
                improved_lpath.append((module_id, recent_path[module_id]))
            else:
                # Otherwise, add it with the base timestamp
                improved_lpath.append((module_id, base_timestamp))

        # Sort the final improved path by the timestamps to reflect recent actions where applicable
        improved_lpath.sort(key=lambda item: item[1])

        # Update the improved path in the user's data, keeping only module IDs in order
        user_data[result_key] = [module_id for module_id, _ in improved_lpath]

    return total_user_data

def update_LA_LPath_improved(total_user_data):
    """Updates LA_LPath_improved with Cur_LA_LPath determining the order."""
    return update_lpath_improved(total_user_data, 'Cur_LA_LPath', 'Cur_student_LPath', 'LA_LPath_improved')

def update_Student_LPath_improved(total_user_data):
    """Updates Student_LPath_improved with Cur_student_LPath determining the order."""
    return update_lpath_improved(total_user_data, 'Cur_student_LPath', 'Cur_LA_LPath', 'Student_LPath_improved')
