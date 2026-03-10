"""
Intelligent Career Recommendation Platform
Main Streamlit Application — Premium Edition
"""

import streamlit as st


# Import custom modules
from auth import register_user, authenticate_user
from database import (
    save_resume, get_latest_resume, get_latest_analysis,
    save_analysis, get_user_by_id, add_favorite, remove_favorite,
    is_favorite, get_all_resumes, get_analysis_for_resume
)
from resume_parser import extract_text, validate_file_size, validate_file_extension
from resume_analyzer import analyze_resume, enhance_resume_text
from job_matcher import get_job_recommendations
from components import (
    render_skill_badges, render_score_gauge, render_header,
    render_section_header, render_job_card, render_metric_card,
    render_alert, render_skills_chart, render_progress_bar, render_glow_card
)
from config import APP_TITLE, APP_ICON, MAX_FILE_SIZE_MB, ALLOWED_EXTENSIONS
import requests as _requests
import re as _re
import html as _html_mod

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_job_from_source(url: str) -> dict:
    """
    Fetch real job posting from any URL via Jina Reader and parse:
      - company: exact company name as shown on the posting
      - description: first 2-3 meaningful sentences of the job description
      - content: full raw text (trimmed)
    Works on LinkedIn, Greenhouse, Workday, Lever, direct company sites.
    """
    # Navigation/boilerplate words to skip when parsing content
    _NAV_NOISE = {
        'linkedin', 'sign in', 'join now', 'skip to main content',
        'clear text', 'jobs', 'search', 'home', 'notifications',
        'messaging', 'me', 'post a job', 'find a job',
        'easy apply', 'save', 'show more', 'show less',
        'follow', 'report', 'share', 'dismiss', 'cookie policy',
        'privacy policy', 'terms of service', 'copyright',
    }
    try:
        jina_url = f"https://r.jina.ai/{url}"
        headers  = {
            "Accept":          "text/plain",
            "User-Agent":      "Mozilla/5.0 (compatible; CareerPlatform/1.0)",
            "X-Return-Format": "text",
        }
        resp = _requests.get(jina_url, headers=headers, timeout=20)
        if resp.status_code != 200:
            return {"title": "", "company": "", "description": "", "content": "", "error": f"HTTP {resp.status_code}"}

        text    = resp.text.strip()
        content = text[:8000] + ("\n\n[Content trimmed…]" if len(text) > 8000 else "")

        # Filter out noise lines — keep lines that are real content
        all_lines = [l.strip() for l in text.splitlines() if l.strip()]
        clean = [
            l for l in all_lines
            if len(l) > 3
            and l.lower() not in _NAV_NOISE
            and not l.startswith('http')
            and not l.startswith('#')
            and len(l) < 200          # skip huge blobs that are really one long line
        ]

        # Structure for LinkedIn / ATS pages:
        #   clean[0] → job title  (e.g. "Senior Angular Engineer")
        #   clean[1] → company    (e.g. "Netlify")
        #   clean[2] → location / meta
        #   clean[3+] → description body
        job_title   = clean[0] if len(clean) > 0 else "Job Posting"
        company     = clean[1] if len(clean) > 1 else ""
        # Description: skip location/meta lines (usually short), grab first substantive sentences
        desc_lines  = [l for l in clean[2:] if len(l) > 40][:4]
        description = " ".join(desc_lines)
        if len(description) > 280:
            description = description[:280].rstrip() + "…"

        return {
            "title":       job_title,
            "company":     company,
            "description": description,
            "content":     content,
            "error":       None,
        }
    except Exception as e:
        return {"title": "", "company": "", "description": "", "content": "", "error": str(e)}


