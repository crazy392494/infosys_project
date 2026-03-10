"""
Job Matching and Recommendation Engine
Matches resume skills with job requirements and ranks opportunities
Enhanced with live API integration
"""

from typing import List, Dict, Any, Set
from database import get_all_jobs, save_recommendations, get_latest_analysis


def normalize_skill(skill: str) -> str:
    """Normalize skill name for better matching"""
    return skill.lower().strip()


def extract_skills_from_description(description: str, title: str = '') -> List[str]:
    """
    Highly robust skill extraction.
    """
    import re
    def normalize(t):
        return re.sub(r'[^a-z0-9+# ]', ' ', t.lower().replace('-', ' ')).strip()

    full_text = normalize(f"{title} {description}")
    found = set()
    
    # Core technical keywords
    core_tech = {
        'python', 'java', 'javascript', 'typescript', 'react', 'angular', 'node', 
        'html', 'css', 'sql', 'mysql', 'postgresql', 'aws', 'docker', 'devops',
        'backend', 'frontend', 'data science', 'api', 'rest', 'git', 'ui', 'ux', 'web'
    }
    
    # Attempt to import more from config
    try:
        from config import TECHNICAL_SKILLS, SOFT_SKILLS
        all_skills = set(TECHNICAL_SKILLS) | set(SOFT_SKILLS) | core_tech
    except:
        all_skills = core_tech
        
    for skill in all_skills:
        s_norm = normalize(skill)
        if f" {s_norm} " in f" {full_text} " or full_text.startswith(s_norm) or full_text.endswith(s_norm):
            found.add(skill)
            
    return sorted(list(found))


def calculate_skill_match(resume_skills: List[str], job_skills: List[str], title: str = '', description: str = '') -> Dict[str, Any]:
    """
    Role-aware matching engine that handles diverse terminology.
    """
    import re
    def normalize(t):
        return re.sub(r'[^a-z0-9+# ]', ' ', t.lower().replace('-', ' ')).strip()

    r_skills = {normalize(s) for s in resume_skills if s}
    j_skills = {normalize(s) for s in job_skills if s}
    title_norm = normalize(title)
    
    # Extract from title/desc if missing
    if not j_skills and (description or title):
        extracted = extract_skills_from_description(description, title)
        j_skills = {normalize(s) for s in extracted}
    
    # Define Roles and their associated core skill keywords
    roles = {
        'frontend': {'frontend', 'front end', 'react', 'angular', 'vue', 'web', 'javascript', 'html', 'css', 'ui', 'ux', 'frontend developer', 'web developer'},
        'backend': {'backend', 'back end', 'python', 'java', 'node', 'sql', 'api', 'server', 'database', 'django', 'flask'},
        'data': {'data', 'analytical', 'statistics', 'python', 'sql', 'machine learning', 'ai', 'data science', 'analyst'},
        'devops': {'devops', 'aws', 'docker', 'kubernetes', 'cloud', 'infrastructure', 'ci', 'cd'},
        'software': {'software', 'engineer', 'developer', 'coding', 'programming'}
    }

    # Calculate Synergy
    direct_matches = r_skills & j_skills
    
    # Role Matching Logic
    title_matches_role = False
    for role_key, role_skills in roles.items():
        # Does the job title imply this role?
        is_job_this_role = any(s in title_norm for s in role_skills if len(s) > 3) or role_key in title_norm
        # Does the user have skills for this role?
        user_has_role_skills = any(s in r_skills for s in role_skills)
        
        if is_job_this_role and user_has_role_skills:
            title_matches_role = True
            break

    # ── Final Score Compilation ─────────────────────────────────────────────
    # Factor A: Direct Skill Overlap (0-60%)
    n = max(len(j_skills), 1)
    skill_score = (len(direct_matches) / n) * 60
    
    # Factor B: Role Synergy (0-30%)
    synergy_score = 30 if title_matches_role else 0
    
    # Factor C: Keyword Relevance (0-10%)
    title_keyword_matches = sum(1 for s in r_skills if len(s) > 3 and s in title_norm)
    keyword_score = min(title_keyword_matches * 5, 10)
    
    total = skill_score + synergy_score + keyword_score
    
    # Guarantee minimum score for role relevance
    if title_matches_role:
        total = max(total, 45.0)
        
    return {
        'match_percentage': min(round(total, 1), 100),
        'direct_matches': sorted(list(direct_matches)),
        'related_matches': [],
        'total_required': len(j_skills),
        'total_matched': len(direct_matches),
    }


