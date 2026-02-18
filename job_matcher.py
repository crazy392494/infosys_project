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


def calculate_skill_match(resume_skills: List[str], job_skills: List[str]) -> Dict[str, Any]:
    """
    Calculate how well resume skills match job requirements
    Returns match details including score and matching skills
    """
    # Normalize all skills
    resume_skills_set = {normalize_skill(s) for s in resume_skills}
    job_skills_set = {normalize_skill(s) for s in job_skills}
    
    # Skill synonyms and related technologies
    skill_synonyms = {
        'javascript': {'js', 'ecmascript'},
        'typescript': {'ts'},
        'nodejs': {'node.js', 'node'},
        'reactjs': {'react', 'react.js'},
        'vuejs': {'vue', 'vue.js'},
        'python': {'py'},
        'docker': {'containerization'},
        'kubernetes': {'k8s'},
        'amazon web services': {'aws'},
        'google cloud platform': {'gcp', 'google cloud'},
        'microsoft azure': {'azure'},
        'sql': {'mysql', 'postgresql', 'sql server'},
        'nosql': {'mongodb', 'cassandra', 'dynamodb'},
    }
    
    # Related skills (partial credit)
    related_skills = {
        'react': {'javascript', 'typescript', 'html', 'css'},
        'angular': {'javascript', 'typescript', 'html', 'css'},
        'vue': {'javascript', 'typescript', 'html', 'css'},
        'django': {'python'},
        'flask': {'python'},
        'spring': {'java'},
        'express': {'nodejs', 'javascript'},
        'docker': {'linux', 'devops'},
        'kubernetes': {'docker', 'linux', 'devops'},
        'aws': {'cloud', 'devops'},
        'azure': {'cloud', 'devops'},
        'gcp': {'cloud', 'devops'},
    }
    
    # Direct matches
    direct_matches = set()
    for job_skill in job_skills_set:
        if job_skill in resume_skills_set:
            direct_matches.add(job_skill)
        else:
            # Check synonyms
            for key, synonyms in skill_synonyms.items():
                if job_skill in synonyms or job_skill == key:
                    if key in resume_skills_set or resume_skills_set & synonyms:
                        direct_matches.add(job_skill)
                        break
    
    # Related matches (partial credit)
    related_matches = set()
    for job_skill in job_skills_set - direct_matches:
        for key, related in related_skills.items():
            if job_skill == key and resume_skills_set & related:
                related_matches.add(job_skill)
                break
    
    # Calculate match score
    if not job_skills_set:
        match_percentage = 0
    else:
        direct_score = len(direct_matches) / len(job_skills_set) * 0.6  # 60% weight
        related_score = len(related_matches) / len(job_skills_set) * 0.2  # 20% weight
        
        # Experience level matching (simplified - 10% weight)
        experience_score = 0.1  # Default partial credit
        
        # Industry alignment (simplified - 10% weight)
        industry_score = 0.1 if resume_skills_set & job_skills_set else 0.05
        
        match_percentage = (direct_score + related_score + experience_score + industry_score) * 100
    
    return {
        'match_percentage': min(round(match_percentage, 1), 100),
        'direct_matches': sorted(list(direct_matches)),
        'related_matches': sorted(list(related_matches)),
        'total_required': len(job_skills_set),
        'total_matched': len(direct_matches) + len(related_matches)
    }


def extract_skills_from_description(description: str) -> List[str]:
    """
    Extract skills from job description using pattern matching
    """
    from config import TECHNICAL_SKILLS
    
    description_lower = description.lower()
    found_skills = []
    
    for skill in TECHNICAL_SKILLS:
        if skill.lower() in description_lower:
            found_skills.append(skill)
    
    return found_skills[:15]  # Limit to top 15 skills


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
    
    if job_api.is_configured and user_skills:
        # Use top skills as search keywords
        keywords = analysis['technical_skills'][:5] if analysis['technical_skills'] else user_skills[:5]
        live_jobs = job_api.search_jobs(keywords=keywords, max_results=limit * 2)
    
    # If we got live jobs, use them; otherwise fall back to database
    if live_jobs:
        all_jobs = live_jobs
        # Convert live job format to match our expected format
        formatted_jobs = []
        for job in all_jobs:
            # Extract skills from job description using AI or pattern matching
            job_skills = extract_skills_from_description(job['description'])
            
            formatted_jobs.append({
                'job_id': hash(job['url']),  # Use URL hash as ID
                'title': job['title'],
                'company': job['company'],
                'location': job['location'],
                'description': job['description'][:500],  # Truncate for display
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
        match_result = calculate_skill_match(user_skills, job.get('required_skills', []))
        
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
    
    # Sort by Easy Apply first, then match score
    job_matches.sort(key=lambda x: (not x.get('easy_apply', False), -x['match_score']))
    
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
