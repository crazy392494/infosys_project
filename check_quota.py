import requests
import sys

# Force UTF-8 stdout
sys.stdout.reconfigure(encoding='utf-8')

url = "https://job-search-global.p.rapidapi.com/latest_jobs.php"

headers = {
	"x-rapidapi-host": "job-search-global.p.rapidapi.com",
	"x-rapidapi-key": "db72a492d5mshee54c5f3acf06aap1bd121jsn3dadf64fa3a3"
}

print("Checking API quota status...")
try:
    response = requests.post(url, headers=headers, timeout=10)
    print(f"Status: {response.status_code}")
    print(f"Headers: {response.headers}") # RapidAPI often sends x-ratelimit-requests-remaining
    print(f"Response Body: {response.text}")
except Exception as e:
    print(f"Error: {e}")
