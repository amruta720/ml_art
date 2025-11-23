# Asset System - Reference Images for Story Generation

## Overview

The **Asset System** allows users to upload reference images/files that **influence storybook generation**. Uploaded assets can be used as:

- **Style references** - Define the visual aesthetic (e.g., watercolor painting style)
- **Character references** - Ensure consistent character appearance across all pages
- **Story sources** - Inspire story themes and content
- **Base images** - Use as starting point for image-to-image generation

---

## How It Works

### Upload Flow

1. **User uploads an image** via the frontend
2. **Backend stores the file** in `static/assets/` with a unique ID
3. **Asset metadata is registered** with usage type and optional description
4. **Asset ID is attached** to story generation requests
5. **LLM agents receive asset context** in their prompts
6. **Image generation uses references** for style/character consistency

### Asset Influence Points

**Phase 1 (Story Draft)**
- Asset descriptions influence story themes and character descriptions
- Style references inform visual planning

**Phase 2 (Text Generation)**
- Asset context helps maintain consistency with visual references
- Character descriptions align with uploaded character images

**Phase 3 (Art Generation)**
- Asset context included in art prompt generation
- Reference images used for image-to-image generation
- Ensures visual consistency across all pages

---

## Backend Implementation

### Data Models

**`models/schemas.py`**

```python
class AssetUsage(str, Enum):
    STYLE = "style"              # Visual style reference
    CHARACTER = "character"       # Character appearance reference
    STORY_SOURCE = "story_source" # Story theme inspiration
    BASE_IMAGE = "base_image"     # Image-to-image base

class StoryAsset(BaseModel):
    id: str                    # Unique identifier
    url: str                   # Relative path to file
    filename: str              # Original filename
    mime_type: str             # MIME type (e.g., 'image/png')
    usage: AssetUsage          # How to use this asset
    description: Optional[str] # User-provided description
```

### Asset Manager Service

**`services/asset_manager.py`**

Manages asset storage and retrieval:

```python
# Register a new asset
asset = asset_manager.register_asset(
    file_path=path,
    filename="elephant.png",
    mime_type="image/png",
    usage=AssetUsage.CHARACTER,
    description="Small brown elephant with big ears"
)

# Get assets by ID
assets = asset_manager.get_assets(["asset-id-1", "asset-id-2"])

# Build text context for LLM prompts
context = asset_manager.build_asset_context(asset_ids)
# Returns formatted string like:
# "CHARACTER REFERENCES:
#  - Small brown elephant with big ears"

# Get image paths for image-to-image generation
image_paths = asset_manager.get_image_asset_paths(asset_ids)
```

### API Endpoints

#### Upload Asset
```http
POST /api/upload-asset
Content-Type: multipart/form-data

file: <image file>
usage: "style" | "character" | "story_source" | "base_image"
description: "Optional description"

Response:
{
  "asset": {
    "id": "uuid",
    "url": "/static/assets/uuid.png",
    "filename": "elephant.png",
    "mime_type": "image/png",
    "usage": "character",
    "description": "Small brown elephant"
  },
  "message": "Asset uploaded successfully"
}
```

#### List Assets
```http
GET /api/assets

Response:
[
  { "id": "...", "filename": "...", ... }
]
```

#### Delete Asset
```http
DELETE /api/assets/{asset_id}

Response:
{ "message": "Asset deleted successfully" }
```

### Updated Request Schemas

All generation requests now accept `asset_ids`:

```python
class ThreePhaseStoryRequest(BaseModel):
    story_idea: str
    num_pages: int
    age_range: str = "4-7"
    style: Optional[ImageStyle] = None
    asset_ids: List[str] = []  # ✨ NEW
```

### Agent Integration

**Story Draft Agent** (`agents/story_draft_agent.py`)
```python
def generate_story_outline(
    self,
    story_idea: str,
    num_pages: int,
    asset_context: Optional[str] = None,  # ✨ NEW
) -> dict:
    prompt = f"""Create a {num_pages}-page storybook.

Story Idea: {story_idea}

{asset_context if asset_context else ""}

Generate a complete story outline..."""
```

**Story Art Agent** (`agents/story_art_agent.py`)
```python
def generate_art_prompts(
    self,
    story_title: str,
    characters: List[str],
    pages_data: List[Dict],
    asset_context: Optional[str] = None,  # ✨ NEW
) -> dict:
    prompt = f"""Story: "{story_title}"

Characters: {characters}

{asset_context if asset_context else ""}

Create detailed art prompts..."""
```

### Image-to-Image Generation

**Stability AI Integration** (`services/stability_ai_image.py`)

New method for reference-based generation:

```python
def generate_image_with_reference(
    self,
    prompt: str,
    reference_image_path: Path,
    negative_prompt: Optional[str] = None,
    style_strength: float = 0.6,  # 0.0-1.0, higher = more influence
) -> str:
    # Reads reference image
    # Encodes as base64
    # Calls Stability AI image-to-image endpoint
    # Returns generated image path
```

