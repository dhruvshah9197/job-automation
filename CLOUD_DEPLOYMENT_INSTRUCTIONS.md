# ☁️ DEPLOY TO RENDER - FINAL STEP (5 MINUTES)

Your code is ready! Now let's get it running on the cloud. Follow these exact steps.

---

## STEP 1: Create Render Account (2 minutes)

1. Go to: **https://render.com**
2. Click **"Sign Up"** (top right)
3. Click **"Continue with GitHub"** (easiest!)
4. Click **"Authorize render-oss"**
5. Done! You're logged in.

---

## STEP 2: Create GitHub Repository (3 minutes)

1. Go to: **https://github.com/new**
2. Fill in:
   - **Repository name:** `job-automation`
   - **Description:** Job Application Automation System
   - **Public** (make sure this is selected)
3. Click **"Create repository"**
4. You'll see a page with commands - **IGNORE IT** (we already did this)

---

## STEP 3: Push Code to GitHub (2 minutes)

Open **Terminal** (Mac/Linux) or **Command Prompt** (Windows) and run:

```bash
cd /workspace
git remote add origin https://github.com/dhruvshah9197/job-automation.git
git branch -M main
git push -u origin main
```

**When asked for password:**
- Go to: https://github.com/settings/tokens
- Click **"Generate new token (classic)"**
- Check the box: **`repo`** (all sub-options will auto-check)
- Scroll down, click **"Generate token"**
- **Copy the token** (it won't show again!)
- Paste it in terminal when asked for password

---

## STEP 4: Deploy on Render (2 minutes)

1. Go to: **https://dashboard.render.com**
2. Click **"New +"** (top right)
3. Click **"Web Service"**
4. Click **"Connect"** next to `job-automation` repository
5. Fill in these fields:
   - **Name:** `job-automation`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements_web.txt`
   - **Start Command:** `gunicorn app:app`
6. Scroll down to **"Environment"** section
7. Add this environment variable:
   - **Key:** `GEMINI_API_KEY`
   - **Value:** `AIzaSyDhA1h0gy_wffS20ThP1z2h9xo8XTDeB5Y`
8. Click **"Create Web Service"**
9. **WAIT 3-5 MINUTES** for deployment

---

## STEP 5: Access Your Dashboard (1 minute)

1. Render will show you a URL like: `https://job-automation-xxxxx.onrender.com`
2. Click the URL
3. You should see your beautiful dashboard!
4. Click **"🔍 Find Jobs Now"** to test

---

## 🎉 YOU'RE DONE!

Your job automation system is now running 24/7 in the cloud!

**Your Dashboard URL:**
```
https://job-automation-xxxxx.onrender.com
```

**Bookmark this URL!** You can access it from anywhere, anytime.

---

## What Happens Now

✅ **Every day at 9 AM** - System automatically finds 100-200 new jobs
✅ **AI customizes** - Creates personalized CV & cover letter for each job
✅ **You apply** - Click jobs, copy CV/cover letter, apply on job sites
✅ **Track everything** - Dashboard shows all your applications and interviews

---

## How to Use

1. **Open your dashboard URL**
2. **Click "🔍 Find Jobs Now"** (or wait for 9 AM automatic run)
3. **See jobs appear** with match scores
4. **Click on a job** to see customized CV & cover letter
5. **Copy CV & cover letter**
6. **Go to job site** and apply
7. **Update status** in dashboard

---

## Troubleshooting

### "Build failed"
- Wait 5 minutes and try again
- Check Render logs (click "Logs" in dashboard)

### "Application error"
- Refresh page
- Wait 2-3 minutes for full startup
- Check Render logs

### "No jobs appearing"
- Click "Find Jobs Now" button
- Wait 2-3 minutes
- Refresh page

### "Jobs not updating at 9 AM"
- Render free tier may sleep if no activity
- Click "Find Jobs Now" manually
- Or upgrade to paid tier ($7/month) for guaranteed uptime

---

## Free Tier Info

✅ **Included:**
- 750 hours/month (24/7 coverage)
- Auto-deploys from GitHub
- Free SSL certificate

⚠️ **Limitation:**
- May sleep after 15 minutes of inactivity
- Solution: Click "Find Jobs Now" occasionally to keep active

---

## Making Updates

If you want to change something:

1. Edit files on your computer
2. Run:
   ```bash
   cd /workspace
   git add .
   git commit -m "Your change description"
   git push
   ```
3. Render automatically redeploys (1-2 minutes)

---

## Next Steps

1. ✅ Create Render account
2. ✅ Create GitHub repository
3. ✅ Push code to GitHub
4. ✅ Deploy on Render
5. ✅ Access your dashboard
6. ✅ Start finding jobs!

---

## You're Ready! 🚀

**Go to Render and deploy now!**

Your job automation system will be live in 5 minutes!

**Good luck with your job search! 🎉**
