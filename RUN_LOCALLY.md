# 🏠 Run Locally on Your Computer

Want to test the system before deploying to the cloud? Follow these steps!

---

## Prerequisites

- Python 3.8+ installed
- Internet connection
- Your Gemini API key (you already have this)

---

## 3-Step Local Setup (5 minutes)

### Step 1: Install Python Packages

Open terminal/command prompt and run:

```bash
pip install -r requirements_web.txt
```

Wait for it to finish (you'll see "Successfully installed...").

### Step 2: Start the System

Run:

```bash
python app.py
```

You should see:
```
Running on http://localhost:5000
```

### Step 3: Open in Browser

Go to: **http://localhost:5000**

You should see your beautiful dashboard!

---

## How to Use Locally

### First Time
1. Click **"🔍 Find Jobs Now"** button
2. Wait 2-3 minutes (system is finding and customizing jobs)
3. Jobs appear on screen!

### For Each Job
1. Click on a job card
2. See your customized CV and cover letter
3. Click "View Full Job Posting"
4. Apply on the job site (paste CV + cover letter)
5. Update status to "Applied"

### Daily
- System automatically finds new jobs at 9 AM
- Check dashboard for new jobs
- Apply to 5-10 jobs
- Update status as you apply

---

## Stopping the System

Press `Ctrl + C` in terminal to stop.

---

## Troubleshooting

### "Port 5000 already in use"
Change port in `app.py`:
```python
app.run(debug=True, port=5001)  # Change 5000 to 5001
```

### "Module not found"
Run:
```bash
pip install -r requirements_web.txt
```

### "No jobs appearing"
- Click "Find Jobs Now" button
- Wait 2-3 minutes
- Refresh page (F5)

### "API key error"
- Check API key is correct in `app.py`
- Make sure you have internet connection

---

## Next Steps

1. ✅ Test locally
2. ✅ Make sure everything works
3. ✅ Deploy to Render (see DEPLOY_TO_RENDER.md)
4. ✅ Access from anywhere 24/7

---

## Tips

- **Keep terminal open** - System runs while terminal is open
- **Refresh browser** - If something looks wrong, refresh (F5)
- **Check logs** - Terminal shows what's happening
- **Test features** - Try all buttons and filters before deploying

---

## Ready to Deploy?

Once you're happy with local testing, follow: **DEPLOY_TO_RENDER.md**

---

**Good luck! 🚀**
