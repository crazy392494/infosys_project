import requests
import json
import sys
import time

# Force UTF-8 stdout
sys.stdout.reconfigure(encoding='utf-8')

url = "https://job-search-global.p.rapidapi.com/latest_jobs.php"

headers = {
	"Content-Type": "application/x-www-form-urlencoded",
	"x-rapidapi-host": "job-search-global.p.rapidapi.com",
	"x-rapidapi-key": "db72a492d5mshee54c5f3acf06aap1bd121jsn3dadf64fa3a3"
}

print("Sleeping 2s to avoid rate limits...")
time.sleep(2)

try:
    response = requests.post(url, headers=headers, timeout=15)
    
    try:
        data = response.json()
        if isinstance(data, list):
            if len(data) > 0:
                print("ROOT IS LIST. First item keys:", list(data[0].keys()))
                print("First item sample:", json.dumps(data[0], indent=2)[:300])
            else:
                print("ROOT IS EMPTY LIST")
        elif isinstance(data, dict):
            print("ROOT IS DICT. Keys:", list(data.keys()))
            if 'data' in data:
                 print("DATA Keys:", list(data['data'][0].keys()) if len(data['data']) > 0 else "Empty Data")
            if 'jobs' in data:
                 print("JOBS Keys:", list(data['jobs'][0].keys()) if len(data['jobs']) > 0 else "Empty Jobs")
    except:
        print("NOT JSON. First 200 chars:", response.text[:200])

except Exception as e:
    print(f"Error: {e}")