def rank_jobs(user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get and rank job recommendations for a user based on their resume analysis
    Uses live API when available, falls back to database
    """
    from job_search_api import get_job_api
    
    # Get user's latest analysis
    analysis = get_latest_analysis(user_id)
    if not analysis:
        return []
    
    # Combine all user skills
    user_skills = analysis['technical_skills'] + analysis['soft_skills']
    
    # Try to fetch live jobs first
    job_api = get_job_api()
    live_jobs = []
    
    # Use top skills as search keywords
    keywords = analysis['technical_skills'][:5] if analysis.get('technical_skills') else user_skills[:5]
    if not keywords:
        keywords = ["Software"]
        
    live_jobs = job_api.search_jobs(keywords=keywords, max_results=limit * 2)
    
    # If we got live jobs, use them; otherwise fall back to database
    if live_jobs:
        all_jobs = live_jobs
        # Convert live job format to match our expected format
        formatted_jobs = []
        for job in all_jobs:
            # Extract skills from job description and title
            job_skills = extract_skills_from_description(job['description'], job['title'])
            
            formatted_jobs.append({
                'job_id': hash(job['url']),  # Use URL hash as ID
                'title': job['title'],
                'company': job['company'],
                'location': job['location'],
                'description': job['description'],  # Keep full description; UI handles display truncation
                'required_skills': job_skills,
                'apply_link': job['url'],
                'salary': job.get('salary', 'Not specified'),
                'posted_date': job.get('posted_date', ''),
                'days_ago': job.get('days_ago', 0),
                'contract_type': job.get('contract_type', 'Full-time'),
                'source': job.get('source', 'Multiple Platforms'),
                'easy_apply': job.get('easy_apply', False),  # Easy Apply indicator
                'is_live': True  # Flag to indicate this is from live API
            })
        all_jobs = formatted_jobs
    else:
        # Fallback to database jobs
        all_jobs = get_all_jobs()
        # Add is_live flag and missing fields
        for job in all_jobs:
            job['is_live'] = False
            job['salary'] = job.get('salary', 'Not specified')
            job['days_ago'] = 0
            job['contract_type'] = job.get('contract_type', 'Full-time')
            job['easy_apply'] = False
    
    # Calculate match for each job
    job_matches = []
    for job in all_jobs:
        match_result = calculate_skill_match(
            user_skills,
            job.get('required_skills', []),
            title=job.get('title', ''),
            description=job.get('description', '')
        )
        
        job_matches.append({
            'job_id': job.get('job_id', job.get('id', 0)),
            'title': job['title'],
            'company': job['company'],
            'location': job['location'],
            'description': job.get('description', ''),
            'required_skills': job.get('required_skills', []),
            'apply_link': job.get('apply_link', '#'),
            'salary': job.get('salary', 'Not specified'),
            'posted_date': job.get('posted_date', ''),
            'days_ago': job.get('days_ago', 0),
            'contract_type': job.get('contract_type', 'Full-time'),
            'source': job.get('source', 'Job Board'),
            'easy_apply': job.get('easy_apply', False),
            'is_live': job.get('is_live', False),
            'match_score': match_result['match_percentage'],
            'direct_matches': match_result['direct_matches'],
            'related_matches': match_result['related_matches'],
            'total_required': match_result['total_required'],
            'total_matched': match_result['total_matched']
        })
    
    # Sort by match score descending
    job_matches.sort(key=lambda x: -x['match_score'])
    
    # Get top N recommendations
    top_recommendations = job_matches[:limit]
    
    # Save recommendations to database (only for non-live jobs)
    recommendations_to_save = [
        {'job_id': rec['job_id'], 'match_score': rec['match_score']}
        for rec in top_recommendations
        if not rec.get('is_live', False) and isinstance(rec['job_id'], int)
    ]
    if recommendations_to_save:
        save_recommendations(user_id, recommendations_to_save)
    
    return top_recommendations


def get_job_recommendations(user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Main entry point for getting job recommendations
    """
    return rank_jobs(user_id, limit)
