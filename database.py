"""
Database management module for the Career Recommendation Platform
Handles SQLite database initialization and CRUD operations
"""

import sqlite3
from datetime import datetime
from typing import Optional, List, Dict, Any
import json
from config import DATABASE_PATH


def get_connection():
    """Create and return a database connection"""
    conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    """Create all necessary tables if they don't exist"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Resumes table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS resumes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            filename TEXT NOT NULL,
            original_text TEXT NOT NULL,
            upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Analysis table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            resume_id INTEGER NOT NULL,
            summary TEXT,
            technical_skills TEXT,
            soft_skills TEXT,
            strengths TEXT,
            weaknesses TEXT,
            missing_skills TEXT,
            score INTEGER,
            suggestions TEXT,
            analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (resume_id) REFERENCES resumes(id)
        )
    ''')
    
    # Jobs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            company TEXT NOT NULL,
            location TEXT NOT NULL,
            description TEXT NOT NULL,
            required_skills TEXT NOT NULL,
            apply_link TEXT,
            posted_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Recommendations table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS recommendations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            job_id INTEGER NOT NULL,
            match_score REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (job_id) REFERENCES jobs(id)
        )
    ''')
    
    # Favorites table (optional feature)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            job_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (job_id) REFERENCES jobs(id),
            UNIQUE(user_id, job_id)
        )
    ''')
    
    conn.commit()
    conn.close()


# ==================== USER OPERATIONS ====================

def create_user(username: str, email: str, password_hash: str) -> Optional[int]:
    """Create a new user and return user ID"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
            (username, email, password_hash)
        )
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return user_id
    except sqlite3.IntegrityError:
        return None


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Retrieve user by email"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve user by ID"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


# ==================== RESUME OPERATIONS ====================

def save_resume(user_id: int, filename: str, text_content: str) -> int:
    """Save resume text to database"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO resumes (user_id, filename, original_text) VALUES (?, ?, ?)',
        (user_id, filename, text_content)
    )
    conn.commit()
    resume_id = cursor.lastrowid
    conn.close()
    return resume_id


def get_latest_resume(user_id: int) -> Optional[Dict[str, Any]]:
    """Get the most recent resume for a user"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT * FROM resumes WHERE user_id = ? ORDER BY upload_date DESC LIMIT 1',
        (user_id,)
    )
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_all_resumes(user_id: int) -> List[Dict[str, Any]]:
    """Get all resumes for a user"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT * FROM resumes WHERE user_id = ? ORDER BY upload_date DESC',
        (user_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


# ==================== ANALYSIS OPERATIONS ====================

def save_analysis(resume_id: int, analysis_data: Dict[str, Any]) -> int:
    """Save resume analysis results"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO analysis (
            resume_id, summary, technical_skills, soft_skills, 
            strengths, weaknesses, missing_skills, score, suggestions
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        resume_id,
        analysis_data.get('summary', ''),
        json.dumps(analysis_data.get('technical_skills', [])),
        json.dumps(analysis_data.get('soft_skills', [])),
        json.dumps(analysis_data.get('strengths', [])),
        json.dumps(analysis_data.get('weaknesses', [])),
        json.dumps(analysis_data.get('missing_skills', [])),
        analysis_data.get('score', 0),
        json.dumps(analysis_data.get('suggestions', []))
    ))
    conn.commit()
    analysis_id = cursor.lastrowid
    conn.close()
    return analysis_id


def get_latest_analysis(user_id: int) -> Optional[Dict[str, Any]]:
    """Get the most recent analysis for a user"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT a.* FROM analysis a
        JOIN resumes r ON a.resume_id = r.id
        WHERE r.user_id = ?
        ORDER BY a.analyzed_at DESC
        LIMIT 1
    ''', (user_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        data = dict(row)
        # Parse JSON fields
        data['technical_skills'] = json.loads(data['technical_skills'])
        data['soft_skills'] = json.loads(data['soft_skills'])
        data['strengths'] = json.loads(data['strengths'])
        data['weaknesses'] = json.loads(data['weaknesses'])
        data['missing_skills'] = json.loads(data['missing_skills'])
        data['suggestions'] = json.loads(data['suggestions'])
        return data
    return None


def get_analysis_for_resume(resume_id: int) -> Optional[Dict[str, Any]]:
    """Get analysis for a specific resume"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM analysis WHERE resume_id = ?', (resume_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        data = dict(row)
        # Parse JSON fields
        try:
            data['technical_skills'] = json.loads(data['technical_skills']) if data['technical_skills'] else []
            data['soft_skills'] = json.loads(data['soft_skills']) if data['soft_skills'] else []
            data['strengths'] = json.loads(data['strengths']) if data['strengths'] else []
            data['weaknesses'] = json.loads(data['weaknesses']) if data['weaknesses'] else []
            data['missing_skills'] = json.loads(data['missing_skills']) if data['missing_skills'] else []
            data['suggestions'] = json.loads(data['suggestions']) if data['suggestions'] else []
        except json.JSONDecodeError:
            pass
        return data
    return None


