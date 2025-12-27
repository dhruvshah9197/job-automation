#!/usr/bin/env python3
"""
Autonomous Job Finder + AI CV Customizer
Finds jobs, customizes materials, tracks everything
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import os
import json
import time
from datetime import datetime
import requests
import sqlite3
import hashlib
import logging
import google.generativeai as genai

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

GEMINI_API_KEY = "AIzaSyDhA1h0gy_wffS20ThP1z2h9xo8XTDeB5Y"
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel('gemini-pro')

DB_FILE = 'jobs.db'

def init_db():
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
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

# ============================================================================
# JOB FINDING - Using Working APIs
# ============================================================================

def find_jobs_from_apis():
    """Find jobs from multiple working APIs"""
    all_jobs = []
    
    # RemoteOK API - WORKS
    try:
        logger.info("Searching RemoteOK...")
        url = "https://remoteok.com/api/jobs?tag=fintech,saas,operations,compliance"
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            data = response.json()
            for job in data[:100]:
                if isinstance(job, dict) and 'title' in job and 'company' in job:
                    all_jobs.append({
                        'title': job.get('title', ''),
                        'company': job.get('company', ''),
                        'location': job.get('location', 'Remote'),
                        'salary': job.get('salary', ''),
                        'description': job.get('description', ''),
                        'url': job.get('url', ''),
                        'source': 'RemoteOK',
                    })
            logger.info(f"RemoteOK: {len([j for j in all_jobs if j['source']=='RemoteOK'])} jobs")
    except Exception as e:
        logger.error(f"RemoteOK error: {e}")
    
    time.sleep(2)
    
    # Remote100 API - WORKS
    try:
        logger.info("Searching Remote100...")
        url = "https://remote100.co/api/jobs"
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            data = response.json()
            for job in data[:100]:
                if isinstance(job, dict) and 'title' in job:
                    all_jobs.append({
                        'title': job.get('title', ''),
                        'company': job.get('company_name', 'Unknown'),
                        'location': 'Remote',
                        'salary': job.get('salary', ''),
                        'description': job.get('description', ''),
                        'url': job.get('url', ''),
                        'source': 'Remote100',
                    })
            logger.info(f"Remote100: {len([j for j in all_jobs if j['source']=='Remote100'])} jobs")
    except Exception as e:
        logger.error(f"Remote100 error: {e}")
    
    time.sleep(2)
    
    # Hacker News Who's Hiring - WORKS
    try:
        logger.info("Searching Hacker News...")
        url = "https://news.ycombinator.com/jobs"
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            rows = soup.find_all('tr', class_='athing')
            for row in rows[:50]:
                try:
                    title_elem = row.find('span', class_='titleline')
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                        if any(kw in title.lower() for kw in ['remote', 'operations', 'compliance', 'fintech']):
                            all_jobs.append({
                                'title': title,
                                'company': 'HN Job',
                                'location': 'Remote',
                                'salary': '',
                                'description': '',
                                'url': title_elem.find('a').get('href', '') if title_elem.find('a') else '',
                                'source': 'Hacker News',
                            })
                except:
                    continue
            logger.info(f"Hacker News: {len([j for j in all_jobs if j['source']=='Hacker News'])} jobs")
    except Exception as e:
        logger.error(f"Hacker News error: {e}")
    
    time.sleep(2)
    
    # GitHub Jobs API - WORKS
    try:
        logger.info("Searching GitHub Jobs...")
        url = "https://jobs.github.com/positions.json"
        params = {'description': 'operations', 'location': 'remote'}
        response = requests.get(url, params=params, timeout=15)
        if response.status_code == 200:
            data = response.json()
            for job in data[:50]:
                if isinstance(job, dict) and 'title' in job:
                    all_jobs.append({
                        'title': job.get('title', ''),
                        'company': job.get('company', ''),
                        'location': job.get('location', 'Remote'),
                        'salary': '',
                        'description': job.get('description', ''),
                        'url': job.get('url', ''),
                        'source': 'GitHub Jobs',
                    })
            logger.info(f"GitHub Jobs: {len([j for j in all_jobs if j['source']=='GitHub Jobs'])} jobs")
    except Exception as e:
        logger.error(f"GitHub Jobs error: {e}")
    
    logger.info(f"Total jobs found: {len(all_jobs)}")
    return all_jobs

def filter_jobs(jobs):
    """Filter by criteria"""
    filtered = []
    keywords = ['operations', 'compliance', 'risk', 'fintech', 'saas', 'manager', 'revenue', 'customer success']
    
    for job in jobs:
        title = job.get('title', '').lower()
        location = job.get('location', '').lower()
        
        title_match = any(kw in title for kw in keywords)
        location_match = any(loc in location for loc in ['remote', 'finland', 'europe', 'uae', 'anywhere'])
        
        if title_match and location_match:
            filtered.append(job)
    
    logger.info(f"Filtered to {len(filtered)} jobs")
    return filtered

def deduplicate(jobs):
    """Remove duplicates"""
    seen = set()
    unique = []
    
    for job in jobs:
        job_hash = hashlib.md5(f"{job.get('title')}{job.get('company')}".encode()).hexdigest()
        if job_hash not in seen:
            seen.add(job_hash)
            unique.append(job)
    
    logger.info(f"After dedup: {len(unique)} unique jobs")
    return unique

def rank_jobs(jobs):
    """Rank by match score"""
    for job in jobs:
        score = 50
        title = job.get('title', '').lower()
        
        if 'revenue' in title or 'operations' in title:
            score += 20
        if 'compliance' in title or 'risk' in title:
            score += 15
        if 'manager' in title:
            score += 10
        
        location = job.get('location', '').lower()
        if 'finland' in location:
            score += 15
        elif 'remote' in location:
            score += 10
        
        job['match_score'] = min(score, 100)
    
    jobs.sort(key=lambda x: x.get('match_score', 0), reverse=True)
    return jobs

def customize_cv_for_job(job_title, company, description):
    """AI customizes CV for job"""
    try:
        prompt = f"""Create an ATS-optimized CV section for Dhruvin Shah applying to {job_title} at {company}.

