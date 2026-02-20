"""
Live Job Search API Integration
Fetches real-time job postings from Job Search Global (RapidAPI)
"""

import os
import requests
import random
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from config import (
    ADZUNA_APP_ID, 
    ADZUNA_API_KEY, 
    RAPIDAPI_KEY,
    JOB_SEARCH_GLOBAL_HOST,
    ACTIVE_JOBS_DB_KEY,
    ACTIVE_JOBS_DB_HOST,
    DEFAULT_COUNTRY, 
    DEFAULT_LOCATION,
    JOBS_PER_PAGE,
    MAX_JOB_AGE_DAYS
)

class BaseJobSearch:
    """Base class for job search providers"""
    
    def search_jobs(self, keywords: List[str], location: str, max_results: int) -> List[Dict[str, Any]]:
        raise NotImplementedError
    
    def _calculate_days_ago(self, date_str: str) -> int:
        """Calculate days since posting"""
        try:
            if not date_str: return 0
            # Handle various date formats
            posted_date = None
            try:
                posted_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            except:
                try:
                    posted_date = datetime.strptime(date_str, "%Y-%m-%d")
                except:
                    pass
            
            if posted_date:
                if posted_date.tzinfo:
                    days = (datetime.now(posted_date.tzinfo) - posted_date).days
                else:
                    days = (datetime.now() - posted_date).days
                return max(0, days)
        except:
            return 0
        return 0
        
    def _format_salary(self, min_sal, max_sal):
        if min_sal and max_sal:
            return f"${int(min_sal):,} - ${int(max_sal):,}"
        return "Not specified"

class AdzunaJobSearch(BaseJobSearch):
    """Adzuna API Provider"""
    
    def __init__(self):
        self.app_id = ADZUNA_APP_ID
        self.api_key = ADZUNA_API_KEY
        self.base_url = f"https://api.adzuna.com/v1/api/jobs/{DEFAULT_COUNTRY}/search"
        self.is_configured = bool(self.app_id and self.api_key)
    
    def search_jobs(self, keywords: List[str], location: str, max_results: int) -> List[Dict[str, Any]]:
        if not self.is_configured:
            return []
            
        try:
            query = ' OR '.join(keywords[:5])
            params = {
                'app_id': self.app_id,
                'app_key': self.api_key,
                'results_per_page': max_results,
                'what': query,
                'where': location,
                'content-type': 'application/json',
                'max_days_old': MAX_JOB_AGE_DAYS
            }
            
            response = requests.get(self.base_url + '/1', params=params, timeout=10)
            if response.status_code != 200:
                return []
                
            data = response.json()
            jobs = []
            
            for result in data.get('results', []):
                jobs.append(self._parse_job(result))
                
            return jobs
        except Exception as e:
            print(f"Adzuna Error: {e}")
            return []

    def _parse_job(self, result: Dict) -> Dict[str, Any]:
        """Parse Adzuna job"""
        return {
            'title': result.get('title', 'N/A'),
            'company': result.get('company', {}).get('display_name', 'N/A'),
            'location': result.get('location', {}).get('display_name', 'N/A'),
            'description': result.get('description', ''),
            'salary': self._format_salary(result.get('salary_min'), result.get('salary_max')),
            'url': result.get('redirect_url', '#'),
            'posted_date': result.get('created', ''),
            'days_ago': self._calculate_days_ago(result.get('created', '')),
            'contract_type': result.get('contract_type', 'Full-time'),
            'source': 'Adzuna',
            'easy_apply': False 
        }

