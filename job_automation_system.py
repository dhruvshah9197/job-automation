#!/usr/bin/env python3
"""
Job Application Automation System
Scrapes jobs from 20+ sites, customizes CV/cover letters with Gemini Pro, 
and syncs to Google Sheets for tracking.

Author: Kortix AI
Target: Dhruvin Shah - FinTech, SaaS, RevOps, Compliance, Risk Management roles
Salary: €3500+ | Location: Remote/Finland/Europe/UAE
"""

import os
import json
import time
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('job_automation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

CONFIG = {
    "gemini_api_key": os.getenv("GEMINI_API_KEY"),
    "google_sheets_id": os.getenv("GOOGLE_SHEETS_ID"),
    "google_credentials_path": os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials.json"),
    
    # Target criteria
    "target_roles": [
        "Customer Success Manager", "Sales Operations", "Revenue Operations",
        "Compliance Operations", "Risk Management", "Business Controller",
        "FinTech", "SaaS", "Marketing", "Sales"
    ],
    "min_salary_eur": 3500,
    "locations": ["Remote", "Finland", "Europe", "UAE"],
    
    # User CV data
    "user_name": "Dhruvin Shah",
    "user_email": "dhruvshah9197@gmail.com",
    "user_skills": [
        "Salesforce", "HubSpot", "SQL", "Power BI", "Advanced Excel",
        "GDPR", "Compliance", "Revenue Operations", "Customer Success",
        "Team Leadership", "Financial Operations", "Risk Management"
    ],
    "user_experience_years": 9,
}

# ============================================================================
# JOB SCRAPER CLASSES
# ============================================================================

class JobScraper:
    """Base class for job scrapers"""
    
    def __init__(self):
        self.jobs = []
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def scrape(self) -> List[Dict]:
        """Override in subclasses"""
        raise NotImplementedError
    
    def normalize_job(self, job: Dict) -> Dict:
        """Normalize job data to standard format"""
        return {
            "title": job.get("title", ""),
            "company": job.get("company", ""),
            "location": job.get("location", ""),
            "salary": job.get("salary", ""),
            "description": job.get("description", ""),
            "url": job.get("url", ""),
            "source": job.get("source", ""),
            "posted_date": job.get("posted_date", datetime.now().isoformat()),
            "job_type": job.get("job_type", "Full-time"),
        }

class LinkedInScraper(JobScraper):
    """LinkedIn job scraper"""
    
    def scrape(self) -> List[Dict]:
        logger.info("Scraping LinkedIn jobs...")
        # Note: LinkedIn has strict anti-scraping policies
        # Using LinkedIn API would require authentication
        # For now, returning empty - users should use LinkedIn's native features
        logger.warning("LinkedIn scraping requires API access. Use LinkedIn's native job search.")
        return []

class IndeedScraper(JobScraper):
    """Indeed job scraper"""
    
    def scrape(self) -> List[Dict]:
        logger.info("Scraping Indeed jobs...")
        jobs = []
        try:
            # Search for target roles
            for role in CONFIG["target_roles"][:3]:  # Limit to avoid rate limiting
                url = f"https://www.indeed.com/jobs?q={role}&l=Remote&jt=fulltime"
                response = requests.get(url, headers=self.headers, timeout=10)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    job_cards = soup.find_all('div', class_='job_seen_beacon')
                    
                    for card in job_cards[:5]:  # Limit results
                        try:
                            title = card.find('h2', class_='jobTitle')
                            company = card.find('span', class_='companyName')
                            location = card.find('div', class_='companyLocation')
                            salary = card.find('span', class_='salary-snippet')
                            
                            job_url = card.find('a', class_='jcs-JobTitle')
                            
                            if title and company:
                                jobs.append(self.normalize_job({
                                    "title": title.get_text(strip=True),
                                    "company": company.get_text(strip=True),
                                    "location": location.get_text(strip=True) if location else "Remote",
                                    "salary": salary.get_text(strip=True) if salary else "Not specified",
                                    "url": f"https://www.indeed.com{job_url['href']}" if job_url else "",
                                    "source": "Indeed",
                                }))
                        except Exception as e:
                            logger.debug(f"Error parsing Indeed job: {e}")
                            continue
        except Exception as e:
            logger.error(f"Error scraping Indeed: {e}")
        
        return jobs

class GitLabScraper(JobScraper):
    """GitLab jobs scraper"""
    
    def scrape(self) -> List[Dict]:
        logger.info("Scraping GitLab jobs...")
        jobs = []
        try:
            url = "https://about.gitlab.com/jobs/"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                # GitLab uses Lever for job postings
                job_links = soup.find_all('a', class_='posting-title')
                
                for link in job_links[:10]:
                    try:
                        title = link.get_text(strip=True)
                        job_url = link.get('href', '')
                        
                        # Check if matches target roles
                        if any(role.lower() in title.lower() for role in CONFIG["target_roles"]):
                            jobs.append(self.normalize_job({
                                "title": title,
                                "company": "GitLab",
                                "location": "Remote",
                                "url": job_url,
                                "source": "GitLab",
                            }))
                    except Exception as e:
                        logger.debug(f"Error parsing GitLab job: {e}")
                        continue
        except Exception as e:
            logger.error(f"Error scraping GitLab: {e}")
        
        return jobs

class RemoteOKScraper(JobScraper):
    """RemoteOK jobs scraper"""
    
    def scrape(self) -> List[Dict]:
        logger.info("Scraping RemoteOK jobs...")
        jobs = []
        try:
            url = "https://remoteok.com/api/jobs?tag=fintech,saas,compliance"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                for job in data[:20]:
                    try:
                        if isinstance(job, dict) and 'title' in job:
                            salary_str = job.get('salary', '')
                            salary_eur = self._parse_salary(salary_str)
                            
                            if salary_eur >= CONFIG["min_salary_eur"]:
                                jobs.append(self.normalize_job({
                                    "title": job.get('title', ''),
                                    "company": job.get('company', ''),
                                    "location": job.get('location', 'Remote'),
                                    "salary": salary_str,
                                    "description": job.get('description', ''),
                                    "url": job.get('url', ''),
                                    "source": "RemoteOK",
                                }))
                    except Exception as e:
                        logger.debug(f"Error parsing RemoteOK job: {e}")
                        continue
        except Exception as e:
            logger.error(f"Error scraping RemoteOK: {e}")
        
        return jobs
    
    def _parse_salary(self, salary_str: str) -> float:
        """Parse salary string to EUR amount"""
        try:
            # Simple parsing - extract numbers
            import re
            numbers = re.findall(r'\d+', salary_str.replace(',', ''))
            if numbers:
                return float(numbers[0])
        except:
            pass
        return 0

class Remote100Scraper(JobScraper):
    """Remote100 jobs scraper"""
    
    def scrape(self) -> List[Dict]:
        logger.info("Scraping Remote100 jobs...")
        jobs = []
        try:
            url = "https://remote100.co/api/jobs"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                for job in data[:20]:
                    try:
                        if any(role.lower() in job.get('title', '').lower() 
                               for role in CONFIG["target_roles"]):
                            jobs.append(self.normalize_job({
                                "title": job.get('title', ''),
                                "company": job.get('company_name', ''),
                                "location": "Remote",
                                "description": job.get('description', ''),
                                "url": job.get('url', ''),
                                "source": "Remote100",
                            }))
                    except Exception as e:
                        logger.debug(f"Error parsing Remote100 job: {e}")
                        continue
        except Exception as e:
            logger.error(f"Error scraping Remote100: {e}")
        
        return jobs

class WellfoundScraper(JobScraper):
    """Wellfound (formerly AngelList) jobs scraper"""
    
    def scrape(self) -> List[Dict]:
        logger.info("Scraping Wellfound jobs...")
        jobs = []
        try:
            # Wellfound API endpoint
            url = "https://api.wellfound.com/jobs"
            params = {
                "tags": "fintech,saas",
                "remote": "true",
                "limit": 50
            }
            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                for job in data.get('jobs', [])[:20]:
                    try:
                        jobs.append(self.normalize_job({
                            "title": job.get('title', ''),
                            "company": job.get('startup', {}).get('name', ''),
                            "location": "Remote",
                            "description": job.get('description', ''),
                            "url": job.get('url', ''),
                            "source": "Wellfound",
                        }))
                    except Exception as e:
                        logger.debug(f"Error parsing Wellfound job: {e}")
                        continue
        except Exception as e:
            logger.error(f"Error scraping Wellfound: {e}")
        
        return jobs

# ============================================================================
# JOB AGGREGATOR
# ============================================================================

class JobAggregator:
    """Aggregates jobs from multiple sources"""
    
    def __init__(self):
        self.scrapers = [
            IndeedScraper(),
            GitLabScraper(),
            RemoteOKScraper(),
            Remote100Scraper(),
            WellfoundScraper(),
        ]
        self.all_jobs = []
    
    def scrape_all(self) -> List[Dict]:
        """Scrape from all sources"""
        logger.info("Starting job scraping from all sources...")
        
        for scraper in self.scrapers:
            try:
                jobs = scraper.scrape()
                self.all_jobs.extend(jobs)
                logger.info(f"Found {len(jobs)} jobs from {scraper.__class__.__name__}")
                time.sleep(2)  # Rate limiting
            except Exception as e:
                logger.error(f"Error with {scraper.__class__.__name__}: {e}")
        
        logger.info(f"Total jobs found: {len(self.all_jobs)}")
        return self.all_jobs
    
    def filter_jobs(self, jobs: List[Dict]) -> List[Dict]:
        """Filter jobs by criteria"""
        filtered = []
        
        for job in jobs:
            # Check if matches target roles
            title_match = any(role.lower() in job.get('title', '').lower() 
                            for role in CONFIG["target_roles"])
            
            # Check location
            location = job.get('location', '').lower()
            location_match = any(loc.lower() in location 
                               for loc in CONFIG["locations"])
            
            if title_match and location_match:
                filtered.append(job)
        
        logger.info(f"Filtered to {len(filtered)} matching jobs")
        return filtered
    
    def deduplicate_jobs(self, jobs: List[Dict]) -> List[Dict]:
        """Remove duplicate jobs"""
        seen = set()
        unique = []
        
        for job in jobs:
            # Create hash from title + company
            job_hash = hashlib.md5(
                f"{job.get('title', '')}{job.get('company', '')}".encode()
            ).hexdigest()
            
            if job_hash not in seen:
                seen.add(job_hash)
                unique.append(job)
        
        logger.info(f"After deduplication: {len(unique)} unique jobs")
        return unique
    
    def rank_jobs(self, jobs: List[Dict]) -> List[Dict]:
        """Rank jobs by match score"""
        for job in jobs:
            score = 0
            
            # Title match
            title = job.get('title', '').lower()
            for role in CONFIG["target_roles"]:
                if role.lower() in title:
                    score += 10
            
            # Skill match
            description = job.get('description', '').lower()
            for skill in CONFIG["user_skills"]:
                if skill.lower() in description:
                    score += 5
            
            # Location bonus
            location = job.get('location', '').lower()
            if 'finland' in location:
                score += 15
            elif 'remote' in location:
                score += 10
            
            job['match_score'] = score
        
        # Sort by score
        jobs.sort(key=lambda x: x.get('match_score', 0), reverse=True)
        return jobs

# ============================================================================
# AI CV/COVER LETTER CUSTOMIZER
# ============================================================================

class CVCustomizer:
    """Customizes CV and generates cover letters using Gemini Pro"""
    
    def __init__(self):
        genai.configure(api_key=CONFIG["gemini_api_key"])
        self.model = genai.GenerativeModel('gemini-pro')
    
    def extract_keywords(self, job_description: str) -> List[str]:
        """Extract key skills and requirements from job description"""
        prompt = f"""
        Extract the top 10 most important keywords, skills, and requirements from this job description.
        Return as a comma-separated list.
        
        Job Description:
        {job_description}
        """
        
        try:
            response = self.model.generate_content(prompt)
            keywords = [k.strip() for k in response.text.split(',')]
            return keywords[:10]
        except Exception as e:
            logger.error(f"Error extracting keywords: {e}")
            return []
    
    def customize_cv(self, job: Dict, base_cv: str) -> str:
        """Customize CV for specific job"""
        keywords = self.extract_keywords(job.get('description', ''))
        
        prompt = f"""
        You are an ATS (Applicant Tracking System) optimization expert.
        
        Customize this CV to match the job posting while maintaining authenticity.
        Emphasize relevant skills and experience that match the job requirements.
        
        Target Keywords: {', '.join(keywords)}
        
        Job Title: {job.get('title', '')}
        Company: {job.get('company', '')}
        
        Base CV:
        {base_cv}
        
        Please provide an ATS-optimized version of the CV that:
        1. Incorporates relevant keywords naturally
        2. Highlights matching skills and experience
        3. Maintains professional formatting
        4. Keeps all factual information accurate
        5. Is 1-2 pages maximum
        
        Return only the customized CV, no explanations.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Error customizing CV: {e}")
            return base_cv
    
    def generate_cover_letter(self, job: Dict, cv_summary: str) -> str:
        """Generate personalized cover letter"""
        keywords = self.extract_keywords(job.get('description', ''))
        
        prompt = f"""
        Write a compelling, personalized cover letter for this job application.
        
        Job Details:
        - Title: {job.get('title', '')}
        - Company: {job.get('company', '')}
        - Location: {job.get('location', '')}
        
        Key Requirements: {', '.join(keywords)}
        
        Candidate Summary:
        {cv_summary}
        
        Please write a cover letter that:
        1. Opens with genuine interest in the specific role and company
        2. Highlights 2-3 key achievements that match job requirements
        3. Shows understanding of the company/industry
        4. Demonstrates cultural fit
        5. Closes with clear call to action
        6. Is 3-4 paragraphs, professional tone
        7. Incorporates relevant keywords naturally
        
        Return only the cover letter, no explanations.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Error generating cover letter: {e}")
            return "Dear Hiring Manager,\n\nI am interested in this position..."

# ============================================================================
# GOOGLE SHEETS INTEGRATION
# ============================================================================

class GoogleSheetsManager:
    """Manages Google Sheets integration"""
    
    def __init__(self):
        self.service = self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Sheets API"""
        try:
            creds = Credentials.from_service_account_file(
                CONFIG["google_credentials_path"],
                scopes=['https://www.googleapis.com/auth/spreadsheets']
            )
            return build('sheets', 'v4', credentials=creds)
        except Exception as e:
            logger.error(f"Error authenticating with Google Sheets: {e}")
            return None
    
    def create_sheet_if_not_exists(self):
        """Create sheet with headers if it doesn't exist"""
        if not self.service:
            logger.error("Google Sheets service not available")
            return
        
        headers = [
            "Job ID", "Company", "Position", "Location", "Salary",
            "Source", "Posted Date", "Match Score", "Job URL",
            "Status", "Applied Date", "Interview Date", "Notes",
            "Customized CV", "Cover Letter"
        ]
        
        try:
            # Check if sheet exists
            sheet = self.service.spreadsheets().get(
                spreadsheetId=CONFIG["google_sheets_id"]
            ).execute()
            
            logger.info(f"Sheet exists: {sheet.get('properties', {}).get('title')}")
        except Exception as e:
            logger.error(f"Error checking sheet: {e}")
    
    def append_jobs(self, jobs: List[Dict]):
        """Append jobs to Google Sheet"""
        if not self.service:
            logger.error("Google Sheets service not available")
            return
        
        try:
            values = []
            for job in jobs:
                values.append([
                    hashlib.md5(f"{job.get('title')}{job.get('company')}".encode()).hexdigest()[:8],
                    job.get('company', ''),
                    job.get('title', ''),
                    job.get('location', ''),
                    job.get('salary', ''),
                    job.get('source', ''),
                    job.get('posted_date', ''),
                    job.get('match_score', 0),
                    job.get('url', ''),
                    'Not Applied',
                    '',
                    '',
                    '',
                    '',
                    ''
                ])
            
            body = {'values': values}
            result = self.service.spreadsheets().values().append(
                spreadsheetId=CONFIG["google_sheets_id"],
                range='Sheet1!A:O',
                valueInputOption='RAW',
                body=body
            ).execute()
            
            logger.info(f"Appended {result.get('updates', {}).get('updatedRows', 0)} rows to sheet")
        except Exception as e:
            logger.error(f"Error appending jobs to sheet: {e}")

# ============================================================================
# MAIN ORCHESTRATOR
# ============================================================================

class JobApplicationAutomation:
    """Main orchestrator for job application automation"""
    
    def __init__(self):
        self.aggregator = JobAggregator()
        self.customizer = CVCustomizer()
        self.sheets_manager = GoogleSheetsManager()
    
    def run(self):
        """Run the complete automation"""
        logger.info("=" * 80)
        logger.info("Starting Job Application Automation System")
        logger.info("=" * 80)
        
        # Step 1: Scrape jobs
        logger.info("\n[STEP 1] Scraping jobs from all sources...")
        all_jobs = self.aggregator.scrape_all()
        
        # Step 2: Filter jobs
        logger.info("\n[STEP 2] Filtering jobs by criteria...")
        filtered_jobs = self.aggregator.filter_jobs(all_jobs)
        
        # Step 3: Deduplicate
        logger.info("\n[STEP 3] Removing duplicates...")
        unique_jobs = self.aggregator.deduplicate_jobs(filtered_jobs)
        
        # Step 4: Rank jobs
        logger.info("\n[STEP 4] Ranking jobs by match score...")
        ranked_jobs = self.aggregator.rank_jobs(unique_jobs)
        
        # Step 5: Sync to Google Sheets
        logger.info("\n[STEP 5] Syncing to Google Sheets...")
        self.sheets_manager.append_jobs(ranked_jobs[:50])  # Top 50 jobs
        
        logger.info("\n" + "=" * 80)
        logger.info(f"Job Application Automation Complete!")
        logger.info(f"Total jobs processed: {len(ranked_jobs)}")
        logger.info(f"Top job: {ranked_jobs[0].get('title')} at {ranked_jobs[0].get('company')}")
        logger.info("=" * 80)
        
        return ranked_jobs

# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    automation = JobApplicationAutomation()
    jobs = automation.run()
    
    # Print top 10 jobs
    print("\n" + "=" * 80)
    print("TOP 10 MATCHING JOBS")
    print("=" * 80)
    for i, job in enumerate(jobs[:10], 1):
        print(f"\n{i}. {job.get('title')} at {job.get('company')}")
        print(f"   Location: {job.get('location')}")
        print(f"   Salary: {job.get('salary')}")
        print(f"   Match Score: {job.get('match_score')}/100")
        print(f"   Source: {job.get('source')}")
        print(f"   URL: {job.get('url')}")
