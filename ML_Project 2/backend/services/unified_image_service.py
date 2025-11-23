"""Unified image service that routes to different backends."""
import logging
from typing import Optional, List
from pathlib import Path

from config import settings
from services.image_generator import image_generator
from services.gemini_image import gemini_image_generator, GEMINI_AVAILABLE
from services.stability_ai_image import stability_ai_generator
from core.exceptions import AIGenerationError, ModelNotLoadedError

logger = logging.getLogger(__name__)


class UnifiedImageService:
    """
    Unified image service that routes to different image generation backends
    based on configuration.
    """

    def __init__(self):
        """Initialize the unified image service."""
        self.backend = settings.image_backend
        logger.info(f"UnifiedImageService initialized with backend: {self.backend}")

    def load_model(self):
        """Load the appropriate model based on backend configuration."""
        if self.backend == "stability_ai":
            stability_ai_generator.load_model()
            logger.info("Stability AI model loaded")
        elif self.backend == "gemini_imagen":
            if not GEMINI_AVAILABLE:
                logger.error("Gemini backend selected but google-generativeai not installed")
                raise ModelNotLoadedError(
                    "Google Generative AI library not installed. "
                    "Install with: pip install google-generativeai"
                )
            gemini_image_generator.load_model()
            logger.info("Gemini/Imagen model loaded")
        elif self.backend == "local_diffusion":
            image_generator.load_model()
            logger.info("Stable Diffusion model loaded")
        else:
            raise ValueError(
                f"Invalid IMAGE_BACKEND: {self.backend}. "
                "Must be 'local_diffusion', 'stability_ai', or 'gemini_imagen'"
            )

    def generate_image(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        num_inference_steps: int = 50,
        guidance_scale: float = 7.5,
        width: int = 512,
        height: int = 512,
        reference_images: Optional[List[Path]] = None,
    ) -> str:
        """
        Generate an image using the configured backend.

        Args:
            prompt: Text description of the desired image
            negative_prompt: Optional negative prompt (things to avoid)
            num_inference_steps: Number of denoising steps (for Stable Diffusion)
            guidance_scale: Guidance scale (for Stable Diffusion)
            width: Image width
            height: Image height
            reference_images: Optional list of reference image paths for style/composition

        Returns:
            str: Relative path to the saved image
        """
        # If reference images provided, use image-to-image generation (if supported)
        if reference_images and len(reference_images) > 0:
            logger.info(f"Generating with {len(reference_images)} reference image(s)")
            return self._generate_with_reference(
                prompt=prompt,
                negative_prompt=negative_prompt,
                reference_image=reference_images[0],  # Use first reference
                num_inference_steps=num_inference_steps,
                guidance_scale=guidance_scale,
                width=width,
                height=height
            )

        if self.backend == "stability_ai":
            # Map width/height to aspect ratio for Stability AI
            aspect_ratio = self._get_aspect_ratio(width, height)
            return stability_ai_generator.generate_image(
                prompt=prompt,
                negative_prompt=negative_prompt,
                aspect_ratio=aspect_ratio,
                number_of_images=1
            )
        elif self.backend == "gemini_imagen":
            # Map width/height to aspect ratio for Gemini
            aspect_ratio = self._get_aspect_ratio(width, height)
            return gemini_image_generator.generate_image(
                prompt=prompt,
                negative_prompt=negative_prompt,
                aspect_ratio=aspect_ratio,
                number_of_images=1
            )
        elif self.backend == "local_diffusion":
            # Build enhanced prompt with negative prompt if provided
            enhanced_prompt = prompt
            if negative_prompt:
                # For Stable Diffusion, we can't pass negative prompts directly
                # in the simple API, so we mention what to avoid in the prompt
                logger.info(f"Note: Negative prompt specified but not directly supported: {negative_prompt}")

            return image_generator.generate_image(
                prompt=enhanced_prompt,
                num_inference_steps=num_inference_steps,
                guidance_scale=guidance_scale,
                width=width,
                height=height
            )
        else:
            raise ValueError(f"Invalid backend: {self.backend}")

    def _generate_with_reference(
        self,
        prompt: str,
        reference_image: Path,
        negative_prompt: Optional[str] = None,
        num_inference_steps: int = 50,
        guidance_scale: float = 7.5,
        width: int = 512,
        height: int = 512,
    ) -> str:
        """
        Generate image using a reference image (image-to-image).

        Args:
            prompt: Text description
            reference_image: Path to reference image
            negative_prompt: Optional negative prompt
            num_inference_steps: Denoising steps
            guidance_scale: Guidance scale
            width: Image width
            height: Image height

        Returns:
            str: Path to generated image
        """
        if self.backend == "stability_ai":
            # Stability AI supports image-to-image
            return stability_ai_generator.generate_image_with_reference(
                prompt=prompt,
                reference_image_path=reference_image,
                negative_prompt=negative_prompt,
                style_strength=0.6  # Moderate influence from reference
            )
        else:
            # Fallback to regular generation for backends that don't support it
            logger.warning(f"Backend {self.backend} doesn't support reference images, using regular generation")
            return self.generate_image(
                prompt=prompt,
                negative_prompt=negative_prompt,
                num_inference_steps=num_inference_steps,
                guidance_scale=guidance_scale,
                width=width,
                height=height
            )

    def is_loaded(self) -> bool:
        """Check if the current backend's model is loaded."""
        if self.backend == "stability_ai":
            return stability_ai_generator.is_loaded()
        elif self.backend == "gemini_imagen":
            return gemini_image_generator.is_loaded()
        elif self.backend == "local_diffusion":
            return image_generator.is_loaded()
        return False

    @staticmethod
    def _get_aspect_ratio(width: int, height: int) -> str:
        """
        Convert width/height to aspect ratio string.

        Args:
            width: Image width
            height: Image height

        Returns:
            str: Aspect ratio like "1:1", "16:9", etc.
        """
        # Common aspect ratios
        ratio = width / height
        if abs(ratio - 1.0) < 0.1:
            return "1:1"
        elif abs(ratio - 16/9) < 0.1:
            return "16:9"
        elif abs(ratio - 9/16) < 0.1:
            return "9:16"
        elif abs(ratio - 4/3) < 0.1:
            return "4:3"
        elif abs(ratio - 3/4) < 0.1:
            return "3:4"
        else:
            # Default to square
            return "1:1"


# Singleton instance
unified_image_service = UnifiedImageService()
