import json
import getWordCountFromLogfile as wordCount
import genericEstimatedTimeBudget as genericTB
from processLogfiles import initialize_user, initialize_module, get_time_watched

with open('timeAnalytics/data/config_WiSe_2425.json', 'r') as f:
    config = json.load(f)
    # minimum amount of time (in seconds) a user should spend in a module for the recording to get evaluated
    MIN_THRESHOLD = config['MIN_THRESHOLD']
    # threshhold for text-type LE_coverage rate for the LE to be completed
    LE_COMPLETED_THRESHOLD = config['LE_COMPLETED_THRESHOLD']
    FIRST_SLIDE_COVERAGE = config['FIRST_SLIDE_COVERAGE']
    TBA_FILES = config['TBA_FILES']
    EXTERNAL_LINKS = config['EXTERNAL_LINKS']
    PLAIN_TEXT_MODULES = config['PLAIN_TEXT_MODULES']
    PDF_MODULES = config['PDF_MODULES']
    HTML_MODULES = config['HTML_MODULES']
    QUIZ_MODULES = config['QUIZ_MODULES']
    EXERCISE_MODULES = config['EXERCISE_MODULES']
    AUDIO_MODULES = config['AUDIO_MODULES']
    VIDEO_MODULES = config['VIDEO_MODULES']
    MEDIA_MODULES = AUDIO_MODULES + VIDEO_MODULES
    SUBMISSION_EXERCISES = config['SUBMISSION_EXERCISES']
    DOWNLOAD_EXERCISES = config['DOWNLOAD_EXERCISES']
    PDF_EXERCISES = config['PDF_EXERCISES']
    BROKEN_EXERCISES = config['BROKEN_EXERCISES'] 
    # adjust if necessary
    NON_HTML_EXERCISES = SUBMISSION_EXERCISES + DOWNLOAD_EXERCISES + PDF_EXERCISES + BROKEN_EXERCISES   
    # 15 seconds to look at this simple solution pdf for module_id 57. arbitrarily chosen and guesstimated
    STATIC_TIME_BUDGET_FOR_EXERCISE = config['STATIC_TIME_BUDGET_FOR_EXERCISE']
    
    QUIZ_RESULTS = config['QUIZ_RESULTS']
    QUIZ_MAPPING_FILE = config['QUIZ_MAPPING_FILE']
    ASSIGNMENT_CSV = config['ASSIGNMENT_CSV']
    MEDIA_RUNTIME_CSV = config['MEDIA_RUNTIME_CSV']



def initialize_quiz(user_id, module_id, module_type, user_data):
    """initialize module for quiz specification. Has quiz_results instead of time_entries since we do not care about the user recordings here.

    Args:
        user_id (int): integer that represents the user
        module_id (int): integer that represents the module id
        module_type (str): a given module type
        user_data (dict): dict that contains the user data and LA data
    """
    user_data[user_id]['modules'][module_id] = {
        'quiz_results': {               # results of the quiz; grade and timestamp
            'grade': 0,
            'timestamp': 0
        },             
        'LE_type': module_type,         # module_type for this module_id
        'total_LE_time': 0,             # total time spent in this module_id for this user
        'LE_completed': False,          # whether the LE is marked as completed on basis of LA-heuristic
        'LE_completed_timestamp': 0,    # timestamp when the LE is deemed completed by the LA system
        'LE_coverage': 0.0,             # coverage rate as float for how much time the student has spent in a module_id
        'LE_consumption_reliable': None
        }


