import json
import os
import csv
import ast

with open('timeAnalytics/data/config_WiSe_2425.json', 'r') as f:
    config = json.load(f)
    HTML_WORD_COUNTS_CSV = config['HTML_WORD_COUNTS_CSV']
    PDF_WORD_COUNTS_CSV = config['PDF_WORD_COUNTS_CSV']

def get_word_count_from_logfile(filename):
    """fetches word count from a given logfile and tries to only get the relevant text from the html site.
    Starts at the 'Mark as Done' button above the text and stops at "last modified at" text since that is at the end of the page.
    Thus ignoring all the navigation modules and links to the other course elements that are in the side panel and take up large amount of space in the logfiles.
    Somewhat of a rough prototype and can probably be improved by understanding logfiles more.

    Args:
        filename (str): the file that should be evaluated

    Returns:
        the word count for this file.
    """
    textContents = []
    start_counting = False  # Flag to track when to start counting words

    with open(filename, 'r', encoding='utf-8') as file:
        logfile_content = file.read()

    data = json.loads(logfile_content)

    def extract_text_content(node):
        nonlocal start_counting  # Reference the outer variable

        if isinstance(node, dict):
            if 'textContent' in node:
                content = node['textContent'].strip()

                # Stop processing if "Last modified at" is found
                if 'Last modified' in content:
                    return True  # Signal to stop processing further

                # Start processing after finding 'Mark as done' or 'Done'
                if 'Mark as done' in content or content == 'Done':
                    start_counting = True

                # If counting has started, add content
                if start_counting and content:
                    textContents.append(content)

            # Recursively search child nodes
            for key in node:
                if extract_text_content(node[key]):
                    return True  # Stop processing if "Last modified at" was found

        elif isinstance(node, list):
            for item in node:
                if extract_text_content(item):
                    return True  # Stop processing if "Last modified at" was found
    
    # Start extracting text content from the JSON structure
    extract_text_content(data)
    
    # Combine all text content into one string
    combined_text = ' '.join(textContents)
    
    # Split by whitespace to count words
    word_count = len(combined_text.split())
    
    return word_count


def get_word_count_from_csv(module_id, is_pdf):
    """function to fetch the word count of a given module from the word_count csv file. Can be either plain text or pdf file

    Args:
        module_id (int): integer that represents the current module
        is_pdf (bool): boolean to determine if the word count should be fetched from the pdf or the generic word count csv file

    Returns:
        integer or dict containing the word count (and time budget if pdf) for this module id. Returns None if module_id cannot be found in the csv file.
    """
    if not is_pdf:
        csv_file = HTML_WORD_COUNTS_CSV
        #csv_file = 'timeAnalytics/data/word_counts.csv'
    else:
        csv_file = PDF_WORD_COUNTS_CSV
        #csv_file = 'timeAnalytics/data/pdf_word_count_WiSe_2425.csv'
    with open(csv_file, 'r') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip header row

        for row in reader:
            if not is_pdf:
                if int(row[0]) == module_id:
                    return int(row[1])
            else: # fetch pdf_word_count
                if row[0].endswith(f'_{module_id}.pdf'):
                    time_per_page = ast.literal_eval(row[3]) if row[3] else []
                    return {
                        'Word Count':int(row[1]),
                        'Num Pages':int(row[4]),
                        'Time per Page': [time * 60 for time in time_per_page],
                        'Time Budget':float(row[5])*60,
                        'Height':float(row[6])
                    }
    return None  # Return None if module_id is not found


def save_word_count_to_csv(directory, output_csv):
    word_counts = []

    for root, _, files in os.walk(directory):
        for file in files:
            parts = file.split('_')
            module_id = parts[1].split('.')[0]  # module_id is the second part of the filename
            filepath = os.path.join(root, file)
            word_count = get_word_count_from_logfile(filepath)
            word_counts.append((module_id, word_count))

    # Save the word counts to a CSV file
    with open(output_csv, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Module ID', 'Word Count'])
        writer.writerows(word_counts)
        print(f"Successfully saved the word counts to {output_csv}")


if __name__ == "__main__":
    # Example usage: iterate through sample_recording directory and fetch the word count for every module_id there
    directory = 'utils/sample_recordings_WiSe_2425'
    output_csv = HTML_WORD_COUNTS_CSV
    save_word_count_to_csv(directory, output_csv)       

