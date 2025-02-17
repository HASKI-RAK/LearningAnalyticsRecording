# RRWEB implementation
The rrweb implementation is hosted on HASKI's Moodle server. 
The corresponding setup provided in this directory contains the last work-in-progress templates that were used to capture recordings and ensure video recordings work.

As such, the given files in the /src/ directory are to be used as guidelines and references.
security tokens that were used in the debugging process have been hidden

# Basic documentation reference for logfile events

## IncrementalSource ("source" field in each type:3 line)

    export enum IncrementalSource {
    Mutation,
    MouseMove,
    MouseInteraction,
    Scroll,
    ViewportResize,
    Input,
    TouchMove,
    MediaInteraction,
    StyleSheetRule,
    CanvasMutation,
    Font,
    Log,
    Drag,
    StyleDeclaration,
    Selection,
    AdoptedStyleSheet,
    }
    // example for an Input event:
    {"type":3,"data":{"source":5,"text":"1","isChecked":false,"id":450},"timestamp":1728890471418}

## Mouse Movement (type:3, source:1)

    export type mousemoveData = {
    source:
        | IncrementalSource.MouseMove
        | IncrementalSource.TouchMove
        | IncrementalSource.Drag;
    positions: mousePosition[];
    };

    // example: 
    // {"type":3,"data":{"source":1,"positions":[{"x":595,"y":346,"id":586,"timeOffset":0}]},"timestamp":1728890468050}

## Mouse Interaction (type:3, source:2)

    type of mouseinteractions is defined as:
    export enum MouseInteractions {
    MouseUp,
    MouseDown,
    Click,
    ContextMenu,
    DblClick,
    Focus,
    Blur,
    TouchStart,
    TouchMove_Departed, // we will start a separate observer for touch move event
    TouchEnd,
    TouchCancel,
    }
    // can be left-click, right-click, swipe, ...
    // example for a Focus event: 
    {"type":3,"data":{"source":2,"type":5,"id":586},"timestamp":1728890468550}

## Media Interaction (type:3, source:7)

    export const enum MediaInteractions {
    Play,
    Pause,
    Seeked,
    VolumeChange,
    RateChange,
    }
    // for all media types (audio and video within html)
    // example of a play event: 
    // {"type":3,"data":{"source":7,"type":0,"id":491,"currentTime":0,"volume":1,"muted":false,"playbackRate":1},"timestamp":1729003478736}
    
    youtube lines are custom-made and include player-id, play, pause and video-has-ended events
    // example of a Youtube-play event:
    // {"type":"custom","data":{"type":"play","currentTime":0.047895165939331054,"playbackRate":1,"videoId":"video-0"},"timestamp":1729169254193}
    // can search for media lines with the search term "currentTime" (with the quotation marks, otherwise it will find some metadata about the media player)

check rrweb github for more info.

https://github.com/rrweb-io/rrweb/blob/9488deb6d54a5f04350c063d942da5e96ab74075/src/types.ts#L10

https://github.com/rrweb-io/rrweb/blob/98e71cd0d23628cd1fbdbe47664a65748084c4a4/packages/types/src/index.ts#L69

https://www.rrweb.io/

https://github.com/rrweb-io/rrweb/tree/98e71cd0d23628cd1fbdbe47664a65748084c4a4/docs

# JSON Output Documentation

## 1. Overview  
The JSON output is structured with the **student's user ID** as the top-level key (e.g., `"2"`, `"63"`, or `"105"`).  
Each **student ID** contains a set of attributes that describe their engagement with LEs.  

## 2. Student-Level Attributes  
Each student entry includes the following fields:  

- **`modules`**: A list of LEs the student engaged with.  
- **`total_overall_time`**: The cumulative time spent across all LEs.  
- **`recording_files`**: A flag indicating whether a recording exists for the student or if only a "Mark as Done" event is available.  
- **`Cur_Student_LPath`**:  
  A list of **LE-IDs** representing the sequence of LEs the student manually marked as completed by selecting the "Mark as Done" checkbox.  
- **`Cur_LA_LPath`**:  
  A list of **LE-IDs** representing the sequence of LEs completed based on **recording evaluations**, disregarding manual "Mark as Done" events.  
- **`LA_LPath_improved`**:  
  A combined learning path that uses `Cur_LA_LPath` as the primary structure but adjusts the sequence to align with `Cur_Student_LPath` where overlap exists.  
