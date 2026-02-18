# AI Sentinel: Ghost AI with Ollama

## Step 1: Install Ollama

### Windows:
1. Download from: https://ollama.com/download/windows
2. Run the installer
3. Ollama will start automatically

### Verify Installation:
```powershell
ollama --version
```

---

## Step 2: Download the Llama 3.2 Model

Open PowerShell and run:

```powershell
ollama pull llama3.2
```

**This will download ~2GB.** Wait for it to complete.

**Alternative models** (if llama3.2 doesn't work):
```powershell
# Smaller, faster (1.3GB)
ollama pull llama3.2:1b

# Larger, more accurate (7.4GB)
ollama pull llama3.1:8b
```

---

## Step 3: Verify Ollama is Running

```powershell
ollama list
```

You should see `llama3.2` in the list.

**Test it:**
```powershell
ollama run llama3.2 "What is Ghost AI?"
```

You should get a response!

---

## Step 4: Install Python Package

```powershell
cd C:\Users\devik\Desktop\rabodemo
pip install ollama
```

---

## Step 5: Verify .env Configuration

Your `.env` file should have:
```
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama3.2
```

---

## Step 6: Restart Streamlit

Stop the current Streamlit app (Ctrl+C) and restart:

```powershell
python -m streamlit run app.py
```

---

## Troubleshooting

### "Connection refused" error
Ollama service isn't running. Restart it:
```powershell
# Check if Ollama is running
Get-Process ollama

# If not, start it from Start Menu or run:
ollama serve
```

### "Model not found"
Run the pull command again:
```powershell
ollama pull llama3.2
```

### To switch back to OpenAI:
Edit `.env`:
```
LLM_PROVIDER=openai
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4o-mini
```

---

## Benefits of Ollama

✅ **100% FREE** - No API costs ever  
✅ **Privacy** - All data stays on your computer  
✅ **Offline** - Works without internet  
✅ **No rate limits** - Use as much as you want  

The only cost is disk space (~2-7GB for models) and compute time (slower on older computers).

---

**Ready to test!** Once Ollama is installed and the model is downloaded, restart your Streamlit app and try the analysis! 🚀
