#!/usr/bin/env python3
"""
Job Application Automation System - Web Interface
Simple, beautiful dashboard for finding and tracking jobs
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import os
import json
import threading
import schedule
import time
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
import sqlite3
import hashlib
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask
app = Flask(__name__)
CORS(app)

# Configuration
GEMINI_API_KEY = "AIzaSyDhA1h0gy_wffS20ThP1z2h9xo8XTDeB5Y"
USER_NAME = "Dhruvin Shah"

# Initialize Gemini
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel('gemini-pro')

# Database setup
DB_FILE = 'jobs.db'

def init_db():
    """Initialize SQLite database"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS jobs
                 (id TEXT PRIMARY KEY, company TEXT, position TEXT, location TEXT, 
                  salary TEXT, source TEXT, url TEXT, description TEXT, 
                  match_score REAL, customized_cv TEXT, cover_letter TEXT,
                  status TEXT, applied_date TEXT, created_date TEXT)''')
    conn.commit()
    conn.close()

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

# ============================================================================
# JOB SCRAPING
# ============================================================================

class JobScraper:
    """Base job scraper"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def scrape(self):
        return []

class RemoteOKScraper(JobScraper):
    """RemoteOK scraper"""
    
    def scrape(self):
        jobs = []
        try:
            url = "https://remoteok.com/api/jobs?tag=fintech,saas,compliance"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                for job in data[:30]:
                    if isinstance(job, dict) and 'title' in job:
                        jobs.append({
                            'title': job.get('title', ''),
                            'company': job.get('company', ''),
                            'location': job.get('location', 'Remote'),
                            'salary': job.get('salary', ''),
                            'description': job.get('description', ''),
                            'url': job.get('url', ''),
                            'source': 'RemoteOK',
                        })
        except Exception as e:
            logger.error(f"RemoteOK scraping error: {e}")
        
        return jobs

class Remote100Scraper(JobScraper):
    """Remote100 scraper"""
    
    def scrape(self):
        jobs = []
        try:
            url = "https://remote100.co/api/jobs"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                for job in data[:30]:
                    if any(role in job.get('title', '').lower() 
                           for role in ['manager', 'operations', 'compliance', 'risk', 'fintech', 'saas']):
                        jobs.append({
                            'title': job.get('title', ''),
                            'company': job.get('company_name', ''),
                            'location': 'Remote',
                            'salary': job.get('salary', ''),
                            'description': job.get('description', ''),
                            'url': job.get('url', ''),
                            'source': 'Remote100',
                        })
        except Exception as e:
            logger.error(f"Remote100 scraping error: {e}")
        
        return jobs

class IndeedScraper(JobScraper):
    """Indeed scraper"""
    
    def scrape(self):
        jobs = []
        try:
            url = "https://www.indeed.com/jobs?q=revenue+operations&l=Remote&jt=fulltime"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                job_cards = soup.find_all('div', class_='job_seen_beacon')
                
                for card in job_cards[:20]:
                    try:
                        title = card.find('h2', class_='jobTitle')
                        company = card.find('span', class_='companyName')
                        location = card.find('div', class_='companyLocation')
                        
                        if title and company:
                            jobs.append({
                                'title': title.get_text(strip=True),
                                'company': company.get_text(strip=True),
                                'location': location.get_text(strip=True) if location else 'Remote',
                                'salary': 'Not specified',
                                'description': '',
                                'url': 'https://www.indeed.com',
                                'source': 'Indeed',
                            })
                    except:
                        continue
        except Exception as e:
            logger.error(f"Indeed scraping error: {e}")
        
        return jobs

class GitLabScraper(JobScraper):
    """GitLab jobs scraper"""
    
    def scrape(self):
        jobs = []
        try:
            url = "https://about.gitlab.com/jobs/"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                job_links = soup.find_all('a', class_='posting-title')
                
                for link in job_links[:15]:
                    try:
                        title = link.get_text(strip=True)
                        if any(role in title.lower() for role in ['manager', 'operations', 'compliance']):
                            jobs.append({
                                'title': title,
                                'company': 'GitLab',
                                'location': 'Remote',
                                'salary': 'Competitive',
                                'description': '',
                                'url': link.get('href', ''),
                                'source': 'GitLab',
                            })
                    except:
                        continue
        except Exception as e:
            logger.error(f"GitLab scraping error: {e}")
        
        return jobs

class WellfoundScraper(JobScraper):
    """Wellfound (AngelList) jobs scraper"""
    
    def scrape(self):
        jobs = []
        try:
            url = "https://wellfound.com/jobs"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                job_items = soup.find_all('div', class_='job-item')
                
                for item in job_items[:15]:
                    try:
                        title_elem = item.find('h3')
                        company_elem = item.find('span', class_='company-name')
                        
                        if title_elem and company_elem:
                            jobs.append({
                                'title': title_elem.get_text(strip=True),
                                'company': company_elem.get_text(strip=True),
                                'location': 'Remote',
                                'salary': 'Not specified',
                                'description': '',
                                'url': item.find('a', href=True).get('href', '') if item.find('a', href=True) else '',
                                'source': 'Wellfound',
                            })
                    except:
                        continue
        except Exception as e:
            logger.error(f"Wellfound scraping error: {e}")
        
        return jobs

class ContraScraper(JobScraper):
    """Contra jobs scraper"""
    
    def scrape(self):
        jobs = []
        try:
            url = "https://contra.com/search/jobs"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                job_items = soup.find_all('div', class_='job-card')
                
                for item in job_items[:15]:
                    try:
                        title_elem = item.find('h3')
                        company_elem = item.find('span', class_='company')
                        
                        if title_elem:
                            jobs.append({
                                'title': title_elem.get_text(strip=True),
                                'company': company_elem.get_text(strip=True) if company_elem else 'Freelance',
                                'location': 'Remote',
                                'salary': 'Varies',
                                'description': '',
                                'url': item.find('a', href=True).get('href', '') if item.find('a', href=True) else '',
                                'source': 'Contra',
                            })
                    except:
                        continue
        except Exception as e:
            logger.error(f"Contra scraping error: {e}")
        
        return jobs

class CareerJetScraper(JobScraper):
    """CareerJet jobs scraper"""
    
    def scrape(self):
        jobs = []
        try:
            url = "https://www.careerjet.com/search/jobs?s=revenue+operations&l=remote"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                job_items = soup.find_all('div', class_='job')
                
                for item in job_items[:15]:
                    try:
                        title_elem = item.find('h2')
                        company_elem = item.find('span', class_='company')
                        
                        if title_elem:
                            jobs.append({
                                'title': title_elem.get_text(strip=True),
                                'company': company_elem.get_text(strip=True) if company_elem else 'Unknown',
                                'location': 'Remote',
                                'salary': 'Not specified',
                                'description': '',
                                'url': item.find('a', href=True).get('href', '') if item.find('a', href=True) else '',
                                'source': 'CareerJet',
                            })
                    except:
                        continue
        except Exception as e:
            logger.error(f"CareerJet scraping error: {e}")
        
        return jobs

class SimplyHiredScraper(JobScraper):
    """SimplyHired jobs scraper"""
    
    def scrape(self):
        jobs = []
        try:
            url = "https://www.simplyhired.com/search?q=revenue+operations&l=remote"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                job_items = soup.find_all('div', class_='job-item')
                
                for item in job_items[:15]:
                    try:
                        title_elem = item.find('h2')
                        company_elem = item.find('span', class_='company')
                        
                        if title_elem:
                            jobs.append({
                                'title': title_elem.get_text(strip=True),
                                'company': company_elem.get_text(strip=True) if company_elem else 'Unknown',
                                'location': 'Remote',
                                'salary': 'Not specified',
                                'description': '',
                                'url': item.find('a', href=True).get('href', '') if item.find('a', href=True) else '',
                                'source': 'SimplyHired',
                            })
                    except:
                        continue
        except Exception as e:
            logger.error(f"SimplyHired scraping error: {e}")
        
        return jobs

class WorkingNomadsScraper(JobScraper):
    """Working Nomads jobs scraper"""
    
    def scrape(self):
        jobs = []
        try:
            url = "https://www.workingnomads.co/jobs"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                job_items = soup.find_all('div', class_='job')
                
                for item in job_items[:15]:
                    try:
                        title_elem = item.find('h3')
                        company_elem = item.find('span', class_='company')
                        
                        if title_elem:
                            jobs.append({
                                'title': title_elem.get_text(strip=True),
                                'company': company_elem.get_text(strip=True) if company_elem else 'Unknown',
                                'location': 'Remote',
                                'salary': 'Not specified',
                                'description': '',
                                'url': item.find('a', href=True).get('href', '') if item.find('a', href=True) else '',
                                'source': 'Working Nomads',
                            })
                    except:
                        continue
        except Exception as e:
            logger.error(f"Working Nomads scraping error: {e}")
        
        return jobs

# ============================================================================
# JOB AGGREGATION
# ============================================================================

class JobAggregator:
    """Aggregates jobs from multiple sources"""
    
    def __init__(self):
        self.scrapers = [
            RemoteOKScraper(),
            Remote100Scraper(),
            IndeedScraper(),
            GitLabScraper(),
            WellfoundScraper(),
            ContraScraper(),
            CareerJetScraper(),
            SimplyHiredScraper(),
            WorkingNomadsScraper(),
        ]
        self.all_jobs = []
    
    def scrape_all(self) -> list:
        """Scrape from all sources"""
        logger.info("Starting job scraping from all sources...")
        
        for scraper in self.scrapers:
            try:
                jobs = scraper.scrape()
                self.all_jobs.extend(jobs)
                logger.info(f"Found {len(jobs)} jobs from {scraper.__class__.__name__}")
                time.sleep(2)
            except Exception as e:
                logger.error(f"Error with {scraper.__class__.__name__}: {e}")
        
        logger.info(f"Total jobs found: {len(self.all_jobs)}")
        return self.all_jobs
    
    def filter_jobs(self, jobs: list) -> list:
        """Filter jobs by criteria"""
        filtered = []
        
        for job in jobs:
            title_match = any(role.lower() in job.get('title', '').lower() 
                            for role in ['manager', 'operations', 'compliance', 'risk', 'fintech', 'saas'])
            
            location = job.get('location', '').lower()
            location_match = any(loc.lower() in location 
                               for loc in ['remote', 'finland', 'europe', 'uae'])
            
            if title_match and location_match:
                filtered.append(job)
        
        logger.info(f"Filtered to {len(filtered)} matching jobs")
        return filtered
    
    def deduplicate_jobs(self, jobs: list) -> list:
        """Remove duplicate jobs"""
        seen = set()
        unique = []
        
        for job in jobs:
            job_hash = hashlib.md5(
                f"{job.get('title', '')}{job.get('company', '')}".encode()
            ).hexdigest()
            
            if job_hash not in seen:
                seen.add(job_hash)
                unique.append(job)
        
        logger.info(f"After deduplication: {len(unique)} unique jobs")
        return unique
    
    def rank_jobs(self, jobs: list) -> list:
        """Rank jobs by match score"""
        for job in jobs:
            score = 50
            
            title = job.get('title', '').lower()
            if 'revenue' in title or 'operations' in title:
                score += 20
            if 'compliance' in title or 'risk' in title:
                score += 15
            
            location = job.get('location', '').lower()
            if 'finland' in location:
                score += 15
            elif 'remote' in location:
                score += 10
            
            job['match_score'] = min(score, 100)
        
        jobs.sort(key=lambda x: x.get('match_score', 0), reverse=True)
        return jobs

def save_jobs_to_db(jobs):
    """Save jobs to database"""
    conn = get_db_connection()
    c = conn.cursor()
    
    for job in jobs:
        job_id = hashlib.md5(f"{job.get('title')}{job.get('company')}".encode()).hexdigest()
        
        c.execute('SELECT id FROM jobs WHERE id = ?', (job_id,))
        if c.fetchone():
            continue
        
        c.execute('''INSERT INTO jobs 
                     (id, company, position, location, salary, source, url, description, 
                      match_score, customized_cv, cover_letter, status, created_date)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (job_id, job.get('company', ''), job.get('title', ''), 
                   job.get('location', ''), job.get('salary', ''), job.get('source', ''),
                   job.get('url', ''), job.get('description', ''), job.get('match_score', 0),
                   '', '', 'Not Applied', datetime.now().isoformat()))
    
    conn.commit()
    conn.close()

