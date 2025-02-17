import json
import requests

def send_user_data(file_path, changed_user_ids):
    # Load the user_data.json file
    with open(file_path, 'r') as file:
        user_data = json.load(file)
    
    # Moodle API endpoint and token
    url = "YYYYYYYYYYYYYYY" # hidden
    token = "XXXXXXXXXXXXX" # hidden
    function_name = "post_learninganalytics"

    # Iterate over each user_id and their data
    for user_id, data in user_data.items():
        if user_id in changed_user_ids:
            # Convert user data to a JSON string, then URL-encode it for safe transmission
            data_string = json.dumps(data)
            
            # Payload for the POST request
            payload = {
                "wstoken": token,
                "wsfunction": function_name,
                "moodlewsrestformat": "json",
                "user_id": user_id,
                "learninganalytics": data_string
            }   
            
            # Sending the POST request
            response = requests.post(url, data=payload)
            
            # Checking the response
            if response.status_code == 200:
                print(f"Request was successful for user {user_id}!")
                print("Response JSON:", response.json())  # Assuming the response is in JSON format
            else:
                print("Request failed with status code:", response.status_code)
                print("Response text:", response.text)
    print("sent all data")

# Usage
#send_user_data("/home/rico/learninganalytics/timeAnalytics/data/user_data_WiSe_2425.json")
#print("sent user data")
