import sys
import os

# turns recording logfiles to valid json by adding commas in every line except the last one and adding brackets [] at start and end

def add_commas_to_log(input_file):
    try:
        with open(input_file, 'r') as infile:
            lines = infile.readlines()
            
        # Open the same file for writing (overwrite mode)
        with open(input_file, 'w') as outfile:
            # Write the opening bracket
            outfile.write('[\n')
            
            # Process all lines except the last one
            for line in lines[:-1]:
                stripped_line = line.strip()
                if stripped_line:
                    outfile.write(stripped_line + ',\n')
            
            # Process the last line without adding a comma
            last_line = lines[-1].strip()
            if last_line:
                outfile.write(last_line + '\n')
            
            # Write the closing bracket
            outfile.write(']\n')
        
        print(f"JSON format has been corrected and saved to {input_file}")
    
    except Exception as e:
        print(f"Error processing the file: {e}")

def process_directory(directory):
    try:
        for filename in os.listdir(directory):
            # Only process files with .log extension
            if filename.endswith(".log"):
                file_path = os.path.join(directory, filename)
                add_commas_to_log(file_path)
    
    except Exception as e:
        print(f"Error processing directory {directory}: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 format_log_to_json.py <directory>")
        sys.exit(1)
    
    directory = sys.argv[1]
    
    if os.path.isdir(directory):
        process_directory(directory)
    else:
        print(f"Directory not found: {directory}")