# Page configuration
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========================== PREMIUM CSS ==========================
st.markdown("""
<style>
    /* ===== Google Font Import ===== */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

    /* ===== Global Styles ===== */
    *, *::before, *::after {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }

    /* Hide broken Material Icons / arrow text in Expanders */
    div[data-testid="stExpander"] details summary svg {
        display: none !important;
    }
    
    /* Target the broken 'V' or 'arrow' ligature text directly */
    div[data-testid="stExpander"] details summary div[data-testid="stExpanderToggleIcon"] {
        display: none !important;
    }
    
    /* Absolute hammer to hide any junk text appearing where icons should be */
    .st-emotion-cache-p5msec, .st-emotion-cache-12w0qpk, .st-emotion-cache-6q9sum, .st-emotion-cache-ue6ba6 {
        display: none !important;
        font-size: 0 !important;
        color: transparent !important;
    }
    
    /* Custom clean look for Expanders in Sidebar */
    section[data-testid="stSidebar"] div[data-testid="stExpander"] {
        border: none !important;
        background: rgba(255, 255, 255, 0.05) !important;
        border-radius: 8px !important;
        margin-bottom: 10px;
    }

    .main .block-container {
        padding-top: 2rem;
        max-width: 1200px;
        animation: fadeIn 0.6s ease-out;
    }

    /* ===== ENTRANCE ANIMATIONS ===== */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    @keyframes slideInLeft {
        from { opacity: 0; transform: translateX(-30px); }
        to { opacity: 1; transform: translateX(0); }
    }

    @keyframes slideInRight {
        from { opacity: 0; transform: translateX(30px); }
        to { opacity: 1; transform: translateX(0); }
    }

    @keyframes scaleIn {
        from { opacity: 0; transform: scale(0.9); }
        to { opacity: 1; transform: scale(1); }
    }

    @keyframes shimmer {
        0% { background-position: -1000px 0; }
        100% { background-position: 1000px 0; }
    }

    /* Animated gradient mesh background */
    @keyframes gradientMesh {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }

    /* ===== Enhanced Scrollbar ===== */
    ::-webkit-scrollbar { 
        width: 10px; 
        height: 10px; 
    }
    ::-webkit-scrollbar-track { 
        background: #0F172A;
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb { 
        background: linear-gradient(180deg, #7C3AED, #2563EB);
        border-radius: 10px;
        transition: all 0.3s ease;
    }
    ::-webkit-scrollbar-thumb:hover { 
        background: linear-gradient(180deg, #6D28D9, #1D4ED8);
        box-shadow: 0 0 10px rgba(124, 58, 237, 0.5);
    }

    /* ===== Enhanced Sidebar ===== */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1E1B4B 0%, #0F172A 100%) !important;
        border-right: 1px solid rgba(124, 58, 237, 0.2);
        animation: slideInLeft 0.5s ease-out;
    }

    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stMarkdown label,
    section[data-testid="stSidebar"] .stMarkdown h1,
    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown h3 {
        color: #E2E8F0 !important;
    }

    /* ===== Enhanced Buttons with Ripple Effect ===== */
    .stButton > button {
        background: linear-gradient(135deg, #7C3AED 0%, #2563EB 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px 28px !important;
        font-weight: 600 !important;
        font-size: 0.92em !important;
        letter-spacing: 0.3px;
        transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 14px rgba(124, 58, 237, 0.3) !important;
        position: relative;
        overflow: hidden;
    }

    .stButton > button::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.3);
        transform: translate(-50%, -50%);
        transition: width 0.6s, height 0.6s;
    }

    .stButton > button:hover::before {
        width: 300px;
        height: 300px;
    }

    .stButton > button:hover {
        transform: translateY(-3px) scale(1.02) !important;
        box-shadow: 0 12px 30px rgba(124, 58, 237, 0.5) !important;
        background: linear-gradient(135deg, #6D28D9 0%, #1D4ED8 100%) !important;
    }

    .stButton > button:active {
        transform: translateY(-1px) scale(0.98) !important;
    }

    /* ===== Enhanced Form Inputs ===== */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div,
    .stMultiSelect > div > div {
        background: rgba(15, 23, 42, 0.8) !important;
        border: 1px solid rgba(148, 163, 184, 0.2) !important;
        border-radius: 12px !important;
        color: #E2E8F0 !important;
        transition: all 0.3s ease !important;
        backdrop-filter: blur(10px);
    }

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #7C3AED !important;
        box-shadow: 0 0 0 4px rgba(124, 58, 237, 0.15), 0 8px 20px rgba(124, 58, 237, 0.2) !important;
        background: rgba(15, 23, 42, 0.95) !important;
        transform: translateY(-2px);
    }

    /* ===== Enhanced Tabs ===== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background: rgba(15, 23, 42, 0.7);
        border-radius: 16px;
        padding: 6px;
        border: 1px solid rgba(148, 163, 184, 0.15);
        backdrop-filter: blur(20px);
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 12px !important;
        padding: 14px 28px !important;
        font-weight: 600 !important;
        color: #94A3B8 !important;
        background: transparent !important;
        border: none !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(124, 58, 237, 0.1) !important;
        color: #C4B5FD !important;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #7C3AED, #2563EB) !important;
        color: white !important;
        box-shadow: 0 6px 16px rgba(124, 58, 237, 0.4) !important;
        transform: translateY(-2px);
    }

    .stTabs [data-baseweb="tab-highlight"] {
        display: none !important;
    }

    .stTabs [data-baseweb="tab-border"] {
        display: none !important;
    }

    /* ===== Enhanced Sidebar Radio Navigation ===== */
    [data-testid="stSidebar"] .stRadio > div {
        gap: 6px !important;
    }
    
    [data-testid="stSidebar"] .stRadio label {
        background: rgba(15, 23, 42, 0.6) !important;
        border: 1px solid rgba(148, 163, 184, 0.15) !important;
        border-radius: 12px !important;
        padding: 14px 18px !important;
        color: #94A3B8 !important;
        cursor: pointer !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        font-weight: 600 !important;
        margin: 0 !important;
        backdrop-filter: blur(10px);
    }
    
    [data-testid="stSidebar"] .stRadio label:hover {
        background: rgba(124, 58, 237, 0.2) !important;
        border-color: rgba(124, 58, 237, 0.4) !important;
        color: #E2E8F0 !important;
        transform: translateX(4px);
    }
    
    [data-testid="stSidebar"] .stRadio label[data-checked="true"],
    [data-testid="stSidebar"] .stRadio label:has(input:checked) {
        background: linear-gradient(135deg, rgba(124, 58, 237, 0.35), rgba(37, 99, 235, 0.35)) !important;
        border-color: rgba(124, 58, 237, 0.6) !important;
        color: #F8FAFC !important;
        box-shadow: 0 6px 16px rgba(124, 58, 237, 0.3) !important;
        transform: translateX(6px);
    }
    
    /* Hide the radio circle indicator */
    [data-testid="stSidebar"] .stRadio label > div:first-child {
        display: none !important;
    }

    /* Hide sidebar collapse button */
    [data-testid="stSidebarCollapseButton"],
    [data-testid="collapsedControl"],
    [data-testid="stSidebar"] > div:first-child > div:first-child > button,
    section[data-testid="stSidebar"] button[kind="header"] {
        display: none !important;
    }

    /* ===== Enhanced File Uploader ===== */
    .stFileUploader > div {
        background: rgba(15, 23, 42, 0.6) !important;
        border: 2px dashed rgba(124, 58, 237, 0.4) !important;
        border-radius: 16px !important;
        transition: all 0.3s ease !important;
        backdrop-filter: blur(10px);
    }

    .stFileUploader > div:hover {
        border-color: rgba(124, 58, 237, 0.7) !important;
        background: rgba(124, 58, 237, 0.05) !important;
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(124, 58, 237, 0.2);
    }

    /* ===== Enhanced Progress Bar ===== */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #7C3AED, #2563EB, #06B6D4) !important;
        border-radius: 12px !important;
        box-shadow: 0 0 15px rgba(124, 58, 237, 0.5);
        animation: shimmer 2s infinite linear;
        background-size: 200% 100%;
    }

    .stProgress > div > div > div {
        background: rgba(15, 23, 42, 0.7) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(148, 163, 184, 0.1);
    }

    /* ===== Enhanced Metrics ===== */
    [data-testid="stMetricValue"] {
        color: #A78BFA !important;
        font-weight: 800 !important;
        animation: fadeIn 0.6s ease-out;
    }

    [data-testid="stMetricLabel"] {
        color: #94A3B8 !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-size: 0.85em !important;
    }

    /* ===== Enhanced Expanders & Containers ===== */
    .stExpander {
        background: rgba(30, 41, 59, 0.6) !important;
        border: 1px solid rgba(148, 163, 184, 0.15) !important;
        border-radius: 14px !important;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }

    .stExpander:hover {
        border-color: rgba(124, 58, 237, 0.3) !important;
        box-shadow: 0 4px 16px rgba(124, 58, 237, 0.15);
    }

    /* ===== Dividers ===== */
    hr {
        border-color: rgba(148, 163, 184, 0.15) !important;
        margin: 2rem 0;
    }

    /* ===== Enhanced Links ===== */
    a {
        color: #A78BFA !important;
        text-decoration: none !important;
        transition: all 0.2s ease;
        position: relative;
    }

    a:hover {
        color: #C4B5FD !important;
        transform: translateY(-1px);
    }

    a::after {
        content: '';
        position: absolute;
        width: 0;
        height: 2px;
        bottom: -2px;
        left: 0;
        background: linear-gradient(90deg, #7C3AED, #2563EB);
        transition: width 0.3s ease;
    }

    a:hover::after {
        width: 100%;
    }

    /* ===== Enhanced Alerts ===== */
    .stAlert {
        border-radius: 14px !important;
        backdrop-filter: blur(10px);
        animation: slideInRight 0.4s ease-out;
    }

    /* ===== Enhanced Spinner ===== */
    .stSpinner > div {
        border-top-color: #7C3AED !important;
        border-right-color: #2563EB !important;
    }

    /* ===== Selection highlight ===== */
    ::selection {
        background: rgba(124, 58, 237, 0.4);
        color: #F8FAFC;
    }

    /* ===== Enhanced Glassmorphism Card ===== */
    .glass-card {
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(25px) saturate(180%);
        -webkit-backdrop-filter: blur(25px) saturate(180%);
        border: 1px solid rgba(148, 163, 184, 0.15);
        border-radius: 18px;
        padding: 28px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        animation: scaleIn 0.5s ease-out;
    }

    .glass-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(124, 58, 237, 0.2);
        border-color: rgba(124, 58, 237, 0.3);
    }

    /* ===== Animated gradient text ===== */
    .gradient-text {
        background: linear-gradient(135deg, #7C3AED 0%, #2563EB 40%, #06B6D4 100%);
        background-size: 200% 200%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: gradientMesh 6s ease infinite;
    }

    /* ===== Float animation ===== */
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-8px); }
    }

    .float-anim {
        animation: float 3.5s ease-in-out infinite;
    }

    /* ===== 3D Float Animation ===== */
    @keyframes float-3d {
        0%, 100% { 
            transform: translateY(0px) rotateX(0deg) rotateY(0deg); 
        }
        50% { 
            transform: translateY(-12px) rotateX(5deg) rotateY(5deg); 
        }
    }
    
    .three-d-icon {
        animation: float-3d 6s ease-in-out infinite;
        transform-style: preserve-3d;
        perspective: 1000px;
        filter: drop-shadow(0 10px 20px rgba(124, 58, 237, 0.3));
    }
    
    .icon-container {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 180px;
        margin-bottom: 20px;
    }

    /* ===== Enhanced 3D Glow Card ===== */
    .glow-card {
        background: rgba(30, 41, 59, 0.75) !important;
        backdrop-filter: blur(25px) saturate(180%);
        border: 1px solid rgba(124, 58, 237, 0.25) !important;
        border-radius: 18px !important;
        padding: 28px !important;
        transition: all 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        position: relative;
        transform-style: preserve-3d;
        perspective: 1000px;
        margin-bottom: 18px;
        animation: fadeIn 0.6s ease-out;
    }

    .glow-card:hover {
        transform: translateY(-10px) rotateX(3deg) rotateY(3deg) scale(1.02) !important;
        box-shadow: 0 25px 50px -12px rgba(124, 58, 237, 0.5) !important;
        border-color: rgba(124, 58, 237, 0.7) !important;
    }

    /* Glow effect removed as per user request */
    .glow-card::before {
        content: none;
    }

    .glow-card:hover::before {
        content: none;
    }
    
    .glow-icon {
        font-size: 2.2em;
        margin-bottom: 14px;
        background: linear-gradient(135deg, #A78BFA 0%, #2563EB 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        filter: drop-shadow(0 6px 10px rgba(124, 58, 237, 0.4));
        animation: float 3s ease-in-out infinite;
    }

    /* ===== Staggered Card Entrance ===== */
    .glass-card:nth-child(1) { animation-delay: 0.1s; }
    .glass-card:nth-child(2) { animation-delay: 0.2s; }
    .glass-card:nth-child(3) { animation-delay: 0.3s; }
    .glass-card:nth-child(4) { animation-delay: 0.4s; }
    .glass-card:nth-child(5) { animation-delay: 0.5s; }

    /* ===== Loading Skeleton ===== */
    @keyframes skeleton-loading {
        0% { background-position: -200px 0; }
        100% { background-position: calc(200px + 100%) 0; }
    }

    .skeleton {
        background: linear-gradient(90deg, rgba(30, 41, 59, 0.5) 0px, rgba(124, 58, 237, 0.2) 40px, rgba(30, 41, 59, 0.5) 80px);
        background-size: 200px 100%;
        animation: skeleton-loading 1.5s infinite;
        border-radius: 12px;
    }
</style>
""", unsafe_allow_html=True)


# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user' not in st.session_state:
    st.session_state.user = None
if 'page' not in st.session_state:
    st.session_state.page = 'login'


def logout():
    """Handle user logout"""
    st.session_state.logged_in = False
    st.session_state.user = None
    st.session_state.page = 'login'
    st.rerun()