# ==================== JOB OPERATIONS ====================

def add_job(title: str, company: str, location: str, description: str, 
            required_skills: List[str], apply_link: str = '') -> int:
    """Add a new job posting"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO jobs (title, company, location, description, required_skills, apply_link)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (title, company, location, description, json.dumps(required_skills), apply_link))
    conn.commit()
    job_id = cursor.lastrowid
    conn.close()
    return job_id


def get_all_jobs() -> List[Dict[str, Any]]:
    """Get all job postings"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM jobs ORDER BY posted_date DESC')
    rows = cursor.fetchall()
    conn.close()
    
    jobs = []
    for row in rows:
        job = dict(row)
        job['required_skills'] = json.loads(job['required_skills'])
        jobs.append(job)
    return jobs


def get_job_by_id(job_id: int) -> Optional[Dict[str, Any]]:
    """Get a specific job by ID"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM jobs WHERE id = ?', (job_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        job = dict(row)
        job['required_skills'] = json.loads(job['required_skills'])
        return job
    return None


# ==================== RECOMMENDATION OPERATIONS ====================

def save_recommendations(user_id: int, recommendations: List[Dict[str, Any]]):
    """Save job recommendations for a user"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Clear old recommendations
    cursor.execute('DELETE FROM recommendations WHERE user_id = ?', (user_id,))
    
    # Insert new recommendations
    for rec in recommendations:
        cursor.execute('''
            INSERT INTO recommendations (user_id, job_id, match_score)
            VALUES (?, ?, ?)
        ''', (user_id, rec['job_id'], rec['match_score']))
    
    conn.commit()
    conn.close()


def get_recommendations(user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
    """Get job recommendations for a user"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT r.*, j.title, j.company, j.location, j.description, 
               j.required_skills, j.apply_link
        FROM recommendations r
        JOIN jobs j ON r.job_id = j.id
        WHERE r.user_id = ?
        ORDER BY r.match_score DESC
        LIMIT ?
    ''', (user_id, limit))
    rows = cursor.fetchall()
    conn.close()
    
    recommendations = []
    for row in rows:
        rec = dict(row)
        rec['required_skills'] = json.loads(rec['required_skills'])
        recommendations.append(rec)
    return recommendations


# ==================== FAVORITES OPERATIONS ====================

def add_favorite(user_id: int, job_id: int) -> bool:
    """Add a job to favorites"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO favorites (user_id, job_id) VALUES (?, ?)',
            (user_id, job_id)
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False


def remove_favorite(user_id: int, job_id: int):
    """Remove a job from favorites"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'DELETE FROM favorites WHERE user_id = ? AND job_id = ?',
        (user_id, job_id)
    )
    conn.commit()
    conn.close()


def get_favorites(user_id: int) -> List[Dict[str, Any]]:
    """Get all favorite jobs for a user"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT j.* FROM favorites f
        JOIN jobs j ON f.job_id = j.id
        WHERE f.user_id = ?
        ORDER BY f.created_at DESC
    ''', (user_id,))
    rows = cursor.fetchall()
    conn.close()
    
    jobs = []
    for row in rows:
        job = dict(row)
        job['required_skills'] = json.loads(job['required_skills'])
        jobs.append(job)
    return jobs


def is_favorite(user_id: int, job_id: int) -> bool:
    """Check if a job is in user's favorites"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT 1 FROM favorites WHERE user_id = ? AND job_id = ?',
        (user_id, job_id)
    )
    result = cursor.fetchone()
    conn.close()
    return result is not None


# Initialize database on module import
initialize_database()
