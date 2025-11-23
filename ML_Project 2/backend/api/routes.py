"""FastAPI routes for Image Mode and Storybook Mode."""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse, StreamingResponse
import time
import logging
from typing import List, Optional
from pathlib import Path
from PIL import Image
import io
import shutil

from models.schemas import (
    ImageModeRequest,
    ImageModeResponse,
    StoryModeRequest,
    StoryModeResponse,
    RevisionRequest,
    HealthResponse,
    StoryPanel,
    DialogueLine,
    EditTextSegmentRequest,
    EditTextSegmentResponse,
    DownloadStorybookRequest,
    ThreePhaseStoryRequest,
    ThreePhaseStoryResponse,
    StoryBook,
    StoryMeta,
    StoryPage,
    StoryAsset,
    AssetUsage,
    UploadAssetResponse
)
from services.unified_image_service import unified_image_service
from services.storybook_prompt_builder import enhance_storybook_prompt_with_style
from services.pdf_generator import pdf_generator
from agents.prompt_stylist_agent import prompt_stylist
from agents.storyboard_agent import storyboard_agent
from agents.revision_agent import revision_agent
from agents.text_editor_agent import text_editor_agent
from agents.story_draft_agent import story_draft_agent
from agents.story_text_agent import story_text_agent
from agents.story_art_agent import story_art_agent
from services.asset_manager import asset_manager
from core.exceptions import AIGenerationError, ModelNotLoadedError
import uuid

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        models_loaded=unified_image_service.is_loaded()
    )


@router.post("/upload-asset", response_model=UploadAssetResponse)
async def upload_asset(
    file: UploadFile = File(...),
    usage: AssetUsage = Form(default=AssetUsage.STYLE),
    description: Optional[str] = Form(default=None)
):
    """
    Upload an asset (image/file) to use as reference for story generation.

    The asset can be used as:
    - Style reference for image generation
    - Character reference for consistent characters
    - Story source for content inspiration
    - Base image for image-to-image generation
    """
    try:
        logger.info(f"Uploading asset: {file.filename}, usage: {usage}")

        # Validate file type
        if not file.content_type:
            raise HTTPException(status_code=400, detail="File type not specified")

        # Create storage directory
        storage_dir = Path("static/assets")
        storage_dir.mkdir(parents=True, exist_ok=True)

        # Generate unique filename
        file_ext = Path(file.filename).suffix
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = storage_dir / unique_filename

        # Save the file
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        logger.info(f"File saved to: {file_path}")

        # Register the asset
        asset = asset_manager.register_asset(
            file_path=file_path,
            filename=file.filename,
            mime_type=file.content_type,
            usage=usage,
            description=description
        )

        return UploadAssetResponse(
            asset=asset,
            message=f"Asset uploaded successfully as {usage.value} reference"
        )

    except Exception as e:
        logger.error(f"Asset upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Asset upload failed: {str(e)}")


@router.get("/assets", response_model=List[StoryAsset])
async def list_assets():
    """List all uploaded assets."""
    return asset_manager.list_all_assets()


@router.delete("/assets/{asset_id}")
async def delete_asset(asset_id: str):
    """Delete an asset by ID."""
    if asset_manager.delete_asset(asset_id):
        return {"message": "Asset deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Asset not found")


@router.post("/image-mode", response_model=ImageModeResponse)
async def generate_single_image(request: ImageModeRequest):
    """
    Generate a single image from a prompt (Image Mode).

    This endpoint:
    1. Optionally enhances the prompt using Prompt Stylist Agent
    2. Generates an image using Stable Diffusion
    3. Returns the image URL and metadata
    """
    try:
        start_time = time.time()
        logger.info(f"Image Mode request: {request.prompt[:100]}")

        # Step 1: Enhance prompt if requested
        if request.enhance_prompt:
            enhanced_prompt = prompt_stylist.enhance_prompt(
                request.prompt,
                request.style.value if request.style else None
            )
        else:
            enhanced_prompt = request.prompt

        # Step 2: Generate image
        image_url = unified_image_service.generate_image(
            prompt=enhanced_prompt,
            num_inference_steps=50,
            guidance_scale=7.5
        )

        generation_time = time.time() - start_time

        return ImageModeResponse(
            image_url=image_url,
            original_prompt=request.prompt,
            enhanced_prompt=enhanced_prompt,
            style_applied=request.style.value if request.style else None,
            generation_time=generation_time
        )

    except ModelNotLoadedError:
        raise HTTPException(status_code=503, detail="Model not loaded. Please wait.")
    except AIGenerationError as e:
        raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in image-mode: {e}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@router.post("/story-mode", response_model=StoryModeResponse)