**Unified Image Service** (`services/unified_image_service.py`)

```python
def generate_image(
    self,
    prompt: str,
    reference_images: Optional[List[Path]] = None,  # ✨ NEW
    ...
) -> str:
    if reference_images:
        # Use image-to-image generation
        return self._generate_with_reference(
            prompt=prompt,
            reference_image=reference_images[0]
        )
    else:
        # Regular text-to-image generation
        ...
```

### 3-Phase Pipeline Integration

**`api/routes.py` - `/generate-storybook-3phase` endpoint**

```python
# Build asset context from IDs
asset_context = None
if request.asset_ids:
    asset_context = asset_manager.build_asset_context(request.asset_ids)

# Phase 1: Pass asset context to story draft agent
story_outline = story_draft_agent.generate_story_outline(
    story_idea=request.story_idea,
    asset_context=asset_context
)

# Phase 3: Get reference images and pass to art agent
reference_images = asset_manager.get_image_asset_paths(request.asset_ids)

art_data = story_art_agent.generate_art_prompts(
    asset_context=asset_context,
    ...
)

# Generate images with references
image_url = unified_image_service.generate_image(
    prompt=art_page["art_prompt"],
    reference_images=reference_images  # ✨ Used for image-to-image
)
```

---

## Frontend Implementation

### Type Definitions

**`frontend/src/types/index.ts`**

```typescript
export enum AssetUsage {
  STYLE = 'style',
  CHARACTER = 'character',
  STORY_SOURCE = 'story_source',
  BASE_IMAGE = 'base_image',
}

export interface StoryAsset {
  id: string;
  url: string;
  filename: string;
  mime_type: string;
  usage: AssetUsage;
  description?: string;
}

// Updated request types include asset_ids
export interface ThreePhaseStoryRequest {
  story_idea: string;
  num_pages: number;
  age_range?: string;
  style?: ImageStyle;
  asset_ids?: string[];  // ✨ NEW
}
```

### API Client

**`frontend/src/services/api.ts`**

```typescript
class ApiClient {
  // Upload an asset
  async uploadAsset(
    file: File,
    usage: AssetUsage = AssetUsage.STYLE,
    description?: string
  ): Promise<UploadAssetResponse> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('usage', usage);
    if (description) formData.append('description', description);

    const response = await fetch('/api/upload-asset', {
      method: 'POST',
      body: formData,
    });
    return response.json();
  }

  // List all assets
  async listAssets(): Promise<StoryAsset[]> {
    return this.request<StoryAsset[]>('/assets');
  }

  // Delete an asset
  async deleteAsset(assetId: string): Promise<{ message: string }> {
    const response = await fetch(`/api/assets/${assetId}`, {
      method: 'DELETE',
    });
    return response.json();
  }
}
```

### AssetUploader Component

**`frontend/src/components/common/AssetUploader.tsx`**

A reusable component for uploading and managing assets:

```typescript
interface AssetUploaderProps {
  onAssetUploaded: (asset: StoryAsset) => void;
  onAssetsChanged: (assets: StoryAsset[]) => void;
  selectedAssets: StoryAsset[];
}

export const AssetUploader: React.FC<AssetUploaderProps> = ({
  onAssetUploaded,
  onAssetsChanged,
  selectedAssets,
}) => {
  // File upload handler
  const handleFileUpload = async (event) => {
    const file = event.target.files?.[0];
    const response = await apiClient.uploadAsset(file, AssetUsage.STYLE);
    onAssetUploaded(response.asset);
  };

  // Displays grid of uploaded assets with preview images
  // Allows removing assets
  // Shows asset filename and usage type
};
```

### StoryGenerator Integration

**`frontend/src/components/StoryMode/StoryGenerator.tsx`**

```typescript
const [selectedAssets, setSelectedAssets] = useState<StoryAsset[]>([]);

// Include AssetUploader in the form
<AssetUploader
  onAssetUploaded={(asset) => setSelectedAssets([...selectedAssets, asset])}
  onAssetsChanged={setSelectedAssets}
  selectedAssets={selectedAssets}
/>

// Pass asset IDs to generation request
const response = await apiClient.generateStorybook3Phase({
  story_idea: storyIdea,
  num_pages: numPanels,
  asset_ids: selectedAssets.map(a => a.id),  // ✨ Attach assets
});
```

---

## Usage Examples

### Example 1: Style Reference

**User uploads** a watercolor painting

**Asset registered as**:
```json
{
  "usage": "style",
  "description": "Soft watercolor painting with pastel colors"
}
```

**Result**: All generated images use watercolor style with similar color palette

### Example 2: Character Reference

**User uploads** an image of an elephant character

