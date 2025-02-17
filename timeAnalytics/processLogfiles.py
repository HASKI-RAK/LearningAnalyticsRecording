import os
import json
import re
from collections import defaultdict
import getSemesterQuantile
from getWordCountFromLogfile import get_word_count_from_csv

    
with open('timeAnalytics/data/config_WiSe_2425.json', 'r') as f:
    config = json.load(f)
    TBA_FILES = config['TBA_FILES']
    PDF_FILES = config['PDF_FILES']
    NON_EVALUATABLE_FILES = config['NON_EVALUATABLE_FILES']
    EXTERNAL_LINKS = config['EXTERNAL_LINKS']
    PLAIN_TEXT_MODULES = config['PLAIN_TEXT_MODULES']
    PDF_MODULES = config['PDF_MODULES']
    # 30 seconds of inactivity between last mouse movement and end of recording
    INACTIVITY_THRESHOLD = config['INACTIVITY_THRESHOLD'] 
    CUTOFF_DATE = config['CUTOFF_DATE']


def initialize_user(user_id, user_data, recording_exists):
    """initializes user id entry in the user data dict

    Args:
        user_id (int): integer that represents the user
        user_data (dict): dict that contains the user data and LA data
        recording_exists (bool): boolean value to determine whether a recording for this user exists. False if user_id occurs in moodle db events but not in rrweb recordings
    """
    user_data[user_id] = {
        'modules': {},                              # learning elements the student interacted with
        'total_overall_time': 0,                    # total overall time the student has spent interacting with larning elements
        'recording_files': recording_exists,        # indicate whether any recording logfiles exist for this user_id
        'Cur_student_LPath': {},                    # list of LE ids(ints); sequence of LE the studet defined by checking Mark as Done checkbox
        'Cur_LA_LPath': {},                         # list of LE ids(ints); sequence of learning elements the student completed; ignore Mark as Done
        'LA_LPath_improved': [],                    # list of LE ids(ints); sequence of LE_coverage/completed + Mark as Done(MAD); only includes MAD learning elements
                                                    # LA event has higher weight than MAD event;
        'Student_LPath_improved': []                # list of LE ids(ints); sequence of MAD + LE_coverage; only includes Cur_LA_LPath modules;
                                                    # MAD event has higher weight than LA event;
                                                    # LPath entry depends on timestamp for user action: did the LA system determine LE_completed before or
                                                    # after the student has triggered a MAD event?
    }

def initialize_module(user_id, module_id, module_type, user_data):
    """initializes module data for this module id for this user id.

    Args:
        user_id (int): integer that represents the user
        module_id (int): integer that represents the module
        module_type (str): current module type for this module id
        user_data (dict): dict that contains the user data and LA data
    """
    user_data[user_id]['modules'][module_id] = {
        'time_entries': {},             # list of times spent in module_id at a time
        'LE_type': module_type,         # module_type for this module_id
        'total_LE_time': 0,             # total time spent in this module_id for this user
        'LE_completed': False,          # whether the LE is marked as completed on basis of LA-heuristic
        'LE_completed_timestamp': 0,    # timestamp when the LE is deemed completed by the LA system
        'LE_coverage': 0.0,             # coverage rate as float for how much time the student has spent in a module_id
        'LE_consumption_reliable': None
        
    }


