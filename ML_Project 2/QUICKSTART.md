# Quick Start Guide

Get up and running in 5 minutes!

## Option 1: Automated Setup (Recommended)

Run the automated setup script:

```bash
chmod +x setup.sh
./setup.sh
```

Then follow the on-screen instructions.

## Option 2: Manual Setup

### Step 1: Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # On Mac/Linux
# OR
venv\Scripts\activate     # On Windows

# Install dependencies
pip3 install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env  # Add your OPENAI_API_KEY
```

### Step 2: Frontend Setup

```bash
cd frontend

# Install dependencies
npm install
```

### Step 3: Run the Application

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

### Step 4: Access the App

Open your browser and navigate to:
- **Frontend:** http://localhost:5173
- **API Docs:** http://localhost:8000/docs

## Getting Your OpenAI API Key

1. Go to https://platform.openai.com/
2. Sign up or log in
3. Navigate to "API keys" in your account settings
4. Click "Create new secret key"
5. Copy the key (starts with `sk-`)
6. Add it to `backend/.env`:
   ```
   OPENAI_API_KEY=sk-your-key-here
   ```

## First Time Running

**Note:** The first time you run the backend, it will download Stable Diffusion models (~5GB). This takes 5-10 minutes. Subsequent starts are much faster.

## Troubleshooting

### "pip: command not found"
Use `pip3` instead of `pip`:
```bash
pip3 install -r requirements.txt
```

### "python: command not found"
Use `python3`:
```bash
python3 main.py
```

### Backend won't start
- Check if port 8000 is available
- Ensure your OpenAI API key is set in `.env`
- Check logs for specific error messages

### Frontend won't connect
- Make sure backend is running on port 8000
- Check browser console for errors
- Clear browser cache

### Models loading forever
- First load takes 5-10 minutes
- Ensure you have ~5GB free disk space
- Check GPU availability (optional but faster)

## Testing It Works

### Test 1: Health Check
```bash
curl http://localhost:8000/api/health
```

Should return: `{"status":"healthy","models_loaded":true}`

### Test 2: Generate Image
Use the frontend at http://localhost:5173 or test via API docs at http://localhost:8000/docs

## What's Next?

1. **Try Image Mode:** Generate single images with AI-enhanced prompts
2. **Try Storybook Mode:** Create multi-panel visual stories
3. **Experiment with Styles:** Try different art styles (anime, watercolor, etc.)
4. **Use Revision:** Refine images with the feedback system

## Need Help?

- Check the main [README.md](README.md) for detailed documentation
- Review API docs at http://localhost:8000/docs
- Check backend logs for error messages
- Verify environment variables in `.env`

---

**Happy Creating! <¨**
