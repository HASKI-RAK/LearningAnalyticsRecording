import csv

# define average reading speed
WORDS_PER_MINUTE = 250

# returns time it should take to read a given amount of words in minutes
def generic_estimated_time_budget(word_count):
    """estimation for generic plain text

    Args:
        word_count (int): the word count for which the necessary time to read should be approximated

    Returns:
        time_budget for the given word count_
    """
    time_budget = word_count/WORDS_PER_MINUTE
    return time_budget


def extract_grades_for_module_id(csv_file, module_id, submission_exercises):
    """extracts grades for a specific module ID from a CSV file.

    Args:
        csv_file (str): path to the CSV file.
        module_id (int): a specific module ID to filter for.

    Returns:
        A list of tuples containing (user_id, module_id, timemodified, grade).
    """

    grades = []
    with open(csv_file, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            assignment_id = int(row['assignment'])
            user_id = int(row['userid'])
            timestamp = int(row['timemodified'])
            grade = round(float(row['grade']),2)
            # there are no graded assignments in course 2, only in the Übungskurs, so the grades in dataset are negative
            if assignment_id - 1 in range(len(submission_exercises)):
                if submission_exercises[assignment_id-1] == module_id:
                    if grade < 0:
                        grade = 0
                    grades.append((user_id, submission_exercises[assignment_id-1], timestamp, grade))
    return grades

def map_quiz_ids(mapping_file):
    """Load the quiz ID to module ID mapping from a CSV file."""
    quiz_mapping = {}
    with open(mapping_file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            moodle_quiz_id = int(row['moodle_quiz_id'])
            quiz_module_id = int(row['quiz_module_id'])
            quiz_max_grade = float(row['max_grade'])
            quiz_mapping[moodle_quiz_id] = {
                'module_id': quiz_module_id,
                'max_grade': quiz_max_grade
            }
    return quiz_mapping

def fetch_quiz_results(module_id, quiz_results_file, quiz_mapping_file):
    """Fetch quiz results from the CSV file."""
    quiz_results = {}
    quiz_mapping = map_quiz_ids(quiz_mapping_file)
    
    # Reverse the quiz_mapping to find the moodle_quiz_id from module_id
    module_to_quiz_id = {v['module_id']: k for k, v in quiz_mapping.items()}
    
    # Get the corresponding Moodle quiz ID for the given module_id
    moodle_quiz_id = module_to_quiz_id.get(module_id)
    if moodle_quiz_id is None:
        print(f"No mapping found for module_id {module_id}.")
        return quiz_results
    
    max_grade = quiz_mapping[moodle_quiz_id]['max_grade']
    
    with open(quiz_results_file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)  
        for row in reader:
            quiz_id = int(row['quiz'])  # moodle's internal quiz id
            user_id = int(row['userid'])
            grade = float(row['grade'])
            timestamp = int(row['timemodified']) * 1000
            
            if quiz_id == moodle_quiz_id:
                if module_id not in quiz_results:
                    quiz_results[module_id] = {}
                
                # Check if this user's grade is higher than the current stored grade
                if user_id not in quiz_results[module_id] or grade > quiz_results[module_id][user_id][0]:
                    quiz_results[module_id][user_id] = (grade, timestamp)
                    
    return quiz_results, max_grade

def get_media_runtime(module_id, media_csv):
    """reads the runtime for the given module id (media can be of type audio or video)

    Args:
        module_id (int): integer that represents the current module
        media_csv (str): filepath to the csv file containing info about length of the the media for the modules

    Returns:
        dict: containing total_time, media_amount and individual_runtime if several video / audio files are available under a module id
    """
    media_runtime = {
        'total_time':0, # total runtime of module in seconds
        'media_amount':0, # numbers of media per module
        'individual_runtime':[] # runtime (in seconds) of each media in a single module
    }

    with open(media_csv, newline='') as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader) # skip header
        for line in reader:
            if int(line[0]) == module_id:
                if line[1] == 'None':
                    media_runtime['total_time'] = 0
                    media_runtime['media_amount'] = 1
                    break
                media_runtime['total_time'] = int(line[1])
                media_runtime['media_amount'] = int(line[2])
                if int(line[2]) > 1:
                    individual_runtimes_str = line[3]
                    media_runtime['individual_runtime'] = [int(runtime) for runtime in individual_runtimes_str.split('+')]
                break
    return media_runtime

        
        