- **`Student_LPath_improved`** *(or `MAD_LPath_improved`, depending on the version)*:  
  Similar to `LA_LPath_improved`, but with `Cur_Student_LPath` as the primary structure. The order of elements is adjusted based on timestamps from `Cur_LA_LPath`.  

## 3. Module-Level Attributes  
Each module in `modules` contains detailed engagement data at the LE level, including:  

- **`time_entries`**: A list of timestamped engagement records for the LE.  
- **`LE_type`**: The type of the LE (e.g., Manuscript, Quiz, etc.).  
- **`total_LE_time`**: The total time spent on this specific LE across all recordings.  
- **`LE_completed`**: A Boolean flag indicating whether the student completed the LE based on their recorded engagement.  
- **`LE_completed_timestamp`**: The timestamp of completion.  
- **`LE_coverage`**:  
  A metric indicating the proportion of expected engagement that was met. The evaluation method depends on the LE type:  
  - **Text-based LEs**: Based on estimated reading time.  
  - **Quizzes and exercises**: Determined by LMS submission data (e.g., 8 correct answers on a Quiz with 10 questions -> coverage of 0.8).  
  - **Multimedia (video/audio)**: Derived from video runtime and the recorded interactions with the media player (e.g., play, pause, seek events).  
- **`LE_Consumption_reliable`**:  
  A Boolean flag indicating whether the student's `total_LE_time` falls within a standard deviation of data for their peers.  
  - For example, if a student's engagement time is significantly longer than the other students (e.g., three times the average reading time), their engagement can be considered unreliable due to potential inactivity. Additionally, future work should strive to implement another form of inactivity threshold within the recordings.


# Static data for each semester

The scripts for this data are for the most part stored in timeAnalytics/utils. Everything else is in timeAnalytics/data.

## Config File

path: timeAnalytics/data

Update the config file with your settings, you can look at config_SoSe24.json and config_WiSe_2425.json to get an idea of what you need. You should note any external or broken links in the respective fields to avoid any errors when trying to generate the user_data.json. The filepaths can be left as they are.