**Asset registered as**:
```json
{
  "usage": "character",
  "description": "Small brown elephant with big floppy ears, wearing a red scarf"
}
```

**LLM receives context**:
```
CHARACTER REFERENCES:
- Small brown elephant with big floppy ears, wearing a red scarf
```

**Result**:
- Story outline includes matching character description
- All generated images show the same elephant appearance
- Image-to-image generation uses the reference for consistency

### Example 3: Multiple Assets

**User uploads**:
1. Watercolor landscape (style reference)
2. Elephant drawing (character reference)

**Asset context sent to LLM**:
```
VISUAL STYLE REFERENCES:
- Soft watercolor landscape with gentle colors

CHARACTER REFERENCES:
- Small brown elephant with big floppy ears
```

**Image generation**:
- Uses watercolor landscape as style reference (image-to-image)
- LLM art prompts mention the elephant description
- All pages have consistent style and character

---

## Technical Details

### Storage

- **Directory**: `backend/static/assets/`
- **Filename format**: `{uuid}.{extension}` (e.g., `a1b2c3d4.png`)
- **Access**: Via relative URL `/static/assets/{filename}`

### Asset Registry

Currently **in-memory** (stored in `AssetManager._assets` dict)

**For production**, should use:
- Database (PostgreSQL, MongoDB)
- Persistent storage (S3, cloud storage)
- Asset cleanup/expiration policies

### Image-to-Image Support

**Stability AI**: ✅ Supported via `/v1/generation/{model}/image-to-image` endpoint

**Local Stable Diffusion**: ⚠️ Not currently supported (would require additional implementation)

**Gemini/Imagen**: ⚠️ Not currently supported

### Limitations

1. **Single reference per generation**: Currently uses first asset for image-to-image
2. **In-memory storage**: Assets lost on server restart
3. **No asset validation**: Doesn't verify image quality/resolution
4. **No deduplication**: Same image uploaded multiple times creates multiple assets

---

## Future Enhancements

### Asset Management
- [ ] Persistent database storage
- [ ] Asset tagging and search
- [ ] Asset collections/libraries
- [ ] Automatic thumbnail generation
- [ ] Image preprocessing (resize, optimize)

### Generation Features
- [ ] Multi-asset blending (combine multiple style references)
- [ ] Per-page asset assignment (different references per page)
- [ ] Asset weight/influence control (slider for reference strength)
- [ ] Character sheet support (multiple poses of same character)

### User Experience
- [ ] Drag-and-drop upload
- [ ] Asset preview modal
- [ ] Batch upload
- [ ] Asset usage analytics
- [ ] Recommended assets based on story idea

### Advanced Features
- [ ] ControlNet integration for pose/composition control
- [ ] Automatic character extraction from images
- [ ] Style transfer learning
- [ ] Asset versioning

---

## Testing the Asset System

### Test Flow

1. **Start the backend**:
   ```bash
   cd backend
   python main.py
   ```

2. **Open frontend**: Navigate to http://localhost:5173

3. **Go to Story Mode**

4. **Upload a reference image**:
   - Click "Upload Reference Images"
   - Select an image (e.g., watercolor painting, character drawing)
   - Image appears in the assets grid

5. **Generate a story**:
   - Enter story idea: "an elephant learning to paint"
   - Select 8 pages, watercolor style
   - Click "Generate Storybook"

6. **Observe the influence**:
   - Check backend logs for "Using X asset(s) for context"
   - Phase 1: Story outline should reference uploaded asset style
   - Phase 3: Images should reflect the reference style/character

### Example Backend Logs

```
INFO: Uploading asset: elephant_character.png, usage: character
INFO: File saved to: static/assets/uuid.png
INFO: Asset registered: uuid (elephant_character.png)
INFO: Starting 3-phase story generation: 'elephant learning to paint' (8 pages)
INFO: Using 1 asset(s) for context
INFO: Phase 1: Generating story outline...
INFO: Phase 3: Generating art prompts and images...
INFO: Using 1 reference image(s) for generation
INFO: Generating image with reference: static/assets/uuid.png
```

---

## Troubleshooting

### Asset upload fails

**Problem**: "Asset upload failed: File type not specified"
- **Solution**: Ensure file has valid MIME type, use common image formats (PNG, JPG, WEBP)

### Reference images not influencing generation

**Problem**: Generated images don't match uploaded reference
- **Check**: Backend logs show "Using X asset(s) for context"
- **Verify**: IMAGE_BACKEND=stability_ai (image-to-image requires Stability AI)
- **Adjust**: Asset description should be clear and detailed

### Images look nothing like reference

**Problem**: Style strength too low
- **Solution**: Adjust `style_strength` in `unified_image_service.py` (line 154)
- Default is 0.6, try 0.7-0.8 for stronger influence

---

**Happy creating with reference-influenced storybooks!** 🎨📚
