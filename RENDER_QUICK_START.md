# RENDER DEPLOYMENT - QUICK START GUIDE

## ✅ COMPLETED STEPS:
- [x] Created `Procfile` (tells Render how to run your app)
- [x] Created `runtime.txt` (Python 3.11.7)
- [x] Created `.gitignore` (excludes unnecessary files)
- [x] Updated `requirements.txt` (added Gunicorn)
- [x] Updated `app.py` (production-ready)
- [x] Initialized Git repository
- [x] Created initial Git commit with all files

---

## 📋 NEXT STEPS (FOLLOW IN ORDER):

### STEP 1: Create GitHub Repository
1. Go to https://github.com/new
2. Fill in:
   - **Repository name:** `security-baseline-checker`
   - **Description:** Security Baseline Compliance Checker Application
   - **Visibility:** Public
3. Click **Create repository**

### STEP 2: Connect Local Git to GitHub
Copy and paste these commands in PowerShell (one at a time):

```powershell
# Replace YOUR_USERNAME with your GitHub username
git remote add origin https://github.com/YOUR_USERNAME/security-baseline-checker.git

# Rename branch if needed
git branch -M main

# Push code to GitHub
git push -u origin main
```

### STEP 3: Create Render Account
1. Go to https://render.com
2. Sign up (use GitHub to sign up faster)
3. Verify email

### STEP 4: Deploy on Render
1. Login to Render dashboard
2. Click **New +** → **Web Service**
3. Click **Connect account** and authorize GitHub
4. Search and select `security-baseline-checker` repo
5. Configure:
   - **Name:** `security-baseline-checker`
   - **Environment:** Python 3
   - **Start Command:** `gunicorn app:app`
6. Click **Create Web Service**
7. Wait for deployment (check Logs tab)
8. Get your public URL when status shows **"Live"**

---

## 🚀 YOUR APP WILL BE LIVE AT:
`https://your-app-name.onrender.com`

---

## 📱 TEST YOUR DEPLOYED APP:
- Homepage: `https://your-app-name.onrender.com/`
- Scan Page: `https://your-app-name.onrender.com/scan`
- History: `https://your-app-name.onrender.com/history`

---

## ⚠️ IMPORTANT NOTES:

### Free Tier:
- App sleeps after 15 minutes of inactivity
- First request takes ~30 seconds
- Upgrade to Starter ($7+/month) for always-on

### Database:
- Currently uses SQLite (data lost on redeploy)
- For production, add PostgreSQL

### Auto-Deploy:
- Push changes to GitHub → Auto-deploys on Render
- Check Deploy tab for history

---

## 🐛 IF DEPLOYMENT FAILS:
1. Check **Logs** tab in Render for errors
2. Common issues:
   - Missing `Procfile` or `requirements.txt`
   - Python version mismatch
   - Syntax errors in app.py
3. Fix locally, commit to Git, push to GitHub → Render auto-redeploys

---

## 📚 FULL GUIDE:
See `DEPLOYMENT_GUIDE.md` for detailed step-by-step instructions

---

**Good luck! You're about to go live! 🎉**
