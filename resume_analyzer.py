"""
Intelligent Resume Analysis Engine
Analyzes resumes to extract skills, calculate scores, and provide recommendations
"""

import re
from typing import Dict, List, Any, Set
from config import TECHNICAL_SKILLS, SOFT_SKILLS, SCORING_WEIGHTS, ROLE_SKILL_REQUIREMENTS
from ai_service import get_ai_analyzer


class ResumeAnalyzer:
    """Advanced resume analysis with pattern matching and scoring"""
    
    def __init__(self, resume_text: str):
        self.text = resume_text.lower()
        self.original_text = resume_text
        
    def analyze(self) -> Dict[str, Any]:
        """Perform comprehensive resume analysis"""
        
        # Extract skills
        technical_skills = self._extract_technical_skills()
        soft_skills = self._extract_soft_skills()
        
        # Generate summary
        summary = self._generate_summary()
        
        # Identify strengths and weaknesses
        strengths = self._identify_strengths(technical_skills, soft_skills)
        weaknesses = self._identify_weaknesses(technical_skills, soft_skills)
        
        # Calculate score
        score = self._calculate_score(technical_skills, soft_skills)
        
        # Identify missing skills
        missing_skills = self._identify_missing_skills(technical_skills)
        
        # Generate suggestions
        suggestions = self._generate_suggestions(technical_skills, soft_skills, score)
        
        return {
            'summary': summary,
            'technical_skills': sorted(list(technical_skills)),
            'soft_skills': sorted(list(soft_skills)),
            'strengths': strengths,
            'weaknesses': weaknesses,
            'missing_skills': missing_skills,
            'score': score,
            'suggestions': suggestions
        }
    
    def _extract_technical_skills(self) -> Set[str]:
        """Extract technical skills from resume"""
        found_skills = set()
        
        for skill in TECHNICAL_SKILLS:
            # Use word boundary matching for better accuracy
            pattern = r'\b' + re.escape(skill.lower()) + r'\b'
            if re.search(pattern, self.text):
                found_skills.add(skill)
        
        return found_skills
    
    def _extract_soft_skills(self) -> Set[str]:
        """Extract soft skills from resume"""
        found_skills = set()
        
        for skill in SOFT_SKILLS:
            pattern = r'\b' + re.escape(skill.lower()) + r'\b'
            if re.search(pattern, self.text):
                found_skills.add(skill)
        
        return found_skills
    
    def _generate_summary(self) -> str:
        """Generate a professional summary based on resume content"""
        
        # First, try AI-powered summary
        ai_analyzer = get_ai_analyzer()
        tech_skills = list(self._extract_technical_skills())
        
        if ai_analyzer.is_configured:
            ai_summary = ai_analyzer.generate_intelligent_summary(self.original_text, tech_skills)
            if ai_summary:
                return ai_summary
        
        # Fallback to basic summary generation
        # Look for existing summary section
        summary_patterns = [
            r'(?:professional summary|summary|profile|objective)[:\s]+(.*?)(?:\n\n|\n[A-Z])',
            r'(?:about me|overview)[:\s]+(.*?)(?:\n\n|\n[A-Z])'
        ]
        
        for pattern in summary_patterns:
            match = re.search(pattern, self.original_text, re.IGNORECASE | re.DOTALL)
            if match:
                summary = match.group(1).strip()
                if len(summary) > 50:
                    return summary[:500]  # Limit to reasonable length
        
        # Generate generic summary based on skills
        years_exp = self._extract_years_of_experience()
        if years_exp:
            return f"Professional with {years_exp} years of experience in software development and technology. Skilled in multiple programming languages and frameworks with a proven track record of delivering quality solutions."
        else:
            return "Technology professional with experience in software development, demonstrating proficiency in various technical skills and tools."
    
    def _extract_years_of_experience(self) -> str:
        """Extract years of experience from resume"""
        patterns = [
            r'(\d+)\+?\s*(?:years?|yrs?)\s+(?:of\s+)?experience',
            r'experience[:\s]+(\d+)\+?\s*(?:years?|yrs?)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, self.text)
            if match:
                return match.group(1)
        
        return ""
    
    def _identify_strengths(self, technical_skills: Set[str], soft_skills: Set[str]) -> List[str]:
        """Identify candidate strengths"""
        
        # Try AI-powered analysis first
        ai_analyzer = get_ai_analyzer()
        if ai_analyzer.is_configured:
            ai_result = ai_analyzer.analyze_strengths_weaknesses(
                self.original_text,
                list(technical_skills),
                list(soft_skills)
            )
            if ai_result and ai_result.get('strengths'):
                return ai_result['strengths']
        
        # Fallback to basic analysis
        strengths = []
        
        # Technical breadth
        if len(technical_skills) >= 15:
            strengths.append("Extensive technical skill set with expertise across multiple technologies")
        elif len(technical_skills) >= 8:
            strengths.append("Solid technical foundation with diverse technology experience")
        
        # Check for full-stack skills
        frontend = {'react', 'angular', 'vue', 'html', 'css', 'javascript', 'typescript'}
        backend = {'python', 'java', 'nodejs', 'node.js', 'django', 'flask', 'spring'}
        if technical_skills & frontend and technical_skills & backend:
            strengths.append("Full-stack development capabilities demonstrated")
        
        # Cloud expertise
        cloud_skills = {'aws', 'azure', 'gcp', 'google cloud', 'docker', 'kubernetes'}
        if len(technical_skills & cloud_skills) >= 2:
            strengths.append("Modern cloud and DevOps experience")
        
        # Data skills
        data_skills = {'python', 'sql', 'pandas', 'machine learning', 'data science', 'tableau', 'power bi'}
        if len(technical_skills & data_skills) >= 3:
            strengths.append("Strong data analysis and processing capabilities")
        
        # Soft skills presence
        if len(soft_skills) >= 5:
            strengths.append("Well-rounded professional skills including leadership and communication")
        
        # Experience indicators
        if 'senior' in self.text or 'lead' in self.text:
            strengths.append("Leadership and senior-level experience demonstrated")
        
        if 'certified' in self.text or 'certification' in self.text:
            strengths.append("Professional certifications and continuous learning commitment")
        
        # Default strength if none identified
        if not strengths:
            strengths.append("Demonstrated technical competency in software development")
        
        return strengths[:5]  # Limit to top 5
    
    def _identify_weaknesses(self, technical_skills: Set[str], soft_skills: Set[str]) -> List[str]:
        """Identify areas for improvement"""
        
        # Try AI-powered analysis first
        ai_analyzer = get_ai_analyzer()
        if ai_analyzer.is_configured:
            ai_result = ai_analyzer.analyze_strengths_weaknesses(
                self.original_text,
                list(technical_skills),
                list(soft_skills)
            )
            if ai_result and ai_result.get('weaknesses'):
                return ai_result['weaknesses']
        
        # Fallback to basic analysis
        weaknesses = []
        
        # Limited technical skills
        if len(technical_skills) < 5:
            weaknesses.append("Limited range of technical skills - consider expanding technology stack")
        
        # Missing modern technologies
        modern_tech = {'react', 'docker', 'kubernetes', 'aws', 'microservices', 'ci/cd'}
        if len(technical_skills & modern_tech) < 2:
            weaknesses.append("Limited exposure to modern development practices and cloud technologies")
        
        # Soft skills
        if len(soft_skills) < 3:
            weaknesses.append("Soft skills not prominently highlighted - emphasize teamwork and communication")
        
        # No clear summary
        if 'summary' not in self.text and 'objective' not in self.text:
            weaknesses.append("Missing professional summary or objective statement")
        
        # No measurable achievements
        if not re.search(r'\d+%|\$\d+|improved|increased|reduced|optimized', self.text):
            weaknesses.append("Limited quantifiable achievements - add metrics to demonstrate impact")
        
        return weaknesses[:4]  # Limit to top 4
    
    def _calculate_score(self, technical_skills: Set[str], soft_skills: Set[str]) -> int:
        """Calculate overall resume score (0-100)"""
        score = 0
        
        # Content quality (30 points)
        word_count = len(self.text.split())
        if word_count >= 300:
            score += 30
        elif word_count >= 150:
            score += 20
        else:
            score += 10
        
        # Technical skills (25 points)
        skill_count = len(technical_skills)
        if skill_count >= 15:
            score += 25
        elif skill_count >= 10:
            score += 20
        elif skill_count >= 5:
            score += 15
        else:
            score += max(skill_count * 2, 5)
        
        # Experience relevance (20 points)
        experience_keywords = ['experience', 'worked', 'developed', 'implemented', 'designed', 'led', 'managed']
        experience_count = sum(1 for kw in experience_keywords if kw in self.text)
        score += min(experience_count * 3, 20)
        
        # Education and certifications (15 points)
        education_keywords = ['bachelor', 'master', 'phd', 'degree', 'university', 'college', 'certified', 'certification']
        education_count = sum(1 for kw in education_keywords if kw in self.text)
        score += min(education_count * 3, 15)
        
        # Soft skills (10 points)
        soft_skill_count = len(soft_skills)
        score += min(soft_skill_count * 2, 10)
        
        return min(score, 100)  # Cap at 100
    
    def _identify_missing_skills(self, current_skills: Set[str]) -> List[str]:
        """Identify commonly required skills that are missing"""
        
        # Determine likely role based on current skills
        role_scores = {}
        for role, required in ROLE_SKILL_REQUIREMENTS.items():
            overlap = len(set(s.lower() for s in required) & current_skills)
            role_scores[role] = overlap
        
        # Get the most likely role
        if role_scores:
            likely_role = max(role_scores, key=role_scores.get)
            required_skills = set(s.lower() for s in ROLE_SKILL_REQUIREMENTS[likely_role])
            missing = required_skills - current_skills
            
            if missing:
                return sorted(list(missing))[:8]  # Top 8 missing skills
        
        # Generic missing skills for general software development
        common_skills = ['git', 'sql', 'rest api', 'testing', 'docker', 'ci/cd', 'agile']
        missing = set(common_skills) - current_skills
        
        return sorted(list(missing))[:8]
    
    def _generate_suggestions(self, technical_skills: Set[str], soft_skills: Set[str], score: int) -> List[str]:
        """Generate actionable improvement suggestions"""
        
        # Try AI-powered suggestions first
        ai_analyzer = get_ai_analyzer()
        if ai_analyzer.is_configured:
            missing_skills = self._identify_missing_skills(technical_skills)
            ai_suggestions = ai_analyzer.generate_personalized_suggestions(
                self.original_text,
                score,
                list(technical_skills),
                missing_skills
            )
            if ai_suggestions:
                return ai_suggestions
        
        # Fallback to basic suggestions
        suggestions = []
        
        # Score-based suggestions
        if score < 60:
            suggestions.append("Add more detailed descriptions of your work experience and achievements")
            suggestions.append("Include specific technologies and tools you've used in each role")
        
        # Technical skills suggestions
        if len(technical_skills) < 8:
            suggestions.append("Expand your technical skill set by learning in-demand technologies like React, Docker, or AWS")
        
        # Soft skills
        if len(soft_skills) < 4:
            suggestions.append("Highlight soft skills such as leadership, communication, and teamwork in your experience descriptions")
        
        # Quantifiable achievements
        if not re.search(r'\d+%|\$\d+|improved|increased|reduced', self.text):
            suggestions.append("Add quantifiable achievements (e.g., 'Improved performance by 40%', 'Reduced costs by $50K')")
        
        # Modern practices
        modern_tech = {'docker', 'kubernetes', 'ci/cd', 'microservices', 'cloud'}
        if len(technical_skills & modern_tech) < 2:
            suggestions.append("Gain experience with modern DevOps and cloud technologies to stay competitive")
        
        # Structure
        if 'summary' not in self.text and 'objective' not in self.text:
            suggestions.append("Add a professional summary at the top highlighting your key strengths and experience")
        
        # Projects
        if 'project' not in self.text:
            suggestions.append("Include notable projects with descriptions of technologies used and outcomes achieved")
        
        # Certifications
        if 'certifi' not in self.text:
            suggestions.append("Consider obtaining relevant certifications (AWS, Azure, GCP, or technology-specific certifications)")
        
        return suggestions[:6]  # Top 6 suggestions


def analyze_resume(resume_text: str) -> Dict[str, Any]:
    """
    Analyze resume and return comprehensive results
    Main entry point for resume analysis
    """
    analyzer = ResumeAnalyzer(resume_text)
    return analyzer.analyze()


class ResumeEnhancer:
    """AI-powered resume enhancement utility"""
    
    ACTION_VERBS = [
        "Spearheaded", "Orchestrated", "Executed", "Implemented", "Optimized",
        "Streamlined", "Accelerated", "Revitalized", "Pioneered", "Transformation"
    ]
    
    @staticmethod
    def enhance_summary(text: str) -> str:
        """Enhance professional summary"""
        if not text or len(text) < 10:
            return "Results-driven professional with a proven track record of success. Skilled in driving operational efficiency and delivering high-quality solutions. Committed to continuous improvement and achieving organizational goals."
            
        enhanced = text.strip()
        if not any(word in enhanced for word in ["experienced", "professional", "expert"]):
            enhanced = "Experienced " + enhanced[0].lower() + enhanced[1:]
            
        if not enhanced.endswith("."):
            enhanced += "."
            
        return enhanced + " Adept at leveraging technical expertise to solve complex business problems."

    @staticmethod
    def enhance_experience(role: str, description: str) -> str:
        """Enhance experience description with action verbs"""
        if not description:
            return f"Successfully executed key responsibilities as {role}, contributing to overall team success and operational goals."
            
        # simulating AI enhancement by adding professional prefix if missing
        import random
        prefix = random.choice(ResumeEnhancer.ACTION_VERBS)
        
        enhanced = description.strip()
        if not enhanced[0].isupper():
            enhanced = enhanced[0].upper() + enhanced[1:]
            
        return f"{prefix} key initiatives including: {enhanced}. Consistently exceeded performance metrics and fostered collaborative team environment."


def enhance_resume_text(text: str, type: str = "summary", context: str = "") -> str:
    """Wrapper for enhancement functions with AI support"""
    
    # Try AI enhancement first
    ai_analyzer = get_ai_analyzer()
    if ai_analyzer.is_configured:
        ai_result = ai_analyzer.enhance_text(text, type)
        if ai_result:
            return ai_result
    
    # Fallback to basic enhancement
    enhancer = ResumeEnhancer()
    if type == "summary":
        return enhancer.enhance_summary(text)
    elif type == "experience":
        return enhancer.enhance_experience(context, text)
    return text


def extract_resume_details_fallback(resume_text: str) -> Dict[str, Any]:
    """
    Extract structured resume details using regex/pattern matching.
    Fallback for when AI-based extraction is unavailable.
    Returns the same structure as AIResumeAnalyzer.extract_resume_details().
    """
    result = {
        "contact": {"name": "", "email": "", "phone": "", "location": ""},
        "summary": "",
        "experience": [],
        "education": [],
        "projects": []
    }
    
    lines = resume_text.strip().split('\n')
    clean_lines = [l.strip() for l in lines if l.strip()]
    
    # ---- Contact Info ----
    # Email
    email_match = re.search(r'[\w.%+-]+@[\w.-]+\.[a-zA-Z]{2,}', resume_text)
    if email_match:
        result["contact"]["email"] = email_match.group(0)
    
    # Phone
    phone_match = re.search(
        r'(?:\+?\d{1,3}[\s-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}',
        resume_text
    )
    if phone_match:
        result["contact"]["phone"] = phone_match.group(0).strip()
    
    # Name — first non-empty line that is not an email/phone/URL
    for line in clean_lines[:5]:
        stripped = line.strip()
        if (stripped and
            '@' not in stripped and
            not re.match(r'^[\d\+\(\)]', stripped) and
            not stripped.startswith('http') and
            len(stripped) < 60 and
            len(stripped.split()) <= 5):
            result["contact"]["name"] = stripped
            break
    
    # Location — look for common location patterns
    location_patterns = [
        r'(?:location|address|city)\s*[:\-]\s*(.+)',
        r'([A-Z][a-z]+(?:\s[A-Z][a-z]+)?,\s*[A-Z]{2}(?:\s+\d{5})?)',  # City, ST or City, ST ZIP
        r'([A-Z][a-z]+(?:\s[A-Z][a-z]+)?,\s*[A-Z][a-z]+)',             # City, Country
    ]
    for pattern in location_patterns:
        loc_match = re.search(pattern, resume_text, re.IGNORECASE if 'location' in pattern.lower() else 0)
        if loc_match:
            loc = loc_match.group(1).strip() if loc_match.lastindex else loc_match.group(0).strip()
            if len(loc) < 60:
                result["contact"]["location"] = loc
                break

    # ---- Section Splitting ----
    # Common section headers in resumes
    section_headers = [
        'professional summary', 'summary', 'profile', 'objective', 'about me', 'overview',
        'work experience', 'experience', 'employment history', 'professional experience', 'work history',
        'education', 'academic background', 'qualifications',
        'projects', 'personal projects', 'academic projects', 'key projects',
        'skills', 'technical skills', 'core competencies',
        'certifications', 'awards', 'publications', 'references', 'interests', 'hobbies',
        'achievements', 'volunteer', 'languages'
    ]
    
    # Build a pattern to find section boundaries
    header_pattern = r'^[\s]*(?:#+\s*)?(' + '|'.join(re.escape(h) for h in section_headers) + r')[\s]*[:\-]?\s*$'
    
    sections = {}
    current_section = None
    current_content = []
    
    for line in lines:
        stripped = line.strip().rstrip(':').rstrip('-').strip()
        # Check if this line is a section header
        if re.match(header_pattern, stripped, re.IGNORECASE):
            if current_section:
                sections[current_section] = '\n'.join(current_content).strip()
            current_section = stripped.lower().strip('#').strip()
            current_content = []
        elif current_section is not None:
            current_content.append(line)
    
    # Don't forget the last section
    if current_section:
        sections[current_section] = '\n'.join(current_content).strip()

    # ---- Summary ----
    for key in ['professional summary', 'summary', 'profile', 'objective', 'about me', 'overview']:
        if key in sections and sections[key]:
            result["summary"] = sections[key][:500]
            break

    # ---- Experience ----
    exp_text = ""
    for key in ['work experience', 'experience', 'employment history', 'professional experience', 'work history']:
        if key in sections:
            exp_text = sections[key]
            break
    
    if exp_text:
        result["experience"] = _parse_experience_section(exp_text)

    # ---- Education ----
    edu_text = ""
    for key in ['education', 'academic background', 'qualifications']:
        if key in sections:
            edu_text = sections[key]
            break
    
    if edu_text:
        result["education"] = _parse_education_section(edu_text)

    # ---- Projects ----
    proj_text = ""
    for key in ['projects', 'personal projects', 'academic projects', 'key projects']:
        if key in sections:
            proj_text = sections[key]
            break
    
    if proj_text:
        result["projects"] = _parse_projects_section(proj_text)

    return result


def _parse_experience_section(text: str) -> List[Dict[str, str]]:
    """Parse work experience section into structured entries."""
    entries = []
    lines = text.strip().split('\n')
    
    # Date pattern to detect entry boundaries
    date_pattern = r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[\s.,]+\d{4}|' \
                   r'\d{1,2}/\d{4}|\d{4}\s*[-–—]\s*(?:\d{4}|[Pp]resent|[Cc]urrent)|' \
                   r'(?:19|20)\d{2}\s*[-–—to]+\s*(?:(?:19|20)\d{2}|[Pp]resent|[Cc]urrent)'
    
    # Try to split into blocks by detecting date lines or bold/caps lines followed by dates
    current_entry = {"company": "", "role": "", "duration": "", "description": ""}
    desc_lines = []
    
    for line in lines:
        stripped = line.strip()
        if not stripped:
            # Empty line may separate entries
            if current_entry["role"] or current_entry["company"]:
                current_entry["description"] = ' '.join(desc_lines).strip()
                entries.append(current_entry)
                current_entry = {"company": "", "role": "", "duration": "", "description": ""}
                desc_lines = []
            continue
        
        # Check if line contains a date range — likely a new entry header
        duration_match = re.search(date_pattern, stripped, re.IGNORECASE)
        if duration_match:
            # If we already have data in current entry, save it
            if current_entry["role"] or current_entry["company"]:
                current_entry["description"] = ' '.join(desc_lines).strip()
                entries.append(current_entry)
                desc_lines = []
            
            duration = duration_match.group(0).strip()
            remaining = stripped[:duration_match.start()].strip().rstrip('|,-–—').strip()
            
            current_entry = {"company": "", "role": "", "duration": duration, "description": ""}
            
            # The remaining text might be "Role at Company" or "Role | Company" or "Company"
            if remaining:
                parts = re.split(r'\s+(?:at|@|[-–—|,])\s+', remaining, maxsplit=1)
                if len(parts) == 2:
                    current_entry["role"] = parts[0].strip()
                    current_entry["company"] = parts[1].strip()
                else:
                    # Could be just the role or company; treat as role
                    current_entry["role"] = remaining
        elif not current_entry["role"] and not current_entry["duration"]:
            # Might be a role or company name line before the date
            if not current_entry["company"]:
                current_entry["role"] = stripped
            elif not current_entry["company"]:
                current_entry["company"] = stripped
        elif current_entry["role"] and not current_entry["company"] and len(stripped.split()) <= 6:
            # Short line after role, likely company name
            current_entry["company"] = stripped
        else:
            # Description line
            desc_lines.append(stripped)
    
    # Save last entry
    if current_entry["role"] or current_entry["company"]:
        current_entry["description"] = ' '.join(desc_lines).strip()
        entries.append(current_entry)
    
    return entries[:5]  # Max 5 entries


def _parse_education_section(text: str) -> List[Dict[str, str]]:
    """Parse education section into structured entries."""
    entries = []
    lines = text.strip().split('\n')
    
    # Degree keywords
    degree_keywords = [
        'bachelor', 'master', 'b.s.', 'b.a.', 'm.s.', 'm.a.', 'ph.d', 'phd',
        'b.tech', 'btech', 'm.tech', 'mtech', 'bsc', 'msc', 'mba', 'diploma',
        'associate', 'b.e.', 'm.e.', 'bca', 'mca', 'b.com', 'm.com',
        'bachelor of', 'master of', 'doctor of'
    ]
    
    current_entry = {"institution": "", "degree": "", "year": ""}
    
    for line in lines:
        stripped = line.strip()
        if not stripped:
            if current_entry["degree"] or current_entry["institution"]:
                entries.append(current_entry)
                current_entry = {"institution": "", "degree": "", "year": ""}
            continue
        
        # Extract year
        year_match = re.search(r'(?:19|20)\d{2}(?:\s*[-–—]\s*(?:(?:19|20)\d{2}|[Pp]resent|[Cc]urrent))?', stripped)
        
        # Check if line contains a degree keyword
        line_lower = stripped.lower()
        has_degree = any(kw in line_lower for kw in degree_keywords)
        
        # Check for university/college/institute keyword
        has_institution = any(
            kw in line_lower for kw in ['university', 'college', 'institute', 'school', 'academy']
        )
        
        if has_degree:
            if current_entry["degree"] and (current_entry["institution"] or current_entry["year"]):
                entries.append(current_entry)
                current_entry = {"institution": "", "degree": "", "year": ""}
            degree_text = stripped
            if year_match:
                current_entry["year"] = year_match.group(0).strip()
                degree_text = stripped[:year_match.start()].strip().rstrip('|,-–—').strip()
            current_entry["degree"] = degree_text
        elif has_institution:
            inst_text = stripped
            if year_match and not current_entry["year"]:
                current_entry["year"] = year_match.group(0).strip()
                inst_text = stripped[:year_match.start()].strip().rstrip('|,-–—').strip()
            current_entry["institution"] = inst_text
        elif year_match and not current_entry["year"]:
            current_entry["year"] = year_match.group(0).strip()
            remaining = stripped.replace(year_match.group(0), '').strip().rstrip('|,-–—').strip()
            if remaining and not current_entry["degree"]:
                current_entry["degree"] = remaining
        elif not current_entry["institution"] and not current_entry["degree"]:
            # Generic first line — treat as institution or degree
            current_entry["institution"] = stripped
    
    # Save last entry
    if current_entry["degree"] or current_entry["institution"]:
        entries.append(current_entry)
    
    return entries[:3]  # Max 3 entries


def _parse_projects_section(text: str) -> List[Dict[str, str]]:
    """Parse projects section into structured entries."""
    entries = []
    lines = text.strip().split('\n')
    
    current_entry = {"name": "", "technologies": "", "description": ""}
    desc_lines = []
    
    # Tech keywords to detect technology mentions
    tech_pattern = r'(?:technologies|tech stack|built with|tools|using)\s*[:\-]\s*(.+)'
    
    for line in lines:
        stripped = line.strip()
        if not stripped:
            if current_entry["name"]:
                current_entry["description"] = ' '.join(desc_lines).strip()
                entries.append(current_entry)
                current_entry = {"name": "", "technologies": "", "description": ""}
                desc_lines = []
            continue
        
        # Check for technology line
        tech_match = re.search(tech_pattern, stripped, re.IGNORECASE)
        if tech_match and current_entry["name"]:
            tech_str = tech_match.group(1).strip()
            if isinstance(tech_str, list):
                tech_str = ', '.join(tech_str)
            current_entry["technologies"] = tech_str
            continue
        
        # If line starts with bullet or dash, it's description
        if stripped.startswith(('-', '•', '*', '–', '▪')) and current_entry["name"]:
            desc_lines.append(stripped.lstrip('-•*–▪ ').strip())
        elif not current_entry["name"]:
            # First non-empty line is the project name
            # Strip any leading bullets/numbers
            name = re.sub(r'^[\d.)\-•*]+\s*', '', stripped).strip()
            current_entry["name"] = name
        else:
            desc_lines.append(stripped)
    
    # Save last entry
    if current_entry["name"]:
        current_entry["description"] = ' '.join(desc_lines).strip()
        entries.append(current_entry)
    
    return entries[:3]  # Max 3 entries
