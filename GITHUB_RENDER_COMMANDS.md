# RENDER DEPLOYMENT - COPY & PASTE COMMANDS

## Prerequisites
- GitHub account (https://github.com) - CREATE ONE if you don't have it
- Render account (https://render.com) - CREATE ONE if you don't have it
- Git installed on your computer (already done ✅)

---

## PART 1: Push Code to GitHub

### Step 1: Create GitHub Repository
1. Go to https://github.com/new
2. Fill in:
   - **Repository name:** `security-baseline-checker`
   - **Description:** Security Baseline Compliance Checker Application
   - **Visibility:** Public
3. Click "Create repository"

### Step 2: Copy These Commands and Run in PowerShell

Open PowerShell in your project folder and paste these one by one:

```powershell
# Navigate to your project (if not already there)
cd C:\Users\HP\Desktop\security-baseline-checker

# Configure Git with your GitHub info (replace with your actual email/name)
git config --global user.email "your-email@example.com"
git config --global user.name "Your Name"

# Add remote repository (REPLACE YOUR_USERNAME with your GitHub username!)
git remote add origin https://github.com/YOUR_USERNAME/security-baseline-checker.git

# Rename branch to main
git branch -M main

# Push code to GitHub (you may be prompted for GitHub credentials)
git push -u origin main
```

### What to Expect
- Git will ask for GitHub login credentials
- Upload may take 30-60 seconds depending on internet
- When complete, you'll see: `Branch 'main' set up to track 'origin/main'.`

### Verify Success
- Go to https://github.com/YOUR_USERNAME/security-baseline-checker
- You should see all your project files

---

## PART 2: Deploy on Render

### Step 1: Create Render Account
1. Go to https://render.com
2. Click "Sign Up"
3. Option 1: Sign up with GitHub (recommended - faster)
4. Verify email

### Step 2: Deploy Your App

Follow these exact steps:

1. Go to https://dashboard.render.com/
2. Click **New +** button → Select **Web Service**
3. Click **Connect account** (if needed)
4. Authorize Render to access GitHub
5. In the repository search, type: `security-baseline-checker`
6. Click **Connect** next to your repository

### Step 3: Configure Service Settings

Fill in these fields on the Render form:

| Field | Value |
|-------|-------|
| **Name** | `security-baseline-checker` |
| **Environment** | `Python 3` |
| **Region** | `US` (or nearest to you) |
| **Branch** | `main` |
| **Build Command** | *(leave empty)* |
| **Start Command** | `gunicorn app:app` |

**Plan:** Choose `Free` (or `Starter` for $7+/month if you want always-on)

### Step 4: Click "Create Web Service"

- Render will start building your app
- Check the **Logs** tab to see progress
- Wait for status to turn **"Live"** (takes 2-5 minutes)

### Step 5: Get Your Live URL

When status shows "Live", Render displays your URL:
- Example: `https://security-baseline-checker-abc123.onrender.com`
- This is your live app! Share this URL!

---

## PART 3: Test Your Live App

Open these URLs in your browser:

```
https://YOUR_APP_URL/
https://YOUR_APP_URL/scan
https://YOUR_APP_URL/history
```

Replace `YOUR_APP_URL` with the URL Render gave you.

---

## Making Updates

To update your app after deployment:

1. Make changes locally
2. Test locally: `python app.py`
3. Commit changes: `git add . && git commit -m "Description of changes"`
4. Push to GitHub: `git push origin main`
5. Render automatically redeploys (watch Logs tab)

---

## Troubleshooting

### Deployment Failed - Check Logs
1. Go to Render dashboard
2. Click your service
3. Go to **Logs** tab
4. Look for red error messages
5. Common issues:
   - `No module named 'flask'` → missing requirements.txt
   - `Command 'gunicorn' not found` → missing from requirements.txt
   - Syntax errors → check app.py

### App Not Starting
- Check if `Procfile` exists in repo root
- Check if `app.py` exists in repo root
- Verify Start Command is: `gunicorn app:app`

### Static Files Not Loading
- Ensure CSS/JS URLs use `{{ url_for() }}` in HTML
- Clear browser cache (Ctrl+Shift+Delete)

### Still Having Issues?
1. Check DEPLOYMENT_GUIDE.md for detailed help
2. Render Docs: https://render.com/docs
3. Flask Docs: https://flask.palletsprojects.com/

---

## Quick Reference

```powershell
# Check git status
git status

# View changes
git diff

# Stage files
git add .

# Commit with message
git commit -m "Your message"

# Push to GitHub
git push origin main

# Check git log
git log --oneline
```

---

## Free Tier Notes

✅ **Included:**
- 750 hours/month compute time
- GitHub integration
- Auto-deploy on push
- HTTPS/SSL certificate
- Web console

⚠️ **Limitations:**
- Spins down after 15 minutes of inactivity
- First request after spin-down takes ~30 seconds
- Limited to small projects

💰 **Upgrade Options:**
- Starter: $7/month - Always on, better performance
- Pro: $19/month - More resources
- Premium: Custom pricing

---

## Your Deployment Timeline

```
Immediate: ✅ Git repo created
0-5 min:   Push code to GitHub
5-10 min:  Create Render account & configure
10-15 min: Deployment starts
15-20 min: ✅ APP LIVE! 🎉
```

---

**YOU'RE ALL SET! Start with PART 1 and follow each step carefully. You'll have a live app in 20 minutes!**
