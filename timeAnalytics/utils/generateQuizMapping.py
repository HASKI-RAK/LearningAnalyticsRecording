import mysql.connector
import csv

# Database connection details
db_config = {
    'user': 'newuser',             # replace with your new username
    'password': 'new_password',     # replace with your new password
    'host': 'localhost',
    'database': 'moodle_db'
}

# Initialize cursor and connection
conn = None
cursor = None

try:
    # Connect to the database
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Query to get quiz_id and course_module_id
    query = """
    SELECT q.id AS moodle_quiz_id, cm.id AS quiz_module_id, q.grade AS max_grade
    FROM mdl_course_modules cm
    JOIN mdl_quiz q ON cm.instance = q.id
    WHERE cm.module = 17;
    """
    
    # Execute the query
    cursor.execute(query)
    
    # Fetch all results
    results = cursor.fetchall()

    # Define CSV file path
    csv_file_path = 'timeAnalytics/data/quiz_id_mapping_WiSe24_25.csv'

    # Write results to CSV
    with open(csv_file_path, mode='w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        # Write the header
        csv_writer.writerow(['moodle_quiz_id', 'quiz_module_id', 'max_grade'])
        
        # Write the data
        for row in results:
            csv_writer.writerow(row)

    print(f"Data successfully written to {csv_file_path}")

except mysql.connector.Error as err:
    print(f"Error: {err}")

finally:
    # Close the cursor and connection if they were created
    if cursor is not None:
        cursor.close()
    if conn is not None:
        conn.close()