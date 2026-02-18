import requests
import json
import sys

# Force UTF-8 stdout
sys.stdout.reconfigure(encoding='utf-8')

url = "https://job-search-global.p.rapidapi.com/latest_jobs.php"

headers = {
	"Content-Type": "application/x-www-form-urlencoded",
	"x-rapidapi-host": "job-search-global.p.rapidapi.com",
	"x-rapidapi-key": "db72a492d5mshee54c5f3acf06aap1bd121jsn3dadf64fa3a3"
}

print(f"Testing {url}")
try:
    response = requests.post(url, headers=headers, timeout=10)
    print(f"STATUS: {response.status_code}")
    
    try:
        data = response.json()
        print("JSON KEYS:", list(data.keys()))
        if 'message' in data:
            print("MESSAGE:", data['message'])
        if 'error' in data:
             print("ERROR:", data['error'])
        
        # Check for job list structure
        if isinstance(data, list) and len(data) > 0:
             print("FIRST JOB:", json.dumps(data[0], indent=2))
        elif 'data' in data and isinstance(data['data'], list) and len(data['data']) > 0:
             print("FIRST JOB:", json.dumps(data['data'][0], indent=2))
        elif 'jobs' in data and isinstance(data['jobs'], list) and len(data['jobs']) > 0:
             print("FIRST JOB:", json.dumps(data['jobs'][0], indent=2))
        else:
             print("FULL JSON:", json.dumps(data, indent=2))

    except Exception as e:
        print("NOT JSON:", response.text[:200])

except Exception as e:
    print(f"EXCEPTION: {e}")
