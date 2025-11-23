# Agentic AI Art Generator & Storybook Editor

A complete monorepo project featuring an **AI-powered image generator** and **storybook creator** using **Stable Diffusion**, **FastAPI**, **React**, and **3 specialized LLM agents**.

## Features

### Image Mode
- Generate single images from text prompts
- AI-powered **Prompt Stylist Agent** enhances your prompts
- Multiple art styles (realistic, anime, fantasy, watercolor, etc.)
- **Revision Agent** helps refine images based on feedback
- View enhanced prompts and generation metadata

### Storybook Mode
- Create multi-panel visual stories (2-12 panels)
- **Storyboard Agent** crafts coherent narratives
- Consistent style across all panels
- Print-ready storybook output
- Auto-generated story titles and descriptions

### AI Agents
1. **Prompt Stylist Agent**: Enhances prompts with rich visual details
2. **Storyboard Agent**: Creates compelling story narratives
3. **Revision Agent**: Refines images based on user feedback

## Tech Stack

### Backend
- **Python 3.9+**
- **FastAPI** - Modern async web framework
- **Stable Diffusion** - Image generation (diffusers library)
- **OpenAI GPT-4** - LLM agents
- **Pydantic** - Data validation

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **CSS3** - Styling with gradients and animations

## Project Structure

```
Project/
├── backend/
│   ├── agents/
│   │   ├── base_agent.py
│   │   ├── prompt_stylist_agent.py
│   │   ├── storyboard_agent.py
│   │   └── revision_agent.py
│   ├── api/
│   │   └── routes.py
│   ├── core/
│   │   └── exceptions.py
│   ├── models/
│   │   └── schemas.py
│   ├── services/
│   │   └── image_generator.py
│   ├── static/
│   │   └── images/
│   ├── config.py
│   ├── main.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ImageMode/
│   │   │   ├── StoryMode/
│   │   │   └── common/
│   │   ├── services/
│   │   │   └── api.ts
│   │   ├── types/
│   │   │   └── index.ts
│   │   ├── App.tsx
│   │   ├── App.css
│   │   └── main.tsx
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── index.html
└── README.md
```

## Installation & Setup

### Prerequisites

- **Python 3.9+**
- **Node.js 18+** and npm
- **CUDA-capable GPU** (recommended) or CPU
- **OpenAI API Key** (for LLM agents)

### Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**:
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

5. **Run the backend**:
   ```bash
   python main.py
   ```

   The API will start at `http://localhost:8000`
   - API docs: `http://localhost:8000/docs`
   - Health check: `http://localhost:8000/api/health`

   **Note**: First startup will download Stable Diffusion models (~5GB). This may take several minutes.

### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Run development server**:
   ```bash
   npm run dev
   ```

   The app will open at `http://localhost:5173`

4. **Build for production** (optional):
   ```bash
   npm run build
   ```

## Usage

### Image Mode

1. Navigate to the app at `http://localhost:5173`
2. Click **"Image Mode"**
3. Enter your image description (e.g., "a serene mountain lake at sunset")
4. Select a style (optional)
5. Keep "Use AI Prompt Stylist" checked (recommended)
6. Click **"Generate Image"**
7. View your generated image with metadata
8. Use the revision feature to refine the image

### Storybook Mode

1. Click **"Storybook Mode"**
2. Enter your story idea (e.g., "a robot learning to paint")
3. Choose number of panels (2-12)
4. Select a consistent style
5. Click **"Generate Storybook"**
6. Wait for all panels to generate
7. Print or save your storybook

## API Endpoints

### Health Check
```
GET /api/health
```

### Image Mode
```
POST /api/image-mode
Body: {
  "prompt": "string",
  "style": "realistic" | "artistic" | etc,
  "enhance_prompt": true
}
```

### Story Mode
```
POST /api/story-mode
Body: {
  "story_idea": "string",
  "num_panels": 4,
  "style": "digital art"
}
```

### Revision
```
POST /api/revise
Body: {
  "original_prompt": "string",
  "feedback": "string",
  "style": "realistic"
}
```

## Configuration

### Backend Configuration (config.py)

- `OPENAI_API_KEY`: Your OpenAI API key
- `LLM_MODEL`: GPT model to use (default: gpt-4-turbo-preview)
- `STABLE_DIFFUSION_MODEL`: SD model (default: stabilityai/stable-diffusion-2-1)
- `STATIC_DIR`: Image storage directory
- `MAX_IMAGE_SIZE`: Maximum image dimension

### Frontend Configuration (vite.config.ts)

- API proxy configured for `/api` and `/static`
- Development server port: 5173

## Example Prompts

### Image Mode
- "a serene mountain lake at sunset"
- "a futuristic cyberpunk city at night"
- "a magical forest with glowing mushrooms"
- "a steampunk robot reading a book"

### Storybook Mode
- "a robot learning to paint"
- "a cat's adventure in space"
- "the journey of a lonely cloud"
- "a wizard's first day at magic school"

## Troubleshooting

### Backend Issues

**Models not loading**:
- Ensure you have enough disk space (~5GB for SD models)
- Check CUDA availability: `python -c "import torch; print(torch.cuda.is_available())"`
- First load takes 5-10 minutes

**OpenAI API errors**:
- Verify your API key in `.env`
- Check your OpenAI account has credits
- Ensure `OPENAI_API_KEY` is set correctly

**Image generation fails**:
- Check GPU memory (needs ~4GB VRAM)
- Reduce image size in config if OOM errors occur
- CPU generation is slower but works

### Frontend Issues

**Cannot connect to backend**:
- Ensure backend is running on port 8000
- Check CORS settings in `main.py`
- Verify proxy configuration in `vite.config.ts`

**TypeScript errors**:
- Run `npm install` to install dependencies
- Errors about missing React types are expected until dependencies are installed

## Performance Tips

1. **GPU Acceleration**: Use CUDA-enabled GPU for 10x faster generation
2. **Model Caching**: Models load once and stay in memory
3. **Batch Generation**: Story mode generates all panels sequentially
4. **Prompt Optimization**: AI agents automatically optimize prompts

## Development

### Adding New Agents

1. Create new agent in `backend/agents/`
2. Extend `BaseAgent` class
3. Implement `process()` method
4. Add to routes in `backend/api/routes.py`

### Adding New Styles

1. Update `ImageStyle` enum in `backend/models/schemas.py`
2. Update frontend types in `frontend/src/types/index.ts`
3. Styles will appear automatically in dropdown

## Security Notes

- API keys are stored in `.env` (never commit!)
- Frontend uses proxy to avoid CORS issues
- Static files served securely by FastAPI
- Input validation with Pydantic schemas

## Production Deployment

### Backend
```bash
pip install gunicorn
gunicorn backend.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

### Frontend
```bash
npm run build
# Serve the dist/ folder with nginx or any static server
```

## License

MIT License - Free for personal and commercial use

## Credits

- **Stable Diffusion** by Stability AI
- **FastAPI** by Sebastián Ramírez
- **React** by Meta
- **OpenAI** GPT models

## Support

For issues or questions:
- Check API docs at `/docs`
- Review error messages in browser console
- Verify environment configuration
- Ensure all dependencies are installed

---

**Built with love using FastAPI, React, Stable Diffusion, and AI Agents**
