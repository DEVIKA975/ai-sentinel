# GitHub Upload Instructions - AI Sentinel

## Quick Upload Guide

Follow these steps to upload your AI Sentinel project to GitHub.

---

## Step 1: Create GitHub Repository (Via Web Browser)

### Manual Steps:

1. **Open your web browser** and go to: https://github.com/new

2. **Fill in the repository details**:
   - **Repository name**: `ai-sentinel`
   - **Description**: `Shadow AI Detection & Mitigation Platform - Built with GPT-4, Streamlit, and Python`
   - **Visibility**: Choose **Public** (to showcase in your portfolio)
   - **DO NOT** check "Initialize this repository with a README" (you already have one!)
   - Leave all other checkboxes unchecked

3. **Click "Create repository"**

---

## Step 2: Connect Your Local Repository to GitHub

After creating the repository, GitHub will show you commands. Here's what to run in PowerShell:

### Commands to Run:

```powershell
# Navigate to your project directory (if not already there)
cd C:\Users\devik\Desktop\rabodemo

# Add GitHub as the remote origin
# REPLACE 'YOUR-USERNAME' with your actual GitHub username
git remote add origin https://github.com/YOUR-USERNAME/ai-sentinel.git

# Rename branch to main (standard GitHub branch name)
git branch -M main

# Push your code to GitHub
git push -u origin main
```

### Example with actual username:
If your GitHub username is `devikagarwal`, the command would be:
```powershell
git remote add origin https://github.com/devikagarwal/ai-sentinel.git
git branch -M main
git push -u origin main
```

---

## Step 3: Authentication

When you run `git push`, you'll be prompted for credentials:

### Option A: GitHub Personal Access Token (Recommended)
1. Go to: https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Give it a name: `AI Sentinel Upload`
4. Check the **`repo`** scope (full control of private repositories)
5. Click "Generate token"
6. **Copy the token** (you won't see it again!)
7. When prompted for password, **paste the token** (not your GitHub password)

### Option B: SSH Key (Advanced)
If you have SSH keys set up, use SSH instead:
```powershell
git remote add origin git@github.com:YOUR-USERNAME/ai-sentinel.git
git push -u origin main
```

---

## Step 4: Verify Upload

After successful push:

1. Go to: `https://github.com/YOUR-USERNAME/ai-sentinel`
2. You should see:
   - ✅ README.md displayed on the homepage
   - ✅ All your files and folders
   - ✅ Your commit history (3 commits)

---

## Step 5: Configure Repository (Optional but Recommended)

### Add Topics:
1. Click the ⚙️ gear icon next to "About"
2. Add topics: `ai`, `security`, `shadow-ai`, `gpt4`, `streamlit`, `python`, `machine-learning`
3. Click "Save changes"

### Set Repository Description:
The description should already be there, but verify it shows:
> Shadow AI Detection & Mitigation Platform - Built with GPT-4, Streamlit, and Python

---

## Troubleshooting

### Error: "remote origin already exists"
```powershell
# Remove existing remote and try again
git remote remove origin
git remote add origin https://github.com/YOUR-USERNAME/ai-sentinel.git
```

### Error: "failed to push some refs"
```powershell
# Pull first, then push
git pull origin main --allow-unrelated-histories
git push -u origin main
```

### Error: "authentication failed"
- Make sure you're using a Personal Access Token, not your password
- GitHub disabled password authentication in 2021

---

## Quick Reference

```powershell
# Check current remote
git remote -v

# Check current branch
git branch

# View commit history
git log --oneline

# View repository status
git status
```

---

## What's Next?

After uploading to GitHub:

### 1. Share Your Portfolio
Your repository URL will be:
```
https://github.com/YOUR-USERNAME/ai-sentinel
```

### 2. Deploy to Streamlit Cloud (Optional)
For a live demo:
1. Go to https://share.streamlit.io
2. Click "New app"
3. Connect your GitHub repository
4. Set main file: `app.py`
5. Add secrets: Your `OPENAI_API_KEY`
6. Deploy!

### 3. Add a Badge to README (Optional)
After deployment, add this to your README:
```markdown
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-url.streamlit.app)
```

---

## Need Help?

If you encounter issues:
1. Check that your GitHub username is correct
2. Verify you're in the right directory (`C:\Users\devik\Desktop\rabodemo`)
3. Make sure you have internet connection
4. Confirm you're using a Personal Access Token, not password

---

**You're ready to showcase your work! 🚀**
