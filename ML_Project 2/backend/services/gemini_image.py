"""Google Gemini/Imagen image generation service."""
import os
import logging
from typing import Optional
from pathlib import Path
import uuid
import base64

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    genai = None

from config import settings
from core.exceptions import AIGenerationError, ModelNotLoadedError

logger = logging.getLogger(__name__)


class GeminiImageGenerator:
    """Handles image generation using Google Gemini/Imagen."""

    def __init__(self):
        """Initialize the Gemini image generator."""
        self.api_key: Optional[str] = None
        self.model = None
        self.static_dir = Path(settings.static_dir)
        self.static_dir.mkdir(parents=True, exist_ok=True)
        logger.info("GeminiImageGenerator initialized")

    def load_model(self):
        """Load and configure the Gemini API client."""
        if not GEMINI_AVAILABLE:
            raise ModelNotLoadedError(
                "Google Generative AI library not installed. "
                "Install with: pip install google-generativeai"
            )

        # Read API key from settings (which loads from .env)
        self.api_key = settings.gemini_api_key
        if not self.api_key:
            raise ModelNotLoadedError(
                "GEMINI_API_KEY not found in .env file. "
                "Please add 'GEMINI_API_KEY=your_key_here' to backend/.env"
            )

        # Mark as loaded (we create the client on-demand during generation)
        self.model = "imagen-3.0-generate-001"  # Just store the model name
        logger.info("Gemini/Imagen API configured successfully")

    def generate_image(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        aspect_ratio: str = "1:1",
        number_of_images: int = 1,
    ) -> str:
        """
        Generate an image using Google Gemini/Imagen.

        Args:
            prompt: Text description of the desired image
            negative_prompt: Optional negative prompt (things to avoid)
            aspect_ratio: Image aspect ratio (e.g., "1:1", "16:9", "9:16")
            number_of_images: Number of images to generate (currently only 1 supported)

        Returns:
            str: Relative path to the saved image
        """
        if not self.model:
            raise ModelNotLoadedError(
                "Gemini model not loaded. Call load_model() first or check GEMINI_API_KEY."
            )

        try:
            logger.info(f"Generating image with Gemini for prompt: {prompt[:100]}...")

            # Construct the full prompt (Gemini doesn't support negative prompts directly,
            # so we incorporate them into the main prompt)
            full_prompt = prompt
            if negative_prompt:
                full_prompt = f"{prompt}. Avoid: {negative_prompt}"

            # Configure the API
            genai.configure(api_key=self.api_key)

            # Use ImageGenerationModel for Imagen
            # Note: The google-generativeai library primarily supports text generation
            # For actual image generation with Imagen, we'd need the Vertex AI SDK
            # As a workaround, we'll use the text model to generate better prompts
            # and note that true Imagen support requires Vertex AI

            # For now, let's use a text model approach or raise a helpful error
            raise AIGenerationError(
                "Imagen image generation requires Google Cloud Vertex AI SDK. "
                "The google-generativeai library doesn't directly support Imagen. "
                "Please use IMAGE_BACKEND=local_diffusion instead, or set up Vertex AI. "
                "See: https://cloud.google.com/vertex-ai/docs/generative-ai/image/generate-images"
            )

        except AIGenerationError:
            raise
        except Exception as e:
            logger.error(f"Gemini image generation failed: {e}")
            raise AIGenerationError(f"Failed to generate image with Gemini: {e}")

    def is_loaded(self) -> bool:
        """Check if the Gemini model is configured."""
        return self.model is not None and self.api_key is not None


# Singleton instance
gemini_image_generator = GeminiImageGenerator()