def update_LE_completed(module_id, user_data, module_type, filtered_recordings):    
    """compares a given module_id and its time budget to the recording data for said module_id.

    Args:
        module_id (int): integer that represents the current module
        user_data (dict): dictionary that contains the user data and the LA events
        module_type (str): the current module type
        filtered_recordings (list): filepaths to the relevant recordings for this module type

    Returns:
        dict: the updated user_data dict with LE_completed, LE_coverage, LE_completed_timestamp, quiz grades (if necessary), LE_type (if necessary) and total_LE_time
    """
    num_pages = 1
    if module_id in EXTERNAL_LINKS:
        #print(f"cannot evaluate external link. skipping module id {module_id}")
        return None
    
    # fetch word count for module_id from dedicated csv file to calculate time budget
    # return early if no entry for the given module_id can be found
    if module_type in PDF_MODULES and module_id not in PLAIN_TEXT_MODULES:
        pdf_data = wordCount.get_word_count_from_csv(module_id, is_pdf=True)
        if pdf_data is not None:
            word_count = pdf_data['Word Count']
            num_pages = pdf_data['Num Pages']
            time_budget_in_seconds = round(pdf_data['Time Budget'])

        else:
            return None

            
    # if module_type is of generic html text structure
    elif module_type in HTML_MODULES or module_id in PLAIN_TEXT_MODULES:
        # number of pages is always 1 for plain text html modules 
        word_count = wordCount.get_word_count_from_csv(module_id, is_pdf=False)
        if word_count is not None:
            time_budget_in_seconds = genericTB.generic_estimated_time_budget(word_count) * 60
        else: 
            return None
            
    # if module_type is a quiz, use exported quiz result from the moodle DB
    elif module_type in QUIZ_MODULES:
        results, max_grade = genericTB.fetch_quiz_results(module_id, QUIZ_RESULTS, QUIZ_MAPPING_FILE)
        if len(results) == 0:
            return None
        for user_id, quiz_values in results[module_id].items():
            #initialize new user, if not yet present
            if user_id not in user_data:
                initialize_user(user_id, user_data, recording_exists=False)
            
            #initialize new module, if no recording was present
            if module_id not in user_data[user_id]['modules']:
                initialize_quiz(user_id, module_id, module_type, user_data)
                
            else:
                user_data[user_id]['modules'][module_id]['quiz_results'] = {'grade':0,'timestamp':0}
                user_data[user_id]['modules'][module_id]['LE_type'] = module_type
            # tuple of values: quiz grade and timestamp
            user_data[user_id]['modules'][module_id]['quiz_results']['grade'] = quiz_values[0]
            user_data[user_id]['modules'][module_id]['quiz_results']['timestamp'] = quiz_values[1]
            # LE_completed if 80% of the questions are correct
            LE_coverage = round(quiz_values[0] / max_grade, 2)
            user_data[user_id]['modules'][module_id]['LE_coverage'] = round(LE_coverage, 2)
            if (LE_coverage >= 0.8):
                user_data[user_id]['modules'][module_id]['LE_completed'] = True
                user_data[user_id]['modules'][module_id]['LE_completed_timestamp'] = quiz_values[1]
                
    
        return user_data
    

    # if module_type is an exercise
    elif module_type in EXERCISE_MODULES:
        # if exercise is a generic html type, treat it as such
        if module_id not in NON_HTML_EXERCISES:
            word_count = wordCount.get_word_count_from_csv(module_id, is_pdf=False)
            if word_count is not None:
                time_budget_in_seconds = genericTB.generic_estimated_time_budget(word_count) * 60
                # at least 3 minutes + reading time for an exercise
                time_budget_in_seconds = time_budget_in_seconds + 180
            else:
                return None
            
        elif module_id in PDF_EXERCISES:
            pdf_data = wordCount.get_word_count_from_csv(module_id, is_pdf=True)
            if pdf_data is not None:
                # should be treated as normal pdf, but the one pdf exercise file we have is just a simple diagram, so it will be treated
                # differently
                time_budget_in_seconds = STATIC_TIME_BUDGET_FOR_EXERCISE
            else:
                return None
            
        elif module_id in SUBMISSION_EXERCISES:
            submission_grades = genericTB.extract_grades_for_module_id(ASSIGNMENT_CSV, module_id, SUBMISSION_EXERCISES)
            if len(submission_grades) == 0:
                #print(f'no submission for for module {module_id}')
                return None
            
            for submission in submission_grades:
                user_id = submission[0]
                # if user submitted something for this module_id, LE_completed is true
                # no gradings of teachers happened in course, so this is a band-aid solution to this

                # initialize user in user_data if not yet present due to no recordings existing
                if user_id not in user_data:
                    initialize_user(user_id, user_data, recording_exists=False)
                # add module entry for this module
                if module_id not in user_data[user_id]['modules']:
                    initialize_quiz(user_id, module_id, module_type, user_data)

                user_data[user_id]['modules'][module_id]['LE_completed'] = True
                user_data[user_id]['modules'][module_id]['LE_completed_timestamp'] = submission[2]

                # normally would use grade as coverage, but special case here, set it to 1.0 instead
                # todo feedback for this issue
                #user_data[user_id]['modules'][module_id]['LE_coverage'] = submission[3]
                user_data[user_id]['modules'][module_id]['LE_coverage'] = 1.0
                return user_data
        
        elif module_id in BROKEN_EXERCISES:
            return None

    

    
    elif module_type in MEDIA_MODULES:
        media_runtime = genericTB.get_media_runtime(module_id, MEDIA_RUNTIME_CSV)
        # * 0.9 # student can skip intro and outro without it affecting LE_coverage as much
        time_budget = 0.9 * media_runtime['total_time']
        multiple_videos = False
        total_runtime = [media_runtime['total_time']]
        if media_runtime['media_amount'] > 1:
            multiple_videos = True
            total_runtime.append(media_runtime['individual_runtime'])
        # include playbackrate to normalize time_watched?
        media_playback, file_timestamp = get_time_watched(module_id, filtered_recordings, multiple_videos, total_runtime)
        time_watched = 0
        
        for user_id, user_values in media_playback.items():
            time_watched = round(media_playback[user_id][module_id],2)
            if user_id not in user_data:
                print("late init of media, despite recording being there?")
                initialize_user(user_id, user_data, recording_exists=False)
            if module_id not in user_data[user_id]['modules']:
                initialize_module(user_id, module_id, module_type, user_data)
            user_data[user_id]['modules'][module_id]['LE_type'] = module_type
            # get time_watched from recording entries instead of media_playback if no youtube api or improper mediaInteraction prevents more detailed time_watched
            if time_watched == 0:
                time_watched = round(user_data[user_id]['modules'][module_id]['total_LE_time'],2)
            # if total_LE_time has not been updated yet
            if user_data[user_id]['modules'][module_id]['total_LE_time'] == 0:
                user_data[user_id]['modules'][module_id]['total_LE_time'] = user_data[user_id]['modules'][module_id]['total_LE_time'] + time_watched
            # no time_budget for this video, skip this module_id
            if time_budget == 0:
                #print(f'Cannot evaluate external video. Skipping module id {module_id}')
                return user_data
            user_data[user_id]['modules'][module_id]['LE_coverage'] = round(min((time_watched / time_budget),1.0), 2)
            if time_watched / time_budget >= 0.7:
                user_data[user_id]['modules'][module_id]['LE_completed'] = True
                if user_values['player_timestamp'] == 0:
                    user_data[user_id]['modules'][module_id]['LE_completed_timestamp'] = file_timestamp
                else:
                    user_data[user_id]['modules'][module_id]['LE_completed_timestamp'] = user_values['player_timestamp']
                
        return user_data
                
    

    # text and PDF-based modules are analysed below
    
    # target_module copies only those user_data entries that are relevant for the current module_id
    # for debugging purposes mainly
    target_module = {} 
    for user_id in user_data:
        if module_id in user_data[user_id]['modules']:
            if user_id not in target_module:
                target_module[user_id] = {}  # Initialize user_id entry if not already present
            target_module[user_id][module_id] = user_data[user_id]['modules'][module_id]
        else:
            continue

    # iterate throught target_module and compare total time spent against time budget for each module_id (or learning element)
    # only done if no early return happened, which means that this is relevant code for pdf_modules and html_modules
    for entry_id in target_module:
        # delete recordings if they are very short except for when the time_budget is just a few seconds as well
        # this ensures that recordings where the word count is quite small remain, while more of the 'quickly open and close' 
        # recordings get filtered out
        entries_to_delete = []
        for time_key, value in target_module[entry_id][module_id]['time_entries'].items():
            single_recording_coverage = min(round(value['time_spent'] / time_budget_in_seconds, 2), 1.0)
            time_spent_in_logfile = round(value['time_spent'],2)
            # delete very short and useless recordings, reduce total_LE_time and total_overall_time accordingly
            if single_recording_coverage <= 0.1 and time_spent_in_logfile < MIN_THRESHOLD:
                entries_to_delete.append(time_key)
                user_data[entry_id]['modules'][module_id]['total_LE_time'] = round(
                    user_data[entry_id]['modules'][module_id]['total_LE_time'] - time_spent_in_logfile, 2)
                
                user_data[entry_id]['total_overall_time'] = round(user_data[entry_id]['total_overall_time'] - time_spent_in_logfile, 2)
                # After modification, ensure time is rounded to avoid floating-point precision errors
                if abs(user_data[entry_id]['total_overall_time']) < 1e-6:
                    user_data[entry_id]['total_overall_time'] = 0.0
                
              
        for time_key in entries_to_delete:
            del user_data[entry_id]['modules'][module_id]['time_entries'][time_key]

        user_data[entry_id]['modules'][module_id]['LE_type'] = module_type
        # calculate LE_coverage float value and determine LE_completed state
        total_time_in_module = target_module[entry_id][module_id]['total_LE_time']
        # need to fetch scrolling data for each recording. dismiss those wihthout scrolling/limit them to one page of LE_coverage. 
        if num_pages > 1:
            total_time_per_page = {}
            for time_entry, time_values in user_data[entry_id]['modules'][module_id]['time_entries'].items():
                for page_num, time_on_page in time_values['time_per_page'].items():
                    if page_num not in total_time_per_page:
                        total_time_per_page[page_num] = 0
                    total_time_per_page[page_num] += round(time_on_page, 2)
            
            LE_coverage_per_page = []  
            LE_completed_per_page = [] 
            for page_num, accumulated_time in total_time_per_page.items():
                # if user did not scroll, the page num is left at 0. might be useful later one but for evaluation the page num is simply set to 1 here
                if page_num == 0:
                    page_num = 1
                time_budget = round(pdf_data['Time per Page'][page_num -1], 2)
                if time_budget == 0:
                    # module id 365 has 0.0 time budget for page 1
                    time_budget = 1
                    #print(f"time budget is 0 for page {page_num} in module {module_id}")
                page_coverage = min(accumulated_time / time_budget, 1.0)
                if page_coverage < 0:
                    print(f"page coverage is {page_coverage} for user {entry_id} in module {module_id} on page {page_num}")
                # less weight for first page since it's almost always a simple intro slide. workaround. not all first slides are simple intros
                if page_num == 1:
                    page_coverage = min(page_coverage + LE_COMPLETED_THRESHOLD - FIRST_SLIDE_COVERAGE ,1.0)
                if page_coverage >= LE_COMPLETED_THRESHOLD:
                    LE_completed_per_page.append(page_num)
                LE_coverage_per_page.append(page_coverage)
            
            LE_coverage = min(round(len(LE_completed_per_page) / num_pages, 2), 1.0)
            user_data[entry_id]['modules'][module_id]['LE_coverage'] = LE_coverage

                
        # simply take the time budget if no scrolling analysis is needed
        else:
            LE_coverage = min(round(total_time_in_module / time_budget_in_seconds, 2), 1.0) # maximum value can be 1.0; round and cut off value past 2nd decimal
            user_data[entry_id]['modules'][module_id]['LE_coverage'] = LE_coverage
        
        if LE_coverage >= LE_COMPLETED_THRESHOLD:
            user_data[entry_id]['modules'][module_id]['LE_completed'] = True
            completed_timestamp = user_data[entry_id]['modules'][module_id]['LE_completed_timestamp']
            for time_entry, time_values in user_data[entry_id]['modules'][module_id]['time_entries'].items():
                timestamp = time_values['timestamp']
                # update timestamp of LE_completed
                if timestamp > completed_timestamp:
                    if completed_timestamp > 0:
                        print()
                    user_data[entry_id]['modules'][module_id]['LE_completed_timestamp'] = timestamp

                
    return user_data