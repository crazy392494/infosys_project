"""
Configuration file for the Intelligent Career Recommendation Platform
"""

import os

# Database Configuration
DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'career_platform.db')

# File Upload Configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
MAX_FILE_SIZE_MB = 10
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc'}

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Technical Skills Dictionary (comprehensive list for matching)
TECHNICAL_SKILLS = {
    # Programming Languages
    'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'ruby', 'php', 'swift', 'kotlin',
    'go', 'rust', 'scala', 'r', 'matlab', 'sql', 'html', 'css',
    
    # Web Frameworks
    'react', 'angular', 'vue', 'nextjs', 'next.js', 'svelte', 'django', 'flask', 'fastapi',
    'express', 'nodejs', 'node.js', 'spring', 'asp.net', '.net', 'rails', 'laravel',
    
    # Mobile Development
    'android', 'ios', 'react native', 'flutter', 'xamarin', 'ionic',
    
    # Databases
    'mysql', 'postgresql', 'mongodb', 'redis', 'sqlite', 'oracle', 'cassandra',
    'dynamodb', 'elasticsearch', 'mssql', 'mariadb', 'firebase',
    
    # Cloud & DevOps
    'aws', 'azure', 'gcp', 'google cloud', 'docker', 'kubernetes', 'jenkins', 'gitlab',
    'github actions', 'terraform', 'ansible', 'ci/cd', 'nginx', 'apache',
    
    # Data Science & ML
    'machine learning', 'deep learning', 'tensorflow', 'pytorch', 'scikit-learn', 'keras',
    'pandas', 'numpy', 'data analysis', 'data science', 'nlp', 'computer vision',
    'tableau', 'power bi', 'spark', 'hadoop', 'airflow',
    
    # Other Technologies
    'git', 'rest api', 'graphql', 'microservices', 'agile', 'scrum', 'jira',
    'linux', 'bash', 'powershell', 'api', 'json', 'xml', 'oauth', 'jwt',
    'testing', 'unit testing', 'selenium', 'jest', 'pytest', 'kafka', 'rabbitmq'
}

# Soft Skills Dictionary
SOFT_SKILLS = {
    'leadership', 'communication', 'teamwork', 'problem solving', 'critical thinking',
    'time management', 'project management', 'collaboration', 'adaptability', 'creativity',
    'interpersonal', 'presentation', 'analytical', 'decision making', 'conflict resolution',
    'mentoring', 'negotiation', 'strategic thinking', 'attention to detail', 'multitasking',
    'initiative', 'self-motivated', 'organizational', 'customer service', 'public speaking'
}

# Industry Standard Skills by Role
ROLE_SKILL_REQUIREMENTS = {
    'software_engineer': [
        'python', 'java', 'javascript', 'git', 'sql', 'rest api', 'data structures',
        'algorithms', 'testing', 'problem solving', 'teamwork'
    ],
    'frontend_developer': [
        'html', 'css', 'javascript', 'react', 'typescript', 'responsive design',
        'git', 'rest api', 'ui/ux', 'problem solving'
    ],
    'backend_developer': [
        'python', 'java', 'sql', 'rest api', 'microservices', 'docker',
        'database design', 'git', 'problem solving', 'system design'
    ],
    'data_scientist': [
        'python', 'r', 'sql', 'machine learning', 'statistics', 'pandas', 'numpy',
        'data visualization', 'problem solving', 'communication', 'analytical'
    ],
    'devops_engineer': [
        'linux', 'docker', 'kubernetes', 'aws', 'ci/cd', 'terraform', 'bash',
        'python', 'git', 'monitoring', 'problem solving'
    ],
    'full_stack_developer': [
        'javascript', 'python', 'react', 'nodejs', 'sql', 'git', 'rest api',
        'html', 'css', 'problem solving', 'teamwork'
    ]
}

# Resume Scoring Weights
SCORING_WEIGHTS = {
    'content_quality': 30,
    'technical_skills': 25,
    'experience': 20,
    'education': 15,
    'soft_skills': 10
}

# Application Settings
APP_TITLE = "Intelligent Career Recommendation Platform"
APP_ICON = None
SESSION_TIMEOUT_MINUTES = 60

# AI Configuration (Google Gemini)
# Get your free API key from: https://aistudio.google.com/app/apikey
try:
    import streamlit as st
    GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", os.getenv('GEMINI_API_KEY', ''))
except ImportError:
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')

# Job Search API Configuration (Adzuna)
# Get your free API credentials from: https://developer.adzuna.com/
try:
    import streamlit as st
    ADZUNA_APP_ID = st.secrets.get("ADZUNA_APP_ID", os.getenv('ADZUNA_APP_ID', ''))
    ADZUNA_API_KEY = st.secrets.get("ADZUNA_API_KEY", os.getenv('ADZUNA_API_KEY', ''))
except ImportError:
    ADZUNA_APP_ID = os.getenv('ADZUNA_APP_ID', '')
    ADZUNA_API_KEY = os.getenv('ADZUNA_API_KEY', '')

# RapidAPI Configuration (for Job Search Global)
# Get your key from: https://rapidapi.com/PrineshPatel/api/job-search-global
# You can provide multiple keys separated by commas for fallback (e.g. "key1,key2")
try:
    import streamlit as st
    RAPIDAPI_KEY = st.secrets.get("RAPIDAPI_KEY", os.getenv('RAPIDAPI_KEY', ''))
    JOB_SEARCH_GLOBAL_HOST = st.secrets.get("JOB_SEARCH_GLOBAL_HOST", os.getenv('JOB_SEARCH_GLOBAL_HOST', 'job-search-global.p.rapidapi.com'))
except ImportError:
    RAPIDAPI_KEY = os.getenv('RAPIDAPI_KEY', '')
    JOB_SEARCH_GLOBAL_HOST = os.getenv('JOB_SEARCH_GLOBAL_HOST', 'job-search-global.p.rapidapi.com')

# Active Jobs DB Configuration (RapidAPI)
# Endpoint: https://active-jobs-db.p.rapidapi.com/modified-ats-24h
try:
    import streamlit as st
    ACTIVE_JOBS_DB_KEY = st.secrets.get("ACTIVE_JOBS_DB_KEY", os.getenv('ACTIVE_JOBS_DB_KEY', ''))
except ImportError:
    ACTIVE_JOBS_DB_KEY = os.getenv('ACTIVE_JOBS_DB_KEY', '')

ACTIVE_JOBS_DB_HOST = 'active-jobs-db.p.rapidapi.com'

# Job search defaults
DEFAULT_COUNTRY = 'us'  # Change to your country code (us, gb, in, etc.)
DEFAULT_LOCATION = 'remote'  # Default search location
JOBS_PER_PAGE = 10
MAX_JOB_AGE_DAYS = 30  # Only show jobs from last 30 days
JOB_CACHE_MINUTES = 30  # Cache job results for 30 minutes