async def generate_storybook(request: StoryModeRequest):
    """
    Generate a multi-panel storybook (Story Mode).

    This endpoint:
    1. Uses Storyboard Agent to create story narrative
    2. Enhances each panel's prompt using Prompt Stylist Agent
    3. Generates images for all panels
    4. Returns complete storybook with images
    """
    try:
        start_time = time.time()
        logger.info(f"Story Mode request: {request.story_idea[:100]}, panels: {request.num_panels}")

        # Step 1: Create storyboard
        storyboard = storyboard_agent.create_storyboard(
            story_idea=request.story_idea,
            num_panels=request.num_panels,
            style=request.style.value if request.style else None
        )

        story_title = storyboard["title"]
        panels: List[StoryPanel] = []

        # Step 2: Generate images for each panel
        for panel_data in storyboard["panels"]:
            # Ensure panel_data is a dict
            if not isinstance(panel_data, dict):
                logger.error(f"Invalid panel_data type: {type(panel_data)}, value: {panel_data}")
                continue

            # Get the base image prompt from storyboard
            base_prompt = panel_data.get("image_prompt") or panel_data.get("scene_description") or panel_data.get("description", "")

            # Enhance with storybook-specific styling
            enhanced_prompt = enhance_storybook_prompt_with_style(
                base_prompt,
                request.style.value if request.style else None
            )

            # Further enhance with Prompt Stylist Agent
            enhanced_prompt = prompt_stylist.enhance_prompt(
                enhanced_prompt,
                request.style.value if request.style else None
            )

            # Generate image
            image_url = unified_image_service.generate_image(
                prompt=enhanced_prompt,
                num_inference_steps=50,
                guidance_scale=7.5
            )

            # Parse dialogues
            dialogues = []
            if "dialogues" in panel_data and isinstance(panel_data["dialogues"], list):
                for dialogue in panel_data["dialogues"]:
                    if isinstance(dialogue, dict):
                        dialogues.append(DialogueLine(
                            speaker=dialogue.get("speaker", ""),
                            text=dialogue.get("text", "")
                        ))

            # Create panel with full structure
            panel = StoryPanel(
                panel_number=panel_data.get("panel_number", len(panels) + 1),
                title=panel_data.get("title", f"Panel {panel_data.get('panel_number', len(panels) + 1)}"),
                narration=panel_data.get("narration") or panel_data.get("description", ""),
                dialogues=dialogues,
                scene_description=panel_data.get("scene_description", ""),
                image_prompt=enhanced_prompt,
                image_url=image_url
            )
            panels.append(panel)

        total_time = time.time() - start_time

        return StoryModeResponse(
            story_title=story_title,
            panels=panels,
            style_applied=request.style.value if request.style else None,
            total_generation_time=total_time
        )

    except ModelNotLoadedError:
        raise HTTPException(status_code=503, detail="Model not loaded. Please wait.")
    except AIGenerationError as e:
        raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in story-mode: {e}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@router.post("/revise", response_model=ImageModeResponse)
async def revise_image(request: RevisionRequest):
    """
    Revise an image based on feedback (uses Revision Agent).

    This endpoint:
    1. Uses Revision Agent to create revised prompt from feedback
    2. Generates new image with revised prompt
    3. Returns the new image and metadata
    """
    try:
        start_time = time.time()
        logger.info(f"Revision request: {request.feedback[:100]}")

        # Step 1: Create revised prompt
        revised_prompt = revision_agent.revise_prompt(
            original_prompt=request.original_prompt,
            feedback=request.feedback,
            style=request.style.value if request.style else None
        )

        # Step 2: Generate image with revised prompt
        image_url = unified_image_service.generate_image(
            prompt=revised_prompt,
            num_inference_steps=50,
            guidance_scale=7.5
        )

        generation_time = time.time() - start_time

        return ImageModeResponse(
            image_url=image_url,
            original_prompt=request.original_prompt,
            enhanced_prompt=revised_prompt,
            style_applied=request.style.value if request.style else None,
            generation_time=generation_time
        )

    except ModelNotLoadedError:
        raise HTTPException(status_code=503, detail="Model not loaded. Please wait.")
    except AIGenerationError as e:
        raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in revise: {e}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@router.get("/download_image/{filename}")
