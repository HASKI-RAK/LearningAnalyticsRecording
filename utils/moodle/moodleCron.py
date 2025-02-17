import mysql.connector
import csv
import json
import os

# Database connection details
db_config = {
    'user': 'newuser',               
    'password': 'new_password',                    
    'host': 'localhost',
    'database': 'moodle_db'
}

# Initialize cursor and connection
conn = None
cursor = None



def fetch_and_write_completion_data(cursor, csv_file_path):
    """Fetch course module completion data and write it to a CSV file."""
    query = """
    SELECT userid, contextinstanceid, timecreated, other
    FROM mdl_logstore_standard_log
    WHERE eventname = %s 
    AND courseid = %s
    """
    
    # Execute the query with parameters for eventname and courseid
    cursor.execute(query, ('\\core\\event\\course_module_completion_updated', '2'))
    
    # Fetch all results
    results = cursor.fetchall()

    # Write results to CSV
    with open(csv_file_path, mode='w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        # Write the header
        csv_writer.writerow(['userid', 'contextinstanceid', 'timecreated', 'completionstate'])
        
        # Write the data, parsing 'other' JSON field for 'completionstate'
        for row in results:
            userid, contextinstanceid, timecreated, other = row
            other_data = json.loads(other)
            completionstate = other_data.get('completionstate')
            if completionstate == 1:  # Filter for completionstate == 1
                csv_writer.writerow([userid, contextinstanceid, timecreated, completionstate])

    print(f"Completion data successfully written to {csv_file_path}")


def fetch_and_write_quiz_grades(cursor, csv_file_path):
    """Fetch quiz grades data and write it to a CSV file."""
    query = """
    SELECT id, quiz, userid, grade, timemodified
    FROM mdl_quiz_grades
    """
    
    # Execute the query
    cursor.execute(query)
    
    # Fetch all results
    results = cursor.fetchall()

    # Write results to CSV
    with open(csv_file_path, mode='w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        # Write the header
        csv_writer.writerow(['id', 'quiz', 'userid', 'grade', 'timemodified'])
        
        # Write the data
        for row in results:
            csv_writer.writerow(row)

    print(f"Quiz grades successfully written to {csv_file_path}")


def fetch_and_write_assignment_grades(cursor, csv_file_path):
    """Fetch assignment grades data and write it to a CSV file with required columns only."""
    query = """
    SELECT assignment, userid, timemodified, grade
    FROM mdl_assign_grades
    """
    
    cursor.execute(query)
    results = cursor.fetchall()

    with open(csv_file_path, mode='w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['assignment', 'userid', 'timemodified', 'grade'])
        
        for row in results:
            assignment, userid, timemodified, grade = row
            csv_writer.writerow([assignment, userid, timemodified, round(float(grade), 2)])

    print(f"Assignment grades successfully written to {csv_file_path}")


try:
    # Connect to the database
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Define CSV file paths
    data_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../timeAnalytics/data'))
    completion_csv_file_path = os.path.join(data_directory, 'course_module_completion_updated_WiSe24_25.csv')
    quiz_grades_csv_file_path = os.path.join(data_directory, 'quiz_grades_WiSe24_25.csv')
    assignment_grades_csv_file_path = os.path.join(data_directory, 'assignment_grades_WiSe24_25.csv')

    fetch_and_write_completion_data(cursor, completion_csv_file_path)
    fetch_and_write_quiz_grades(cursor, quiz_grades_csv_file_path)
    fetch_and_write_assignment_grades(cursor, assignment_grades_csv_file_path)

except mysql.connector.Error as err:
    print(f"Error: {err}")

finally:
    # Close the cursor and connection if they were created
    if 'cursor' in locals() and cursor is not None:
        cursor.close()
    if 'conn' in locals() and conn is not None:
        conn.close()
