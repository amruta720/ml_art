"""Stable Diffusion image generation service using diffusers."""
import torch
from diffusers import StableDiffusionPipeline
from PIL import Image
from pathlib import Path
import uuid
import time
from typing import Optional
import logging

from config import settings
from core.exceptions import AIGenerationError, ModelNotLoadedError

logger = logging.getLogger(__name__)


class ImageGenerator:
    """Handles image generation using Stable Diffusion."""

    def __init__(self):
        """Initialize the image generator."""
        self.pipeline: Optional[StableDiffusionPipeline] = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.static_dir = Path(settings.static_dir)
        self.static_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"ImageGenerator initialized. Device: {self.device}")

    def load_model(self):
        """Load the Stable Diffusion model."""
        if self.pipeline is not None:
            logger.info("Model already loaded")
            return

        try:
            logger.info(f"Loading Stable Diffusion model: {settings.stable_diffusion_model}")
            self.pipeline = StableDiffusionPipeline.from_pretrained(
                settings.stable_diffusion_model,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                safety_checker=None,
                requires_safety_checker=False
            )
            self.pipeline.to(self.device)

            # Enable memory optimizations
            if self.device == "cuda":
                self.pipeline.enable_attention_slicing()

            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise ModelNotLoadedError(f"Failed to load Stable Diffusion model: {e}")

    def generate_image(
        self,
        prompt: str,
        num_inference_steps: int = 50,
        guidance_scale: float = 7.5,
        width: int = 512,
        height: int = 512,
    ) -> str:
        """
        Generate an image from a text prompt.

        Args:
            prompt: Text description of the desired image
            num_inference_steps: Number of denoising steps
            guidance_scale: Guidance scale for classifier-free guidance
            width: Image width
            height: Image height

        Returns:
            str: Relative path to the saved image
        """
        if self.pipeline is None:
            raise ModelNotLoadedError("Model not loaded. Call load_model() first.")

        try:
            logger.info(f"Generating image for prompt: {prompt[:100]}...")
            start_time = time.time()

            # Generate image
            result = self.pipeline(
                prompt=prompt,
                num_inference_steps=num_inference_steps,
                guidance_scale=guidance_scale,
                width=width,
                height=height,
            )

            image: Image.Image = result.images[0]

            # Save image with unique filename
            filename = f"{uuid.uuid4()}.png"
            filepath = self.static_dir / filename
            image.save(filepath, format="PNG")

            generation_time = time.time() - start_time
            logger.info(f"Image generated in {generation_time:.2f}s: {filename}")

            # Return relative URL path
            return f"/static/images/{filename}"

        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            raise AIGenerationError(f"Failed to generate image: {e}")

    def is_loaded(self) -> bool:
        """Check if the model is loaded."""
        return self.pipeline is not None


# Singleton instance
image_generator = ImageGenerator()
