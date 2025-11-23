# Three-Phase Storybook Pipeline

## Overview

The three-phase pipeline creates **professional children's storybooks** similar to real published books, with a complete narrative structure, flowing text, dialogues, and consistent illustrations.

---

## How It Works

### Phase 1: Story Draft & Outline ✏️
**Agent**: `story_draft_agent.py`

Generates the complete story structure:
- **Story title** and one-sentence logline
- **Character descriptions** (maintained consistently across all pages)
- **Page-by-page outlines** with:
  - Page title
  - Story outline point (what happens)
  - Scene description (visual setting for illustration)

**Output**: Story skeleton with structure but no detailed text yet.

---

### Phase 2: Text & Dialogues 💬
**Agent**: `story_text_agent.py`

Takes the outline and generates:
- **Flowing narration** (1-3 paragraphs per page)
- **Character dialogues** (natural, age-appropriate conversations)
- Maintains **character voice consistency**
- Uses **age-appropriate vocabulary**

**Output**: Complete text content ready for illustration.

---

### Phase 3: Art Prompts & Image Generation 🎨
**Agent**: `story_art_agent.py`

Creates detailed art prompts and generates images:
- **Positive prompts** with:
  - Character descriptions (consistent across pages)
  - Setting and composition
  - Mood and lighting
  - Art style keywords
- **Negative prompts** (what to avoid)
- **Calls image generation service** for each page

**Output**: Complete storybook with all illustrations.

---

## API Endpoint

### `POST /api/generate-storybook-3phase`

**Request**:
```json
{
  "story_idea": "an elephant who loves painting rainbows",
  "num_pages": 8,
  "age_range": "4-7",
  "style": "watercolor"
}
```

**Response**:
```json
{
  "storybook": {
    "id": "unique-id",
    "meta": {
      "title": "Ellie's Rainbow Adventure",
      "logline": "A young elephant discovers the joy of painting.",
      "age_range": "4-7",
      "style_preset": "watercolor",
      "characters": ["Ellie: A small elephant with big dreams", ...]
    },
    "pages": [
      {
        "page_number": 1,
        "title": "A Curious Discovery",
        "outline": "Ellie finds a paintbrush in the forest",
        "scene_description": "Forest clearing with sunlight",
        "narration": "One sunny morning, Ellie...",
        "dialogues": [
          {"speaker": "Ellie", "text": "What's this colorful stick?"}
        ],
        "art_prompt": "Small elephant...",
        "negative_prompt": "scary, dark...",
        "image_url": "/static/images/..."
      }
    ]
  },
  "total_generation_time": 45.2,
  "phase_times": {
    "phase_1_outline": 5.3,
    "phase_2_text": 8.1,
    "phase_3_art": 31.8
  }
}
```

---

## Frontend Integration

### Toggle in Story Mode

Users can choose between two modes:

1. **Quick Storyboard Mode** (original)
   - 2-12 panels
   - Basic structure
   - Faster generation

2. **3-Phase Professional Mode** (new)
   - 4-16 pages
   - Complete narrative
   - Character consistency
   - Age-range targeting
   - Professional layout

### StoryBookViewer Component

Displays storybooks in **real children's book format**:

```
┌─────────────────────┬─────────────────────┐
│                     │                     │
│   [Image]           │   Title             │
│                     │                     │
│   Full-page         │   Narration:        │
│   illustration      │   "Once upon..."    │
│                     │                     │
│   Page 1            │   Dialogues:        │
│                     │   Character: "..."  │
│                     │                     │
│                     │   Page 1            │
└─────────────────────┴─────────────────────┘
```

**Left page**: Full illustration
**Right page**: Title, narration, dialogues

---

## File Structure

### Backend
```
backend/
├── agents/
│   ├── story_draft_agent.py    # Phase 1: Outline
│   ├── story_text_agent.py     # Phase 2: Text
│   └── story_art_agent.py      # Phase 3: Art
├── models/
│   └── schemas.py              # StoryBook, StoryPage, StoryMeta
└── api/
    └── routes.py               # /generate-storybook-3phase endpoint
```

### Frontend
```
frontend/src/
├── components/StoryMode/
│   ├── StoryGenerator.tsx      # Updated with 3-phase toggle
│   └── StoryBookViewer.tsx     # New book-format display
├── types/
│   └── index.ts                # StoryBook types
└── services/
    └── api.ts                  # generateStorybook3Phase()
```

---

## Example Usage

### User Flow

1. User clicks **"Use 3-Phase Pipeline"** checkbox
2. Enters story idea: *"an elephant who loves painting rainbows"*
3. Selects 8 pages, age range 4-7, watercolor style
4. Clicks **"Generate Storybook"**
5. System shows progress:
   - "Phase 1: Creating story outline..."
   - "Phase 2: Generating narration and dialogues..."
   - "Phase 3: Generating art prompts and images..."
6. Complete storybook appears in book format
7. User can print or create a new story

---

## Key Features

### ✅ Professional Quality
- Complete narrative arc
- Consistent characters
- Age-appropriate content
- Flowing prose

### ✅ Visual Consistency
- Characters look the same across pages
- Consistent art style
- Proper composition

### ✅ Educational Value
- Teaches story structure
- Age-appropriate vocabulary
- Moral lessons (optional)

### ✅ Print-Ready
- Book-format layout
- High-quality images
- Printable design

---

## Configuration

All three agents use **Ollama** (local LLM) for text generation and the **unified image service** for illustrations (supports Stability AI, local Stable Diffusion, or Gemini).

### Environment Variables
```bash
# Story generation (uses Ollama)
OLLAMA_MODEL=llama3.2
OLLAMA_HOST=http://localhost:11434

# Image generation (choose one)
IMAGE_BACKEND=stability_ai
STABILITY_API_KEY=sk-your-key-here
```

---

## Benefits Over Original Storyboard Mode

| Feature | Original Mode | 3-Phase Mode |
|---------|--------------|--------------|
| Structure | Basic panels | Full book structure |
| Text | Simple descriptions | Flowing narration + dialogue |
| Characters | Inconsistent | Named & consistent |
| Planning | Direct generation | 3-phase refinement |
| Age targeting | Generic | Specific age ranges |
| Output format | Grid of panels | Book-style spreads |
| Professional quality | Good | Excellent |

---

## Future Enhancements

Potential additions:
- PDF export for 3-phase storybooks
- Interactive editing of outlines before text generation
- Character customization (appearance, personality)
- Theme/moral selection
- Multi-language support
- Voice narration generation

---

**Enjoy creating professional children's storybooks!** 📚✨