```jsonc
{
    // mark as done event filename. file is updated daily by MoodleCron.py / the crontab
    "MAD_csv": "timeAnalytics/data/course_module_completion_updated_WiSe24_25.csv",

    // directory containing all the recording logfiles
    "log_directory": "utils/app/recordings", 

    // output filename for buildUserdata.py
    "export_filename": "timeAnalytics/data/user_data_WiSe_2425.json",

    // output filename for ModuleTypeExporter. maps moduleIDs to moduleTypes
    "module_csv": "timeAnalytics/data/grouped_module_numbers_WiSe_2425.csv",

    // file containing info about plain-text module ids and their word count.
    // Uses text between "Mark as Done" and "Last modified at" strings from the moodle website. 
    "HTML_WORD_COUNTS_CSV": "timeAnalytics/data/word_counts_WISe_2425.csv",

    // file containing info about pdf reading time. output of pdfEstimatedTimetTimeBudget.py
    "PDF_WORD_COUNTS_CSV": "timeAnalytics/data/pdf_word_count_WiSe_2425.csv",

    // cutoff date for the recordings. must include milliseconds. Can use unixtimestamp.com to get the correct number. (len(str(CUTOFF_DATE)) == 13)
    // If timestamp from filename is smaller than this number, it will not be considered for evaluation.
    // currently October 10th as this was when the old course was deleted and no recordings with a faulty moduleID mapping could be included.
    "CUTOFF_DATE": 1728520000000,

    // Start and end dates for each semester to determine semester quantile
    "WINTER_START": "2024-10-01",
    "WINTER_END": "2025-01-22",
    "SUMMER_START": "2024-03-18",
    "SUMMER_END": "2024-07-12",

    // mostly for debugging. ModuleIDs that are still subject to change. Used it to track some module links
    "TBA_FILES": [],

    // in case something is a pdf file, when it is not in a pdf-module-type (ie. an outlier in Lernziel)
    "PDF_FILES": [],

    // any broken files. Mostly same as TBA_FILES but those that will simply be ignored for good
    "NON_EVALUATABLE_FILES": [],

    // external moduleIDs that do not need evaluation. I.e. Wikipedia links or references to an external docs website
    "EXTERNAL_LINKS": [28,44,62,77,80,81,118,139,157,192,261,347,487],

    // in case something is plain text when it should not be. I.e. a Manuscript or Summary not being a pdf.
    "PLAIN_TEXT_MODULES": [115,383],

    // threshold in milliseconds
    // used to check if last mouse-triggered timestamp and end-of-recording timestamp have a notable time diff.
    // uses last mouse-triggered timestamp to determine time spent in a module instead in that case.
    // I.e. when the user switched to another browser tab for over 30 seconds before closing the recording
    "INACTIVITY_THRESHOLD": 30000,

    // delete recordings with very little LE_coverage if the time spent is also smaller than this value (in seconds)
    "MIN_THRESHOLD": 5,

    // determines at what coverage text-based modules are "completed". Affects HTML and PDF modules
    "LE_COMPLETED_THRESHOLD": 0.66,

    // actual coverage needed to complete first page. 
    // Since the unique images are tracked across a pdf, the first page often has a bloated reading time because
    // it contains mutliple logos for the first time. workaround. not all first slides are simple intros. 
    // Might be able to include image size as well in the time budget for future work. 
    // first_page_coverage = min(page_coverage + LE_COMPLETED_THRESHOLD - FIRST_SLIDE_COVERAGE, 1.0)
    "FIRST_SLIDE_COVERAGE": 0.05,

    // which module types are generally PDFs. String comparison with grouped_module_numbers.csv for all of these.
    // NON_HTML_EXERCISES are SUBMISSION_EXERCISES + DOWNLOAD_EXERCISES + PDF_EXERCISES + BROKEN_EXERCISES
    "PDF_MODULES": ["Manuskript", "Zusammenfassung", "Zusatzmaterial Textuell"],
    "HTML_MODULES": ["Lernziel", "Kurzuebersicht"],
    "QUIZ_MODULES": ["Quiz"],
    "EXERCISE_MODULES": ["Uebung"],
    "AUDIO_MODULES": ["Zusatzmaterial Audio"],
    "VIDEO_MODULES": ["Zusatzmaterial Visuell"],


    // outliers in exercises. These are the graded assignments that students can submit (which they tend to not do). 
    // assignment_grades.csv keeps track of the grade results for these each day. 
    "SUBMISSION_EXERCISES": [18,19,20,57,58,72,73,108,381],

    // exercises that prompt a file download.
    "DOWNLOAD_EXERCISES": [123,135,150,170,180,181,197],

    // exercise that is a PDF. Special case that got its own time budget. Hard to come up with a LE threshold for this. Todo for future work.
    "PDF_EXERCISES": [74],
    "STATIC_TIME_BUDGET_FOR_EXERCISE": 15, // 15 second threshold for this special exercise to complete the module

    // used for debugging. Some exercise modules did not load at all at the start of the semester.
    "BROKEN_EXERCISES": [],

    // Output path of moodleCron.py that stores the quiz results for each user.
    "QUIZ_RESULTS": "timeAnalytics/data/quiz_grades_WiSe24_25.csv",

    // Path to ID mapping file for the quiz generated by generateQuizMapping.py. Needs to be done once per semester.
    "QUIZ_MAPPING_FILE": "timeAnalytics/data/quiz_id_mapping_WiSe24_25.csv",

    // Output of moodleCron.py that stores the assignment results for each user.
    "ASSIGNMENT_CSV": "timeAnalytics/data/assignment_grades_WiSe24_25.csv",

    // runtimes of audio and video modules are stored here as well as video amount and individual runtime.
    // wrote this down manually, could probably be automated by having proper access to the videos / crawling through the course and checking the youtube id for the yt api ones. You now need a google dev account to even get video metadata.
    "MEDIA_RUNTIME_CSV": "timeAnalytics/data/media_runtimes_updated.csv",

    // Filepath for the old user_data.json. Used to compare old output with new output each day and send
    // user-ids with updated entries to the moodle db.
    "OLD_FILE_PATH": "timeAnalytics/data/old_user_data.json"
  }
  ```

After changing the config file, you probably need to update the config filepath (they are all set to ```config_WiSe_2425.json```) in buildUserData.py, getWordCountFromLogfile.py, processLogFiles.py, getSemesterQuantile.py, and updateLECompleted.py.

Side note: make sure that no old recordings from prior semesters are in the logfile directory. The IDs of the modules likely change each semester, so trying to evaluate them will lead to faulty data. For WiSe 24/25, the cutoff date was simply set to October 10th.

## Quiz-ID Mapping

path to file: timeAnalytics/data

Fetches the quiz mapping from the imported moodle.sql file

