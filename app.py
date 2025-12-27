#!/usr/bin/env python3
"""
Job Application Automation System - Web Interface
Simple, beautiful dashboard for finding and tracking jobs
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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask
app = Flask(__name__)
CORS(app)

# Configuration
USER_NAME = "Dhruvin Shah"

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
# JOB SCRAPING - Using Free APIs
# ============================================================================

def scrape_remoteok_api():
    """Scrape RemoteOK using their free API"""
    jobs = []
    try:
        url = "https://remoteok.com/api/jobs?tag=fintech,saas,compliance,operations"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            for job in data[:50]:
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
        logger.info(f"RemoteOK: Found {len(jobs)} jobs")
    except Exception as e:
        logger.error(f"RemoteOK error: {e}")
    
    return jobs

def scrape_remote100_api():
    """Scrape Remote100 using their free API"""
    jobs = []
    try:
        url = "https://remote100.co/api/jobs"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            for job in data[:50]:
                if isinstance(job, dict) and 'title' in job:
                    jobs.append({
                        'title': job.get('title', ''),
                        'company': job.get('company_name', ''),
                        'location': 'Remote',
                        'salary': job.get('salary', ''),
                        'description': job.get('description', ''),
                        'url': job.get('url', ''),
                        'source': 'Remote100',
                    })
        logger.info(f"Remote100: Found {len(jobs)} jobs")
    except Exception as e:
        logger.error(f"Remote100 error: {e}")
    
    return jobs

def scrape_jooble_api():
    """Scrape Jooble using their free API"""
    jobs = []
    try:
        url = "https://jooble.org/api/jobs"
        params = {
            'keywords': 'revenue operations manager compliance',
            'location': 'remote',
            'limit': 50
        }
        response = requests.post(url, json=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            for job in data.get('jobs', [])[:50]:
                if isinstance(job, dict) and 'title' in job:
                    jobs.append({
                        'title': job.get('title', ''),
                        'company': job.get('company', ''),
                        'location': job.get('location', 'Remote'),
                        'salary': job.get('salary', ''),
                        'description': job.get('snippet', ''),
                        'url': job.get('link', ''),
                        'source': 'Jooble',
                    })
        logger.info(f"Jooble: Found {len(jobs)} jobs")
    except Exception as e:
        logger.error(f"Jooble error: {e}")
    
    return jobs

def scrape_adzuna_api():
    """Scrape Adzuna using their free API"""
    jobs = []
    try:
        # Using free tier - no API key needed for basic search
        url = "https://api.adzuna.com/v1/api/jobs/gb/search/1"
        params = {
            'what': 'operations manager',
            'where': 'remote',
            'results_per_page': 50,
            'app_id': 'demo',
            'app_key': 'demo'
        }
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            for job in data.get('results', [])[:50]:
                if isinstance(job, dict) and 'title' in job:
                    jobs.append({
                        'title': job.get('title', ''),
                        'company': job.get('company', {}).get('display_name', ''),
                        'location': job.get('location', {}).get('display_name', 'Remote'),
                        'salary': job.get('salary_min', ''),
                        'description': job.get('description', ''),
                        'url': job.get('redirect_url', ''),
                        'source': 'Adzuna',
                    })
        logger.info(f"Adzuna: Found {len(jobs)} jobs")
    except Exception as e:
        logger.error(f"Adzuna error: {e}")
    
    return jobs

def scrape_github_jobs():
    """Scrape GitHub Jobs API"""
    jobs = []
    try:
        url = "https://jobs.github.com/positions.json"
        params = {
            'description': 'operations',
            'location': 'remote',
            'full_time': 'true'
        }
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            for job in data[:50]:
                if isinstance(job, dict) and 'title' in job:
                    jobs.append({
                        'title': job.get('title', ''),
                        'company': job.get('company', ''),
                        'location': job.get('location', 'Remote'),
                        'salary': '',
                        'description': job.get('description', ''),
                        'url': job.get('url', ''),
                        'source': 'GitHub Jobs',
                    })
        logger.info(f"GitHub Jobs: Found {len(jobs)} jobs")
    except Exception as e:
        logger.error(f"GitHub Jobs error: {e}")
    
    return jobs

# ============================================================================
# JOB AGGREGATION
# ============================================================================

def scrape_all_jobs():
    """Scrape from all sources"""
    logger.info("Starting job scraping from all sources...")
    
    all_jobs = []
    
    # Scrape from all APIs
    all_jobs.extend(scrape_remoteok_api())
    time.sleep(1)
    all_jobs.extend(scrape_remote100_api())
    time.sleep(1)
    all_jobs.extend(scrape_jooble_api())
    time.sleep(1)
    all_jobs.extend(scrape_adzuna_api())
    time.sleep(1)
    all_jobs.extend(scrape_github_jobs())
    
    logger.info(f"Total jobs found: {len(all_jobs)}")
    return all_jobs

def filter_jobs(jobs):
    """Filter jobs by criteria"""
    filtered = []
    
    target_keywords = ['operations', 'compliance', 'risk', 'fintech', 'saas', 'manager', 'revenue']
    
    for job in jobs:
        title = job.get('title', '').lower()
        title_match = any(keyword in title for keyword in target_keywords)
        
        location = job.get('location', '').lower()
        location_match = any(loc in location for loc in ['remote', 'finland', 'europe', 'uae', 'anywhere'])
        
        if title_match and location_match:
            filtered.append(job)
    
    logger.info(f"Filtered to {len(filtered)} matching jobs")
    return filtered

def deduplicate_jobs(jobs):
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

def rank_jobs(jobs):
    """Rank jobs by match score"""
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
        elif 'remote' in location or 'anywhere' in location:
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
        jobs = scrape_all_jobs()
        filtered_jobs = filter_jobs(jobs)
        unique_jobs = deduplicate_jobs(filtered_jobs)
        ranked_jobs = rank_jobs(unique_jobs)
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
