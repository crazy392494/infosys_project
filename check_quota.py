import requests
import sys
import os

# Force UTF-8 stdout
sys.stdout.reconfigure(encoding='utf-8')

url = "https://job-search-global.p.rapidapi.com/latest_jobs.php"

RAPIDAPI_KEY = os.getenv('RAPIDAPI_KEY', '')
if not RAPIDAPI_KEY:
    print("ERROR: Set RAPIDAPI_KEY environment variable before running this script.")
    sys.exit(1)

headers = {
	"x-rapidapi-host": "job-search-global.p.rapidapi.com",
	"x-rapidapi-key": RAPIDAPI_KEY
}

print("Checking API quota status...")
try:
    response = requests.post(url, headers=headers, timeout=10)
    print(f"Status: {response.status_code}")
    print(f"Headers: {response.headers}") # RapidAPI often sends x-ratelimit-requests-remaining
    print(f"Response Body: {response.text}")
except Exception as e:
    print(f"Error: {e}")