```bash
cd ~/learninganalytics/timeAnalytics/utils
python3 generateQuizMapping.py
```

## grouped_module_numbers.csv (maps module-ids to module-types)

path: timeAnalytics/data

For the first SoSe and WiSe, I had to manually generate this file by checking every learning element and noting down its id and module type in ``moduleIDs.xlsx``. This could probably be automated with some javascript magic by using the website's icon used for each module type and passing the image filename of the icon to the recording filename. To generate the output csv you can use ``ModuleTypeExporter.py`` after adjusting the filepaths to the new Excel file. This is heavily personalised and would require you to copy my layout exactly as it just reads the relevant lines for the moduleIDs.

```bash
cd ~/learninganalytics/timeAnalytics/utils
python3 ModuleTypeExporter.py
```

Either way, it is still a good idea to check the learning elements manually, since some of them can be unexpected (i.e. a non-pdf Summary link, broken files, external links, etc). Some of these outliers can be filtered by checking the url preview when hovering over an element:

If the link contains 'url' it is an external link. 'assign' or 'quiz' stands for assignment and quiz respectively. Note that not all assignment module type modules are actually assignments for Moodle. These would be a submission with a grading system but they are rather just plain-text a lot of the time. If the url contains 'recorder' it is a pdf file. No further distinction could be made in the SoSe and WiSe course via the URLs.

## Update word_counts.csv and pdf_word_counts.csv for each semester

### HTML word count

path: timeAnalytics/data

HTML-word-counts are taken from the recording files. Initial motivation for this was that all the recordings were present and evaluation happened after the exam. A major downside of this approach is that there has to be one recording for each learning element. So you can either decide to update this wordcount file daily before updating the final output, or create one test recording for each text-based element at the start of the semester. I did the latter.

Fill a sample directory with all the recordings for each module id and update the word count via fillSampleDirectory.py for each html module type individually (Learning Goal, Brief Overview, and some Summaries) taking possible outliers into account (the module ids in the global variables, set in the config.json).

After filling the sample directory, turn them into valid json format with jsonValid.py (requires a directory as input).

You can then use getWordCountFromLogfile.py to generate the word_count csv file for non-pdf files: just execute the script. You can check the variables in its main component at the bottom to see if they need some tweaking. This will generate the wordcounts file for non-pdf elements.

```bash
python3 fillSampleDirectory.py
debian@ei-mob-058:~/learninganalytics$ python3 timeAnalytics/utils jsonValid.py utils/sample_recordings/
# uncomment the bottom lines in getWordCountFromLogFile.py, then
python3 getWordCountFromLogfile.py
# comment the lines out again to enable imports in other scripts
```

### PDF word count

path: timeAnalytics/data

Download all the pdf files from the course and add the moduleID at the end of the filename (i.e. Motivation_34.pdf). There should also be a table in the moodle db that could let you skip this process by mapping the pdf filename to a moduleID instead. Note that mostly all Manuscripts, Summaries and Additional text material are PDFs. You can check the url-link for a module and look for the 'recorder' keyword in the link.

Put them into one directory under ```timeAnalytics/data/pdfs```. PDFs for WiSe can be found in the las3 cloud in /HASKI-LFS/Recordings_WiSe24_25. Check the python script to ensure the correct filepath to your pdf directory.

```bash
python3 pdfEstimatedTimeBudget.py
```

This will parse every page of a pdf file and note its moduleID, number of pages, word-count, image-count and estimated reading time per page in ``timeAnalytics/data/pdf_word_count_WiSe2425.csv``.

## Beginning and end of a semester

path of output: timeAnalytics/data

You will probably need to adjust the start and end dates of the semester so they properly reflect the day of the exam in ``timeAnalytics/getSemesterQuantile.py``. These can be changed in the config.json file.


# Install Requirements for the scripts

```bash
 sudo apt-get install python3 python3-pip python3-venv  # Install Python
 sudo apt-get update && sudo apt-get install jq         # Install jq (required for get-db.sh)
 sudo apt update && sudo apt install mariadb-server -y  # Install MariaDB
 git clone https://gitlab.oth-regensburg.de/EI/Labore/las3/haski/learninganalytics.git  # Clone the repository
 cd ~/learninganalytics
 python3 -m venv venv                                   # Set up Python virtual environment
 source venv/bin/activate                               # Activate virtual environment
 pip install mysql-connector-python                    # Install MySQL connector
```

## mariadb

Some notes about the db tables:

