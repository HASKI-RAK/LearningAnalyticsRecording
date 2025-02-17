import statistics

# debugging function to calculate and print statistics
def print_generic_statistics(user_data, module_data, module_type_data, user_module_type_data):
    # Average LE_coverage per user
    user_avg_coverage = {
    user: round(sum(module['LE_coverage'] for module in data['modules'].values()) / len(data['modules']), 2)
    for user, data in user_data.items()
    }
    for user, avg_coverage in user_avg_coverage.items():
        print(f"User {user}: Average LE Coverage = {avg_coverage}")

    user_avg_times = {user: data['total_time'] / len(data['modules']) for user, data in user_data.items()}

    # Average time spent per module
    module_avg_times = {module: statistics.mean(times) for module, times in module_data.items()}

    # Average time spent per module type
    module_type_avg_times = {module_type: statistics.mean(times) for module_type, times in module_type_data.items()}

    # Total time spent per module type
    module_type_total_times = {module_type: sum(times) for module_type, times in module_type_data.items()}

    # Total time spent on all module types
    total_time_all_types = sum(module_type_total_times.values())

    # Calculate the average time spent across all module types
    all_module_type_averages = list(module_type_avg_times.values())
    total_avg_time = statistics.mean(all_module_type_averages) if all_module_type_averages else 0

    # Calculate percentage spread among module type averages
    module_type_avg_percentage_spread = {
        module_type: (avg_time / total_avg_time) * 100
        for module_type, avg_time in module_type_avg_times.items()
    }

    # Calculate percentage of total time spent for each module type
    module_type_percentage_spread = {
        module_type: (total_time / total_time_all_types) * 100
        for module_type, total_time in module_type_total_times.items()
    }

    print("Average time spent per user:")
    for user, avg_time in user_avg_times.items():
        minutes = avg_time / 60
        print(f"User {user}: {minutes:.1f} minutes")
        

    print("\nAverage time spent per module:")
    for module, avg_time in module_avg_times.items():
        minutes = avg_time / 60
        print(f"Module {module}: {minutes:.1f} minutes")

    print("\nAverage time spent per module type:")
    # Collect average times and module types
    average_time_per_module_type = []
    module_types = []

    # Populate the lists with average times and module types
    for module_type, avg_time in module_type_avg_times.items():
        minutes = avg_time / 60
        average_time_per_module_type.append(minutes)
        module_types.append((module_type, minutes))  # Store module type with its average time

    # Calculate the total average time
    total_average = sum(average_time_per_module_type)

    # Print the average time and percentage spread for each module type
    for module_type, avg_time in module_type_avg_times.items():
        minutes = avg_time / 60
        percentage = (minutes / total_average * 100) if total_average > 0 else 0
        print(f"Average time spent per {module_type}: {minutes:.1f} minutes ({percentage:.1f}%)")


    print("\nTotal time spent per module type:")
    total_time_all_types_minutes = total_time_all_types / 60
    for module_type, total_time in module_type_total_times.items():
        total_minutes = total_time / 60
        percentage = (total_minutes / total_time_all_types_minutes) * 100
        print(f"Module type {module_type}: {total_minutes:.1f} minutes ({percentage:.2f}%)")


# simple print utility to get a better overview over the nested structure of user_data
def print_learning_analytics(user_data):
    for user_id in user_data:
        print(f"User_ID: {user_id}")
        print(f"\tCurrent Student LPath: {user_data[user_id]['Cur_student_LPath']}")
        print(f"\tCurrent LA Path: {user_data[user_id]['Cur_LA_LPath']}")
        print(f"\tLA Path improved1: {user_data[user_id]['LA_LPath_improved']}")
        print(f"\tMark as Done LPAth improved2: {user_data[user_id]['Student_LPath_improved']}")
        print(f"\tModule data for student with id {user_id}")
        for module_id in user_data[user_id]['modules']:
            print(f"\t\tModule_id {module_id}")
            print(f"\t\t\tLE_coverage: {user_data[user_id]['modules'][module_id]['LE_coverage']}")
            print(f"\t\t\tLE_completed: {user_data[user_id]['modules'][module_id]['LE_completed']}")
            print(f"\t\t\tLE_completed_timestamp: {user_data[user_id]['modules'][module_id]['LE_completed_timestamp']}")
            print(f"\t\t\tTotal_LE_time: {user_data[user_id]['modules'][module_id]['total_LE_time']}")
            print(f"\t\t\tLE_type: {user_data[user_id]['modules'][module_id]['LE_type']}")
            recording_index = 0
            if 'time entries' in user_data[user_id]['modules'][module_id]:
                for time_entry in user_data[user_id]['modules'][module_id]['time_entries']:
                    print(f"\t\t\t\trecording #{recording_index+1}:")
                    print(f"\t\t\t\t\tsemester_quanilte_categorical: {user_data[user_id]['modules'][module_id]['time_entries'][time_entry]['semester_quantile_categorical'].name}")
                    print(f"\t\t\t\t\tsemester_quantile_percent: {user_data[user_id]['modules'][module_id]['time_entries'][time_entry]['semester_quantile_percentage']}")
                    print(f"\t\t\t\t\ttime_spent: {user_data[user_id]['modules'][module_id]['time_entries'][time_entry]['time_spent']} seconds")
                    recording_index +=1
            elif 'quiz_results' in user_data[user_id]['modules'][module_id]:
                    print(f"\t\t\t\t\tQuiz_results: {user_data[user_id]['modules'][module_id]['quiz_results']}")
