import json
from collections import defaultdict

def analyze_user_data(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        total_LE_count = 0
        completed_LE_count = 0
        LE_type_distribution = defaultdict(int)
        
        # Separate structures to hold coverage by LE type
        LE_coverage_by_type_completed = defaultdict(list)  # For LE_completed = True
        LE_coverage_by_type_all = defaultdict(list)        # For all modules regardless of LE_completed
        
        # Dictionaries to store user-specific learning path lengths
        user_manual_LP_lengths = defaultdict(int)
        user_internal_LP_lengths = defaultdict(int)

        # Loop through each user_id in the user_data.json
        for user_id, user_info in data.items():
            modules = user_info.get('modules', {})
            
            for module_id, module_info in modules.items():
                # Ensure the module contains necessary fields
                if 'LE_completed' in module_info and 'LE_type' in module_info and 'LE_coverage' in module_info:
                    total_LE_count += 1
                    
                    
                    coverage = module_info['LE_coverage']
                    le_type = module_info['LE_type']

                    # Special handling for Quiz type
                    if le_type == "Quiz" and coverage > 1.0:
                        coverage /= 10  # Adjust coverage for quiz types

                    # Count LE_completed = True
                    if module_info['LE_completed']:
                        completed_LE_count += 1
                        LE_coverage_by_type_completed[le_type].append(coverage)  # Store for completed

                    LE_coverage_by_type_all[le_type].append(coverage)  # Store for all regardless of completed

                    # Count distribution of LE_type
                    LE_type_distribution[le_type] += 1
                    
            # Calculate learning path lengths based on user_data[user_id]['Cur_student_LPath'] and user_data[user_id]['Cur_LA_LPath']
            manual_LP_length = len(user_info.get('Cur_student_LPath', []))
            internal_LP_length = len(user_info.get('Cur_LA_LPath', []))
            user_manual_LP_lengths[user_id] += manual_LP_length
            user_internal_LP_lengths[user_id] += internal_LP_length

        # Calculate completion rate
        completion_rate = (completed_LE_count / total_LE_count) * 100 if total_LE_count > 0 else 0

        # Calculate average LE_coverage for each LE_type (when LE_completed = True)
        average_coverage_by_type_completed = {
            le_type: sum(coverages) / len(coverages) if coverages else 0
            for le_type, coverages in LE_coverage_by_type_completed.items()
        }

        # Calculate average LE_coverage for each LE_type (for all elements)
        average_coverage_by_type_all = {
            le_type: sum(coverages) / len(coverages) if coverages else 0
            for le_type, coverages in LE_coverage_by_type_all.items()
        }

        # Calculate average learning path lengths for each type
        average_manual_LP_length = sum(user_manual_LP_lengths.values()) / len(user_manual_LP_lengths)
        average_internal_LP_length = sum(user_internal_LP_lengths.values()) / len(user_internal_LP_lengths)
        
        # Return the results as a dictionary
        # Return the results as a dictionary
        return {
            'completion_rate': completion_rate,
            'LE_type_distribution': dict(LE_type_distribution),
            'average_coverage_by_type_completed': average_coverage_by_type_completed,
            'average_coverage_by_type_all': average_coverage_by_type_all,
            'average_manual_LP_length': average_manual_LP_length,
            'average_internal_LP_length': average_internal_LP_length,
        }

    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    
# Example usage
user_data_json = 'timeAnalytics/data/user_data_WiSe_2425.json'
result = analyze_user_data(user_data_json)
if result:
    print(f"Completion Rate: {result['completion_rate']:.2f}%")
    print("LE Type Distribution:", result['LE_type_distribution'])
    
    print("Average LE Coverage by LE Type (Completed):")
    for le_type, avg_coverage in result['average_coverage_by_type_completed'].items():
        print(f"  {le_type}: {avg_coverage:.2f}")

    print("Average LE Coverage by LE Type (All):")
    for le_type, avg_coverage in result['average_coverage_by_type_all'].items():
        print(f"  {le_type}: {avg_coverage:.2f}")
    
    print("Average Manual Learning Path Length:", result['average_manual_LP_length'])
    print("Average Internal Learning Path Length:", result['average_internal_LP_length'])


