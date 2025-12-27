# Quick Reference Card

## 🚀 Quick Start (Copy & Paste)

### 1. Install
```bash
pip install -r requirements.txt
```

### 2. Setup .env
```
GEMINI_API_KEY=your_key_here
GOOGLE_SHEETS_ID=your_sheet_id_here
GOOGLE_CREDENTIALS_PATH=./credentials.json
```

### 3. Run
```bash
python job_automation_system.py
```

---

## 📊 Google Sheet Headers

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

---

## 📈 Daily Checklist

- [ ] Run: `python job_automation_system.py`
- [ ] Open Google Sheet
- [ ] Review top 10 jobs (Match Score > 70)
- [ ] Apply to 5-10 jobs
- [ ] Update Status to "Applied"
- [ ] Add Applied Date
- [ ] Add notes

---

## 🎯 Status Values

- Not Applied
- Applied
- Under Review
- Interview Scheduled
- Rejected
- Offer
- Accepted

---

## 💰 Cost Breakdown

| Item | Cost | Notes |
|------|------|-------|
| Google Sheets | FREE | Unlimited |
| Gemini Pro API | $0.01-0.05/job | ~$5-10/month |
| Job Scraping | FREE | Built-in |
| **Total** | **~$5-10/month** | One-time setup |

---

## 🔧 Configuration Quick Edit

**File:** `job_automation_system.py`

**Change target roles:**
```python
"target_roles": [
    "Your Role 1",
    "Your Role 2",
]
```

**Change salary:**
```python
"min_salary_eur": 3500,
```

**Change locations:**
```python
"locations": ["Remote", "Finland"],
```

---

## 📞 Troubleshooting Quick Fixes

| Issue | Fix |
|-------|-----|
| Module not found | `pip install -r requirements.txt` |
| API key invalid | Check .env file, regenerate key |
| No jobs found | Check internet, try again later |
| Sheet not updating | Verify Sheet ID, check service account access |
| Gemini errors | Check API quota, try again in 1 hour |

---

## 📅 Weekly Schedule

**Monday:** Run scraper, review jobs
**Tuesday-Thursday:** Apply to jobs
**Friday:** Review metrics, update dashboard
**Weekend:** Prepare for interviews

---

## 🎓 Expected Results Timeline

**Week 1:** 50-100 jobs, 10-20 applications, 1-2 interviews
**Week 2-4:** 100-200 jobs/week, 20-40 applications/week, 5-10 interviews/week
**Month 2-3:** 15-25 interviews/month, multiple offers

---

## 💡 Pro Tips

1. **Review CV first** - Make sure it's ATS-optimized
2. **Focus on match score** - Apply to jobs with 70+ score
3. **Follow up** - Email hiring managers 1 week after applying
4. **Network** - Connect with hiring managers on LinkedIn
5. **Practice interviews** - Prepare for 15-25 interviews/month
6. **Track metrics** - Monitor conversion rate weekly
7. **Iterate** - Adjust CV based on feedback

---

## 📱 Files You Have

1. **job_automation_system.py** - Main script
2. **requirements.txt** - Python dependencies
3. **SETUP_GUIDE.md** - Detailed setup instructions
4. **USER_MANUAL.md** - Complete user guide
5. **QUICK_REFERENCE.md** - This file
6. **CV_Dhruvin_Shah_Optimized.md** - Your optimized CV
7. **credentials.json** - Google API credentials (you create)
8. **.env** - Environment variables (you create)

---

## 🎯 Your Target Profile

**Name:** Dhruvin Shah
**Location:** Helsinki, Finland (Remote OK)
**Salary:** €3500+
**Target Roles:** FinTech, SaaS, RevOps, Compliance, Risk Management, Customer Success Manager, Sales Operations, Business Controller
**Key Skills:** Salesforce, HubSpot, SQL, Power BI, Advanced Excel, GDPR, Compliance, Revenue Operations
**Experience:** 9+ years
**Certifications:** CCSM, CROP, FTIP, Salesforce AI Specialist, HubSpot RevOps

---

## 🌐 Job Sites Covered

**Tech Companies:** GitLab, Atlassian, Shopify, Doist, Buffer, Automatic
**Remote Specialists:** RemoteOK, Remote100, Working Nomads
**Startup Focused:** Wellfound, Contra
**General:** Indeed, LinkedIn, CareerJet, JobBoom, SimplyHired, Monster
**Freelance:** Upwork

---

## ✅ Success Metrics

Track these weekly:
- Total jobs found
- Total applications
- Interview invitations
- Conversion rate (interviews/applications)
- Average match score
- Top performing job sites

---

## 🚀 You're Ready!

Everything is set up. Now:
1. Get your API keys
2. Create Google Sheet
3. Run the system
4. Start applying!

**Good luck! 🎉**
