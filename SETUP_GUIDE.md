# Job Application Automation System - Setup Guide

## 📋 Overview

This system automates job hunting by:
1. **Scraping** jobs from 20+ sites (GitLab, RemoteOK, Remote100, Wellfound, Indeed, etc.)
2. **Filtering** by your criteria (€3500+, Remote/Finland/Europe/UAE, target roles)
3. **Customizing** CV and cover letters with AI (Gemini Pro)
4. **Syncing** to Google Sheets for tracking
5. **Ranking** by match score

**Expected Results:** 100-200 jobs/week → 15-25 interviews/month (if CV is solid)

---

## 🚀 Quick Start (5 Steps)

### Step 1: Get Your API Keys

#### A. Google Sheets API
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project: "Job Automation"
3. Enable APIs:
   - Google Sheets API
   - Google Drive API
4. Create Service Account:
   - Go to "Service Accounts"
   - Create new service account: "job-automation"
   - Create JSON key
   - Download and save as `credentials.json` in project folder
5. Share your Google Sheet with the service account email

#### B. Gemini Pro API
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create API key
3. Copy the key

### Step 2: Create Google Sheet

1. Create new Google Sheet: "Job Applications Tracker"
2. Create these sheets:
   - **Jobs** (main tracking sheet)
   - **Dashboard** (summary stats)
   - **Archive** (applied jobs)

3. In "Jobs" sheet, add headers:
   ```
   A: Job ID
   B: Company
   C: Position
   D: Location
   E: Salary
   F: Source
   G: Posted Date
   H: Match Score
   I: Job URL
   J: Status
   K: Applied Date
   L: Interview Date
   M: Notes
   N: Customized CV
   O: Cover Letter
   ```

4. Copy the Sheet ID from URL: `https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit`

### Step 3: Set Environment Variables

Create `.env` file in project folder:

```bash
GEMINI_API_KEY=your_gemini_api_key_here
GOOGLE_SHEETS_ID=your_sheet_id_here
GOOGLE_CREDENTIALS_PATH=./credentials.json
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

**requirements.txt:**
```
requests==2.31.0
beautifulsoup4==4.12.2
google-generativeai==0.3.0
google-auth-oauthlib==1.2.0
google-auth-httplib2==0.2.0
google-api-python-client==2.107.0
python-dotenv==1.0.0
```

### Step 5: Run the System

```bash
python job_automation_system.py
```

---

## 📊 Google Sheets Dashboard Setup

### Jobs Sheet (Main Tracking)
- **Status Column (J):** Not Applied → Applied → Interview Scheduled → Rejected → Offer
- **Match Score (H):** 0-100 (auto-calculated)
- **Conditional Formatting:**
  - Green: Match Score > 80
  - Yellow: Match Score 50-80
  - Red: Match Score < 50

### Dashboard Sheet (Summary)
Add these formulas:

```
Total Jobs Found: =COUNTA(Jobs!B:B)-1
Jobs Applied: =COUNTIF(Jobs!J:J,"Applied")
Interviews Scheduled: =COUNTIF(Jobs!J:J,"Interview Scheduled")
Conversion Rate: =COUNTIF(Jobs!J:J,"Interview Scheduled")/COUNTIF(Jobs!J:J,"Applied")
Average Match Score: =AVERAGE(Jobs!H:H)
Top Source: =MODE(Jobs!F:F)
```

### Archive Sheet
- Move completed applications here
- Keep for reference

---

## 🎯 How to Use Daily

### Morning (5 minutes)
1. Run: `python job_automation_system.py`
2. Check Google Sheet for new jobs
3. Sort by Match Score (highest first)

### During Day (30 minutes)
1. Review top 10 jobs
2. Click "Job URL" to open posting
3. Read customized CV and cover letter (in columns N & O)
4. Click "Apply" button on job site
5. Update "Status" to "Applied"
6. Update "Applied Date"

### Weekly (10 minutes)
1. Check "Interview Scheduled" jobs
2. Update interview dates in column L
3. Add notes in column M
4. Move completed to Archive sheet

---

## 🔧 Customization

### Change Target Roles
Edit `job_automation_system.py`:
```python
"target_roles": [
    "Customer Success Manager", "Sales Operations", "Revenue Operations",
    # Add more roles here
]
```

### Change Salary Filter
```python
"min_salary_eur": 3500,  # Change this number
```

### Change Locations
```python
"locations": ["Remote", "Finland", "Europe", "UAE"],  # Add/remove locations
```

### Add More Job Sites
Create new scraper class:
```python
class NewSiteScraper(JobScraper):
    def scrape(self) -> List[Dict]:
        # Your scraping logic here
        return jobs
```

Then add to `JobAggregator.scrapers` list.

---

## ⚠️ Important Notes

### Rate Limiting
- System includes 2-second delays between requests
- Don't run more than 2-3 times per day
- Some sites may block aggressive scraping

### Terms of Service
- Check each job site's ToS before scraping
- Some sites prohibit automated scraping
- Use responsibly

### CV Customization
- Gemini Pro API costs ~$0.01-0.05 per job
- Budget: ~$5-10/month for 100-200 jobs
- You control when customization runs

### Google Sheets Limits
- Free tier: 500 requests/100 seconds
- Plenty for this use case
- No cost

---

## 🐛 Troubleshooting

### "Google Sheets API not found"
- Make sure you enabled Google Sheets API in Cloud Console
- Check credentials.json is in correct folder
- Verify service account has sheet access

### "Gemini API key invalid"
- Check API key is correct in .env file
- Make sure API is enabled in Google AI Studio
- Regenerate key if needed

### "No jobs found"
- Check internet connection
- Some sites may be blocking requests
- Try running again in 1 hour
- Check logs in `job_automation.log`

### "Jobs not appearing in Google Sheet"
- Verify Sheet ID is correct
- Check service account email is shared on sheet
- Make sure "Jobs" sheet exists
- Check for API errors in logs

---

## 📈 Expected Timeline

**Week 1:**
- 50-100 jobs found
- 10-20 applications
- 1-2 interviews

**Week 2-4:**
- 100-200 jobs/week
- 20-40 applications/week
- 5-10 interviews/week

**Month 2-3:**
- Consistent 15-25 interviews/month
- Multiple offers likely
- Negotiate best opportunity

---

## 💡 Pro Tips

1. **Customize your CV first** - Make sure it's ATS-optimized before running
2. **Check match scores** - Focus on jobs with 70+ match score
3. **Follow up** - Email hiring managers 1 week after applying
4. **Network** - Use LinkedIn to connect with hiring managers
5. **Practice interviews** - Prepare for 15-25 interviews/month
6. **Track metrics** - Monitor conversion rate weekly
7. **Iterate** - Adjust CV based on interview feedback

---

## 📞 Support

If you encounter issues:
1. Check `job_automation.log` for error messages
2. Verify all API keys and credentials
3. Test each component separately
4. Check internet connection
5. Try running again in 1 hour (rate limiting)

---

## 🎉 Next Steps

1. ✅ Set up API keys
2. ✅ Create Google Sheet
3. ✅ Install dependencies
4. ✅ Run system
5. ✅ Start applying!

**Good luck! You've got this! 🚀**
