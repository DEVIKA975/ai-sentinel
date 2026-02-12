# GitHub Setup Instructions

## Quick Setup for Your GitHub Repository

### 1. Create GitHub Repository

1. Go to [GitHub](https://github.com/new)
2. Repository name: `ai-sentinel`
3. Description: `Shadow AI Detection & Mitigation Platform for Rabobank`
4. Make it **Public** (to showcase to interviewers)
5. **Do NOT** initialize with README (we already have one)
6. Click "Create repository"

### 2. Push Local Code to GitHub

```powershell
# Set your GitHub username
$GITHUB_USERNAME = "your-username"  # Replace with your actual username

# Add remote origin
git remote add origin https://github.com/$GITHUB_USERNAME/ai-sentinel.git

# Rename branch to main (if needed)
git branch -M main

# Push to GitHub
git push -u origin main
```

Alternative (if you prefer SSH):
```powershell
git remote add origin git@github.com:$GITHUB_USERNAME/ai-sentinel.git
git branch -M main
git push -u origin main
```

### 3. Configure Repository Settings

#### Add Topics (for discoverability)
1. Go to your repository page
2. Click the gear icon next to "About"
3. Add topics: `ai`, `security`, `rabobank`, `shadow-ai`, `gpt4`, `streamlit`, `python`

#### Add Repository Description
```
Shadow AI Detection & Mitigation Platform - Rabobank Interview Project. Built with GPT-4, Streamlit, and Python.
```

#### Enable GitHub Pages (Optional - for docs)
1. Go to Settings → Pages
2. Source: Deploy from a branch
3. Branch: `main`, folder: `/docs`

### 4. Create Releases (Optional)

Mark Phase 1 as a release:
```powershell
git tag -a v1.0.0 -m "Phase 1 PoC: Shadow AI Detection with GPT-4"
git push origin v1.0.0
```

### 5. Add GitHub Actions Badge (Optional)

Create `.github/workflows/python-app.yml` for CI:

```yaml
name: Python CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    - name: Lint with flake8
      run: |
        pip install flake8
        flake8 src/ app.py --count --select=E9,F63,F7,F82 --show-source --statistics
```

## Interview Demonstration URL

Share this with Rabobank:
```
https://github.com/YOUR-USERNAME/ai-sentinel
```

## Quick Demo Commands for Interview

If they want to see it running live:

```powershell
# Clone and run in 3 commands
git clone https://github.com/YOUR-USERNAME/ai-sentinel.git
cd ai-sentinel
pip install -r requirements.txt

# Create .env file
echo "OPENAI_API_KEY=your-key-here" > .env

# Run the app
streamlit run app.py
```

## Professional GitHub Profile Touches

### Add a .github/FUNDING.yml (Optional)
Shows you understand open-source best practices.

### Add CONTRIBUTING.md (Optional)
Even for a demo, shows you think about collaboration.

### Pin the Repository
1. Go to your GitHub profile
2. Click "Customize your pins"
3. Select `ai-sentinel`
4. This will feature it prominently

## Deployment Options to Share

### Option 1: Streamlit Cloud (Free & Easy)
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Connect your GitHub account
3. Deploy from `ai-sentinel` repository
4. Share the public URL with interviewers

**Benefits**: 
- Live demo without them needing to run locally
- Shows deployment skills
- Professional presentation

### Option 2: Docker Hub (Advanced)
```powershell
# Create Dockerfile (included in Phase 2)
docker build -t your-username/ai-sentinel:v1.0.0 .
docker push your-username/ai-sentinel:v1.0.0
```

## README Badges to Add

After setting up, add these to your README:

```markdown
[![GitHub stars](https://img.shields.io/github/stars/YOUR-USERNAME/ai-sentinel)](https://github.com/YOUR-USERNAME/ai-sentinel/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/YOUR-USERNAME/ai-sentinel)](https://github.com/YOUR-USERNAME/ai-sentinel/network)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
```

## Interview Talking Points

When sharing the GitHub repo, highlight:

1. **Rapid Development**: "Built working PoC in under 1 hour"
2. **Clean Code**: "Well-structured, modular, documented"
3. **Production-Ready**: "Architecture designed for scale"
4. **Business Value**: "Measurable impact on security and compliance"
5. **Developer Experience**: "Simple setup, clear documentation"

## Next Steps After Interview

If they're impressed and want to see more:

```powershell
# Create a feature branch for Phase 2
git checkout -b feature/phase2-agents

# Implement Phase 2 features
# (LangGraph, webhooks, etc.)

# Push and create PR
git push origin feature/phase2-agents
```

---

**You're ready to showcase! 🚀**

Remember: The goal is to demonstrate your "Rapid Builder Mindset" and ability to deliver value quickly.