def show_login_page():
    """Display premium login and registration page"""
    
    # Center the content
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Hero Header
        st.markdown(f"""
        <div style="text-align: center; padding: 50px 0 30px 0;">
            <div class="icon-container">
                <svg class="three-d-icon" width="180" height="180" viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <rect x="40" y="40" width="120" height="140" rx="10" fill="url(#grad1)" stroke="rgba(255,255,255,0.2)" stroke-width="2"/>
                    <rect x="55" y="60" width="90" height="10" rx="5" fill="rgba(255,255,255,0.3)"/>
                    <rect x="55" y="80" width="90" height="10" rx="5" fill="rgba(255,255,255,0.3)"/>
                    <rect x="55" y="100" width="60" height="10" rx="5" fill="rgba(255,255,255,0.3)"/>
                    <circle cx="140" cy="160" r="25" fill="url(#grad2)" filter="url(#glow)"/>
                    <path d="M130 160 L138 168 L152 152" stroke="white" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
                    <defs>
                        <linearGradient id="grad1" x1="40" y1="40" x2="160" y2="180" gradientUnits="userSpaceOnUse">
                            <stop offset="0%" stop-color="#7C3AED" stop-opacity="0.9"/>
                            <stop offset="100%" stop-color="#2563EB" stop-opacity="0.8"/>
                        </linearGradient>
                        <linearGradient id="grad2" x1="115" y1="135" x2="165" y2="185" gradientUnits="userSpaceOnUse">
                            <stop offset="0%" stop-color="#10B981"/>
                            <stop offset="100%" stop-color="#059669"/>
                        </linearGradient>
                        <filter id="glow" x="0" y="0" width="200%" height="200%">
                            <feGaussianBlur stdDeviation="5" result="coloredBlur"/>
                            <feMerge>
                                <feMergeNode in="coloredBlur"/>
                                <feMergeNode in="SourceGraphic"/>
                            </feMerge>
                        </filter>
                    </defs>
                </svg>
            </div>
            <h1 style="font-size: 2.4em; margin: 0; font-weight: 900; letter-spacing: -1px;">
                <span class="gradient-text">{APP_TITLE}</span>
            </h1>
            <p style="color: #94A3B8; font-size: 1.1em; margin-top: 14px; font-weight: 400; line-height: 1.6;">
                Analyze your resume &bull; Discover opportunities &bull; Advance your career
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Tabs for Login and Register
        tab1, tab2, tab3 = st.tabs(["Login", "Register", "Forgot Password"])
        
        # Login Tab
        with tab1:
            st.markdown("<br>", unsafe_allow_html=True)
            
            with st.form("login_form"):
                email = st.text_input("Email Address", placeholder="your.email@example.com", key="login_email")
                password = st.text_input("Password", type="password", placeholder="Enter your password", key="login_password")
                submit = st.form_submit_button("Login", use_container_width=True)
                
                if submit:
                    if not email or not password:
                        st.error("Please enter both email and password")
                    else:
                        success, message, user_data = authenticate_user(email, password)
                        
                        if success:
                            st.session_state.logged_in = True
                            st.session_state.user = user_data
                            st.session_state.page = 'dashboard'
                            st.success(f"{message}")
                            st.rerun()
                        else:
                            st.error(f"{message}")

        # Register Tab
        with tab2:
            st.markdown("<br>", unsafe_allow_html=True)
            
            with st.form("register_form"):
                new_username = st.text_input("Username", placeholder="Choose a username", key="reg_username")
                new_email = st.text_input("Email Address", placeholder="your.email@example.com", key="reg_email")
                new_password = st.text_input("Password", type="password", placeholder="Choose a strong password", key="reg_password")
                confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password", key="reg_confirm")
                
                st.markdown("---")
                st.markdown("**Account Recovery Security**")
                security_q = st.selectbox(
                    "Security Question",
                    [
                        "What is your mother's maiden name?",
                        "What was the name of your first pet?",
                        "What city were you born in?",
                        "What was your childhood nickname?",
                        "What is your favorite food?"
                    ],
                    key="reg_sec_q"
                )
                security_a = st.text_input("Security Answer", placeholder="Answer to recover account", key="reg_sec_a")
                
                submit_reg = st.form_submit_button("Create Account", use_container_width=True)
                
                if submit_reg:
                    if not new_username or not new_email or not new_password:
                        st.error("Please fill in all required fields")
                    elif new_password != confirm_password:
                        st.error("Passwords do not match")
                    elif not security_a:
                        st.error("Please provide a security answer for account recovery")
                    else:
                        success, message, user_id = register_user(
                            new_username, new_email, new_password, 
                            security_question=security_q, security_answer=security_a
                        )
                        
                        if success:
                            st.success(f"{message}! Please login.")
                        else:
                            st.error(f"{message}")

        # Forgot Password Tab
        with tab3:
            st.markdown("<br>", unsafe_allow_html=True)
            
            if 'reset_stage' not in st.session_state:
                st.session_state.reset_stage = 1
                
            if st.session_state.reset_stage == 1:
                with st.form("reset_step1"):
                    reset_email = st.text_input("Enter your email address", key="reset_email")
                    submit_step1 = st.form_submit_button("Next", use_container_width=True)
                    
                    if submit_step1:
                        user = get_user_by_email(reset_email)
                        if user and user.get('security_question'):
                            st.session_state.reset_email_confirmed = reset_email
                            st.session_state.reset_question = user['security_question']
                            st.session_state.reset_stage = 2
                            st.rerun()
                        elif user:
                            st.error("Account exists but no security question set. Cannot reset password.")
                        else:
                            st.error("Email not found.")
            
            elif st.session_state.reset_stage == 2:
                st.info(f"Security Question: **{st.session_state.reset_question}**")
                with st.form("reset_step2"):
                    answer = st.text_input("Your Answer", key="reset_answer")
                    submit_step2 = st.form_submit_button("Verify Answer", use_container_width=True)
                    
                    if submit_step2:
                        from auth import verify_security_answer
                        if verify_security_answer(st.session_state.reset_email_confirmed, answer):
                            st.session_state.reset_stage = 3
                            st.rerun()
                        else:
                            st.error("Incorrect answer.")
                
                if st.button("Back"):
                    st.session_state.reset_stage = 1
                    st.rerun()

            elif st.session_state.reset_stage == 3:
                with st.form("reset_step3"):
                    new_pass = st.text_input("New Password", type="password", key="reset_new_pass")
                    confirm_pass = st.text_input("Confirm New Password", type="password", key="reset_confirm_pass")
                    submit_step3 = st.form_submit_button("Reset Password", use_container_width=True)
                    
                    if submit_step3:
                        if new_pass != confirm_pass:
                            st.error("Passwords do not match")
                        else:
                            from auth import reset_password
                            if reset_password(st.session_state.reset_email_confirmed, new_pass):
                                st.success("Password reset successful! You can now login.")
                                st.session_state.reset_stage = 1
                                if 'reset_email_confirmed' in st.session_state:
                                    del st.session_state.reset_email_confirmed
                                if 'reset_question' in st.session_state:
                                    del st.session_state.reset_question
                            else:
                                st.error("Failed to reset password.")
        
        # Footer
        st.markdown("""
        <div style="text-align: center; padding: 30px 0 10px 0; color: #475569; font-size: 0.82em;">
            <p> Your data is securely encrypted and stored locally</p>
        </div>
        """, unsafe_allow_html=True)


def show_dashboard():
    """Display main dashboard with premium glassmorphism design"""
    
    user = st.session_state.user
    
    # Header
    render_header(user['username'], "Career Dashboard")
    
    # Get latest analysis
    analysis = get_latest_analysis(user['id'])
    
    if not analysis:
        # No resume — show stunning empty state
        st.markdown("""
        <div class="glass-card" style="text-align: center; padding: 60px 30px;">
            <div class="icon-container" style="height: 220px;">
                <svg class="three-d-icon" width="200" height="200" viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M100 30 L30 70 L100 110 L170 70 Z" fill="url(#grad3)" stroke="rgba(255,255,255,0.2)"/>
                    <path d="M30 70 L30 140 L100 180 L170 140 L170 70 L100 110 Z" fill="url(#grad4)" stroke="rgba(255,255,255,0.1)"/>
                    <path d="M100 110 L100 180" stroke="rgba(255,255,255,0.1)" stroke-width="1"/>
                    <defs>
                        <linearGradient id="grad3" x1="30" y1="30" x2="170" y2="110" gradientUnits="userSpaceOnUse">
                            <stop offset="0%" stop-color="#8B5CF6"/>
                            <stop offset="100%" stop-color="#6D28D9"/>
                        </linearGradient>
                        <linearGradient id="grad4" x1="30" y1="70" x2="170" y2="180" gradientUnits="userSpaceOnUse">
                            <stop offset="0%" stop-color="#7C3AED" stop-opacity="0.8"/>
                            <stop offset="100%" stop-color="#4C1D95" stop-opacity="0.9"/>
                        </linearGradient>
                    </defs>
                </svg>
            </div>
            <h2 style="margin: 0 0 12px 0; font-weight: 800; font-size: 1.6em;">
                <span class="gradient-text">Get Started with Your Career Journey</span>
            </h2>
            <p style="color: #94A3B8; font-size: 1.05em; margin-bottom: 0; line-height: 1.7; max-width: 500px; margin: 0 auto;">
                Upload your resume to receive personalized AI analysis and tailored job matches.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button(" Upload Resume", use_container_width=True, type="primary", key="dash_empty_upload"):
                st.session_state.page = 'upload'
                st.rerun()
        
        # Feature highlights
        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("""
            <div class="glass-card" style="text-align: center; padding: 28px 20px;">
                <div style="height: 100px; display: flex; justify-content: center; align-items: center; margin-bottom: 12px;">
                    <svg width="80" height="80" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <circle cx="50" cy="50" r="40" fill="url(#grad_ai)" stroke="rgba(124, 58, 237, 0.3)" stroke-width="2"/>
                        <path d="M50 30 L50 70 M30 50 L70 50" stroke="white" stroke-width="4" stroke-linecap="round"/>
                        <circle cx="50" cy="50" r="10" fill="white"/>
                        <defs>
                            <radialGradient id="grad_ai" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate(50 50) rotate(90) scale(40)">
                                <stop stop-color="#7C3AED" stop-opacity="0.8"/>
                                <stop offset="1" stop-color="#2563EB" stop-opacity="0.2"/>
                            </radialGradient>
                        </defs>
                    </svg>
                </div>
                <h4 style="color: #E2E8F0; margin: 0 0 8px 0; font-weight: 700;">AI-Powered Analysis</h4>
                <p style="color: #94A3B8; font-size: 0.88em; margin: 0; line-height: 1.6;">Deep resume parsing with intelligent skill extraction</p>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown("""
            <div class="glass-card" style="text-align: center; padding: 28px 20px;">
                <div style="height: 100px; display: flex; justify-content: center; align-items: center; margin-bottom: 12px;">
                    <svg width="80" height="80" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <circle cx="50" cy="50" r="35" stroke="#10B981" stroke-width="2" fill="rgba(16, 185, 129, 0.1)"/>
                        <circle cx="50" cy="50" r="25" stroke="#10B981" stroke-width="2"/>
                        <circle cx="50" cy="50" r="8" fill="#10B981"/>
                        <path d="M50 10 L50 20 M50 80 L50 90 M90 50 L80 50 M10 50 L20 50" stroke="#10B981" stroke-width="2" stroke-linecap="round"/>
                    </svg>
                </div>
                <h4 style="color: #E2E8F0; margin: 0 0 8px 0; font-weight: 700;">Smart Matching</h4>
                <p style="color: #94A3B8; font-size: 0.88em; margin: 0; line-height: 1.6;">Precision job matching based on your unique profile</p>
            </div>
            """, unsafe_allow_html=True)
        with c3:
            st.markdown("""
            <div class="glass-card" style="text-align: center; padding: 28px 20px;">
                <div style="height: 100px; display: flex; justify-content: center; align-items: center; margin-bottom: 12px;">
                    <svg width="80" height="80" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M20 80 L40 60 L60 70 L80 30" stroke="#F59E0B" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
                        <path d="M80 30 L80 50 M80 30 L60 30" stroke="#F59E0B" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
                        <path d="M20 80 L90 80" stroke="rgba(255,255,255,0.1)" stroke-width="2"/>
                    </svg>
                </div>
                <h4 style="color: #E2E8F0; margin: 0 0 8px 0; font-weight: 700;">Growth Insights</h4>
                <p style="color: #94A3B8; font-size: 0.88em; margin: 0; line-height: 1.6;">Actionable recommendations to boost your career</p>
            </div>
            """, unsafe_allow_html=True)
        
        return
    
    # ===== Dashboard with data =====
    
    # Top Metric Cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(render_metric_card(
            "Resume Score",
            f"{analysis['score']}/100",
            "",
            "#7C3AED"
        ), unsafe_allow_html=True)
    
    with col2:
        st.markdown(render_metric_card(
            "Technical Skills",
            str(len(analysis['technical_skills'])),
            "",
            "#06B6D4"
        ), unsafe_allow_html=True)
    
    with col3:
        st.markdown(render_metric_card(
            "Skill Gaps Identified",
            str(len(analysis['missing_skills'])),
            "",
            "#F59E0B"
        ), unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Two column layout
    col_left, col_right = st.columns([1, 1])
    
    with col_left:
        # Resume Score Gauge
        render_section_header("Resume Performance", "")
        fig = render_score_gauge(analysis['score'])
        st.plotly_chart(fig, use_container_width=True)
        
        # Professional Summary
        render_section_header("Professional Summary", "")
        st.markdown(f"""
        <div class="glass-card">
            <p style="line-height: 1.9; color: #CBD5E1; font-size: 0.98em;">{analysis['summary']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_right:
        # Skills Distribution Chart
        render_section_header("Skills Overview", "")
        if analysis['technical_skills'] or analysis['soft_skills']:
            fig = render_skills_chart(analysis['technical_skills'], analysis['soft_skills'])
            if fig:
                st.plotly_chart(fig, use_container_width=True)
    
    # Technical Skills
    render_section_header("Technical Skills", "")
    if analysis['technical_skills']:
        st.markdown(render_skill_badges(analysis['technical_skills'], "#7C3AED"), unsafe_allow_html=True)
    else:
        render_alert("No technical skills detected in your resume", "warning")
    
    # Soft Skills
    render_section_header("Soft Skills", "")
    if analysis['soft_skills']:
        st.markdown(render_skill_badges(analysis['soft_skills'], "#06B6D4"), unsafe_allow_html=True)
    else:
        render_alert("No soft skills detected in your resume", "warning")
    
    # Strengths and Weaknesses
    col1, col2 = st.columns(2)
    
    with col1:
        render_section_header("Strengths", "")
        if analysis['strengths']:
            for strength in analysis['strengths']:
                st.markdown(f"""
                <div style="
                    background: rgba(16, 185, 129, 0.08);
                    border-left: 3px solid #10B981;
                    padding: 12px 16px;
                    margin-bottom: 8px;
                    border-radius: 0 10px 10px 0;
                    color: #6EE7B7;
                    font-size: 0.93em;
                    line-height: 1.6;
                "> {strength}</div>
                """, unsafe_allow_html=True)
        else:
            st.info("Analyzing strengths...")
    
    with col2:
        render_section_header("Areas for Improvement", "")
        if analysis['weaknesses']:
            for weakness in analysis['weaknesses']:
                st.markdown(f"""
                <div style="
                    background: rgba(245, 158, 11, 0.08);
                    border-left: 3px solid #F59E0B;
                    padding: 12px 16px;
                    margin-bottom: 8px;
                    border-radius: 0 10px 10px 0;
                    color: #FCD34D;
                    font-size: 0.93em;
                    line-height: 1.6;
                "> {weakness}</div>
                """, unsafe_allow_html=True)
        else:
            st.info("No significant weaknesses identified")
    
    # Missing Skills
    if analysis['missing_skills']:
        render_section_header("Skills to Learn", "")
        render_alert(
            f"Based on your profile, consider learning these in-demand skills: {', '.join(analysis['missing_skills'][:5])}",
            "info"
        )
    
    # Improvement Suggestions
    render_section_header("Personalized Recommendations", "")
    if analysis['suggestions']:
        for i, suggestion in enumerate(analysis['suggestions'], 1):
            st.markdown(render_glow_card(
                f"Recommendation #{i}",
                suggestion,
                "🚀",
                "#7C3AED"
            ), unsafe_allow_html=True)
    
    # Action buttons
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("Upload New Resume", use_container_width=True, key="dash_upload_new"):
            st.session_state.page = 'upload'
            st.rerun()
    
    with col2:
        if st.button("✨ Fix Mistakes & Build Resume", use_container_width=True, key="dash_ai_builder"):
            st.session_state.page = 'resume_builder'
            st.rerun()

def show_upload_page():
    """Display premium resume upload page"""
    
    user = st.session_state.user
    
    render_header(user['username'], "Upload Resume")
    
    st.markdown("""
    <div class="glass-card" style="margin-bottom: 30px;">
        <h3 style="color: #A78BFA; margin: 0 0 12px 0; font-weight: 700;">Upload Your Resume for Analysis</h3>
        <p style="color: #94A3B8; line-height: 1.8; margin: 0; font-size: 0.98em;">
            Upload your resume in PDF or DOCX format. Our AI will analyze your skills, experience, 
            and provide personalized recommendations to enhance your career prospects.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Choose your resume file",
        type=list(ALLOWED_EXTENSIONS),
        help=f"Maximum file size: {MAX_FILE_SIZE_MB}MB. Supported formats: {', '.join(ALLOWED_EXTENSIONS).upper()}"
    )
    
    if uploaded_file:
        # Display file info
        st.info(f"Selected file: **{uploaded_file.name}** ({uploaded_file.size / 1024:.1f} KB)")
        
        if st.button("Analyze Resume", type="primary", use_container_width=True):
            # Validate file
            file_bytes = uploaded_file.read()
            
            # Validate file size
            is_valid, message = validate_file_size(file_bytes, MAX_FILE_SIZE_MB)
            if not is_valid:
                st.error(f"{message}")
                return
            
            # Validate file extension
            is_valid, message = validate_file_extension(uploaded_file.name, ALLOWED_EXTENSIONS)
            if not is_valid:
                st.error(f"{message}")
                return
            
            # Extract text
            with st.spinner("Extracting text from resume..."):
                success, message, extracted_text = extract_text(file_bytes, uploaded_file.name)
            
            if not success:
                st.error(f"{message}")
                return
            
            st.success(f"{message}")
            
            # Save resume to database
            with st.spinner("Saving resume..."):
                resume_id = save_resume(user['id'], uploaded_file.name, extracted_text)
            
            # Analyze resume
            with st.spinner("Analyzing your resume with AI... This may take a moment..."):
                analysis_results = analyze_resume(extracted_text)
            
            # Save analysis
            with st.spinner("Saving analysis..."):
                save_analysis(resume_id, analysis_results)
            
            st.success("Analysis complete!")
            
            # ✅ Store results in session_state so the panel below persists on reruns
            st.session_state['last_upload_analysis'] = analysis_results

    # --- Results Panel ---
    # Rendered OUTSIDE the button block so it survives reruns when navigation buttons are clicked
    analysis_results = st.session_state.get('last_upload_analysis')
    if analysis_results:
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(render_metric_card(
                "Resume Score",
                f"{analysis_results['score']}/100",
                "",
                "#7C3AED"
            ), unsafe_allow_html=True)
            st.markdown(render_metric_card(
                "Technical Skills Found",
                str(len(analysis_results['technical_skills'])),
                "",
                "#06B6D4"
            ), unsafe_allow_html=True)
        
        with col2:
            st.markdown(render_metric_card(
                "Soft Skills Found",
                str(len(analysis_results['soft_skills'])),
                "",
                "#10B981"
            ), unsafe_allow_html=True)
            st.markdown(render_metric_card(
                "Improvement Areas",
                str(len(analysis_results['weaknesses'])),
                "",
                "#F59E0B"
            ), unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📊 View Full Analysis", use_container_width=True, type="primary", key="upload_view_analysis"):
                st.session_state.page = 'analysis'
                st.rerun()
        
        with col2:
            if st.button("🚀 Improve with AI Builder", use_container_width=True, key="upload_go_builder"):
                st.session_state.page = 'resume_builder'
                st.rerun()


def show_analysis_page():
    """Display detailed analysis results with premium styling"""
    
    user = st.session_state.user
    
    render_header(user['username'], "Detailed Resume Analysis")
    
    analysis = get_latest_analysis(user['id'])
    
    if not analysis:
        render_alert("No analysis available. Please upload a resume first.", "warning")
        if st.button("Upload Resume", key="analysis_upload"):
            st.session_state.page = 'upload'
            st.rerun()
        return
    
    # Score Section
    col1, col2 = st.columns([1, 2])
    
    with col1:
        fig = render_score_gauge(analysis['score'])
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Score quality label
        if analysis['score'] >= 80:
            score_label = "Excellent"
            score_color = "#10B981"
        elif analysis['score'] >= 60:
            score_label = "Good"
            score_color = "#F59E0B"
        else:
            score_label = "Needs Work"
            score_color = "#EF4444"

        st.markdown(f"""
        <div class="glass-card" style="height: 100%; display: flex; flex-direction: column; justify-content: center;">
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 16px;">
                <span style="
                    background: {score_color}22;
                    color: {score_color};
                    padding: 4px 14px;
                    border-radius: 20px;
                    font-size: 0.85em;
                    font-weight: 700;
                    border: 1px solid {score_color}44;
                ">{score_label}</span>
            </div>
            <h3 style="color: #E2E8F0; margin: 0 0 14px 0; font-weight: 700; font-size: 1.2em;">Score Breakdown</h3>
            <p style="line-height: 1.9; color: #94A3B8; margin: 0; font-size: 0.95em;">
                Your resume scored <strong style="color: #A78BFA;">{analysis['score']}</strong> out of 100. 
                This score is calculated based on content quality, technical skills breadth, 
                experience relevance, education, and soft skills presence.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Professional Summary
    render_section_header("Professional Summary", "")
    st.markdown(f"""
    <div class="glass-card">
        <p style="font-size: 1em; line-height: 1.9; color: #CBD5E1; margin: 0;">{analysis['summary']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Skills
    col1, col2 = st.columns(2)
    
    with col1:
        render_section_header("Technical Skills", "")
        st.markdown(render_skill_badges(analysis['technical_skills'], "#7C3AED"), unsafe_allow_html=True)
    
    with col2:
        render_section_header("Soft Skills", "")
        st.markdown(render_skill_badges(analysis['soft_skills'], "#06B6D4"), unsafe_allow_html=True)
    
    # Strengths and Weaknesses
    col1, col2 = st.columns(2)
    
    with col1:
        render_section_header("Key Strengths", "")
        for strength in analysis['strengths']:
            st.markdown(f"""
            <div style="
                background: rgba(16, 185, 129, 0.08);
                padding: 14px 18px;
                margin-bottom: 8px;
                border-radius: 0 12px 12px 0;
                border-left: 3px solid #10B981;
                color: #6EE7B7;
                font-size: 0.93em;
                line-height: 1.6;
            "> {strength}</div>
            """, unsafe_allow_html=True)
    
    with col2:
        render_section_header("Areas for Improvement", "")
        for weakness in analysis['weaknesses']:
            st.markdown(f"""
            <div style="
                background: rgba(245, 158, 11, 0.08);
                padding: 14px 18px;
                margin-bottom: 8px;
                border-radius: 0 12px 12px 0;
                border-left: 3px solid #F59E0B;
                color: #FCD34D;
                font-size: 0.93em;
                line-height: 1.6;
            "> {weakness}</div>
            """, unsafe_allow_html=True)
    
    # Missing Skills
    render_section_header("Recommended Skills to Learn", "")
    if analysis['missing_skills']:
        st.markdown(render_skill_badges(analysis['missing_skills'], "#F59E0B"), unsafe_allow_html=True)
        st.markdown("""
        <p style="color: #94A3B8; margin-top: 12px; font-style: italic; font-size: 0.92em;">
            Learning these skills can significantly improve your job prospects and resume score.
        </p>
        """, unsafe_allow_html=True)
    else:
        st.info("Great! You have a comprehensive skill set.")
    
    # Suggestions
    render_section_header("Personalized Improvement Suggestions", "")
    for i, suggestion in enumerate(analysis['suggestions'], 1):
        st.markdown(f"""
        <div style="
            background: rgba(30, 41, 59, 0.6);
            backdrop-filter: blur(10px);
            padding: 18px 22px;
            margin-bottom: 12px;
            border-left: 4px solid #7C3AED;
            border-radius: 0 12px 12px 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            border-top: 1px solid rgba(148,163,184,0.06);
            border-right: 1px solid rgba(148,163,184,0.06);
            border-bottom: 1px solid rgba(148,163,184,0.06);
        ">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <strong style="color: #A78BFA; font-size: 1.1em;">{i}.</strong> 
                    <span style="color: #CBD5E1; margin-left: 8px; line-height: 1.7;">{suggestion}</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    if st.button("🛠️ Fix Issues in Resume Builder", type="primary", use_container_width=True, key="analysis_fix_issues"):
        st.session_state.page = 'resume_builder'
        st.rerun()
# ========================== RECOMMENDATIONS PAGE ==========================
def show_recommendations_page():
    """Display career recommendations with real job links"""
    
    user = st.session_state.user
    render_header(user['username'], "Career Recommendations")
    
    analysis = get_latest_analysis(user['id'])
    
    if not analysis:
        render_alert("No analysis available. Please upload and analyze your resume first.", "warning")
        if st.button("Upload Resume", key="rec_upload"):
            st.session_state.page = 'upload'
            st.rerun()
        return
    
    from job_matcher import get_job_recommendations
    import urllib.parse
    
    with st.spinner("Fetching real-time job listings based on your skills..."):
        # Fetch up to 20 jobs to ensure we display more than 10
        job_matches = get_job_recommendations(user['id'], limit=20)
        
    if not job_matches:
        render_alert("No job matching your skills were found at this time.", "warning")
        return
    
    st.markdown(f"""
    <div class="glass-card" style="margin-bottom: 30px;">
        <div style="display: flex; align-items: center; gap: 14px;">
            <span style="font-size: 2em;">💼</span>
            <div>
                <h3 style="color: #E2E8F0; margin: 0; font-weight: 700;">
                    {len(job_matches)} Real-Time Jobs Matched
                </h3>
                <p style="color: #94A3B8; margin: 4px 0 0 0; font-size: 0.92em;">
                    Based on your extracted skills. Click 'Apply on LinkedIn' to apply immediately.
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state for selected job if not present
    if 'selected_job_idx' not in st.session_state:
        st.session_state.selected_job_idx = 0

    # Ensure selected index is valid
    if st.session_state.selected_job_idx >= len(job_matches):
        st.session_state.selected_job_idx = 0

    # Master-Detail Layout
    list_col, detail_col = st.columns([1.3, 2.7], gap="large")
    
    with list_col:
        st.markdown("<h4 style='color: #E2E8F0; margin-top: 0; margin-bottom: 20px;'>Job Recommendations</h4>", unsafe_allow_html=True)
        
        for i, job in enumerate(job_matches):
            is_selected = (st.session_state.selected_job_idx == i)
            ms = job.get('match_score', 0)
            
            # Styling based on selection
            bg_color = "rgba(124, 58, 237, 0.15)" if is_selected else "rgba(30, 41, 59, 0.4)"
            border_color = "#7C3AED" if is_selected else "rgba(148, 163, 184, 0.1)"
            title_color = "#F8FAFC" if is_selected else "#A78BFA"
            
            st.markdown(f"""
                <div style="
                    padding: 16px;
                    padding-bottom: 8px;
                    background: {bg_color};
                    border: 1px solid {border_color};
                    border-radius: 12px;
                    margin-bottom: 12px;
                    transition: all 0.2s ease;
                ">
                    <div style="color: {title_color}; font-weight: 700; font-size: 1.05em; margin-bottom: 4px; line-height: 1.3;">{job['title']}</div>
                    <div style="color: #E2E8F0; font-size: 0.9em; margin-bottom: 2px;">{job['company']}</div>
                    <div style="color: #94A3B8; font-size: 0.85em;">{job['location']}</div>
                    <div style="color: #10B981; font-size: 0.82em; font-weight: 600; margin-top: 8px;">
                        {job.get('days_ago', 0)} days ago • <span style="color: #A78BFA;">{ms}% Match</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Button for selection
            btn_label = "Currently Viewing" if is_selected else f"Select Role #{i+1}"
            if st.button(btn_label, key=f"job_sel_{i}", use_container_width=True, type="primary" if is_selected else "secondary"):
                if st.session_state.selected_job_idx != i:
                    st.session_state.selected_job_idx = i
                    st.rerun()

    with detail_col:
        job = job_matches[st.session_state.selected_job_idx]
        job_title = job['title']
        company = job['company']
        location = job['location']
        match_pct = float(job.get('match_score', 0))
        apply_link = job['apply_link']
        description = job.get('description', '')
        
        # Ensure apply link is a LinkedIn search if it's not a direct provided link
        if "linkedin.com" not in apply_link.lower():
            q = urllib.parse.quote_plus(f'{job_title} {company}')
            apply_link = f'https://www.linkedin.com/jobs/search/?keywords={q}'
        
        # Color based on match
        if match_pct >= 70:
            color = "#10B981"
            badge = "Strong Match"
        elif match_pct >= 40:
            color = "#F59E0B"
            badge = "Moderate Match"
        else:
            color = "#EF4444"
            badge = "Growth Opportunity"
            
        with st.container():
            # Job Header
            st.markdown(f"""
            <div style="margin-bottom: 24px;">
                <h1 style="color: #F8FAFC; margin-bottom: 4px; font-size: 2.2em; font-weight: bold;">{job_title}</h1>
                <p style="color: #94A3B8; font-size: 1.1em; margin-bottom: 12px;">
                    <span style="color: #E2E8F0; font-weight: 600;">{company}</span> &nbsp;·&nbsp; {location} &nbsp;·&nbsp; {job.get('days_ago', 0)} days ago
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Apply Button natively rendered
            st.link_button("Apply Now on LinkedIn ↗", apply_link, type="primary")
            
            # Match Overview
            st.markdown(f"""
            <div style="
                background: rgba(30, 41, 59, 0.4); 
                border-radius: 12px; 
                padding: 20px; 
                margin: 24px 0;
                border: 1px solid rgba(148,163,184,0.1);
            ">
                <div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
                    <span style="color: #E2E8F0; font-weight: bold; font-size: 1.05em;">AI Fit Assessment</span>
                    <span style="
                        background: {color}22;
                        color: {color};
                        padding: 4px 14px;
                        border-radius: 20px;
                        font-size: 0.82em;
                        font-weight: 700;
                        border: 1px solid {color}44;
                    ">{match_pct}% • {badge}</span>
                </div>
                <div style="
                    background: rgba(15, 23, 42, 0.6);
                    border-radius: 10px;
                    height: 12px;
                    overflow: hidden;
                    margin-bottom: 8px;
                ">
                    <div style="
                        background: linear-gradient(90deg, {color}, {color}CC);
                        width: {match_pct}%;
                        height: 100%;
                        border-radius: 10px;
                        transition: width 0.8s ease;
                    "></div>
                </div>
                <p style="color: #94A3B8; font-size: 0.85em; margin-top: 0;">
                    {job.get('total_matched', 0)} of {job.get('total_required', 1)} required skills matched directly from your resume.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Skills breakdown
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<p style="color: #10B981; font-weight: 700; font-size: 0.9em; margin-bottom: 8px;">Matched Skills</p>', unsafe_allow_html=True)
                matched_skills = job.get('direct_matches', []) + job.get('related_matches', [])
                if matched_skills:
                    badges_html = " ".join(
                        f'<span style="display:inline-block; background:#10B98122; color:#10B981; padding:4px 12px; margin:2px; border-radius:16px; font-size:0.82em; border:1px solid #10B98144;">{s}</span>'
                        for s in set(matched_skills)
                    )
                    st.markdown(badges_html, unsafe_allow_html=True)
                else:
                    st.markdown("<p style='color:#64748B; font-size:0.85em;'>None closely matched</p>", unsafe_allow_html=True)
            
            with col2:
                st.markdown('<p style="color: #F59E0B; font-weight: 700; font-size: 0.9em; margin-bottom: 8px;">Missing Skills</p>', unsafe_allow_html=True)
                required_set = set(s.lower() for s in job.get('required_skills', []))
                matched_set = set(s.lower() for s in matched_skills)
                missing_skills = sorted(list(required_set - matched_set))
                
                if missing_skills:
                    badges_html = " ".join(
                        f'<span style="display:inline-block; background:#F59E0B22; color:#F59E0B; padding:4px 12px; margin:2px; border-radius:16px; font-size:0.82em; border:1px solid #F59E0B44;">{s}</span>'
                        for s in missing_skills
                    )
                    st.markdown(badges_html, unsafe_allow_html=True)
                else:
                    st.markdown("<p style='color:#64748B; font-size:0.85em;'>All covered! 🎉</p>", unsafe_allow_html=True)

            # Job Description
            st.markdown("---")
            st.markdown("#### About the job")
            st.markdown(f"<div style='color: #CBD5E1; line-height: 1.6;'>{description}</div>", unsafe_allow_html=True)


# ========================== RESUME BUILDER PAGE ==========================
def show_resume_builder_page():
    """Display resume builder with form, preview, and PDF download"""
    
    user = st.session_state.user
    render_header(user['username'], "Resume Builder")
    
    analysis = get_latest_analysis(user['id'])
    
    st.markdown("""
    <div class="glass-card" style="margin-bottom: 30px;">
        <div style="display: flex; align-items: center; gap: 14px;">
            <span style="font-size: 2em;"></span>
            <div>
                <h3 style="color: #E2E8F0; margin: 0; font-weight: 700;">Build Your Professional Resume</h3>
                <p style="color: #94A3B8; margin: 4px 0 0 0; font-size: 0.92em;">
                    Fill in your details below to generate a professional resume.
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    
    # ---- Profile Form ----
    render_section_header("Personal Information", "")
    
    col1, col2 = st.columns(2)
    with col1:
        # Set defaults via session state so pre-filled resume data takes priority
        if 'rb_name' not in st.session_state:
            st.session_state.rb_name = user.get('username', '')
        if 'rb_email' not in st.session_state:
            st.session_state.rb_email = user.get('email', '')
        full_name = st.text_input("Full Name", key="rb_name")
        email = st.text_input("Email", key="rb_email")
    with col2:
        phone = st.text_input("Phone Number", key="rb_phone")
        location = st.text_input("Location", key="rb_location")
    
    # Professional Summary
    render_section_header("Professional Summary", "")
    
    col_sum_1, col_sum_2 = st.columns([3, 1])
    with col_sum_2:
        if st.button("✨ AI Enhance", key="ai_enhance_summary", use_container_width=True):
            if 'rb_summary' in st.session_state and st.session_state.rb_summary:
                enhanced = enhance_resume_text(st.session_state.rb_summary, "summary")
                st.session_state.rb_summary = enhanced
                st.rerun()
                
    # Logic to prioritize session state (user edits) over default analysis
    if 'rb_summary' not in st.session_state and analysis:
        st.session_state.rb_summary = analysis.get('summary', '')
        
    summary = st.text_area("Write a brief professional summary", key="rb_summary", height=120)
    with col_sum_1:
         st.caption("Tip: Write a draft and click 'AI Enhance' to make it professional.")
    
    # Skills
    render_section_header("Skills", "")
    col1, col2 = st.columns(2)
    with col1:
        if 'rb_tech' not in st.session_state and analysis:
            st.session_state.rb_tech = ", ".join(analysis.get('technical_skills', []))
        tech_skills_input = st.text_area("Technical Skills (comma-separated)", height=80, key="rb_tech")
    with col2:
        if 'rb_soft' not in st.session_state and analysis:
            st.session_state.rb_soft = ", ".join(analysis.get('soft_skills', []))
        soft_skills_input = st.text_area("Soft Skills (comma-separated)", height=80, key="rb_soft")
    
    # Education
    render_section_header("Education", "")
    if "rb_edu_count" not in st.session_state:
        st.session_state.rb_edu_count = 1
    edu_count = st.number_input("Number of education entries", min_value=0, max_value=5, key="rb_edu_count")
    education_entries = []
    for i in range(int(edu_count)):
        with st.container():
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                inst = st.text_input(f"Institution {i+1}", key=f"rb_edu_inst_{i}")
            with col2:
                degree = st.text_input(f"Degree {i+1}", key=f"rb_edu_deg_{i}")
            with col3:
                year = st.text_input(f"Year {i+1}", key=f"rb_edu_year_{i}")
            education_entries.append({'institution': inst, 'degree': degree, 'year': year})
    
    # Experience
    render_section_header("Work Experience", "")
    if "rb_exp_count" not in st.session_state:
        st.session_state.rb_exp_count = 1
    exp_count = st.number_input("Number of experience entries", min_value=0, max_value=10, key="rb_exp_count")
    experience_entries = []
    for i in range(int(exp_count)):
        with st.container():
            col1, col2 = st.columns(2)
            with col1:
                company = st.text_input(f"Company {i+1}", key=f"rb_exp_comp_{i}")
                role = st.text_input(f"Role {i+1}", key=f"rb_exp_role_{i}")
            with col2:
                duration = st.text_input(f"Duration {i+1}", placeholder="e.g. Jan 2022 - Present", key=f"rb_exp_dur_{i}")
                description = st.text_area(f"Description {i+1}", height=80, key=f"rb_exp_desc_{i}")
                if st.button(f"✨ Enhance Role {i+1}", key=f"ai_exp_{i}", use_container_width=True):
                     if description:
                         enhanced_desc = enhance_resume_text(description, "experience", role)
                         st.session_state[f"rb_exp_desc_{i}"] = enhanced_desc
                         st.rerun()
            experience_entries.append({'company': company, 'role': role, 'duration': duration, 'description': description})
    
    # Projects
    render_section_header("Projects", "")
    if "rb_proj_count" not in st.session_state:
        st.session_state.rb_proj_count = 1
    proj_count = st.number_input("Number of projects", min_value=0, max_value=10, key="rb_proj_count")
    project_entries = []
    for i in range(int(proj_count)):
        with st.container():
            col1, col2 = st.columns(2)
            with col1:
                proj_name = st.text_input(f"Project Name {i+1}", key=f"rb_proj_name_{i}")
            with col2:
                proj_tech = st.text_input(f"Technologies {i+1}", key=f"rb_proj_tech_{i}")
            proj_desc = st.text_area(f"Project Description {i+1}", height=80, key=f"rb_proj_desc_{i}")
            project_entries.append({'name': proj_name, 'technologies': proj_tech, 'description': proj_desc})
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ---- Preview & Download ----
    col_preview, col_download = st.columns([3, 1])
    
    with col_download:
        generate = st.button("Generate Resume", type="primary", use_container_width=True, key="rb_generate")
    
    if generate or "resume_pdf" in st.session_state:
        if generate:
            try:
                # Parse skills
                tech_list = [s.strip() for s in tech_skills_input.split(',') if s.strip()]
                soft_list = [s.strip() for s in soft_skills_input.split(',') if s.strip()]
                
                # Build HTML preview
                preview_html = f"""
                <div style="
                    background: #FFFFFF;
                    color: #1a1a1a;
                    padding: 40px;
                    border-radius: 12px;
                    font-family: 'Inter', Georgia, serif;
                    max-width: 800px;
                    margin: 20px auto;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
                ">
                    <div style="text-align: center; border-bottom: 3px solid #7C3AED; padding-bottom: 20px; margin-bottom: 24px;">
                        <h1 style="color: #1a1a1a; margin: 0; font-size: 1.8em; font-weight: 800; letter-spacing: -0.5px;">{full_name or 'Your Name'}</h1>
                        <p style="color: #555; margin: 8px 0 0 0; font-size: 0.92em;">
                            {' • '.join(filter(None, [email, phone, location]))}
                        </p>
                    </div>
                """
                
                if summary:
                    preview_html += f"""
                    <div style="margin-bottom: 22px;">
                        <h3 style="color: #7C3AED; font-size: 1em; text-transform: uppercase; letter-spacing: 1.5px; border-bottom: 1px solid #ddd; padding-bottom: 6px; margin-bottom: 10px;">Professional Summary</h3>
                        <p style="color: #333; line-height: 1.7; font-size: 0.92em;">{summary}</p>
                    </div>
                    """
                
                if tech_list or soft_list:
                    all_skills = tech_list + soft_list
                    skills_html = " ".join(f'<span style="display:inline-block; background:#f0ecff; color:#7C3AED; padding:3px 10px; margin:2px; border-radius:12px; font-size:0.82em;">{s}</span>' for s in all_skills)
                    preview_html += f"""
                    <div style="margin-bottom: 22px;">
                        <h3 style="color: #7C3AED; font-size: 1em; text-transform: uppercase; letter-spacing: 1.5px; border-bottom: 1px solid #ddd; padding-bottom: 6px; margin-bottom: 10px;">Skills</h3>
                        {skills_html}
                    </div>
                    """
                
                valid_exp = [e for e in experience_entries if e['company'] or e['role']]
                if valid_exp:
                    preview_html += '<div style="margin-bottom: 22px;"><h3 style="color: #7C3AED; font-size: 1em; text-transform: uppercase; letter-spacing: 1.5px; border-bottom: 1px solid #ddd; padding-bottom: 6px; margin-bottom: 10px;">Work Experience</h3>'
                    for exp in valid_exp:
                        preview_html += f"""
                        <div style="margin-bottom: 14px;">
                            <div style="display: flex; justify-content: space-between;">
                                <strong style="color: #1a1a1a;">{exp['role']}</strong>
                                <span style="color: #777; font-size: 0.85em;">{exp['duration']}</span>
                            </div>
                            <p style="color: #555; font-style: italic; margin: 2px 0 4px 0; font-size: 0.9em;">{exp['company']}</p>
                            <p style="color: #333; line-height: 1.6; font-size: 0.88em; margin: 0;">{exp['description']}</p>
                        </div>
                        """
                    preview_html += '</div>'
                
                valid_edu = [e for e in education_entries if e['institution'] or e['degree']]
                if valid_edu:
                    preview_html += '<div style="margin-bottom: 22px;"><h3 style="color: #7C3AED; font-size: 1em; text-transform: uppercase; letter-spacing: 1.5px; border-bottom: 1px solid #ddd; padding-bottom: 6px; margin-bottom: 10px;">Education</h3>'
                    for edu in valid_edu:
                        preview_html += f"""
                        <div style="margin-bottom: 10px; display: flex; justify-content: space-between;">
                            <div><strong style="color: #1a1a1a;">{edu['degree']}</strong><br><span style="color: #555; font-size: 0.88em;">{edu['institution']}</span></div>
                            <span style="color: #777; font-size: 0.85em;">{edu['year']}</span>
                        </div>
                        """
                    preview_html += '</div>'
                
                valid_proj = [p for p in project_entries if p['name']]
                if valid_proj:
                    preview_html += '<div style="margin-bottom: 22px;"><h3 style="color: #7C3AED; font-size: 1em; text-transform: uppercase; letter-spacing: 1.5px; border-bottom: 1px solid #ddd; padding-bottom: 6px; margin-bottom: 10px;">Projects</h3>'
                    for proj in valid_proj:
                        preview_html += f"""
                        <div style="margin-bottom: 14px;">
                            <strong style="color: #1a1a1a;">{proj['name']}</strong>
                            {'<span style="color: #7C3AED; font-size: 0.82em; margin-left: 8px;">' + proj['technologies'] + '</span>' if proj['technologies'] else ''}
                            <p style="color: #333; line-height: 1.6; font-size: 0.88em; margin: 4px 0 0 0;">{proj['description']}</p>
                        </div>
                        """
                    preview_html += '</div>'
                
                preview_html += '</div>'
                
                # Store preview
                st.session_state.resume_preview = preview_html
                
                # Check import before generation
                try:
                    from fpdf import FPDF
                except ImportError:
                    st.error("FPDF library not found. Please verify dependencies.")
                    return
                
                # Generate PDF (re-using logic inside try block for simplicity of context)
                pdf = FPDF()
                pdf.add_page()
                pdf.set_auto_page_break(auto=True, margin=15)
                
                # Helper to clean text for FPDF (latin-1)
                def clean_text(text):
                    if not text: return ""
                    replacements = {
                        u'\u2018': "'", u'\u2019': "'", u'\u201c': '"', u'\u201d': '"',
                        u'\u2013': '-', u'\u2014': '-', u'\u2022': '*', u'\u2026': '...',
                    }
                    for k, v in replacements.items():
                        text = text.replace(k, v)
                    return text.encode('latin-1', 'replace').decode('latin-1')

                # Header
                pdf.set_font("Helvetica", "B", 22)
                pdf.cell(0, 12, text=clean_text(full_name or "Your Name"), ln=True, align="C")
                pdf.set_font("Helvetica", "", 10)
                contact = " | ".join(filter(None, [clean_text(email), clean_text(phone), clean_text(location)]))
                pdf.cell(0, 7, text=contact, ln=True, align="C")
                pdf.set_draw_color(124, 58, 237)
                pdf.set_line_width(0.8)
                pdf.line(10, pdf.get_y() + 3, 200, pdf.get_y() + 3)
                pdf.ln(8)
                
                def section_title(title):
                    pdf.set_font("Helvetica", "B", 13)
                    pdf.set_text_color(124, 58, 237)
                    pdf.cell(0, 9, text=clean_text(title), ln=True)
                    pdf.set_draw_color(200, 200, 200)
                    pdf.set_line_width(0.3)
                    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
                    pdf.ln(3)
                    pdf.set_text_color(0, 0, 0)
                
                if summary:
                    section_title("PROFESSIONAL SUMMARY")
                    pdf.set_font("Helvetica", "", 10)
                    pdf.multi_cell(0, 5.5, text=clean_text(summary))
                    pdf.ln(4)
                
                if tech_list or soft_list:
                    section_title("SKILLS")
                    pdf.set_font("Helvetica", "", 10)
                    all_s = [clean_text(s) for s in (tech_list + soft_list)]
                    pdf.multi_cell(0, 5.5, text=" | ".join(all_s))
                    pdf.ln(4)
                
                if valid_exp:
                    section_title("WORK EXPERIENCE")
                    for exp in valid_exp:
                        pdf.set_font("Helvetica", "B", 11)
                        pdf.cell(130, 6, text=clean_text(exp['role']))
                        pdf.set_font("Helvetica", "", 9)
                        pdf.cell(0, 6, text=clean_text(exp['duration']), ln=True, align="R")
                        pdf.set_font("Helvetica", "I", 10)
                        pdf.cell(0, 5.5, text=clean_text(exp['company']), ln=True)
                        if exp['description']:
                            pdf.set_font("Helvetica", "", 10)
                            pdf.multi_cell(0, 5.5, text=clean_text(exp['description']))
                        pdf.ln(3)
                
                if valid_edu:
                    section_title("EDUCATION")
                    for edu in valid_edu:
                        pdf.set_font("Helvetica", "B", 11)
                        pdf.cell(130, 6, text=clean_text(edu['degree']))
                        pdf.set_font("Helvetica", "", 9)
                        pdf.cell(0, 6, text=clean_text(edu['year']), ln=True, align="R")
                        pdf.set_font("Helvetica", "", 10)
                        pdf.cell(0, 5.5, text=clean_text(edu['institution']), ln=True)
                        pdf.ln(2)
                
                if valid_proj:
                    section_title("PROJECTS")
                    for proj in valid_proj:
                        pdf.set_font("Helvetica", "B", 11)
                        proj_title = clean_text(proj['name'])
                        if proj['technologies']:
                            proj_title += f"  ({clean_text(proj['technologies'])})"
                        pdf.cell(0, 6, text=proj_title, ln=True)
                        if proj['description']:
                            pdf.set_font("Helvetica", "", 10)
                            pdf.multi_cell(0, 5.5, text=clean_text(proj['description']))
                        pdf.ln(3)
                
                # Store PDF bytes
                st.session_state.resume_pdf = pdf.output(dest='S') # Return bytes string
                
            except Exception as e:
                st.error(f"Error generating resume: {e}")
        
        # Display Preview
        if "resume_preview" in st.session_state:
            render_section_header("Resume Preview", "")
            st.html(st.session_state.resume_preview)
        
        # Display Download Button
        if "resume_pdf" in st.session_state:
            st.markdown("<br>", unsafe_allow_html=True)
            # We need to wrap bytearray-like object for download if needed, but fpdf output(dest='S') returns bytearray since fpdf2 v2.5.0
            # For older fpdf it returned string. Let's handle generic bytes.
            
            # Using bytes directly
            pdf_data = st.session_state.resume_pdf
            if isinstance(pdf_data, str):
                pdf_data = pdf_data.encode('latin-1') # Encode if it returned string (older fpdf behavior)
            
            st.download_button(
                label="Download Resume as PDF",
                data=pdf_data,
                file_name=f"{full_name.replace(' ', '_') if full_name else 'resume'}_resume.pdf",
                mime="application/pdf",
                use_container_width=True,
                key="rb_download_persistent"
            )



def show_sidebar():
    """Display premium sidebar navigation"""
    
    with st.sidebar:
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.session_state.logged_in:
            user = st.session_state.user
            
            # User profile card
            st.markdown(f"""
            <div style="
                background: rgba(124, 58, 237, 0.12);
                backdrop-filter: blur(10px);
                padding: 24px;
                border-radius: 16px;
                margin-bottom: 28px;
                border: 1px solid rgba(124, 58, 237, 0.2);
                text-align: center;
            ">
                <div style="
                    width: 60px;
                    height: 60px;
                    background: linear-gradient(135deg, #7C3AED, #2563EB);
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 1.6em;
                    margin: 0 auto 14px auto;
                    box-shadow: 0 4px 16px rgba(124, 58, 237, 0.3);
                    line-height: 60px;
                    text-align: center;
                "><svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg></div>
                <h3 style="color: #E2E8F0; text-align: center; margin: 0; font-weight: 700; font-size: 1.1em;">{user['username']}</h3>
                <p style="color: #94A3B8; text-align: center; font-size: 0.82em; margin-top: 6px;">
                    {user['email']}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Navigation using radio buttons
            page_map = {
                "Dashboard": "dashboard",
                "Upload Resume": "upload",
                "Analysis": "analysis",
                "Resume Builder": "resume_builder",
                "Career Recommendations": "recommendations"
            }
            
            reverse_map = {v: k for k, v in page_map.items()}
            current_label = reverse_map.get(st.session_state.page, "Dashboard")
            
            selected = st.radio(
                "Navigation",
                list(page_map.keys()),
                index=list(page_map.keys()).index(current_label),
                label_visibility="collapsed"
            )
            
            new_page = page_map[selected]
            if new_page != st.session_state.page:
                st.session_state.page = new_page
                st.rerun()
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("Logout", use_container_width=True, key="nav_logout"):
                logout()
                
            st.markdown("---")
            with st.expander("Google Gemini API Setup"):
                st.caption("Enter your Gemini API key to enable AI features and real-time job synthesis.")
                try:
                    import config
                    current_gemini = getattr(config, 'GEMINI_API_KEY', '')
                except Exception:
                    current_gemini = ''
                
                gemini_key_input = st.text_input("Gemini API Key", value=current_gemini, type="password", key="sidebar_gemini_key")
                if st.button("Save Key", use_container_width=True, key="sidebar_save_gemini"):
                    import os, re
                    os.makedirs(".streamlit", exist_ok=True)
                    secrets_path = ".streamlit/secrets.toml"
                    content = ""
                    if os.path.exists(secrets_path):
                        with open(secrets_path, "r", encoding="utf-8") as f:
                            content = f.read()
                    
                    if "GEMINI_API_KEY" in content:
                        content = re.sub(r'GEMINI_API_KEY\s*=\s*".*"', f'GEMINI_API_KEY = "{gemini_key_input}"', content)
                    else:
                        content += f'\nGEMINI_API_KEY = "{gemini_key_input}"\n'
                        
                    with open(secrets_path, "w", encoding="utf-8") as f:
                        f.write(content)
                        
                    # Force reload of components
                    import sys
                    import importlib
                    if 'config' in sys.modules:
                        importlib.reload(sys.modules['config'])
                        
                    if 'ai_service' in sys.modules:
                        if hasattr(sys.modules['ai_service'], '_ai_analyzer'):
                            sys.modules['ai_service']._ai_analyzer = None
                        importlib.reload(sys.modules['ai_service'])
                        
                    if 'job_search_api' in sys.modules:
                        if hasattr(sys.modules['job_search_api'], '_job_api'):
                            sys.modules['job_search_api']._job_api = None # Reset singleton
                        importlib.reload(sys.modules['job_search_api'])
                        
                    st.success("Gemini Key successfully saved and loaded!")
                    st.rerun()

        
        else:
            st.markdown("""
            <div style="text-align: center; padding: 30px 10px;">
                <div class="float-anim" style="font-size: 2.8em; margin-bottom: 16px;">💼</div>
                <h3 style="color: #E2E8F0; margin: 0 0 10px 0; font-weight: 800;">
                    <span class="gradient-text">Career Platform</span>
                </h3>
                <p style="color: #94A3B8; font-size: 0.88em; margin: 0; line-height: 1.6;">
                    Login to access your personalized dashboard
                </p>
            </div>
            """, unsafe_allow_html=True)


# Main app logic
def main():
    """Main application entry point"""
    
    show_sidebar()
    
    if not st.session_state.logged_in:
        show_login_page()
    else:
        page = st.session_state.page
        
        if page == 'dashboard':
            show_dashboard()
        elif page == 'upload':
            show_upload_page()
        elif page == 'analysis':
            show_analysis_page()
        elif page == 'resume_builder':
            show_resume_builder_page()
        elif page == 'recommendations':
            show_recommendations_page()
        else:
            show_dashboard()


if __name__ == "__main__":
    main()