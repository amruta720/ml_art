# Quick Setup Guide

## Option 1: Using Local Stable Diffusion (Default)

This is the default configuration. No additional setup required!

```bash
# Backend
cd backend
pip install -r requirements.txt
python main.py

# Frontend (in another terminal)
cd frontend
npm install
npm run dev
```

Visit: http://localhost:5173

---

## Option 2: Using Google Gemini/Imagen

### Step 1: Get API Key
1. Visit https://makersuite.google.com/app/apikey
2. Create API key
3. Copy it

### Step 2: Configure Backend

Create `backend/.env`:
```bash
IMAGE_BACKEND=gemini_imagen
GEMINI_API_KEY=your_api_key_here
```

### Step 3: Install Dependencies
```bash
cd backend
pip install google-generativeai reportlab
```

### Step 4: Run
```bash
# Backend
python main.py

# Frontend (in another terminal)
cd ../frontend
npm run dev
```

---

## New Features Quick Reference

### 1. Download Images (Multiple Formats)
- **Location**: Image Mode or Storybook panels
- **Formats**: PNG, JPG, WEBP
- **How**: Select format → Click "⬇ Download"

### 2. Download Storybook as PDF
- **Location**: Storybook Mode (after generation)
- **How**: Click "📥 Download Storybook (PDF)"
- **Contains**: Full storybook with images, narration, and dialogue

### 3. Inline Text Editing
- **Location**: Any storybook panel
- **How**:
  1. Click "✏️ Edit" next to narration or dialogue
  2. Type what you want to change (e.g., "make it more exciting")
  3. Click "Apply"
- **Powered by**: Local Ollama LLM

---

## Environment Variables Reference

### Required for All Setups
```bash
# Ollama (for AI agents)
OLLAMA_MODEL=llama3.2
OLLAMA_HOST=http://localhost:11434
```

### For Gemini Backend (Optional)
```bash
IMAGE_BACKEND=gemini_imagen
GEMINI_API_KEY=your_key_here
```

### For Local Diffusion (Default)
```bash
IMAGE_BACKEND=local_diffusion
STABLE_DIFFUSION_MODEL=runwayml/stable-diffusion-v1-5
```

---

## Prerequisites

### Required for Both Options
- Python 3.8+
- Node.js 16+
- Ollama (running locally)
  ```bash
  ollama serve
  ollama pull llama3.2
  ```

### For Local Stable Diffusion
- ~5GB disk space for model
- GPU recommended (CUDA support) but CPU works

### For Gemini
- Internet connection
- Valid Google API key

---

## Quick Test

After setup, try:

1. **Image Mode**:
   - Prompt: "a cute robot painting a picture"
   - Click Generate
   - Download as JPG

2. **Storybook Mode**:
   - Idea: "a mouse who loves cheese"
   - Panels: 4
   - Generate
   - Edit dialogue with AI
   - Download as PDF

---

## Troubleshooting

**Images not generating?**
- Check if models are loaded: Visit http://localhost:8000/api/health
- Status should show `"models_loaded": true`

**Ollama errors?**
- Make sure Ollama is running: `ollama serve`
- Check model is downloaded: `ollama pull llama3.2`

**Frontend not connecting?**
- Backend must be running on port 8000
- Frontend runs on port 5173
- Check CORS is enabled (it is by default)

---

## What's New?

All these features work with **both** Stable Diffusion and Gemini backends:

✅ Enhanced storybooks with dialogue and narration
✅ Multi-format image downloads (PNG/JPG/WEBP)
✅ PDF storybook export
✅ Inline AI text editing
✅ Improved storybook image prompts
✅ Better child-friendly content generation

See [FEATURES.md](FEATURES.md) for detailed documentation.

---

**Ready to create amazing stories!** 🎨📚✨
