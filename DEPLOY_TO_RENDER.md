# 🚀 Deploy to Render (Cloud) - Complete Guide

Your job automation system will run 24/7 on Render's free tier. No more running it locally!

---

## What You'll Get

✅ **24/7 Uptime** - System runs all day, every day
✅ **Automatic Daily Jobs** - Finds jobs at 9 AM automatically
✅ **Free Tier** - No credit card needed
✅ **Easy Updates** - Just push to GitHub, Render auto-deploys
✅ **Your Own URL** - Access from anywhere

---

## 5-Step Deployment (15 minutes)

### Step 1: Create GitHub Account (if you don't have one)

1. Go to: https://github.com/signup
2. Create account with your email
3. Verify email
4. Done!

### Step 2: Create GitHub Repository

1. Go to: https://github.com/new
2. Fill in:
   - **Repository name:** `job-automation`
   - **Description:** Job Application Automation System
   - **Public** (select this)
3. Click "Create repository"
4. You'll see instructions - **COPY THE COMMANDS**

### Step 3: Push Your Code to GitHub

Open terminal/command prompt and run these commands:

```bash
# Navigate to your project folder
cd /path/to/your/job-automation

# Initialize git
git init

# Add all files
git add .

# Create first commit
git commit -m "Initial commit: Job automation system"

# Add remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/job-automation.git

# Push to GitHub
git branch -M main
git push -u origin main
```

**You'll be asked for your GitHub password** - use your GitHub token instead:
1. Go to: https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Check: `repo` (all options under it)
4. Click "Generate token"
5. Copy the token
6. Paste it when asked for password

### Step 4: Deploy on Render

1. Go to: https://render.com
2. Click "Sign up" (use GitHub to sign up - easier!)
3. Click "New +" → "Web Service"
4. Select "Deploy an existing repository"
5. Click "Connect" next to your `job-automation` repository
6. Fill in:
   - **Name:** `job-automation`
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements_web.txt`
   - **Start Command:** `gunicorn app:app`
7. Click "Create Web Service"
8. **Wait 2-3 minutes** for deployment

### Step 5: Verify It's Working

1. Render will show you a URL like: `https://job-automation-xxxxx.onrender.com`
2. Click the URL
3. You should see your beautiful dashboard!
4. Click "Find Jobs Now" to test

---

## Your Dashboard URL

Once deployed, you'll have a URL like:
```
https://job-automation-xxxxx.onrender.com
```

**Bookmark this!** You can access it from anywhere, anytime.

---

## How It Works on Render

✅ **Web Server** - Your dashboard runs 24/7
✅ **Job Scraping** - Runs automatically at 9 AM daily
✅ **Database** - Stores all jobs locally
✅ **AI Customization** - Uses your Gemini API key

---

## Making Updates

If you want to change something:

1. Edit files locally
2. Run:
   ```bash
   git add .
   git commit -m "Your change description"
   git push
   ```
3. Render automatically redeploys (takes 1-2 minutes)

---

## Troubleshooting

### "Build failed"
- Check that all files are in the repository
- Make sure `requirements_web.txt` exists
- Check `Procfile` exists

### "Application error"
- Wait 2-3 minutes for full deployment
- Refresh the page
- Check Render logs (click "Logs" in Render dashboard)

### "No jobs appearing"
- Click "Find Jobs Now" button
- Wait 2-3 minutes
- Refresh page

### "Jobs not updating at 9 AM"
- Render free tier may sleep if no activity
- Click "Find Jobs Now" manually to trigger
- Or upgrade to paid tier for guaranteed uptime

---

## Free Tier Limitations

✅ **What's Included:**
- 750 hours/month (enough for 24/7)
- Auto-deploys from GitHub
- Free SSL certificate
- Custom domain support

⚠️ **Limitations:**
- May sleep after 15 minutes of inactivity
- Limited to 512 MB RAM
- Limited to 0.5 CPU

**Solution:** Click "Find Jobs Now" occasionally to keep it active, or upgrade to paid tier ($7/month).

---

## Upgrade to Paid (Optional)

If you want guaranteed 24/7 uptime:

1. Go to your Render dashboard
2. Click your service
3. Click "Settings"
4. Change plan from "Free" to "Starter" ($7/month)
5. Done!

---

## Next Steps

1. ✅ Create GitHub account
2. ✅ Create GitHub repository
3. ✅ Push code to GitHub
4. ✅ Deploy on Render
5. ✅ Access your dashboard
6. ✅ Start finding jobs!

---

## Your Deployment Checklist

- [ ] GitHub account created
- [ ] Repository created
- [ ] Code pushed to GitHub
- [ ] Render account created
- [ ] Web service deployed
- [ ] Dashboard URL working
- [ ] "Find Jobs Now" button works
- [ ] Jobs appearing in dashboard

---

## Support

**Render Dashboard:** https://dashboard.render.com
**Render Docs:** https://render.com/docs

---

## You're Done! 🎉

Your job automation system is now running 24/7 in the cloud!

**Access it anytime at:** `https://job-automation-xxxxx.onrender.com`

**Good luck with your job search! 🚀**
