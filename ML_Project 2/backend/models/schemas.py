"""Pydantic models for request/response validation."""
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class ImageStyle(str, Enum):
    """Available image styles."""
    REALISTIC = "realistic"
    ARTISTIC = "artistic"
    ANIME = "anime"
    FANTASY = "fantasy"
    SCIFI = "sci-fi"
    WATERCOLOR = "watercolor"
    OIL_PAINTING = "oil painting"
    DIGITAL_ART = "digital art"


class ImageModeRequest(BaseModel):
    """Request model for single image generation."""
    prompt: str = Field(..., description="User's image description")
    style: Optional[ImageStyle] = Field(None, description="Desired image style")
    enhance_prompt: bool = Field(True, description="Use Prompt Stylist Agent")
    asset_ids: List[str] = Field(default_factory=list, description="List of asset IDs to use as references")

    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "a serene mountain lake at sunset",
                "style": "realistic",
                "enhance_prompt": True,
                "asset_ids": []
            }
        }


class ImageModeResponse(BaseModel):
    """Response model for single image generation."""
    image_url: str = Field(..., description="URL to generated image")
    original_prompt: str = Field(..., description="Original user prompt")
    enhanced_prompt: str = Field(..., description="AI-enhanced prompt")
    style_applied: Optional[str] = Field(None, description="Style used")
    generation_time: float = Field(..., description="Time taken in seconds")


class DialogueLine(BaseModel):
    """A single line of dialogue in a story panel."""
    speaker: str = Field(..., description="Character speaking")
    text: str = Field(..., description="What the character says")


class StoryPanel(BaseModel):
    """A single panel in a storybook."""
    panel_number: int = Field(..., description="Panel sequence number")
    title: str = Field(..., description="Panel title/heading")
    narration: str = Field(..., description="Narrative text for this panel")
    dialogues: List[DialogueLine] = Field(default_factory=list, description="Dialogue lines")
    scene_description: str = Field(..., description="Visual scene description")
    image_prompt: str = Field(..., description="Generated image prompt for illustration")
    image_url: Optional[str] = Field(None, description="Generated image URL")


class StoryModeRequest(BaseModel):
    """Request model for storybook generation."""
    story_idea: str = Field(..., description="Story concept or theme")
    num_panels: int = Field(4, ge=2, le=12, description="Number of panels (2-12)")
    style: Optional[ImageStyle] = Field(None, description="Consistent visual style")
    asset_ids: List[str] = Field(default_factory=list, description="List of asset IDs to influence the story")

    class Config:
        json_schema_extra = {
            "example": {
                "story_idea": "a robot learning to paint",
                "num_panels": 4,
                "style": "digital art",
                "asset_ids": []
            }
        }


class StoryModeResponse(BaseModel):
    """Response model for storybook generation."""
    story_title: str = Field(..., description="Generated story title")
    panels: List[StoryPanel] = Field(..., description="Story panels with images")
    style_applied: Optional[str] = Field(None, description="Style used")
    total_generation_time: float = Field(..., description="Total time in seconds")


class RevisionRequest(BaseModel):
    """Request model for image revision."""
    original_prompt: str = Field(..., description="Original prompt")
    feedback: str = Field(..., description="User feedback for revision")
    style: Optional[ImageStyle] = Field(None, description="Desired style")

    class Config:
        json_schema_extra = {
            "example": {
                "original_prompt": "a serene mountain lake at sunset",
                "feedback": "make it more dramatic with stormy clouds",
                "style": "realistic"
            }
        }


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Service status")
    models_loaded: bool = Field(..., description="Whether AI models are loaded")


class EditTextSegmentRequest(BaseModel):
    """Request model for editing a text segment."""
    original_text: str = Field(..., description="Original text to edit")
    instruction: str = Field(..., description="Instruction for how to edit the text")
    context: Optional[str] = Field(None, description="Optional context about the text")


class EditTextSegmentResponse(BaseModel):
    """Response model for text editing."""
    edited_text: str = Field(..., description="The edited text")