class JobSearchGlobalProvider(BaseJobSearch):
    """Job Search Global API via RapidAPI (PrineshPatel)"""
    
    def __init__(self):
        # Support multiple keys for fallback
        env_keys = RAPIDAPI_KEY.split(',') if RAPIDAPI_KEY else []
        self.api_keys = [k.strip() for k in env_keys if k.strip()]
        
        # No hardcoded fallback key — set RAPIDAPI_KEY env variable or add to .streamlit/secrets.toml
            
        self.host = JOB_SEARCH_GLOBAL_HOST
        self.is_configured = bool(self.api_keys and self.host)
        self.search_url = f"https://{self.host}/search.php" 
        self.latest_url = f"https://{self.host}/latest_jobs.php"
        
    def search_jobs(self, keywords: List[str], location: str, max_results: int) -> List[Dict[str, Any]]:
        if not self.is_configured:
            return []
            
        # Try each key until successful
        for i, key in enumerate(self.api_keys):
            try:
                result = self._search_with_key(key, keywords, location, max_results)
                if result:
                    if i > 0:
                        print(f"✅ Success with fallback key #{i+1}")
                    return result
            except Exception as e:
                print(f"⚠️ Key #{i+1} failed: {e}")
                continue
                
        print("❌ All API keys failed or quota exceeded.")
        return []

    def _search_with_key(self, api_key: str, keywords: List[str], location: str, max_results: int) -> List[Dict[str, Any]]:
        query = ' '.join(keywords[:3])
        
        headers = {
            "x-rapidapi-key": api_key,
            "x-rapidapi-host": self.host,
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        # Try search endpoint first
        try:
            payload = {"keyword": query, "location": location}
            response = requests.post(self.search_url, headers=headers, data=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) or (isinstance(data, dict) and ('data' in data or 'jobs' in data)):
                    return self._process_response(data, max_results)
        except:
            pass 
            
        # Fallback to latest_jobs.php
        response = requests.post(self.latest_url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            # Raise error to trigger next key (except for 404 which is weird)
            raise Exception(f"API request failed with status {response.status_code}")
            
        data = response.json()
        
        # Check for specific quota error messages in 200 OK responses (common in RapidAPI)
        if isinstance(data, dict) and 'message' in data and 'exceeded' in data['message'].lower():
            raise Exception("Quota exceeded")
            
        return self._process_response(data, max_results)
            
    def _process_response(self, data: Any, max_results: int) -> List[Dict[str, Any]]:
        results = []
        if isinstance(data, list):
            results = data
        elif isinstance(data, dict):
            if 'data' in data: results = data['data']
            elif 'jobs' in data: results = data['jobs']
            
        jobs = []
        for job in results:
            jobs.append(self._parse_job(job))
            
        return jobs[:max_results]

    def _parse_job(self, job: Dict) -> Dict[str, Any]:
        """Parse generic job object from Job Search Global"""
        
        # Robust parsing for various possible keys
        title = job.get('title') or job.get('job_title') or job.get('jobTitle') or 'N/A'
        
        company = 'N/A'
        if 'company' in job and isinstance(job['company'], str):
            company = job['company']
        elif 'company_name' in job:
            company = job['company_name']
        elif 'company' in job and isinstance(job['company'], dict):
            company = job['company'].get('name', 'N/A')
            
        location = job.get('location') or job.get('job_location') or 'Remote'
        url = job.get('url') or job.get('job_url') or job.get('link') or '#'
        
        # Handle slug if present
        if url == '#' and 'slug' in job:
             # Make a best guess URL if slug is present but URL isn't
             url = f"https://www.google.com/search?q={title}+{company}"
        
        date_str = job.get('date') or job.get('posted_date') or job.get('date_posted') or datetime.now().isoformat()
        
        # Determine source
        source = 'Job Board'
        url_lower = url.lower()
        if 'linkedin' in url_lower: source = 'LinkedIn'
        elif 'indeed' in url_lower: source = 'Indeed'
        elif 'ziprecruiter' in url_lower: source = 'ZipRecruiter'
        elif 'glassdoor' in url_lower: source = 'Glassdoor'
        elif 'naukri' in url_lower: source = 'Naukri'
        
        return {
            'title': title,
            'company': company,
            'location': location,
            'description': job.get('description') or job.get('summary') or title,
            'salary': job.get('salary') or "See job post",
            'url': url,
            'posted_date': date_str,
            'days_ago': self._calculate_days_ago(date_str),
            'contract_type': 'Full-time',
            'source': source,
            'easy_apply': False
        }

class ActiveJobsDBProvider(BaseJobSearch):
    """
    Active Jobs DB via RapidAPI
    Endpoint: GET https://active-jobs-db.p.rapidapi.com/modified-ats-24h
    Returns real-time ATS job postings updated every 24 hours.
    """

    def __init__(self):
        self.api_key = ACTIVE_JOBS_DB_KEY
        self.host    = ACTIVE_JOBS_DB_HOST
        self.base_url = f"https://{self.host}/modified-ats-24h"
        self.is_configured = bool(self.api_key)

    def search_jobs(self, keywords: List[str], location: str, max_results: int) -> List[Dict[str, Any]]:
        if not self.is_configured:
            return []

        try:
            headers = {
                "x-rapidapi-key":  self.api_key,
                "x-rapidapi-host": self.host,
            }
            params = {
                "limit":            min(max_results * 3, 500),  # fetch extra so we can filter
                "offset":           0,
                "description_type": "text",
            }
            response = requests.get(self.base_url, headers=headers, params=params, timeout=15)

            if response.status_code != 200:
                print(f"ActiveJobsDB Error: HTTP {response.status_code}")
                return []

            data = response.json()

            # API returns a list directly or dict with a key
            if isinstance(data, list):
                raw_jobs = data
            elif isinstance(data, dict):
                raw_jobs = data.get('data', data.get('jobs', []))
            else:
                return []

            # Keyword filter (client-side since API has no keyword filter)
            kw_lower = [k.lower() for k in keywords]
            filtered = []
            for job in raw_jobs:
                title = (job.get('title') or '').lower()
                desc  = (job.get('description') or '').lower()
                if any(k in title or k in desc for k in kw_lower):
                    filtered.append(job)

            # Fall back to all jobs if nothing matched
            results = filtered if filtered else raw_jobs
            return [self._parse_job(j) for j in results[:max_results]]

        except Exception as e:
            print(f"ActiveJobsDB Error: {e}")
            return []

    def _parse_job(self, job: Dict) -> Dict[str, Any]:
        """Normalise an Active Jobs DB job record to the app's common schema."""
        title   = job.get('title') or job.get('job_title') or 'N/A'
        company = job.get('company') or job.get('organization') or job.get('company_name') or 'N/A'
        location = (
            job.get('location') or
            job.get('job_location') or
            (', '.join(filter(None, [job.get('city'), job.get('state'), job.get('country')]))) or
            'Remote'
        )
        url = (
            job.get('url') or
            job.get('job_url') or
            job.get('apply_url') or
            job.get('link') or '#'
        )
        date_str = (
            job.get('date_posted') or
            job.get('posted_date') or
            job.get('date') or
            datetime.now().isoformat()
        )
        description = job.get('description') or job.get('summary') or title
        # Active Jobs DB often gives very long descriptions — trim for display
        if len(description) > 600:
            description = description[:597] + '...'

        # Determine source platform from URL
        source  = 'Active Jobs DB'
        url_low = url.lower()
        if 'linkedin'     in url_low: source = 'LinkedIn'
        elif 'indeed'     in url_low: source = 'Indeed'
        elif 'glassdoor'  in url_low: source = 'Glassdoor'
        elif 'ziprecruiter' in url_low: source = 'ZipRecruiter'
        elif 'lever.co'   in url_low: source = 'Lever'
        elif 'greenhouse' in url_low: source = 'Greenhouse'
        elif 'workday'    in url_low: source = 'Workday'
        elif 'ashby'      in url_low: source = 'Ashby'

        return {
            'title':         title,
            'company':       company,
            'location':      location,
            'description':   description,
            'salary':        job.get('salary') or job.get('salary_range') or 'See job post',
            'url':           url,
            'posted_date':   date_str,
            'days_ago':      self._calculate_days_ago(date_str),
            'contract_type': job.get('employment_type') or job.get('job_type') or 'Full-time',
            'source':        source,
            'easy_apply':    False,
        }


class JobSearchAPI:
    """Composite Job Search Manager"""
    
    def __init__(self):
        self.providers = []

        # Active Jobs DB (Primary — fresh ATS postings every 24h)
        active_jobs = ActiveJobsDBProvider()
        if active_jobs.is_configured:
            self.providers.append(active_jobs)
            print("✅ Active Jobs DB provider ready")

        # Job Search Global (Secondary)
        global_search = JobSearchGlobalProvider()
        if global_search.is_configured:
            self.providers.append(global_search)

        # Adzuna (Fallback)
        adzuna = AdzunaJobSearch()
        if adzuna.is_configured:
            self.providers.append(adzuna)

        self.is_configured = len(self.providers) > 0

        if not self.is_configured:
            print("⚠️ No job search APIs configured. Using mock data.")

    def search_jobs(
        self, 
        keywords: List[str], 
        location: str = DEFAULT_LOCATION,
        max_results: int = JOBS_PER_PAGE,
        remote_only: bool = False,
        min_salary: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        
        if not self.is_configured:
            return self._get_mock_jobs(keywords)
            
        all_jobs = []
        jobs_per_provider = max(5, max_results)
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            future_to_provider = {
                executor.submit(p.search_jobs, keywords, location, jobs_per_provider): p 
                for p in self.providers
            }
            
            for future in as_completed(future_to_provider):
                try:
                    jobs = future.result()
                    all_jobs.extend(jobs)
                except Exception as e:
                    print(f"Provider failed: {e}")
        
        # Deduplication
        unique_jobs = {job['url']: job for job in all_jobs}.values()
        final_jobs = list(unique_jobs)
        final_jobs.sort(key=lambda x: x.get('days_ago', 999))
        
        # Fallback to mock data if no jobs found (e.g. API quota exceeded)
        if not final_jobs:
            print("⚠️ No live jobs found (check API quota). Using mock data.")
            return self._get_mock_jobs(keywords)
            
        return final_jobs[:max_results]

    def _get_mock_jobs(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """Return mock job data when API is not configured"""
        keyword_str = keywords[0] if keywords else "Software"
        encoded_keyword = requests.utils.quote(keyword_str)
        
        return [
            {
                'title': f'Senior {keyword_str} Engineer',
                'company': 'TechCorp Solutions',
                'location': 'Remote',
                'description': f'Looking for an experienced {keyword_str} engineer to join our team. Easy Apply available!',
                'salary': '$100,000 - $150,000',
                'url': f'https://www.linkedin.com/jobs/search/?keywords={encoded_keyword}',
                'posted_date': datetime.now().isoformat(),
                'days_ago': 2,
                'contract_type': 'Full-time',
                'source': 'LinkedIn',
                'easy_apply': True
            },
            {
                'title': f'{keyword_str} Developer',
                'company': 'Innovation Labs',
                'location': 'San Francisco, CA',
                'description': f'Join our team as a {keyword_str} developer working on cutting-edge projects...',
                'salary': '$90,000 - $130,000',
                'url': f'https://www.indeed.com/jobs?q={encoded_keyword}',
                'posted_date': datetime.now().isoformat(),
                'days_ago': 5,
                'contract_type': 'Full-time',
                'source': 'Indeed',
                'easy_apply': False
            },
            {
                'title': f'Junior {keyword_str} Engineer',
                'company': 'StartupXYZ',
                'location': 'New York, NY',
                'description': f'Entry-level {keyword_str} position with growth opportunities. Quick Apply now!',
                'salary': '$70,000 - $90,000',
                'url': f'https://www.glassdoor.com/Job/jobs.htm?sc.keyword={encoded_keyword}',
                'posted_date': (datetime.now() - timedelta(days=1)).isoformat(),
                'days_ago': 1,
                'contract_type': 'Full-time',
                'source': 'Glassdoor',
                'easy_apply': True
            }
        ]

# Global job search instance
_job_api = None

def get_job_api() -> JobSearchAPI:
    """Get or create job API singleton"""
    global _job_api
    if _job_api is None:
        _job_api = JobSearchAPI()
    return _job_api
