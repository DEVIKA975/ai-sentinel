# 🚀 AI Sentinel Quick Start Guide: Ghost AI Detection

This guide will get you from zero to running AI Sentinel in **5 minutes**.

## Prerequisites

- Python 3.10 or higher
- OpenAI API key ([get one here](https://platform.openai.com/api-keys))
- Git (optional)

## Step 1: Get the Code

### Option A: Clone from GitHub
```powershell
git clone https://github.com/YOUR-USERNAME/ai-sentinel.git
cd ai-sentinel
```

### Option B: Already have the folder?
```powershell
cd C:\Users\devik\Desktop\rabodemo
```

## Step 2: Install Dependencies

```powershell
# Create a virtual environment (recommended)
python -m venv .venv

# Activate it
.\.venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

**Expected output**: Should see packages like `streamlit`, `openai`, `pandas` installing.

## Step 3: Configure Environment

```powershell
# Copy the example environment file
copy .env.example .env

# Edit .env with your API key
notepad .env
```

**Edit this line** in `.env`:
```
OPENAI_API_KEY=your_openai_api_key_here
```

Replace `your_openai_api_key_here` with your actual OpenAI API key.

## Step 4: Run the Application

```powershell
streamlit run app.py
```

**Expected output**:
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.1.x:8501
```

Your browser should automatically open to the application!

## Step 5: Try the Demo

1. In the sidebar, **check "Use sample logs"** (should already be checked)
2. Click the big **"🔍 Analyze Ghost AI Threats"** button
3. Wait 10-30 seconds for GPT-4 to analyze the logs
4. Explore the dashboard!

## Troubleshooting

### "OPENAI_API_KEY not found"
- Make sure you created a `.env` file (not `.env.example`)
- Make sure there are no spaces around the `=` sign
- Restart the Streamlit app after creating `.env`

### "Module not found"
```powershell
# Make sure you activated the virtual environment
.\.venv\Scripts\activate

# Reinstall requirements
pip install -r requirements.txt
```

### Port 8501 already in use
```powershell
# Kill any existing Streamlit processes
Get-Process | Where-Object {$_.ProcessName -eq "streamlit"} | Stop-Process

# Or use a different port
streamlit run app.py --server.port=8502
```

### Import errors (can't find `src.detector`)
Make sure you're running from the project root directory:
```powershell
# Should show app.py, src/, data/, etc.
ls

# If not, navigate to the right folder
cd C:\Users\devik\Desktop\rabodemo
```

## Next Steps

### 1. Upload Your Own Logs
Create a JSON file with this format:
```json
[
  {
    "timestamp": "2026-02-12T10:15:23Z",
    "user_id": "user@the Organization.nl",
    "department": "Engineering",
    "request_url": "https://chat.openai.com/api/conversation",
    "request_method": "POST",
    "payload_size_kb": 12,
    "payload_snippet": "Your payload here",
    "user_agent": "Mozilla/5.0",
    "ip_address": "10.20.30.45"
  }
]
```

Upload via the sidebar.

### 2. Customize Policies
Edit `src/policies.py` to add:
- Your organization's approved AI domains
- Custom sensitive data patterns
- Department-specific risk levels

### 3. Adjust Risk Thresholds
Edit `.env`:
```
RISK_THRESHOLD_HIGH=75    # Score above this = high risk
RISK_THRESHOLD_MEDIUM=40  # Score above this = medium risk
```

## Development Mode

To make changes and see them live:

```powershell
# Install dev dependencies (optional)
pip install black flake8 pytest

# Format code
black src/ app.py

# Run linter
flake8 src/ app.py
```

## Deployment Options

### Deploy to Streamlit Cloud (Free)
1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repo
4. Add your `OPENAI_API_KEY` in the secrets
5. Deploy!

### Run in Docker
```powershell
# Build image (requires Dockerfile - Phase 2)
docker build -t ai-sentinel .

# Run container
docker run -p 8501:8501 --env-file .env ai-sentinel
```

## Support

- **Documentation**: See `README.md` for full details
- **Architecture**: See `docs/architecture.md` for technical deep-dive
- **GitHub Setup**: See `GITHUB_SETUP.md` for repository configuration

---

**🎉 You're all set! Enjoy using AI Sentinel!**

If you're preparing for the the Organization interview, practice giving a **5-minute demo**:
1. Show the architecture (2 min)
2. Run a live analysis (2 min)
3. Explain business value (1 min)
