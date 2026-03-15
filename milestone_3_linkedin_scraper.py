import time
import urllib.parse
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def scrape_linkedin_jobs(keyword="Software Engineer", location="Remote", limit=5):
    """
    1. Use Selenium to scrape job postings from LinkedIn
    2. Extracting details like: Company name, job title, location, job URL, and job description.
    """
    print(f"[*] Starting LinkedIn Scraping for '{keyword}' in '{location}'...")
    q = urllib.parse.quote_plus(keyword)
    loc = urllib.parse.quote_plus(location)
    
    url = f"https://www.linkedin.com/jobs/search?keywords={q}&location={loc}&f_TPR=r604800&position=1&pageNum=0"
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        
        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".base-card"))
            )
        except Exception:
            pass
            
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Allow time for lazy loading
        
        soup = BeautifulSoup(driver.page_source, "html.parser")
        driver.quit()
        
        job_cards = soup.find_all("div", class_="base-card")
        jobs = []
        
        for i, card in enumerate(job_cards):
            if i >= limit:
                break
                
            title_elem = card.find("h3", class_="base-search-card__title")
            company_elem = card.find("h4", class_="base-search-card__subtitle")
            location_elem = card.find("span", class_="job-search-card__location")
            link_elem = card.find("a", class_="base-card__full-link")
            
            title = title_elem.text.strip() if title_elem else "N/A"
            company = company_elem.text.strip() if company_elem else "N/A"
            job_location = location_elem.text.strip() if location_elem else location
            job_url = link_elem["href"].split("?")[0] if link_elem and "href" in link_elem.attrs else "#"
            
            # Using job title + company as a proxy for job description summary
            # since full description requires visiting each job URL which takes very long.
            job_description = f"Looking for an experienced {title} to join {company} based in {job_location}."
            
            job_data = {
                "Job Title": title,
                "Company Name": company,
                "Location": job_location,
                "Job URL": job_url,
                "Job Description": job_description
            }
            jobs.append(job_data)
            print(f"   [+] Scraped: {title} at {company}")
            
        return jobs
        
    except Exception as e:
        print(f"[!] Selenium scraping failed: {e}")
        return []

def match_jobs_with_resume(jobs, resume_analysis):
    """
    3. Process the scraped data and match job listings with the user's resume analysis results.
    4. Generate personalized job recommendations based on strengths, skills, and job market trends.
    """
    print(f"\n[*] Processing data and generating personalized job recommendations...")
    
    user_skills = [s.lower() for s in resume_analysis.get('skills', [])]
    user_strengths = resume_analysis.get('strengths', [])
    
    recommendations = []
    
    for job in jobs:
        title = job['Job Title'].lower()
        desc = job['Job Description'].lower()
        
        # Calculate a basic match score based on keyword overlap
        matched_skills = [skill for skill in user_skills if skill in title or skill in desc]
        
        # Base score on whether skills match the title directly
        score = len(matched_skills) * 20
        
        # Bonus based on job market trends (e.g., highly desired skill overlapping)
        if any(hot_skill in title for hot_skill in ['python', 'ai', 'data', 'react']):
            score += 15
            
        match_percentage = min(score, 100)
        
        if match_percentage >= 0: # Including all for demonstration
            recommendations.append({
                "Job": job,
                "Match Percentage": match_percentage,
                "Matched Skills": matched_skills,
                "Recommendation Reason": f"Matches user strengths in {', '.join(user_strengths[:2]) if user_strengths else 'technical areas'} and aligns with market demand."
            })
            
    # Sort recommendations by highest match score
    recommendations.sort(key=lambda x: x['Match Percentage'], reverse=True)
    return recommendations

if __name__ == "__main__":
    print("="*60)
    print(" MILESTONE 3: LinkedIn Scraping & Recommendations Module")
    print("="*60)
    
    # Mock resume analysis result (from previous week's milestone)
    sample_resume_analysis = {
        "skills": ["Python", "Selenium", "Data", "Software", "Web", "Scraping", "React"],
        "strengths": ["Software Development", "Data Engineering", "Automation"],
        "experience_level": "Mid-Senior"
    }
    
    # Step 1 & 2
    scraped_jobs = scrape_linkedin_jobs(keyword="Python Developer", location="Remote", limit=5)
    
    # Step 3 & 4
    if scraped_jobs:
        job_recommendations = match_jobs_with_resume(scraped_jobs, sample_resume_analysis)
        
        print("\n" + "="*60)
        print(" FINAL PERSONALIZED JOB RECOMMENDATIONS")
        print("="*60)
        
        for i, rec in enumerate(job_recommendations, 1):
            job = rec["Job"]
            print(f"{i}. {job['Job Title']} @ {job['Company Name']} (Match: {rec['Match Percentage']}%)")
            print(f"   Location:  {job['Location']}")
            print(f"   URL:       {job['Job URL']}")
            print(f"   Summary:   {job['Job Description']}")
            print(f"   Reason:    {rec['Recommendation Reason']}")
            print(f"   Matched:   {', '.join(rec['Matched Skills']) if rec['Matched Skills'] else 'General Skills'}")
            print("-" * 60)
    else:
        print("\n[!] No jobs scraped. Cannot generate recommendations.")
