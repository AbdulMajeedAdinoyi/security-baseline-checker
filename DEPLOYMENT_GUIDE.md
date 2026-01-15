# Security Baseline Checker - Deployment Guide to Render

## Overview
This guide will help you deploy the Security Baseline Checker application to Render (render.com).

---

## Step 1: Prepare Your Project ✅ DONE

I've already created the necessary deployment files:

### Files Created:
- **Procfile** - Tells Render how to run your app (uses Gunicorn WSGI server)
- **runtime.txt** - Specifies Python version (3.11.7)
- **.gitignore** - Excludes unnecessary files from Git
- **requirements.txt** - Updated with Gunicorn dependency
- **app.py** - Updated to accept PORT environment variable

---

## Step 2: Initialize Git Repository

Open PowerShell in your project directory and run:

```powershell
# Navigate to project directory (if not already there)
cd C:\Users\HP\Desktop\security-baseline-checker

# Initialize git repository
git init

# Add all files to git
git add .

# Create initial commit
git commit -m "Initial commit: Security Baseline Checker app"
```

---

## Step 3: Create GitHub Repository

1. Go to **https://github.com/new**
2. Create a new repository:
   - **Repository name:** `security-baseline-checker`
   - **Description:** Security Baseline Compliance Checker Application
   - **Visibility:** Public (recommended for easier setup)
   - Click **Create repository**

3. Follow GitHub's instructions to push your code. In PowerShell, run:

```powershell
# Add GitHub remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/security-baseline-checker.git

# Rename branch to main (if needed)
git branch -M main

# Push code to GitHub
git push -u origin main
```

---

## Step 4: Create Render Account

1. Go to **https://render.com**
2. Sign up for a free account (you can use GitHub to sign up)
3. Verify your email address

---

## Step 5: Connect GitHub to Render

1. After signing in to Render, go to **Dashboard**
2. Click **New +** button → select **Web Service**
3. Click **Connect account** to link your GitHub
4. Authorize Render to access your GitHub repositories

---

## Step 6: Deploy on Render

### Configuration:

1. **Select Repository:**
   - Search for `security-baseline-checker`
   - Click **Connect**

2. **Configure Web Service:**
   - **Name:** `security-baseline-checker` (or your preferred name)
   - **Environment:** `Python 3`
   - **Region:** Select closest to your users (e.g., US, EU)
   - **Branch:** `main`
   - **Build Command:** Leave empty (default is fine)
   - **Start Command:** `gunicorn app:app`

3. **Environment Variables (Optional but Recommended):**
   - Click **Add Environment Variable**
   - Add: `FLASK_ENV=production`

4. **Plan:** 
   - Select **Free** or **Starter** plan
   - Note: Free tier will pause after 15 minutes of inactivity

5. Click **Create Web Service**

---

## Step 7: Monitor Deployment

1. Render will automatically start building your app
2. Check the **Logs** tab to monitor progress
3. Wait for the status to show **"Live"**
4. Your app URL will be displayed (e.g., `https://security-baseline-checker.onrender.com`)

---

## Step 8: Test Your Deployed App

Open your browser and go to:
- **Homepage:** `https://your-app-name.onrender.com`
- **Scan Page:** `https://your-app-name.onrender.com/scan`
- **History Page:** `https://your-app-name.onrender.com/history`

---

## Important Notes for Render Deployment

### ⚠️ Database Persistence
- Currently, your app uses SQLite which stores data in the file system
- **Problem:** Render doesn't persist files between deployments
- **Solution:** For production, migrate to PostgreSQL (Render provides free tier)

### Free Tier Limitations
- App will spin down after 15 minutes of inactivity
- First request after inactivity may be slow (30 seconds)
- **Upgrade:** Paid plans ($7+/month) run continuously

### Auto-Deployments
- Render will automatically redeploy when you push changes to GitHub
- Check the **Deploy** tab to see deployment history

---

## Step 9: Custom Domain (Optional)

1. Go to **Settings** tab on Render
2. Under **Custom Domain**, enter your domain
3. Follow DNS configuration instructions
4. Update your domain's DNS records

---

## Troubleshooting

### Build Failures
- Check **Logs** tab for error messages
- Ensure all dependencies are in `requirements.txt`
- Verify `Procfile` and `runtime.txt` are correct

### App Not Starting
- Check logs for Python errors
- Ensure port is set to `PORT` environment variable
- Verify Flask app initialization

### Static Files Not Loading
- Ensure paths in HTML use `{{ url_for() }}` (already done)
- Static files should auto-serve from `web/static/`

---

## Future Improvements

1. **Add PostgreSQL database** for persistent storage
2. **Add environment configuration** using `.env` files
3. **Enable HTTPS** (Render does this automatically)
4. **Add error tracking** with Sentry
5. **Set up CI/CD** with GitHub Actions

---

## Quick Reference Commands

```powershell
# Test locally before deploying
python app.py

# View Git status
git status

# Stage changes
git add .

# Commit changes
git commit -m "Your message"

# Push to GitHub
git push origin main
```

---

## Support

- **Render Docs:** https://render.com/docs
- **Flask Deployment:** https://flask.palletsprojects.com/deployment/
- **Gunicorn Docs:** https://gunicorn.org/

---

**Your app will be live in minutes! Follow these steps and you'll have a public URL to share.**
