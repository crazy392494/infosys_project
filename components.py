"""
Reusable premium UI components for the Streamlit application
Modern glassmorphism design with dark-theme support
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px


# ========================== COLOR PALETTE ==========================
COLORS = {
    'primary': '#7C3AED',
    'primary_light': '#A78BFA',
    'secondary': '#06B6D4',
    'accent': '#F59E0B',
    'success': '#10B981',
    'warning': '#F59E0B',
    'error': '#EF4444',
    'surface': 'rgba(30, 41, 59, 0.7)',
    'surface_solid': '#1E293B',
    'card': 'rgba(30, 41, 59, 0.6)',
    'text': '#E2E8F0',
    'text_muted': '#94A3B8',
    'border': 'rgba(148, 163, 184, 0.15)',
    'glow_purple': 'rgba(124, 58, 237, 0.3)',
    'glow_cyan': 'rgba(6, 182, 212, 0.3)',
}


def render_skill_badge(skill: str, color: str = "#7C3AED"):
    """Render a styled skill badge with gradient, glow, and hover effect"""
    return f'''<span style="
        display: inline-block;
        background: linear-gradient(135deg, {color}25, {color}45);
        color: {color};
        padding: 7px 18px;
        margin: 5px;
        border-radius: 24px;
        font-size: 0.87em;
        font-weight: 600;
        border: 1px solid {color}60;
        backdrop-filter: blur(10px);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        letter-spacing: 0.3px;
        box-shadow: 0 2px 8px {color}20;
        cursor: default;
    " onmouseover="this.style.transform='translateY(-3px) scale(1.05)'; this.style.boxShadow='0 6px 16px {color}40';" 
       onmouseout="this.style.transform='translateY(0) scale(1)'; this.style.boxShadow='0 2px 8px {color}20';">{skill}</span>'''


def render_skill_badges(skills: list, color: str = "#7C3AED"):
    """Render multiple skill badges with staggered animation"""
    if not skills:
        return f'<p style="color: {COLORS["text_muted"]}; font-style: italic; font-size: 0.92em;">No skills detected</p>'
    
    badges_html = ""
    for i, skill in enumerate(skills):
        # Add inline animation delay for staggered entrance
        badge = render_skill_badge(skill, color)
        badges_html += f'<span style="animation: fadeIn 0.5s ease-out {i * 0.05}s backwards;">{badge}</span>'
    
    return f'<div style="line-height: 3; padding: 10px 0;">{badges_html}</div>'


def render_score_gauge(score: int):
    """Render a modern gauge chart for resume score"""
    
    # Dynamic gradient based on score
    if score >= 80:
        bar_color = "#10B981"
        gauge_gradient = ["#064E3B", "#10B981", "#34D399"]
    elif score >= 60:
        bar_color = "#F59E0B"
        gauge_gradient = ["#78350F", "#F59E0B", "#FCD34D"]
    else:
        bar_color = "#EF4444"
        gauge_gradient = ["#7F1D1D", "#EF4444", "#FCA5A5"]
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Resume Score", 'font': {'size': 20, 'color': '#E2E8F0', 'family': 'Inter, sans-serif'}},
        number={'font': {'size': 52, 'color': bar_color, 'family': 'Inter, sans-serif'},
                'suffix': '<span style="font-size:0.4em; color:#94A3B8">/100</span>'},
        gauge={
            'axis': {
                'range': [0, 100],
                'tickwidth': 1,
                'tickcolor': "#334155",
                'tickfont': {'color': '#94A3B8', 'size': 10}
            },
            'bar': {'color': bar_color, 'thickness': 0.75},
            'bgcolor': "#1E293B",
            'borderwidth': 0,
            'steps': [
                {'range': [0, 40], 'color': 'rgba(239, 68, 68, 0.1)'},
                {'range': [40, 60], 'color': 'rgba(245, 158, 11, 0.08)'},
                {'range': [60, 80], 'color': 'rgba(245, 158, 11, 0.05)'},
                {'range': [80, 100], 'color': 'rgba(16, 185, 129, 0.08)'}
            ],
            'threshold': {
                'line': {'color': "#7C3AED", 'width': 3},
                'thickness': 0.8,
                'value': 90
            }
        }
    ))
    
    fig.update_layout(
        height=280,
        margin=dict(l=25, r=25, t=55, b=15),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={'family': "Inter, sans-serif"}
    )
    
    return fig


def render_skills_chart(technical_skills: list, soft_skills: list):
    """Render a modern donut chart showing skill distribution"""
    
    if not technical_skills and not soft_skills:
        return None
    
    labels = ['Technical Skills', 'Soft Skills']
    values = [len(technical_skills), len(soft_skills)]
    colors = ['#7C3AED', '#06B6D4']
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=.55,
        marker=dict(
            colors=colors,
            line=dict(color='#0F172A', width=3)
        ),
        textinfo='label+value',
        textfont=dict(size=13, color='#E2E8F0', family='Inter, sans-serif'),
        hoverinfo='label+percent+value',
        textposition='outside',
        pull=[0.03, 0.03]
    )])
    
    fig.update_layout(
        title=dict(
            text="Skills Distribution",
            font=dict(size=18, color='#E2E8F0', family='Inter, sans-serif'),
            x=0.5
        ),
        height=350,
        margin=dict(l=30, r=30, t=60, b=30),
        showlegend=True,
        legend=dict(
            font=dict(color='#94A3B8', size=12, family='Inter, sans-serif'),
            bgcolor='rgba(0,0,0,0)',
            borderwidth=0
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    
    return fig


def render_match_bar(match_score: float):
    """Render a horizontal bar for match percentage"""
    
    if match_score >= 70:
        color = "#10B981"
        glow = "rgba(16, 185, 129, 0.4)"
    elif match_score >= 50:
        color = "#F59E0B"
        glow = "rgba(245, 158, 11, 0.4)"
    else:
        color = "#64748B"
        glow = "rgba(100, 116, 139, 0.3)"
    
    return f'''
    <div style="background: rgba(15, 23, 42, 0.6); border-radius: 12px; overflow: hidden; height: 28px; position: relative; border: 1px solid rgba(148,163,184,0.1);">
        <div style="background: linear-gradient(90deg, {color}88, {color}); width: {match_score}%; height: 100%; border-radius: 12px; transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1); box-shadow: 0 0 12px {glow};"></div>
        <span style="position: absolute; right: 12px; top: 3px; font-weight: 700; color: #E2E8F0; font-size: 0.85em; text-shadow: 0 1px 3px rgba(0,0,0,0.5);">{match_score}%</span>
    </div>
    '''


def render_job_card(job: dict, match_score: float, direct_matches: list):
    """Render a premium styled job recommendation card"""
    
    if match_score >= 70:
        badge_color = "#10B981"
        badge_text = "Excellent Match"
        badge_icon = ""
    elif match_score >= 50:
        badge_color = "#F59E0B"
        badge_text = "Good Match"
        badge_icon = ""
    else:
        badge_color = "#64748B"
        badge_text = "Potential Match"
        badge_icon = ""
    
    description = job.get('description', '')
    if len(description) > 200:
        description = description[:200] + "..."
    
    match_skills_html = ""
    if direct_matches:
        skills_badges = "".join(
            [f'<span style="display:inline-block; background:{badge_color}22; color:{badge_color}; padding:3px 10px; margin:2px; border-radius:12px; font-size:0.8em; border:1px solid {badge_color}44;">{s}</span>'
             for s in direct_matches[:5]]
        )
        if len(direct_matches) > 5:
            skills_badges += f'<span style="color:#94A3B8; font-size:0.85em; margin-left:4px;">+{len(direct_matches) - 5} more</span>'
        match_skills_html = f'<div style="margin-top: 12px;"><strong style="color:#94A3B8; font-size:0.85em;">MATCHING SKILLS</strong><br/>{skills_badges}</div>'
    
    card_html = f'''
    <div style="
        background: rgba(30, 41, 59, 0.6);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(148, 163, 184, 0.12);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 24px rgba(0,0,0,0.15);
    ">
        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 12px;">
            <div>
                <h3 style="margin: 0; color: #A78BFA; font-size: 1.15em; font-weight: 700;">{job['title']}</h3>
                <strong style="color: #E2E8F0;">{job['company']}</strong> &bull; {job['location']} &bull; <span style="color: #64748B; font-size: 0.9em;">via {job.get('source', 'Job Board')}</span>
                </p>
            </div>
            <span style="
                background: {badge_color}22;
                color: {badge_color};
                padding: 6px 16px;
                border-radius: 20px;
                font-size: 0.82em;
                font-weight: 700;
                white-space: nowrap;
                border: 1px solid {badge_color}44;
                letter-spacing: 0.3px;
            ">
                {badge_icon} {badge_text}
            </span>
        </div>
        
        {render_match_bar(match_score)}
        
        <p style="color: #94A3B8; line-height: 1.7; margin: 14px 0 0 0; font-size: 0.92em;">{description}</p>
        
        {match_skills_html}
        
        <a href="{job['url']}" target="_blank" style="text-decoration: none; display: block; margin-top: 16px;">
            <div style="
                background: linear-gradient(135deg, {COLORS['primary']}, {COLORS['secondary']});
                color: white;
                padding: 10px 0;
                border-radius: 10px;
                text-align: center;
                font-weight: 600;
                font-size: 0.95em;
                transition: transform 0.2s ease, box-shadow 0.2s ease;
                box-shadow: 0 4px 12px rgba(124, 58, 237, 0.3);
            " onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 6px 20px rgba(124, 58, 237, 0.5)';"
               onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 12px rgba(124, 58, 237, 0.3)';">
                Apply Now <span style="margin-left: 5px;">➜</span>
            </div>
        </a>
    </div>
    '''
    
    return card_html


def render_metric_card(title: str, value: str, icon: str = "", color: str = "#7C3AED"):
    """Render a premium glassmorphism metric card with animated gradient"""
    
    card_html = f'''
    <div style="
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(25px) saturate(180%);
        border: 1px solid rgba(148, 163, 184, 0.18);
        border-radius: 18px;
        padding: 28px;
        position: relative;
        overflow: hidden;
        box-shadow: 0 8px 32px rgba(0,0,0,0.2);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        animation: scaleIn 0.6s ease-out;
    " onmouseover="this.style.transform='translateY(-6px) scale(1.02)'; this.style.boxShadow='0 16px 48px {color}30';" 
       onmouseout="this.style.transform='translateY(0) scale(1)'; this.style.boxShadow='0 8px 32px rgba(0,0,0,0.2)';">
        <div style="
            position: absolute;
            top: -30px;
            right: -30px;
            width: 120px;
            height: 120px;
            background: radial-gradient(circle, {color}35, transparent 70%);
            border-radius: 50%;
            filter: blur(20px);
        "></div>
        <div style="font-size: 2.2em; margin-bottom: 14px; filter: drop-shadow(0 4px 12px {color}50);">{icon}</div>
        <div style="font-size: 2.2em; font-weight: 900; color: {color}; margin-bottom: 8px; letter-spacing: -1px; text-shadow: 0 2px 10px {color}40;">{value}</div>
        <div style="color: #94A3B8; font-size: 0.88em; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;">{title}</div>
    </div>
    '''
    
    return card_html


def render_header(username: str, page_title: str):
    """Render premium page header with animated gradient and depth"""
    
    header_html = f'''
    <div style="
        background: linear-gradient(135deg, #7C3AED 0%, #2563EB 50%, #06B6D4 100%);
        padding: 36px 40px;
        border-radius: 22px;
        margin-bottom: 36px;
        color: white;
        box-shadow: 0 12px 40px rgba(124, 58, 237, 0.3);
        position: relative;
        overflow: hidden;
        animation: fadeIn 0.6s ease-out;
    ">
        <div style="
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            background: radial-gradient(circle at 85% 15%, rgba(255,255,255,0.15), transparent 50%),
                        radial-gradient(circle at 15% 85%, rgba(6,182,212,0.2), transparent 50%);
        "></div>
        <h1 style="margin: 0; font-size: 2.2em; font-weight: 900; position: relative; z-index: 1; letter-spacing: -0.8px; text-shadow: 0 2px 20px rgba(0,0,0,0.2);">{page_title}</h1>
        <p style="margin: 12px 0 0 0; opacity: 0.92; font-size: 1.08em; position: relative; z-index: 1; font-weight: 500;">Welcome back, <strong style="font-weight: 700;">{username}</strong>!</p>
    </div>
    '''
    
    st.markdown(header_html, unsafe_allow_html=True)


def render_section_header(title: str, icon: str = ""):
    """Render a modern section header with accent line"""
    
    if icon:
        title = f"{icon} {title}"
    
    st.markdown(f'''
    <div style="margin-top: 36px; margin-bottom: 16px;">
        <h2 style="
            color: #E2E8F0;
            font-size: 1.4em;
            font-weight: 700;
            margin: 0;
            padding-bottom: 12px;
            border-bottom: 2px solid rgba(124, 58, 237, 0.4);
            letter-spacing: -0.3px;
        ">{title}</h2>
    </div>
    ''', unsafe_allow_html=True)


def render_progress_bar(current: int, total: int, label: str = ""):
    """Render an animated gradient progress bar"""
    
    percentage = (current / total * 100) if total > 0 else 0
    
    progress_html = f'''
    <div style="margin: 16px 0;">
        {f"<p style='margin-bottom: 8px; font-weight: 600; color: #E2E8F0; font-size: 0.95em;'>{label}</p>" if label else ""}
        <div style="background: rgba(15, 23, 42, 0.6); border-radius: 12px; overflow: hidden; height: 22px; border: 1px solid rgba(148,163,184,0.1);">
            <div style="
                background: linear-gradient(90deg, #7C3AED, #06B6D4);
                width: {percentage}%;
                height: 100%;
                border-radius: 12px;
                transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
                box-shadow: 0 0 16px rgba(124, 58, 237, 0.3);
            "></div>
        </div>
        <p style="text-align: right; margin-top: 6px; color: #94A3B8; font-size: 0.85em; font-weight: 500;">{current} / {total}</p>
    </div>
    '''
    
    st.markdown(progress_html, unsafe_allow_html=True)


def render_alert(message: str, alert_type: str = "info"):
    """Render a modern glassmorphism alert box"""
    
    colors = {
        'info': {'bg': 'rgba(37, 99, 235, 0.12)', 'border': '#2563EB', 'icon': '', 'text': '#93C5FD'},
        'success': {'bg': 'rgba(16, 185, 129, 0.12)', 'border': '#10B981', 'icon': '', 'text': '#6EE7B7'},
        'warning': {'bg': 'rgba(245, 158, 11, 0.12)', 'border': '#F59E0B', 'icon': '', 'text': '#FCD34D'},
        'error': {'bg': 'rgba(239, 68, 68, 0.12)', 'border': '#EF4444', 'icon': '', 'text': '#FCA5A5'}
    }
    
    color_scheme = colors.get(alert_type, colors['info'])
    
    alert_html = f'''
    <div style="
        background: {color_scheme['bg']};
        border-left: 4px solid {color_scheme['border']};
        padding: 18px 20px;
        border-radius: 0 12px 12px 0;
        margin: 16px 0;
        backdrop-filter: blur(10px);
        border-top: 1px solid rgba(148,163,184,0.06);
        border-right: 1px solid rgba(148,163,184,0.06);
        border-bottom: 1px solid rgba(148,163,184,0.06);
    ">
        <span style="font-size: 1.2em; margin-right: 10px;">{color_scheme['icon']}</span>
        <span style="color: {color_scheme['text']}; font-size: 1em; font-weight: 500; line-height: 1.6;">{message}</span>
    </div>
    '''
    
    st.markdown(alert_html, unsafe_allow_html=True)


def render_glow_card(title: str, content: str, icon: str = "✨", color: str = "#7C3AED"):
    """Render a generic card with 3D glow hover effect"""
    return f'''
    <div class="glow-card">
        <div class="glow-icon">{icon}</div>
        <h3 style="color: #F8FAFC; font-weight: 700; margin: 0 0 8px 0; font-size: 1.15em; letter-spacing: -0.3px;">{title}</h3>
        <p style="color: #94A3B8; margin: 0; line-height: 1.6; font-size: 0.95em;">{content}</p>
    </div>
    '''
