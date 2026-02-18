import sys
import os
import time

# Add current directory to path
sys.path.append('c:/Users/Windows/infosys')

def log(msg):
    print(msg)
    sys.stdout.flush()

try:
    from job_search_api import JobSearchGlobalProvider
except ImportError as e:
    log(f"Import Error: {e}")
    sys.exit(1)

log("Initializing Provider...")
try:
    provider = JobSearchGlobalProvider()
    log(f"Configured: {provider.is_configured}")
    
    if provider.api_key:
        mask_key = provider.api_key[:5] + "..." + provider.api_key[-5:] if len(provider.api_key) > 10 else "SHORT_KEY"
        log(f"API Key: {mask_key}")
    else:
        log("API Key: None")
        
    log(f"Host: {provider.host}")

    log("Starting search...")
    keywords = ["python"]
    location = "remote"
    
    log(f"Calling search_jobs with keywords={keywords}, location={location}")
    jobs = provider.search_jobs(keywords, location, 5)
    
    log(f"Search completed. Found {len(jobs)} jobs")
    
    if len(jobs) > 0:
        log(f"First job title: {jobs[0].get('title', 'N/A')}")
        log(f"First job source: {jobs[0].get('source', 'N/A')}")
        desc = jobs[0].get('description', '')
        log(f"First job desc: {desc[:50]}")
    else:
        log("No jobs found (list empty)")
        
except Exception as e:
    log(f"EXCEPTION in Execution: {e}")
    import traceback
    traceback.print_exc()
