"""
AI Service Module - Google Gemini Integration
Provides intelligent resume analysis and personalized recommendations
"""

import os
import google.generativeai as genai
from typing import Dict, List, Optional, Any

# Configure Gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')

class AIResumeAnalyzer:
    """AI-powered resume analyzer using Google Gemini"""
    
    def __init__(self):
        self.model = None
        self.is_configured = False
        
        # Try to configure Gemini
        if GEMINI_API_KEY:
            try:
                genai.configure(api_key=GEMINI_API_KEY)
                self.model = genai.GenerativeModel(
                    'gemini-1.5-flash',
                    generation_config={
                        'temperature': 0.7,
                        'top_p': 0.95,
                        'top_k': 40,
                        'max_output_tokens': 2048,
                    }
                )
                self.is_configured = True
            except Exception as e:
                print(f"⚠️ Gemini AI not configured: {e}")
                self.is_configured = False
    
    def generate_intelligent_summary(self, resume_text: str, skills: List[str]) -> Optional[str]:
        """Generate AI-powered professional summary"""
        if not self.is_configured:
            return None
        
        try:
            prompt = f"""You are an expert career coach and resume writer. 

Based on the following resume content, generate a compelling professional summary (2-3 sentences) that:
- Highlights key strengths and expertise
- Mentions relevant years of experience if available
- Emphasizes unique value proposition
- Uses professional, confident tone
- Is concise and impactful

Resume Content:
{resume_text[:2000]}

Skills Found: {', '.join(skills[:15])}

Write ONLY the professional summary, nothing else."""

            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"AI Summary Error: {e}")
            return None

    def extract_resume_details(self, resume_text: str) -> Dict[str, Any]:
        """Extract full resume details including experience, education, and projects"""
        if not self.is_configured:
            return {}
        
        try:
            prompt = f"""Analyze the resume text below and extract structured data in JSON format.

Resume Text:
{resume_text[:4000]}

Extract the following:
1. Contact Info: name, email, phone, location
2. Professional Summary (text)
3. Work Experience: List of objects (max 5) with keys: "company", "role", "duration", "description"
4. Education: List of objects (max 3) with keys: "institution", "degree", "year"
5. Projects: List of objects (max 3) with keys: "name", "technologies", "description"

Return ONLY valid JSON with keys: "contact", "summary", "experience", "education", "projects".
Do not include markdown formatting.
JSON:"""

            response = self.model.generate_content(prompt)
            text = response.text.strip()
            # Clean up potential markdown code blocks
            if text.startswith('```json'):
                text = text[7:]
            if text.startswith('```'):
                text = text[3:]
            if text.endswith('```'):
                text = text[:-3]
            
            import json
            return json.loads(text.strip())
        except Exception as e:
            print(f"AI Full Extraction Error: {e}")
            return {}
    
    def analyze_strengths_weaknesses(self, resume_text: str, technical_skills: List[str], 
                                    soft_skills: List[str]) -> Optional[Dict[str, List[str]]]:
        """AI-powered identification of strengths and weaknesses"""
        if not self.is_configured:
            return None
        
        try:
            prompt = f"""You are an expert resume reviewer and career advisor.

Analyze this resume and identify:
1. Top 4-5 STRENGTHS (what this candidate does well)
2. Top 3-4 AREAS FOR IMPROVEMENT (constructive feedback)

Resume Content:
{resume_text[:2000]}

Technical Skills: {', '.join(technical_skills)}
Soft Skills: {', '.join(soft_skills)}

Provide your analysis in this EXACT format:
STRENGTHS:
- [strength 1]
- [strength 2]
- [strength 3]

WEAKNESSES:
- [weakness 1]
- [weakness 2]
- [weakness 3]

Be specific, actionable, and professional."""

            response = self.model.generate_content(prompt)
            return self._parse_strengths_weaknesses(response.text)
        except Exception as e:
            print(f"AI Analysis Error: {e}")
            return None
    
    def generate_personalized_suggestions(self, resume_text: str, score: int, 
                                         technical_skills: List[str], 
                                         missing_skills: List[str]) -> Optional[List[str]]:
        """Generate AI-powered, personalized improvement suggestions"""
        if not self.is_configured:
            return None
        
        try:
            prompt = f"""You are an expert resume coach helping someone improve their resume.

Resume Score: {score}/100
Current Technical Skills: {', '.join(technical_skills[:15])}
Missing In-Demand Skills: {', '.join(missing_skills[:10])}

Resume Content:
{resume_text[:2000]}

Provide 5-6 specific, actionable suggestions to improve this resume. Focus on:
- Adding quantifiable achievements
- Improving structure and formatting
- Highlighting relevant skills
- Learning high-demand technologies
- Strengthening impact statements

Format as a bullet list:
- Suggestion 1
- Suggestion 2
...

Be specific and actionable. No generic advice."""

            response = self.model.generate_content(prompt)
            return self._parse_suggestions(response.text)
        except Exception as e:
            print(f"AI Suggestions Error: {e}")
            return None
    
    def enhance_text(self, text: str, context: str = "summary") -> Optional[str]:
        """AI-powered text enhancement"""
        if not self.is_configured or not text:
            return None
        
        try:
            if context == "summary":
                prompt = f"""Enhance this professional summary to be more impactful:

Original: {text}

Make it:
- More professional and confident
- Include strong action words
- Be concise (2-3 sentences max)
- ATS-friendly

Write ONLY the enhanced summary."""
            
            else:  # experience
                prompt = f"""Enhance this job experience description:

Original: {text}

Improve by:
- Starting with strong action verbs
- Adding more impact
- Being more specific
- Maintaining professional tone

Write ONLY the enhanced description."""
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"AI Enhancement Error: {e}")
            return None
    
    def _parse_strengths_weaknesses(self, ai_response: str) -> Dict[str, List[str]]:
        """Parse AI response into structured strengths and weaknesses"""
        strengths = []
        weaknesses = []
        
        current_section = None
        for line in ai_response.split('\n'):
            line = line.strip()
            
            if 'STRENGTH' in line.upper():
                current_section = 'strengths'
                continue
            elif 'WEAKNESS' in line.upper() or 'IMPROVEMENT' in line.upper() or 'AREA' in line.upper():
                current_section = 'weaknesses'
                continue
            
            if line.startswith('-') or line.startswith('•'):
                cleaned = line.lstrip('-•').strip()
                if cleaned and len(cleaned) > 10:
                    if current_section == 'strengths':
                        strengths.append(cleaned)
                    elif current_section == 'weaknesses':
                        weaknesses.append(cleaned)
        
        return {
            'strengths': strengths[:5],
            'weaknesses': weaknesses[:4]
        }
    
    def _parse_suggestions(self, ai_response: str) -> List[str]:
        """Parse AI response into list of suggestions"""
        suggestions = []
        for line in ai_response.split('\n'):
            line = line.strip()
            if line.startswith('-') or line.startswith('•') or line.startswith('*'):
                cleaned = line.lstrip('-•*').strip()
                if cleaned and len(cleaned) > 15:
                    suggestions.append(cleaned)
        
        return suggestions[:6]


# Global AI analyzer instance
_ai_analyzer = None

def get_ai_analyzer() -> AIResumeAnalyzer:
    """Get or create AI analyzer singleton"""
    global _ai_analyzer
    if _ai_analyzer is None:
        _ai_analyzer = AIResumeAnalyzer()
    return _ai_analyzer
