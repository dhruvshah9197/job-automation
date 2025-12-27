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
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
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
GOOGLE_EMAIL = "dhruvshah9197@gmail.com"
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
                           for role in ['manager', 'operations', 'compliance', 'risk']):
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
    """GitLab scraper"""
    
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

# ============================================================================
# AI CUSTOMIZATION
# ============================================================================

def extract_keywords(description):
    """Extract keywords from job description"""
    try:
        prompt = f"""Extract 10 key skills and requirements from this job description.
        Return as comma-separated list only.
        
        {description}"""
        response = gemini_model.generate_content(prompt)
        return response.text.split(',')[:10]
    except:
        return []

def customize_cv(job_title, company, keywords):
    """Generate customized CV for job"""
    try:
        prompt = f"""Create an ATS-optimized CV section for {USER_NAME} applying to {job_title} at {company}.
        
        Key requirements: {', '.join(keywords)}
        
        Include:
        - Professional summary (2 lines)
        - 3 relevant achievements
        - Key skills matching the role
        
        Keep it concise and professional."""
        
        response = gemini_model.generate_content(prompt)
        return response.text
    except:
        return "Professional CV section"

def generate_cover_letter(job_title, company, keywords):
    """Generate personalized cover letter"""
    try:
        prompt = f"""Write a compelling 3-paragraph cover letter for {USER_NAME} applying to {job_title} at {company}.
        
        Key requirements: {', '.join(keywords)}
        
        Make it:
        - Personalized to the role
        - Professional and concise
        - Highlighting relevant experience"""
        
        response = gemini_model.generate_content(prompt)
        return response.text
    except:
        return "Dear Hiring Manager,\n\nI am interested in this position..."

# ============================================================================
# JOB AGGREGATION
# ============================================================================

def scrape_all_jobs():
    """Scrape jobs from all sources"""
    logger.info("Starting job scraping...")
    
    scrapers = [
        RemoteOKScraper(),
        Remote100Scraper(),
        IndeedScraper(),
        GitLabScraper(),
    ]
    
    all_jobs = []
    for scraper in scrapers:
        try:
            jobs = scraper.scrape()
            all_jobs.extend(jobs)
            logger.info(f"Found {len(jobs)} jobs from {scraper.__class__.__name__}")
            time.sleep(2)
        except Exception as e:
            logger.error(f"Error with {scraper.__class__.__name__}: {e}")
    
    return all_jobs

def filter_and_rank_jobs(jobs):
    """Filter and rank jobs"""
    filtered = []
    
    for job in jobs:
        # Check if matches criteria
        title_match = any(role in job.get('title', '').lower() 
                         for role in ['manager', 'operations', 'compliance', 'risk', 'fintech', 'saas'])
        location_match = any(loc in job.get('location', '').lower() 
                            for loc in ['remote', 'finland', 'europe', 'uae'])
        
        if title_match and location_match:
            # Calculate match score
            score = 0
            if 'remote' in job.get('location', '').lower():
                score += 20
            if 'finland' in job.get('location', '').lower():
                score += 30
            
            job['match_score'] = min(score + 50, 100)
            filtered.append(job)
    
    # Sort by match score
    filtered.sort(key=lambda x: x.get('match_score', 0), reverse=True)
    return filtered

def save_jobs_to_db(jobs):
    """Save jobs to database"""
    conn = get_db_connection()
    c = conn.cursor()
    
    for job in jobs:
        job_id = hashlib.md5(f"{job.get('title')}{job.get('company')}".encode()).hexdigest()
        
        # Check if already exists
        c.execute('SELECT id FROM jobs WHERE id = ?', (job_id,))
        if c.fetchone():
            continue
        
        # Extract keywords and customize
        keywords = extract_keywords(job.get('description', job.get('title', '')))
        customized_cv = customize_cv(job.get('title', ''), job.get('company', ''), keywords)
        cover_letter = generate_cover_letter(job.get('title', ''), job.get('company', ''), keywords)
        
        c.execute('''INSERT INTO jobs 
                     (id, company, position, location, salary, source, url, description, 
                      match_score, customized_cv, cover_letter, status, created_date)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (job_id, job.get('company', ''), job.get('title', ''), 
                   job.get('location', ''), job.get('salary', ''), job.get('source', ''),
                   job.get('url', ''), job.get('description', ''), job.get('match_score', 0),
                   customized_cv, cover_letter, 'Not Applied', datetime.now().isoformat()))
    
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
        jobs = scrape_all_jobs()
        filtered_jobs = filter_and_rank_jobs(jobs)
        save_jobs_to_db(filtered_jobs)
        
        return jsonify({
            'success': True,
            'jobs_found': len(filtered_jobs),
            'message': f'Found {len(filtered_jobs)} new jobs!'
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
# SCHEDULER
# ============================================================================

def scheduled_scrape():
    """Scheduled job scraping"""
    logger.info("Running scheduled scrape at 9 AM")
    try:
        jobs = scrape_all_jobs()
        filtered_jobs = filter_and_rank_jobs(jobs)
        save_jobs_to_db(filtered_jobs)
        logger.info(f"Scheduled scrape completed: {len(filtered_jobs)} jobs")
    except Exception as e:
        logger.error(f"Scheduled scrape error: {e}")

def run_scheduler():
    """Run scheduler in background"""
    schedule.every().day.at("09:00").do(scheduled_scrape)
    
    while True:
        schedule.run_pending()
        time.sleep(60)

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    # Initialize database
    init_db()
    
    # Start scheduler in background thread
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    
    # Run Flask app
    app.run(debug=True, port=5000)
