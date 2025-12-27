# Job Application Automation System - User Manual

## 📖 Table of Contents
1. [System Overview](#system-overview)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Daily Workflow](#daily-workflow)
5. [Google Sheets Guide](#google-sheets-guide)
6. [Troubleshooting](#troubleshooting)
7. [FAQ](#faq)

---

## System Overview

### What This System Does

**Automated Job Hunting Pipeline:**
```
Scrape Jobs → Filter by Criteria → Deduplicate → Rank by Match → 
Customize CV/Cover Letter → Sync to Google Sheets → You Apply & Track
```

### Key Features

✅ **Multi-Site Scraping**
- 20+ job sites (GitLab, RemoteOK, Remote100, Wellfound, Indeed, etc.)
- Targets: FinTech, SaaS, RevOps, Compliance, Risk Management
- Salary: €3500+ | Location: Remote/Finland/Europe/UAE

✅ **AI-Powered Customization**
- Gemini Pro analyzes each job posting
- Customizes your CV with relevant keywords (ATS-optimized)
- Generates personalized cover letters
- Maintains authenticity while optimizing for screening

✅ **Smart Filtering & Ranking**
- Removes duplicates across all sites
- Ranks jobs by match score (0-100)
- Prioritizes best opportunities
- Saves you hours of manual searching

✅ **Google Sheets Integration**
- All jobs synced automatically
- Track application status
- Monitor interview pipeline
- Dashboard with key metrics

### Expected Results

| Metric | Conservative | Realistic | Optimistic |
|--------|--------------|-----------|-----------|
| Jobs/Week | 50-100 | 100-200 | 200-300 |
| Applications/Week | 10-20 | 20-40 | 40-60 |
| Interviews/Month | 5-10 | 15-25 | 25-35 |
| Conversion Rate | 5-10% | 10-15% | 15-20% |

---

## Installation

### Prerequisites
- Python 3.8+
- Google account
- Gemini Pro API access
- Internet connection

### Step-by-Step Installation

#### 1. Clone/Download Project
```bash
# Create project folder
mkdir job-automation
cd job-automation

# Copy all files here:
# - job_automation_system.py
# - requirements.txt
# - SETUP_GUIDE.md
# - USER_MANUAL.md
```

#### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

#### 3. Get API Keys

**Google Sheets API:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project: "Job Automation"
3. Enable APIs:
   - Google Sheets API
   - Google Drive API
4. Create Service Account:
   - Navigation → Service Accounts
   - Create Service Account
   - Name: "job-automation"
   - Create and download JSON key
   - Save as `credentials.json` in project folder

**Gemini Pro API:**
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click "Create API Key"
3. Copy the key

#### 4. Create Google Sheet
1. Go to [Google Sheets](https://sheets.google.com)
2. Create new sheet: "Job Applications Tracker"
3. Add headers in first row (see Google Sheets Guide below)
4. Copy Sheet ID from URL: `https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit`
5. Share sheet with service account email (found in credentials.json)

#### 5. Create .env File
Create `.env` file in project folder:
```
GEMINI_API_KEY=your_gemini_api_key_here
GOOGLE_SHEETS_ID=your_sheet_id_here
GOOGLE_CREDENTIALS_PATH=./credentials.json
```

#### 6. Test Installation
```bash
python job_automation_system.py
```

You should see:
```
Starting Job Application Automation System
Scraping Indeed jobs...
Scraping GitLab jobs...
...
Total jobs found: 150
```

---

## Configuration

### Customize for Your Needs

#### Edit Target Roles
File: `job_automation_system.py`
```python
CONFIG = {
    "target_roles": [
        "Customer Success Manager",
        "Sales Operations",
        "Revenue Operations",
        "Compliance Operations",
        "Risk Management",
        # Add more roles here
    ],
}
```

#### Edit Salary Filter
```python
CONFIG = {
    "min_salary_eur": 3500,  # Change this
}
```

#### Edit Locations
```python
CONFIG = {
    "locations": ["Remote", "Finland", "Europe", "UAE"],  # Add/remove
}
```

#### Edit User Skills
```python
CONFIG = {
    "user_skills": [
        "Salesforce", "HubSpot", "SQL", "Power BI", "Advanced Excel",
        # Add your skills here
    ],
}
```

---

## Daily Workflow

### Morning Routine (5 minutes)

**Step 1: Run the scraper**
```bash
python job_automation_system.py
```

**Step 2: Check Google Sheet**
- Open your "Job Applications Tracker" sheet
- New jobs appear in the "Jobs" sheet
- Sorted by Match Score (highest first)

**Step 3: Review top jobs**
- Look at jobs with Match Score > 70
- Read the job description
- Check salary and location

### During Day (30 minutes)

**For each job you want to apply to:**

1. **Open the job posting**
   - Click the URL in column I (Job URL)
   - Read the full job description

2. **Review your customized materials**
   - Column N: Your customized CV
   - Column O: Your personalized cover letter
   - Copy these to use in application

3. **Apply to the job**
   - Click "Apply" button on job site
   - Paste your customized CV
   - Paste your cover letter
   - Submit application

4. **Update Google Sheet**
   - Change Status (column J) to "Applied"
   - Add Applied Date (column K)
   - Add any notes (column M)

### Weekly Review (10 minutes)

**Every Friday:**
1. Count total applications
2. Check for interview invitations
3. Update interview dates (column L)
4. Move completed applications to "Archive" sheet
5. Review conversion rate on Dashboard

---

## Google Sheets Guide

### Sheet Structure

#### Jobs Sheet (Main Tracking)
| Column | Header | Purpose | Example |
|--------|--------|---------|---------|
| A | Job ID | Unique identifier | abc12345 |
| B | Company | Company name | GitLab |
| C | Position | Job title | Senior RevOps Manager |
| D | Location | Job location | Remote |
| E | Salary | Salary range | €4000-5500 |
| F | Source | Where found | RemoteOK |
| G | Posted Date | When posted | 2025-01-15 |
| H | Match Score | 0-100 score | 85 |
| I | Job URL | Link to apply | https://... |
| J | Status | Application status | Not Applied |
| K | Applied Date | When you applied | 2025-01-20 |
| L | Interview Date | Interview scheduled | 2025-02-01 |
| M | Notes | Your notes | Great fit, follow up |
| N | Customized CV | Your CV for this job | [Full CV text] |
| O | Cover Letter | Your cover letter | [Full letter text] |

#### Status Values
- **Not Applied** - Initial state
- **Applied** - You submitted application
- **Under Review** - Company reviewing
- **Interview Scheduled** - Interview confirmed
- **Rejected** - Company declined
- **Offer** - Job offer received
- **Accepted** - You accepted offer

#### Dashboard Sheet (Summary)
Add these formulas to track progress:

```
=COUNTA(Jobs!B:B)-1                          → Total Jobs Found
=COUNTIF(Jobs!J:J,"Applied")                 → Jobs Applied
=COUNTIF(Jobs!J:J,"Interview Scheduled")     → Interviews Scheduled
=COUNTIF(Jobs!J:J,"Offer")                   → Offers Received
=AVERAGE(Jobs!H:H)                           → Average Match Score
=COUNTIF(Jobs!J:J,"Interview Scheduled")/COUNTIF(Jobs!J:J,"Applied")  → Conversion Rate
```

### Conditional Formatting

**Highlight by Match Score:**
1. Select column H (Match Score)
2. Format → Conditional formatting
3. Add rules:
   - Green: > 80
   - Yellow: 50-80
   - Red: < 50

**Highlight by Status:**
1. Select column J (Status)
2. Format → Conditional formatting
3. Add rules:
   - Green: "Interview Scheduled"
   - Blue: "Applied"
   - Red: "Rejected"

### Sorting & Filtering

**Sort by Match Score (Best First):**
1. Select all data
2. Data → Sort range
3. Sort by column H (Match Score) → Z to A

**Filter by Status:**
1. Select header row
2. Data → Create a filter
3. Click filter icon in Status column
4. Select "Applied" to see only applied jobs

---

## Troubleshooting

### Common Issues

#### "ModuleNotFoundError: No module named 'google'"
**Solution:**
```bash
pip install -r requirements.txt
```

#### "Google Sheets API not found"
**Solution:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Make sure you're in the right project
3. Go to APIs & Services → Enabled APIs
4. Search for "Google Sheets API"
5. Click "Enable"

#### "Invalid API key"
**Solution:**
1. Check .env file has correct key
2. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
3. Regenerate API key
4. Update .env file

#### "No jobs found"
**Solution:**
1. Check internet connection
2. Try running again (some sites rate limit)
3. Check logs: `cat job_automation.log`
4. Verify target roles are reasonable
5. Lower salary filter temporarily

#### "Jobs not appearing in Google Sheet"
**Solution:**
1. Verify Sheet ID is correct
2. Check service account email is shared on sheet
3. Make sure "Jobs" sheet exists
4. Check for errors in logs
5. Try manually adding a row to test

#### "Gemini API errors"
**Solution:**
1. Check API key is valid
2. Make sure API is enabled
3. Check you have API quota remaining
4. Try again in 1 hour

### Check Logs

All errors are logged to `job_automation.log`:
```bash
tail -f job_automation.log
```

---

## FAQ

### Q: How much does this cost?
**A:** 
- Google Sheets: FREE
- Gemini Pro API: ~$0.01-0.05 per job (~$5-10/month for 100-200 jobs)
- Total: ~$5-10/month

### Q: Will I get banned from job sites?
**A:** 
- Unlikely if you follow rate limiting (2-second delays)
- Don't run more than 2-3 times per day
- Check each site's Terms of Service
- Use responsibly

### Q: How accurate is the CV customization?
**A:** 
- Very accurate - Gemini Pro understands context
- Always review before applying
- Maintains all factual information
- Optimizes for ATS screening

### Q: Can I run this on a schedule?
**A:** 
Yes! Use cron (Linux/Mac) or Task Scheduler (Windows):

**Linux/Mac:**
```bash
# Edit crontab
crontab -e

# Add this line to run daily at 9 AM
0 9 * * * cd /path/to/job-automation && python job_automation_system.py
```

**Windows:**
1. Open Task Scheduler
2. Create Basic Task
3. Set trigger: Daily at 9 AM
4. Set action: Run `python job_automation_system.py`

### Q: How do I add more job sites?
**A:** 
Create a new scraper class in `job_automation_system.py`:

```python
class NewSiteScraper(JobScraper):
    def scrape(self) -> List[Dict]:
        # Your scraping logic here
        jobs = []
        # ... scrape jobs ...
        return jobs
```

Then add to `JobAggregator.scrapers` list.

### Q: Can I customize the cover letter template?
**A:** 
Yes! Edit the `generate_cover_letter` method in `CVCustomizer` class to change the prompt.

### Q: What if I want to apply manually?
**A:** 
You can! The system just finds and ranks jobs. You can:
1. Review jobs in Google Sheet
2. Manually apply to any job
3. Update status in Google Sheet
4. System will track everything

### Q: How do I know if it's working?
**A:** 
Check these metrics:
- Jobs found: Should be 50-200 per run
- Match scores: Should average 60-80
- Applications: Should get 1-2 interviews per 10 applications
- Conversion rate: Should improve over time

### Q: Can I use this for other job types?
**A:** 
Yes! Edit the configuration:
- Change target roles
- Change salary filter
- Change locations
- Add new job sites

### Q: What if I get an offer?
**A:** 
1. Update Status to "Offer" in Google Sheet
2. Pause the system (don't run scraper)
3. Negotiate terms
4. Accept or decline
5. Update Status to "Accepted" or "Declined"

---

## Next Steps

1. ✅ Complete installation
2. ✅ Run system first time
3. ✅ Review top 10 jobs
4. ✅ Apply to 5-10 jobs
5. ✅ Track in Google Sheet
6. ✅ Follow up after 1 week
7. ✅ Iterate based on results

---

## Support & Feedback

If you have questions or issues:
1. Check this manual
2. Check SETUP_GUIDE.md
3. Check logs: `job_automation.log`
4. Review error messages carefully

**Good luck with your job search! 🚀**