```mdl_quiz``` contains the mapping of quiz-ids to their real module-ids. Used in generateQuizMappying.py

```mdl_grades_grades``` contains the results for quiz, assignment and exercises from the exercise course. To only get the relevant quiz results, we use "WHERE `courseid` = 2 AND `itemmodule`= 'quiz';". The courseid is dependent on your concrete setup.

You can check the MoodleCron.py script to see how the daily LA-event data is read from the db.

The updated user_data is sent to and stored in ```mdl_haski_learninganalytics```.

```bash
# start mariadb
 sudo systemctl start mariadb
 sudo systemctl enable mariadb

 sudo mysql -u root --password=""

# create user and db, if not already existing (avoids having to use sudo in crontab)

 CREATE DATABASE moodle_db;
 CREATE USER 'newuser'@'localhost' IDENTIFIED BY 'new_password';
 GRANT ALL PRIVILEGES ON moodle_db.* TO 'newuser'@'localhost';
 FLUSH PRIVILEGES;

# import sql file into mariadb

 cd utils/moodle # Open the moodle directory
 chmod +x cron-job.sh, get-db.sh and fix-moodle-line.sh. # might not be needed
 bash fix-moodle-line.sh # to comment out the first line of the moodle.sql, otherwise it won't work
 bash cron-job.sh # reads daily LA-events from db
```

## unpack and rename recordings

This will unpack all the recording.tar archives for the current semester. Simply takes "winter" or "summer" as parameter and extracts recordings starting from either October or March. If you need a different time range you need to manually copy the .tar archives into a separate directory and unpack them there.
Note that all the pre-october recordings from SoSe24 have been put into the pre_october directory. Backups of summer and winter semester are available from the synology.

```bash
 cd ~/learninganalytics/utils
 bash unpack_init.sh winter # unpacks all recordings for winter semester
 python3 filterLessThanFiveLines.py # removes shorter recording files 
 python3 adjustRealModuleId.py  # renames recordings if module_id in filename does not match module_id in logfile
```

## pip requirements

Note that this only works if you activated the virtual environment beforehand with source /venv/bin/activate.

```bash
 pip install numpy
 pip install requests   # to send the updated student-ID data back to the moodle db
 pip install deepdiff   # to compare old vs new output json files and not send the entire output to db
```

## final command

You can comment out the send_user_data line near the end of the file to locally check the data before writing it into the database. There are also a few print lines that are commented out but could be useful for debugging like:

- if the total time_spent is negative in a recording. Happens when system timestamps are not in sync with user timestamps in short recordings.
- a warning about time_budget for a page in a pdf being 0. May indicate faulty pdf parsing when generating the pdf_word_count CSV file.

Feel free to get an overview of the scripts in timeAnalytics and what they do. updateLECompleted.py is probably the most chaotic one right now, I will try to refactor it a bit to make the program flow clearer. A future work is to also implement a flag in the config file to quickly switch these debug prints on or off.

```bash
cd ~/learninganalytics/timeAnalytics
python3 buildUserData.py
 ```

## recap and what is executed in the crontab

content of ``build-and-send-user-data.sh``:

```bash
 cd learninganalytics
 source venv/bin/activate
 cd utils/moodle
 bash get-db.sh
 bash fix-moodle-line.sh
 bash cron-job.sh
 cd ../
 bash unpack-latest-tar.sh
 cd ../
 python3 filterLessThanFiveLines.py
 python3 adjustRealModuleID.py
 cd timeAnalytics/
 python3 buildUserData.py
 deactivate 
 echo "Script completed successfully on: $(date)"
 ```

## add cron-job.sh to crontab

Edit the daily crontab by adding these lines at the end. Feel free to change these around as you see fit. You could also export and delete the videos right after each other by putting them into one script. Right now, recording data between 3:30 am and 4am is lost. We only delete the recordings on the server if the export was successful. Another thing to note is that DeepDiff is used to fetch updates in the user_data.json. If this is deemed unreliable, you can instead skip the comparison step and simply track the IDs where recordings where generated for each day. This might be necessary, as DeepDiff is somewhat of a blackbox, it does recursive comparisons in the nested structure. There might be cases where it does not work as expected, so keep an eye out for unusual changes.

