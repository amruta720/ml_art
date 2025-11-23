# Ollama Setup Guide

##  What's Done

Ollama has been installed and configured! The project now uses **completely free local AI** instead of OpenAI's paid API.

## ó One More Step: Download the Model

Ollama's registry is temporarily down. Once it's back up (usually within minutes/hours), run:

```bash
ollama pull llama3.2
```

This will download the Llama 3.2 model (~2GB). It's a one-time download.

## =€ Running the Project

### Option 1: Model Download Works

If `ollama pull llama3.2` works:

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
python3 main.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Then visit: **http://localhost:5173**

### Option 2: Model Download Still Fails

If Ollama's registry is still down, you can try later with:

```bash
# Check if registry is back
ollama pull llama3.2
```

Or try an alternative model:
```bash
ollama pull mistral    # Smaller, faster
ollama pull phi3       # Even smaller
```

Then update `.env`:
```bash
OLLAMA_MODEL=mistral  # or phi3
```

## = Verify Ollama is Running

```bash
# Check if Ollama service is running
brew services list | grep ollama

# Should show: ollama started

# Test Ollama directly
ollama list  # Shows downloaded models
```

## =¡ Benefits of Ollama

 **100% Free** - No API costs ever
 **Private** - Your prompts stay on your machine
 **Fast** - Runs locally on your Mac
 **No Rate Limits** - Generate unlimited images
 **Works Offline** - No internet needed after setup

## <˜ Troubleshooting

### "Ollama is not running"
```bash
brew services start ollama
```

### "Model not found"
Wait for registry to come back online, then:
```bash
ollama pull llama3.2
```

### Check model download status
```bash
ollama list
```

### Alternative: Download model when starting backend

The app will give you a helpful error if the model isn't downloaded. You can download it anytime before or after starting the backend.

##What Models Can I Use?

Popular models (from smallest to largest):
- `phi3` (3.8GB) - Fastest, good for quick responses
- `llama3.2` (2GB) - Balanced performance
- `mistral` (4.1GB) - Better quality
- `llama3` (4.7GB) - Best quality

Change in `.env`:
```
OLLAMA_MODEL=your_preferred_model
```

---

**Everything else is configured! Just need to download the model when the registry is back.**