Job Description: {description[:500]}

Include:
- Professional summary (2 lines)
- 3 relevant achievements
- Key skills matching the role

Keep it concise and professional."""
        
        response = gemini_model.generate_content(prompt)
        return response.text
    except Exception as e:
        logger.error(f"CV customization error: {e}")
        return ""

def generate_cover_letter(job_title, company, description):
    """AI generates cover letter"""
    try:
        prompt = f"""Write a compelling 3-paragraph cover letter for Dhruvin Shah applying to {job_title} at {company}.

Job Description: {description[:500]}

Make it:
- Personalized to the role
- Professional and concise
- Highlighting relevant experience"""
        
        response = gemini_model.generate_content(prompt)
        return response.text
    except Exception as e:
        logger.error(f"Cover letter error: {e}")
        return ""

def save_jobs(jobs):
    """Save to database"""
    conn = get_db_connection()
    c = conn.cursor()
    
    for job in jobs:
        job_id = hashlib.md5(f"{job.get('title')}{job.get('company')}".encode()).hexdigest()
        
        c.execute('SELECT id FROM jobs WHERE id = ?', (job_id,))
        if c.fetchone():
            continue
        
        # Generate customized materials
        cv = customize_cv_for_job(job.get('title', ''), job.get('company', ''), job.get('description', ''))
        letter = generate_cover_letter(job.get('title', ''), job.get('company', ''), job.get('description', ''))
        
        c.execute('''INSERT INTO jobs 
                     (id, company, position, location, salary, source, url, description, 
                      match_score, customized_cv, cover_letter, status, created_date)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (job_id, job.get('company', ''), job.get('title', ''), 
                   job.get('location', ''), job.get('salary', ''), job.get('source', ''),
                   job.get('url', ''), job.get('description', ''), job.get('match_score', 0),
                   cv, letter, 'Not Applied', datetime.now().isoformat()))
    
    conn.commit()
    conn.close()

# ============================================================================
# ROUTES
# ============================================================================

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/api/jobs', methods=['GET'])
def get_jobs():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM jobs ORDER BY match_score DESC LIMIT 100')
    jobs = [dict(row) for row in c.fetchall()]
    conn.close()
    return jsonify(jobs)

@app.route('/api/jobs/<job_id>', methods=['GET'])
def get_job(job_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM jobs WHERE id = ?', (job_id,))
    job = dict(c.fetchone() or {})
    conn.close()
    return jsonify(job)

@app.route('/api/jobs/<job_id>/status', methods=['POST'])
def update_status(job_id):
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
    try:
        logger.info("Scraping jobs...")
        jobs = find_jobs_from_apis()
        filtered = filter_jobs(jobs)
        unique = deduplicate(filtered)
        ranked = rank_jobs(unique)
        save_jobs(ranked)
        
        return jsonify({
            'success': True,
            'jobs_found': len(ranked),
            'message': f'Found {len(ranked)} jobs with customized CV & cover letters!'
        })
    except Exception as e:
        logger.error(f"Scrape error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/stats', methods=['GET'])
def get_stats():
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

if __name__ == '__main__':
    init_db()
    app.run(debug=False, port=int(os.environ.get('PORT', 5000)))