```bash
crontab -e

# m h  dom mon dow   command
# m h  dom mon dow   command
30 3 * * * bash ~/scripts/export-from-server.sh >> ~/cron_logs/export-from-server.log 2>&1              # export recordings
0 4 * * * bash ~/scripts/delete-from-server.sh >> ~/cron_logs/delete-from-server.log 2>&1               # delete old recordings
30 4 * * * bash ~/scripts/build-and-send-user-data.sh >> ~/cron_logs/build-and-send-user-data.log 2>&1  # update LA
```

The logs for this can be found under ~/cron_logs and are appended to the cron-logfile on each run.

logrotate was set up just to make sure that logfiles don't grow too large.
Currently it is set up to rotate logfiles each week and compress the old logfiles.

The setting for this can be checked or changed with:

```bash
sudo nano /etc/logrotate.d/cron_logs    # or vim, if you prefer ;)

~/cron_logs/*.log {
    weekly                # Rotate logs every week
    rotate 4              # Keep the last 4 weeks of logs
    compress              # Compress old logs
    delaycompress         # Compress logs only after 1 rotation
    missingok             # Ignore errors if logs are missing
    notifempty            # Do not rotate empty logs
    create 644 debian debian # Set permissions for new log files
}
```

## Further notes about the output JSON file and todos

"page 0" in the time_entries part of a user means the user did not scroll at all. Could have decided to add the time to page 1 instead but decided against it since it might be useful for a more granular evaluation of scrolling behavior in the future.
However, during LE_completed evaluation, it simply gets set to page 1 and added there. This could be wrong if browser cache puts the user at a different page and a scrolling event never happens. I could  figure this out when looking at logfiles manually but the dynamic way that the node ids are generated made it nearly impossible to reliably get this correctly. For unknown reasons, the starting page could be set anywhere in the first 5 occurences of related logfile lines (type:3,"source":0 and includes "href" where it would set the current page). Sometimes it instead scrolls down really quickly right at the start of the recording. 

For the scrolling evaluation, the script only starts analyzing the website's mutation after the user has scrolled at least once (type:3,"source":3). The code for this is in the ``get_scrolling_behavior`` function in ``processLogfiles.py``.

For videos that are not youtube-embeds and have more than one video: If the user did not interact with all of the videos on the website, it will probably lead to mismatch between player-id and the time_budget. since the user can freely choose which video to interact with, I have to sort the interactions by player-id. First node to be generated is the first video, next player-node is the second video and so on. For yt-videos, this is simple as the videoID is video-0, video-1, video-2 and so on thanks to the custom event. For dynamically generated rrweb nodes it's not as simple but the code assumes that the ID in the log files sorts the videos from top to bottom. There is a print for this scenario right now in processLogFiles.py. 


For submission type Exercises, the LE_coverage is set to 1.0 if something is submitted at all. This has not been the case this WiSe yet, but did occur a few times in the summer semester (none of the submissions were graded by teachers). Since students already have a dedicated exercise course, they are unlikely to do these optional assignments.

When recordings of any LE type are very short and the LE_coverage of the recording is very small, the entry gets deleted. This is the case why some module entries for a user are empty, since they are initialized and filled earlier but then removed during the evaluation part of the LE_coverage. This is kind of a workaround to further exclude the "quickly open and close" recordings that user might generate.

Currently, pure mouse movement activity not included in the evaluation of LE_coverage. There are a few arguments for this decision, most notably:

    (+) if the user does not interact with the page, no logfile lines are generated anyway
    (+) users can scroll with arrow-keys or other keyboard inputs as well
    (+) smartphones can seemingly only generate TouchMove (swipe) events which are different from MouseMove events.
    (+) using mouse activity as a binary threshold to include recordings would presumbaly filter out a very small amount of recordings but I cannot really think of a case that is not already being caught by the system currently:
        -> short logfiles due to inaction get deleted anyway. 
        -> notable time diff between last user action and end of recording changes time_spent evaluation.
        -> for timestamp extraction, we use all type:3 lines anyway.
        -> video/audio relies on media player events exclusively
        Feel free to let me know of any cases that you can think of!


The recordings on the storage laptop can be a bit cumbersome to work with if there are many of them. One quality of life feature would be to regularly compress all the .tar archives for a semester into one big archive. This was done for SoSe and put into the pre_october directory. The individual archives still exist there alongside the tar.gz file because I needed easier individual access for debugging purposes. For future use though, it is a good idea to do aggregate and archive or delete the individual recording.tar archives after each semester. Backups for SoSe and WiSe exist so the existing recordings can be deleted from the backup device. WiSe includes recordings up to 27.01.2025.