class DownloadStorybookRequest(BaseModel):
    """Request model for downloading a storybook as PDF."""
    story_title: str = Field(..., description="Title of the storybook")
    panels: List[StoryPanel] = Field(..., description="All story panels")


# ============================================================================
# THREE-PHASE STORYBOOK PIPELINE MODELS
# ============================================================================

class StoryPage(BaseModel):
    """A single page in a complete storybook (3-phase pipeline)."""
    page_number: int = Field(..., description="Page sequence number")
    title: str = Field(..., description="Page title/heading")
    outline: str = Field(..., description="Short bullet/summary for planning")
    scene_description: str = Field(..., description="Visual description for illustration")
    narration: str = Field(..., description="Final flowing paragraph(s)")
    dialogues: List[DialogueLine] = Field(default_factory=list, description="Dialogue lines")
    art_prompt: Optional[str] = Field(None, description="AI-generated art prompt")
    negative_prompt: Optional[str] = Field(None, description="Negative prompt for image generation")
    image_url: Optional[str] = Field(None, description="Generated image URL")


class StoryMeta(BaseModel):
    """Metadata for a complete storybook."""
    title: str = Field(..., description="Story title")
    logline: str = Field(..., description="One-sentence story summary")
    age_range: str = Field(default="4-7", description="Target age range (e.g., '4-7')")
    style_preset: str = Field(default="storybook_watercolor", description="Visual style preset")
    characters: List[str] = Field(default_factory=list, description="Character descriptions")


class StoryBook(BaseModel):
    """Complete storybook generated through 3-phase pipeline."""
    id: str = Field(..., description="Unique story identifier")
    meta: StoryMeta = Field(..., description="Story metadata")
    pages: List[StoryPage] = Field(..., description="All story pages")


class ThreePhaseStoryRequest(BaseModel):
    """Request for three-phase story generation."""
    story_idea: str = Field(..., description="Story concept or theme")
    num_pages: int = Field(8, ge=4, le=16, description="Number of pages (4-16)")
    age_range: str = Field(default="4-7", description="Target age range")
    style: Optional[ImageStyle] = Field(None, description="Visual style for illustrations")
    asset_ids: List[str] = Field(default_factory=list, description="List of asset IDs to influence the story")

    class Config:
        json_schema_extra = {
            "example": {
                "story_idea": "an elephant who loves painting rainbows",
                "num_pages": 8,
                "age_range": "4-7",
                "style": "watercolor",
                "asset_ids": []
            }
        }


class ThreePhaseStoryResponse(BaseModel):
    """Response for three-phase story generation."""
    storybook: StoryBook = Field(..., description="Complete generated storybook")
    total_generation_time: float = Field(..., description="Total time in seconds")
    phase_times: dict = Field(default_factory=dict, description="Time for each phase")


# ============================================================================
# ASSET SYSTEM FOR UPLOADED FILES
# ============================================================================

class AssetUsage(str, Enum):
    """How an uploaded asset should be used."""
    STYLE = "style"  # Use as style reference for image generation
    CHARACTER = "character"  # Use as character reference
    STORY_SOURCE = "story_source"  # Use as inspiration for story content
    BASE_IMAGE = "base_image"  # Use as base for image-to-image generation


class StoryAsset(BaseModel):
    """An uploaded file/image that influences story generation."""
    id: str = Field(..., description="Unique asset identifier")
    url: str = Field(..., description="Relative URL to the asset file")
    filename: str = Field(..., description="Original filename")
    mime_type: str = Field(..., description="MIME type (e.g., 'image/png')")
    usage: AssetUsage = Field(default=AssetUsage.STYLE, description="How to use this asset")
    description: Optional[str] = Field(None, description="User description of the asset (e.g., 'elephant in jungle, watercolor style')")


class UploadAssetResponse(BaseModel):
    """Response after uploading an asset."""
    asset: StoryAsset = Field(..., description="Uploaded asset metadata")
    message: str = Field(default="Asset uploaded successfully")