def extract_timestamps(file_path, start_line=None, end_line=None):
    """function to extract timestamps from a given time interval. defaults to first and last line
    of the file. If the last line is a custom system message, the line before that is used to avoid
    large timeframes of inactivity before the recording was shut down.

    Args:
        file_path (str): the path to the file to be evaluated
        start_line (str): optional. start line for the time interval.
        end_line(str): optional. end line for the time interval.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            if not lines:
                return None, None
            first_mouse_timestamp = None
            last_mouse_timestamp = None
            last_line = json.loads(lines[-1])
            last_timestamp = int(last_line.get("timestamp"))
            
            for line in lines:
                current_line = json.loads(line)
                
                if current_line.get("type") == 3:
                    #interaction_type = current_line.get("data", {}).get("source")
                    # if action is mouse movement, click, drag or scroll
                    # leads to errors with videos. need to fetch the very last timestamp or else the time watched can't be calculated properly
                    # since videos still count even when mouse is already outside of browser window
                    #if interaction_type in [1,2,3,4,5,6,7]:
                    current_timestamp = int(current_line.get("timestamp"))        

                    if first_mouse_timestamp is None:
                        first_mouse_timestamp = current_timestamp
                        
                    # always update the last mouse timestamp
                    last_mouse_timestamp = current_timestamp
                        
        # check if last mouse movement and ending of recording have a notable time difference
        if last_mouse_timestamp and (abs(last_timestamp - last_mouse_timestamp)) > INACTIVITY_THRESHOLD:
            last_timestamp = last_mouse_timestamp

        # if no user interaction occurs in the file, use first and last line instead
        if first_mouse_timestamp is None:
            first_line = json.loads(lines[0])
            first_mouse_timestamp = first_line.get("timestamp")
        if last_timestamp is None:
            last_line = json.loads(lines[-1])
            last_timestamp = last_line.get("timestamp")
        return first_mouse_timestamp, last_timestamp
    except Exception as e:
        print(f"Error when extracting timestamps: {e}")  
        return None, None



def get_scrolling_behavior(file_path, module_type, start_timestmp, final_timestmp):
    """returns the time a user spent on each page. Starting page is not completely correct.
    If the very first scrolling line already changes the page, the starting page can be off by one.
    example: the user is one scoll wheel input away from switching pages, then the starting 
    page is set to the new one. This is a very minor issue and should be addressed in the future.
    Couldn't figure out a consistent way of fetching the initial starting page from the logfile since ids are generated dynamically,
    the layout of the initital lines can be completely different and sometimes the second or third occurence
    of the href line is the real starting page.

    Args:
        file_path (str): the path to the file to be evaluated
        module_type (str): the current module_type for this file.
        start_timestmp (int): the start timestamp for this logfile
        final_timestmp (int): the ending timestamp for this logile
    """
    try:
            
        # regex pattern that defines the currently looked at page in the recording
        page_pattern = re.compile(r"#page=(\d+)")
        parts = file_path.split('_')
        module_id = int(parts[2])
        time_on_pages = []
        start_page = 0
        num_pages = 1
        
        if module_type in PDF_MODULES and module_id not in EXTERNAL_LINKS and module_id not in NON_EVALUATABLE_FILES and module_id not in PLAIN_TEXT_MODULES and module_id not in TBA_FILES or module_id in PDF_FILES:
            pdf_data = get_word_count_from_csv(module_id, is_pdf=True)
            if pdf_data is not None:
                num_pages = pdf_data['Num Pages']
            else:
                #print(f"no pdf data for module id {module_id} found")
                return None
        else:
            #print(f"bad module id {module_id} for evaluation. skippin file")
            return None
        
        with open(file_path, 'r', encoding='utf-8') as file:
            scrolling_flag = False  # only look at page string pattern after a scrolling event happened to avoid accidentally reading metadata
            lines = file.readlines()
            if not lines:
                return None
            
            for line in lines:
                current_line = json.loads(line)
                
                # get url href link from metadata line. used to find out the current page that is being shown on screen
                # example: https://xxx_yyyy.de/resource/view.php?id=42#page=1&zoom=auto,-232,596 shows page 1
                # href part in the intital url is without the page and zoom part
                if current_line.get("type") == 4 and 'href' in current_line.get("data"):
                    href = current_line.get("data").get("href")
                    
                # Check if the event is a scrolling event
                elif current_line.get("type") == 3 and current_line.get("data").get("source") == 3:
                    scrolling_flag = True
                    
                # scrolling related transmuation event lines
                elif scrolling_flag and current_line.get("type") == 3 and current_line.get("data").get("source") == 0:
                    attributes = current_line.get("data", {}).get("attributes", [])
                    # check if attributes field is not empty
                    if attributes and len(attributes) > 0:
                        first_attr_href = attributes[0].get("attributes", {}).get("href")
                        # current page only detailed in the first attribute's href field.
                        # also ensures the url is the same as expected
                        if first_attr_href and href in first_attr_href:
                            # search for the current page in the href string
                            match = page_pattern.search(first_attr_href)
                            if match:
                                current_page = int(match.group(1))
                                if current_page > num_pages:
                                    print(f"Warning: Current page is outside of page num scope for page {current_page} in {file_path}. Total Number of pages is {num_pages}.")
                                # init starting page
                                if start_page == 0:
                                    start_page = current_page

                                # if user scrolls to a new page, measure time spent on it
                                if current_page != start_page:
                                    # sometimes the timestamp of the event is wrong for seemingly no reason. 
                                    # can just use the prior event timestamp instead
                                    if current_line.get("timestamp") - start_timestmp == 0:
                                        print("debug file line")
                                    else:
                                        current_timestamp = current_line.get("timestamp")
                                    time_spent_on_page = (current_timestamp - start_timestmp) / 1000
                                    time_on_pages.append((start_page,time_spent_on_page))
                                    start_page = current_page
                                    start_timestmp = current_timestamp
    
        
        cumulative_time = defaultdict(float)
        for page, time_spent in time_on_pages:
            cumulative_time[int(page)] += round(time_spent, 2)
        # add final time to final page
        # if there were scroll entries, append time until recording ended to last page
        if 'current_page' in locals() and 'current_timestamp' in locals():
            time_until_ending = round((final_timestmp - current_timestamp) / 1000, 2)
            cumulative_time[int(current_page)] += time_until_ending
        else: # if user never scrolled, assign recording length to starting page
            time_dif = round((final_timestmp - start_timestmp) / 1000, 2)
            cumulative_time[int(start_page)] = time_dif
        cumulative_time = dict(cumulative_time)

        return cumulative_time
    
    except Exception as e:
        print(f"Error getting scrolling behavior for file {file_path}: {e}")
        return None
                

# two possible uses cases; either get all recordings of a specified module_type or all recordings
# for a given user_id
#ToDo: specify both module_type and user_id? it will include both in an or fashion I assume. Might be useful to get it to filter by an 'and' fashion
def filter_recordings_by_module_type_or_user_id(module_types, directory, module_type=None, user_id=None):
    """filters all the recoridng files in a given directory via a given module type.
    Some currently further unused functionality that allows to filter by either module type or user id

    Args:
        module_types (dict): dictionary of modules types and their corresponding module ids
        directory (str): path to the recording directory
        module_type (str, optional): a given module type for which all recordings should be found. Defaults to None.
        user_id (int, optional): a given user id for which all recordings should be found. Defaults to None.

    Returns:
        filtered_recordings: list of relevant recordings for the given module type or user id
        specified_modules: dict with all the module ids for the given module type
    """
    filtered_recordings = []
    if not module_types and not user_id:
        return "Error, module_type nor user_id specified"
    if module_type: # only executed if module_type is provided as parameter
        #iterate over existing module_types dict and copy items if they match the module_type parameter string
        specified_modules = module_types[module_type]

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".log"):
                parts = file.split('_')
                if len(parts) == 4 and parts[1] != 'null' and parts[2] != 'unknown' and parts[2] != 'null':
                    logfile_user_id = parts[1]
                    logfile_module_id = parts[2]
                    # skip reocrdings of admin / teachers that can access old, hidden course
                    #if logfile_user_id == '63' or logfile_user_id == '2':
                    #    continue
                    # skip recordings before october 10h due to old recordings in SoSe course
                    if int(parts[3].split('.')[0]) < int(CUTOFF_DATE):
                        continue

                    # append logfile if it matches a given user_id
                    if user_id and user_id == logfile_user_id: 
                        filtered_recordings.append(os.path.join(root, file))
                    # append logfile if it matches a given module_type
                    if module_type and int(logfile_module_id) in specified_modules: 
                        filtered_recordings.append(os.path.join(root, file))

    return filtered_recordings, specified_modules


def fetch_data_from_media_line(line, multiple_videos):
    try:
        current_line = json.loads(line)
    except json.JSONDecodeError:
        return None # skip this line
    if "currentTime" not in current_line.get("data", {}):
        return None
    player_id = None
        # youtube api custom event line
    data = current_line.get("data", {})
    if current_line.get("type") == "custom":
        data = current_line.get("data", {})
        event_type = data.get("type")
        currentTime = data.get("currentTime")
        playbackRate = data.get("playbackRate")
        if multiple_videos:
            player_id = data.get("videoId")
    # if regular MediaInteraction event
    elif data.get("source") == 7:
        event_type = data.get("type")
        currentTime = data.get("currentTime")
        playbackRate = data.get("playbackRate")
        if multiple_videos:
            player_id = data.get("id")
        
    timestamp = current_line.get("timestamp")
    if event_type is not None:
        return event_type, currentTime, playbackRate, timestamp, player_id
    else:
        return None
    
    

def split_sessions_by_id(play_sessions):
    """
    Splits play sessions into separate lists by unique video player ID.
    """
    sessions_by_id = defaultdict(list)
    # to map video-player-IDs to the right video later on
    id_order = []
    for session in play_sessions:
        session_id = session.get('id')
        # note down first occurence of an id
        if session_id not in sessions_by_id:
            id_order.append(session_id)
        sessions_by_id[session_id].append(session)
    return list(sessions_by_id.values()), id_order
    
    
def calculate_time_watched(play_sessions, file, video_length, multiple_videos):
    """
    Calculate the time watched by comparing 'play' and 'pause' events. Includes the case where a user does not pause the video before the recording ends.
    yt play events not distinguishable if several videos exist on the website.
    Issue on how to find out which video the user clicked on. If there are 5 videos and user clicks on 5-2-4-3-1 in that order, then I have no way
    of mapping that via the ID and have to go via the browser layout and amount of screens that were scrolled instead?
    """
    start_time = None
    start_timestamp = None
    unique_segments_watched = set()
    current_time = 0
    timestamp = 0
    last_timestamp = 0
    
    
    if len(play_sessions) == 0:
        time_watched = set()
        return time_watched, timestamp
    # todo for videos: use id from player or yt api event
    # if multiple videos, then split actions by id
    if multiple_videos is True and any('id' in session for session in play_sessions):
        session_groups, id_order = split_sessions_by_id(play_sessions)
        time_watched_per_player = []
        
        def sort_key(video_id):
            # for youtube api events
            if str(video_id).startswith("video-"):
                return int(video_id.split('-')[-1])
            else:  #regular rrweb node instead
                return int(video_id)
         
        #Sort id_order to ensure "video-0", "video-1", etc., are in the correct order
        sorted_id_order = sorted(id_order, key=sort_key)      
        numeric_sorted_id_order = [sort_key(video_id) for video_id in sorted_id_order]
        if len(sorted_id_order) != len(video_length[1]) and sum(numeric_sorted_id_order) > 50:
            print(f"More videos available for {file} than were interacted with. Might be unreliable")  
        # mapping dict for individual runtime and video
        id_to_runtime = {sorted_id_order[i]: video_length[1][i] for i in range(len(sorted_id_order))}

        # group by id to get interactions for each video/player separately
        # use as input for function call
        for single_video_session in session_groups:
            video_id = single_video_session[0]['id']
            runtime = id_to_runtime.get(video_id, None)
            if runtime is None:
                print(f"Runtime not found for {file} and video ID {video_id}. Skipping..")
                continue
            segments_watched, last_timestamp = calculate_time_watched(single_video_session, file, [runtime], multiple_videos=False)
            time_watched_per_player.append((segments_watched, last_timestamp))
            # returns sum of total seconds the user watched and the latest timestamp
            # Aggregate the total unique segments across all players
            total_segments_watched = set().union(*(segments for segments, _ in time_watched_per_player))

            # Calculate the latest timestamp
            latest_timestamp = max(last_timestamp for _, last_timestamp in time_watched_per_player)

            # Return the total duration (length of unique segments) and the latest timestamp
            return total_segments_watched, latest_timestamp
        #return sum(time_watched for time_watched, _ in time_watched_per_player), max(last_timestamp for _, last_timestamp in time_watched_per_player)
            
            
    for session in play_sessions:
        event_type = session['type']
        current_time = session['currentTime']
        playback_rate = session['playbackRate'] if session['playbackRate'] else 1
        timestamp = session['timestamp']
        # id = session['id']
        # can technically also add volume / muted info here

        if event_type == 'play' or event_type == 0:
            # Mark the start of a playback session
            start_time = current_time
            start_timestamp = timestamp

        # determine what second within the video has been watched by looking at the media player currentTime
        # i.e. user watched 10 seconds and current_time is 90: user watched from 80 to 90 seconds.
        # a bit off when user skips through video without pause event (skipping causes a pause and play event in 90% of the cases)
        # i.e. start at 0 (play event), watch for 10 seconds, then skip to 60 seconds (pause-event at 60 sec) -> thinks user watched from 50 to 60 seconds
        # todo for future work. 
        elif event_type in ['pause', 'ended', 1] and start_time is not None:
            # Calculate the time watched for this play session
            elapsed_real_time = (timestamp - start_timestamp) / 1000.0  # in seconds
            adjusted_watched_time = elapsed_real_time * playback_rate  # adjust by playbackRate
            
            start_time_in_video = int(current_time - adjusted_watched_time)
            end_time_in_video = int(current_time)
            for second in range(max(0, start_time_in_video), min(end_time_in_video, video_length[0])):
                unique_segments_watched.add(second)
            
            #total_time_watched += round(adjusted_watched_time,2)

            # Reset start_time and start_timestamp
            start_time = None
            start_timestamp = None
            
        # possibly wrong if player is not paused during a seek and seek is forward
        # log file shows no direct info about which direction the seek was performed to
        # backwards is fine, forwards is problematic if trying to find out how much of a video was
        # actually watched
        elif event_type == 2: # seek button is both stop and start
            if start_timestamp is not None:
                elapsed_real_time = (timestamp - start_timestamp) / 1000
                adjusted_watched_time = elapsed_real_time * playback_rate
                
                start_time_in_video = int(current_time - adjusted_watched_time)
                end_time_in_video = int(current_time)
                for second in range(max(0, start_time_in_video), min(end_time_in_video, video_length[0])):
                    unique_segments_watched.add(second)
                
            
            start_time = current_time
            start_timestamp = timestamp
        
    # when final event in logfile is not a pause event, assume user watched until the recording ends
    if start_time is not None:
        first_timestamp, last_timestamp = extract_timestamps(file)
        elapsed_real_time = (last_timestamp - start_timestamp) / 1000
        adjusted_watched_time = elapsed_real_time * playback_rate
        seconds_until_end = abs(int(elapsed_real_time))
        for second in range(seconds_until_end):
            unique_segments_watched.add(second)
            #total_time_watched += adjusted_watched_time
        timestamp = last_timestamp
    total_time_watched = len(unique_segments_watched)
    if total_time_watched < 0:
        print(f"total time_watched is {total_time_watched} for {file} which has {multiple_videos} multiple videos")
    return unique_segments_watched, timestamp
    
    
def get_time_watched(module_id, filtered_recordings, multiple_videos, total_runtime):
    media_playback = {}
    file_timestamp = 0
    
    for file in filtered_recordings:
        file_no_extension = file.rstrip('.log')
        parts = file_no_extension.split('_')
        try:
            recording_module_id = int(parts[2])
        except ValueError:
            continue
        if recording_module_id == module_id:
            try:
                user_id = int(parts[1])
                file_timestamp = int(parts[3])
            except ValueError:
                continue
            
            # initialize user_id for video
            if user_id not in media_playback:
                media_playback[user_id] = {
                    'player_timestamp': 0
                }
            
            
            with open(file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if not lines:
                    continue
                playback_sessions = []
                
                for line in lines:
                    result = fetch_data_from_media_line(line, multiple_videos)
                    # if no media related data in the line, skip to the next one
                    if result is None:
                        continue
                        
                    else:
                        event_type, current_time, playback_rate, timestamp, player_id = result

                        playback_session = {
                            'type': event_type,
                            'currentTime': current_time,
                            'playbackRate': playback_rate,
                            'timestamp': timestamp
                        }
                        
                    # add 'id' if more than one video in module
                    if multiple_videos and player_id is not None:
                        playback_session['id'] = player_id
                        
                    playback_sessions.append(playback_session)
                             
            time_watched, final_timestamp = calculate_time_watched(playback_sessions, file, total_runtime, multiple_videos)
            
            if user_id not in media_playback:
                media_playback[user_id] = {}
            if module_id not in media_playback[user_id]:
                media_playback[user_id][module_id] = 0
            if media_playback[user_id][module_id] == 0:
                media_playback[user_id][module_id] = time_watched 
            else: # merge the two sets
                media_playback[user_id][module_id].update(time_watched)
            # update timestamp of last media event only if it is not 0.
            # can occur if user looked at video in one recording, completed it, then opened another recording without watching anything
            if media_playback[user_id][module_id] != 0 and final_timestamp != 0:
                media_playback[user_id]['player_timestamp'] = final_timestamp 
    # get the total time in seconds that the student watched and return them
    for entry, value in media_playback.items():
        total_segment_watched = len(value[module_id])
        media_playback[entry][module_id] = total_segment_watched               
    return media_playback, file_timestamp
 

def process_log_files(filtered_recordings, module_types):
    """function to process recording logfiles and set up basic statistics

    Args:
        filtered_recordings (list): list of all the filtered recording filepaths
        module_types (dict): dictionary containing the module types and their module ids

    Returns:
        dict: nested dictionary that contains the user info and the LA data for the user
    """
    user_data = {}
    recordings_to_remove = []
    total_time_per_page = {}

    for file in filtered_recordings:
        parts = file.split('_')
        try:
            user_id = int(parts[1])
        except ValueError:
            user_id = 0
        try:
            module_id = int(parts[2])
        except ValueError:
            module_id = 0
            
        
            
        first_timestamp, last_timestamp = extract_timestamps(file)
        if module_id and first_timestamp and last_timestamp:
            time_spent = round((last_timestamp - first_timestamp) / 1000, 2)  # Convert milliseconds to seconds
            if time_spent < 0:
                print(f'time below 0 for recording {file}: {time_spent} seconds')
                recordings_to_remove.append(file)
                continue
            if module_id == 'unknown' or module_id == 'null':
                module_id = 0
            module_id = int(module_id)
            module_type = [mod_type for mod_type, ids in module_types.items() if module_id in ids][0]
            if module_type == []:
                module_type = 'unknown' # default to unknown if no module type found
            # initialize user_id in user_data
            # add more as necessary to conform to LA
            if user_id not in user_data: # set up user_id in dict if new entry
                initialize_user(user_id, user_data, recording_exists=True)
            user_data[user_id]['total_overall_time'] = user_data[user_id]['total_overall_time'] + time_spent # add cumulative time spent to user_id
            
            
            # handle pdf modules differently. if they have more than 1 page, calculate time per page instead of total time
            if module_type in PDF_MODULES:
                #calculate time per page instead of total time.
                if module_id not in NON_EVALUATABLE_FILES and module_id not in EXTERNAL_LINKS:
                    total_time_per_page = get_scrolling_behavior(file, module_type, first_timestamp, last_timestamp)
                    if total_time_per_page is not None:
                        if time_spent > 0:
                            difference =  abs(sum(total_time_per_page.values()) - time_spent) / time_spent
                            if difference > 0.2:
                                print(f"warning, time diff too big: {difference} for {file} \ntime_per_page_sum: {sum(total_time_per_page.values())} vs time_spent: {time_spent}")
                else: 
                    total_time_per_page is None
                    
                if total_time_per_page is None:
                    #print(f"no scrolling actions for user {user_id} in module {module_id}")
                    total_time_per_page = {}
                #if module_id not in user_data[user_id]['modules']:
                    #initialize_pdf_module(user_id, module_id, module_type, user_data,)
                #    print()
            #else:
            # initialize module_id entry for this user
            # append more as necessary to structure the entries for what should be tracked for each module_id entry for each user_id
            if module_id not in user_data[user_id]['modules']:
                initialize_module(user_id, module_id, module_type, user_data)
            
            
            # Add time spent in module along with the semesterQuantile
            time_entry_key = len(user_data[user_id]['modules'][module_id]['time_entries']) + 1  # simple int key for each time_entry data
            semester_quantile_categorical, semester_quantile_percentage = getSemesterQuantile.calculate_semester_quantiles(first_timestamp)
            user_data[user_id]['modules'][module_id]['time_entries'][time_entry_key] = {
                'time_spent': time_spent,
                'time_per_page': {},
                'semester_quantile_categorical': semester_quantile_categorical,
                'semester_quantile_percentage': semester_quantile_percentage,
                'timestamp': first_timestamp
            }
            for page_key, page_values in total_time_per_page.items():
                user_data[user_id]['modules'][module_id]['time_entries'][time_entry_key]['time_per_page'][page_key] = page_values
            
            # update total time spent in module
            user_data[user_id]['modules'][module_id]['total_LE_time'] = round(user_data[user_id]['modules'][module_id]['total_LE_time'] + time_spent,2)
                
    for file_to_remove in recordings_to_remove:
        filtered_recordings.remove(file_to_remove)
    return user_data