# ============================================================================
# FLASK ROUTES
# ============================================================================

@app.route('/')
def index():
    """Main dashboard"""
    return render_template('dashboard.html')

@app.route('/api/jobs', methods=['GET'])
def get_jobs():
    """Get all jobs"""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM jobs ORDER BY match_score DESC LIMIT 100')
    jobs = [dict(row) for row in c.fetchall()]
    conn.close()
    
    return jsonify(jobs)

@app.route('/api/jobs/<job_id>', methods=['GET'])
def get_job(job_id):
    """Get single job details"""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM jobs WHERE id = ?', (job_id,))
    job = dict(c.fetchone() or {})
    conn.close()
    
    return jsonify(job)

@app.route('/api/jobs/<job_id>/status', methods=['POST'])
def update_job_status(job_id):
    """Update job application status"""
    data = request.json
    status = data.get('status', 'Applied')
    
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('UPDATE jobs SET status = ?, applied_date = ? WHERE id = ?',
              (status, datetime.now().isoformat(), job_id))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/api/scrape', methods=['POST'])
def trigger_scrape():
    """Trigger job scraping"""
    try:
        logger.info("Manual scrape triggered")
        aggregator = JobAggregator()
        jobs = aggregator.scrape_all()
        filtered_jobs = aggregator.filter_jobs(jobs)
        unique_jobs = aggregator.deduplicate_jobs(filtered_jobs)
        ranked_jobs = aggregator.rank_jobs(unique_jobs)
        save_jobs_to_db(ranked_jobs)
        
        return jsonify({
            'success': True,
            'jobs_found': len(ranked_jobs),
            'message': f'Found {len(ranked_jobs)} new jobs!'
        })
    except Exception as e:
        logger.error(f"Scrape error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get dashboard statistics"""
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute('SELECT COUNT(*) as total FROM jobs')
    total = c.fetchone()['total']
    
    c.execute('SELECT COUNT(*) as applied FROM jobs WHERE status = "Applied"')
    applied = c.fetchone()['applied']
    
    c.execute('SELECT COUNT(*) as interviews FROM jobs WHERE status = "Interview Scheduled"')
    interviews = c.fetchone()['interviews']
    
    c.execute('SELECT AVG(match_score) as avg_score FROM jobs')
    avg_score = c.fetchone()['avg_score'] or 0
    
    conn.close()
    
    return jsonify({
        'total_jobs': total,
        'applied': applied,
        'interviews': interviews,
        'avg_match_score': round(avg_score, 1),
        'conversion_rate': round((interviews / applied * 100) if applied > 0 else 0, 1)
    })

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    init_db()
    app.run(debug=False, port=int(os.environ.get('PORT', 5000)))
