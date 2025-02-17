import os

def clean_directory(directory_path):
    """removes files with less than five lines.

    Args:
        directory_path (str): path to the recording directory
    """
    # Iterate over every file in the directory
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)

        '''#check if the file does not end with .log and delete it if so
        if not filename.endswith(".log"):
            try:
                os.remove(file_path)
                print(f"Removed non-log file: {filename}")
            except OSError as e:
                print(f"Error removing file {filename}: {e}")
            continue
            '''
        # Check if file has fewer than 5 lines and delete if so
        try:
            with open(file_path, 'r') as file:
                lines = file.readlines()
                if len(lines) < 5:
                    os.remove(file_path)
                    print(f"Removed short file: {filename}")
        except IOError as e:
            print(f"Error reading file {filename}: {e}")

# Usage
directory_path = "utils/app/recordings"
clean_directory(directory_path)