async def download_image(filename: str, format: str = "png"):
    """
    Download a generated image in the specified format.

    Args:
        filename: Image filename (with or without extension)
        format: Desired format (png, jpg, jpeg, webp)

    Returns:
        Image file with appropriate headers for download
    """
    try:
        # Validate format
        format = format.lower()
        if format not in ["png", "jpg", "jpeg", "webp"]:
            raise HTTPException(status_code=400, detail="Invalid format. Supported: png, jpg, jpeg, webp")

        # Normalize format (jpg -> jpeg for PIL)
        pil_format = "JPEG" if format in ["jpg", "jpeg"] else format.upper()

        # Remove extension from filename if present
        filename_base = filename.rsplit(".", 1)[0]

        # Find the original image
        static_dir = Path("static/images")
        original_file = None

        # Try common extensions
        for ext in [".png", ".jpg", ".jpeg", ".webp"]:
            potential_file = static_dir / f"{filename_base}{ext}"
            if potential_file.exists():
                original_file = potential_file
                break

        if not original_file or not original_file.exists():
            raise HTTPException(status_code=404, detail="Image not found")

        # Load image
        image = Image.open(original_file)

        # Convert to RGB if saving as JPEG (JPEG doesn't support transparency)
        if pil_format == "JPEG" and image.mode in ("RGBA", "LA", "P"):
            # Create white background
            rgb_image = Image.new("RGB", image.size, (255, 255, 255))
            if image.mode == "P":
                image = image.convert("RGBA")
            rgb_image.paste(image, mask=image.split()[-1] if image.mode in ("RGBA", "LA") else None)
            image = rgb_image

        # Save to bytes
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format=pil_format, quality=95 if pil_format == "JPEG" else None)
        img_byte_arr.seek(0)

        # Determine MIME type
        mime_types = {
            "PNG": "image/png",
            "JPEG": "image/jpeg",
            "WEBP": "image/webp"
        }
        mime_type = mime_types.get(pil_format, "image/png")

        # Determine download filename
        download_filename = f"{filename_base}.{format}"

        logger.info(f"Serving image download: {download_filename}")

        # Return as download
        return StreamingResponse(
            img_byte_arr,
            media_type=mime_type,
            headers={
                "Content-Disposition": f'attachment; filename="{download_filename}"'
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading image: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")


@router.post("/edit_text_segment", response_model=EditTextSegmentResponse)
async def edit_text_segment(request: EditTextSegmentRequest):
    """
    Edit a small piece of text using the Text Editor Agent.

    This endpoint allows inline editing of narration or dialogue text
    based on user instructions.
    """
    try:
        logger.info(f"Text edit request: '{request.original_text[:50]}...' with instruction: '{request.instruction[:50]}...'")

        # Use Text Editor Agent to edit the text
        edited_text = text_editor_agent.edit_text(
            original_text=request.original_text,
            instruction=request.instruction,
            context=request.context
        )

        return EditTextSegmentResponse(edited_text=edited_text)

    except Exception as e:
        logger.error(f"Text editing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Text editing failed: {str(e)}")


@router.post("/download_storybook")
async def download_storybook(request: DownloadStorybookRequest):
    """
    Generate and download a storybook as a PDF.

    This endpoint creates a formatted PDF with:
    - Story title
    - Each panel with title, image, narration, and dialogues
    """
    try:
        logger.info(f"PDF generation request for: '{request.story_title}'")

        # Generate PDF
        pdf_bytes = pdf_generator.generate_storybook_pdf(
            story_title=request.story_title,
            panels=request.panels
        )

        # Create a safe filename
        safe_filename = "".join(c for c in request.story_title if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_filename = safe_filename.replace(' ', '_')
        if not safe_filename:
            safe_filename = "storybook"
        filename = f"{safe_filename}.pdf"

        logger.info(f"Serving PDF download: {filename}")

        # Return PDF as download
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )

    except ImportError as e:
        raise HTTPException(
            status_code=500,
            detail="PDF generation not available. ReportLab library not installed."
        )
    except Exception as e:
        logger.error(f"PDF generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")


@router.post("/generate-storybook-3phase", response_model=ThreePhaseStoryResponse)
async def generate_storybook_3phase(request: ThreePhaseStoryRequest):
    """
    Generate a complete children's storybook using a three-phase pipeline.

    Phase 1: Story Draft - Generate full book structure with outlines
    Phase 2: Page Text - Generate narration and dialogues for each page
    Phase 3: Art Prompts - Generate image prompts and create images

    This produces professional-quality storybooks like real children's books.
    """
    try:
        total_start = time.time()
        phase_times = {}

        logger.info(f"Starting 3-phase story generation: '{request.story_idea}' ({request.num_pages} pages)")

        # Build asset context if assets are provided
        asset_context = None
        if request.asset_ids:
            asset_context = asset_manager.build_asset_context(request.asset_ids)
            logger.info(f"Using {len(request.asset_ids)} asset(s) for context")

        # ========================================================================
        # PHASE 1: STORY DRAFT & OUTLINE
        # ========================================================================
        phase1_start = time.time()
        logger.info("Phase 1: Generating story outline...")

        story_outline = story_draft_agent.generate_story_outline(
            story_idea=request.story_idea,
            num_pages=request.num_pages,
            age_range=request.age_range,
            style=request.style.value if request.style else None,
            asset_context=asset_context
        )

        phase_times["phase_1_outline"] = time.time() - phase1_start
        logger.info(f"Phase 1 complete: '{story_outline['title']}' ({phase_times['phase_1_outline']:.2f}s)")

        # ========================================================================
        # PHASE 2: PAGE TEXT & DIALOGUES
        # ========================================================================
        phase2_start = time.time()
        logger.info("Phase 2: Generating narration and dialogues...")

        text_data = story_text_agent.generate_page_text(
            story_title=story_outline["title"],
            story_logline=story_outline["logline"],
            characters=story_outline.get("characters", []),
            age_range=story_outline.get("age_range", request.age_range),
            pages_outline=story_outline["pages"]
        )

        phase_times["phase_2_text"] = time.time() - phase2_start
        logger.info(f"Phase 2 complete ({phase_times['phase_2_text']:.2f}s)")

        # Merge outline and text data
        pages_with_text = []
        for outline_page, text_page in zip(story_outline["pages"], text_data["pages"]):
            merged_page = {
                **outline_page,
                "narration": text_page.get("narration", ""),
                "dialogues": text_page.get("dialogues", [])
            }
            pages_with_text.append(merged_page)

        # ========================================================================
        # PHASE 3: ART PROMPTS & IMAGE GENERATION
        # ========================================================================
        phase3_start = time.time()
        logger.info("Phase 3: Generating art prompts and images...")

        # Generate art prompts
        art_data = story_art_agent.generate_art_prompts(
            story_title=story_outline["title"],
            characters=story_outline.get("characters", []),
            age_range=story_outline.get("age_range", request.age_range),
            style=request.style.value if request.style else None,
            pages_data=pages_with_text,
            asset_context=asset_context
        )

        logger.info("Art prompts generated. Starting image generation...")

        # Get reference images from assets (for style/character consistency)
        reference_images = None
        if request.asset_ids:
            reference_images = asset_manager.get_image_asset_paths(request.asset_ids)
            if reference_images:
                logger.info(f"Using {len(reference_images)} reference image(s) for generation")

        # Generate images for each page
        final_pages: List[StoryPage] = []
        for page_data, art_page in zip(pages_with_text, art_data["pages"]):
            # Generate image
            logger.info(f"Generating image for page {page_data['page_number']}...")

            image_url = unified_image_service.generate_image(
                prompt=art_page["art_prompt"],
                negative_prompt=art_page.get("negative_prompt"),
                num_inference_steps=50,
                guidance_scale=7.5,
                reference_images=reference_images
            )

            # Parse dialogues
            dialogues = []
            if "dialogues" in page_data and isinstance(page_data["dialogues"], list):
                for dialogue in page_data["dialogues"]:
                    if isinstance(dialogue, dict):
                        dialogues.append(DialogueLine(
                            speaker=dialogue.get("speaker", ""),
                            text=dialogue.get("text", "")
                        ))

            # Create StoryPage
            page = StoryPage(
                page_number=page_data["page_number"],
                title=page_data["title"],
                outline=page_data.get("outline", ""),
                scene_description=page_data.get("scene_description", ""),
                narration=page_data.get("narration", ""),
                dialogues=dialogues,
                art_prompt=art_page["art_prompt"],
                negative_prompt=art_page.get("negative_prompt"),
                image_url=image_url
            )
            final_pages.append(page)

        phase_times["phase_3_art"] = time.time() - phase3_start
        logger.info(f"Phase 3 complete ({phase_times['phase_3_art']:.2f}s)")

        # ========================================================================
        # BUILD FINAL STORYBOOK
        # ========================================================================
        storybook = StoryBook(
            id=str(uuid.uuid4()),
            meta=StoryMeta(
                title=story_outline["title"],
                logline=story_outline["logline"],
                age_range=story_outline.get("age_range", request.age_range),
                style_preset=request.style.value if request.style else "storybook_watercolor",
                characters=story_outline.get("characters", [])
            ),
            pages=final_pages
        )

        total_time = time.time() - total_start

        logger.info(f"3-phase story generation complete: {total_time:.2f}s total")
        logger.info(f"  Phase 1 (Outline): {phase_times['phase_1_outline']:.2f}s")
        logger.info(f"  Phase 2 (Text): {phase_times['phase_2_text']:.2f}s")
        logger.info(f"  Phase 3 (Art): {phase_times['phase_3_art']:.2f}s")

        return ThreePhaseStoryResponse(
            storybook=storybook,
            total_generation_time=total_time,
            phase_times=phase_times
        )

    except ModelNotLoadedError:
        raise HTTPException(status_code=503, detail="Model not loaded. Please wait.")
    except AIGenerationError as e:
        raise HTTPException(status_code=500, detail=f"Story generation failed: {str(e)}")
    except Exception as e:
        logger.exception(f"Unexpected error in 3-phase story generation: {e}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
