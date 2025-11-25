"""Stability AI image generation service."""
import logging
from typing import Optional
from pathlib import Path
import uuid
import base64
import requests

from config import settings
from core.exceptions import AIGenerationError, ModelNotLoadedError

logger = logging.getLogger(__name__)


class StabilityInsufficientBalance(Exception):
    """Raised when Stability AI reports insufficient balance or credits."""
    pass


class StabilityAIImageGenerator:
    """Handles image generation using Stability AI API (SDXL)."""

    def __init__(self):
        """Initialize the Stability AI image generator."""
        self.api_key: Optional[str] = None
        self.model = None
        self.static_dir = Path(settings.static_dir)
        self.static_dir.mkdir(parents=True, exist_ok=True)
        self.api_host = "https://api.stability.ai"
        logger.info("StabilityAIImageGenerator initialized")

    def load_model(self):
        """Load and configure the Stability AI API client."""
        # Read API key from settings (which loads from .env)
        self.api_key = settings.stability_api_key
        if not self.api_key:
            raise ModelNotLoadedError(
                "STABILITY_API_KEY not found in .env file. "
                "Get your API key from https://platform.stability.ai/account/keys "
                "and add 'STABILITY_API_KEY=your_key_here' to backend/.env"
            )

        # Mark as loaded
        self.model = "stable-diffusion-xl-1024-v1-0"
        logger.info("Stability AI API configured successfully")

    def generate_image(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        aspect_ratio: str = "1:1",
        number_of_images: int = 1,
    ) -> str:
        """
        Generate an image using Stability AI SDXL.

        Args:
            prompt: Text description of the desired image
            negative_prompt: Optional negative prompt (things to avoid)
            aspect_ratio: Image aspect ratio (not used, defaults to 1024x1024)
            number_of_images: Number of images to generate (currently only 1 supported)

        Returns:
            str: Relative path to the saved image
        """
        if not self.model:
            raise ModelNotLoadedError(
                "Stability AI model not loaded. Call load_model() first or check STABILITY_API_KEY."
            )

        try:
            logger.info(f"Generating image with Stability AI for prompt: {prompt[:100]}...")

            # Determine image dimensions based on aspect ratio
            width, height = self._get_dimensions(aspect_ratio)

            # Build the request payload
            payload = {
                "text_prompts": [
                    {
                        "text": prompt,
                        "weight": 1
                    }
                ],
                "cfg_scale": 7,
                "height": height,
                "width": width,
                "samples": 1,
                "steps": 30,
            }

            # Add negative prompt if provided
            if negative_prompt:
                payload["text_prompts"].append({
                    "text": negative_prompt,
                    "weight": -1
                })

            # Make API request
            response = requests.post(
                f"{self.api_host}/v1/generation/{self.model}/text-to-image",
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "Authorization": f"Bearer {self.api_key}"
                },
                json=payload,
            )

            if response.status_code != 200:
                # Try to get detailed error message
                error_msg = response.text
                try:
                    error_data = response.json()
                    error_msg = error_data.get('message', response.text)
                except:
                    pass

                # Check for insufficient balance conditions
                balance_indicators = [
                    "not have enough balance",
                    "insufficient balance",
                    "not enough credits",
                    "grant"
                ]

                error_msg_lower = error_msg.lower()
                is_balance_error = any(indicator in error_msg_lower for indicator in balance_indicators)

                # Raise insufficient balance error for credit-related issues
                if response.status_code in [400, 402, 403, 429] and is_balance_error:
                    raise StabilityInsufficientBalance(f"Stability AI insufficient balance: {error_msg}")

                # For 402/403/429 without clear balance message, also assume it's balance-related
                if response.status_code in [402, 403, 429]:
                    raise StabilityInsufficientBalance(f"Stability AI credit/balance issue: {error_msg}")

                # Other errors
                raise AIGenerationError(f"Stability AI API error: {error_msg}")

            # Parse response
            data = response.json()

            if not data.get("artifacts"):
                raise AIGenerationError("No images returned from Stability AI")

            # Get the first generated image (base64 encoded)
            image_base64 = data["artifacts"][0]["base64"]

            # Decode and save image
            image_bytes = base64.b64decode(image_base64)
            filename = f"{uuid.uuid4()}.png"
            filepath = self.static_dir / filename

            with open(filepath, 'wb') as f:
                f.write(image_bytes)

            logger.info(f"Image generated with Stability AI: {filename}")

            # Return relative URL path
            return f"/static/images/{filename}"

        except StabilityInsufficientBalance:
            # Re-raise balance errors without conversion (for fallback handling)
            raise
        except AIGenerationError:
            raise
        except Exception as e:
            logger.error(f"Stability AI image generation failed: {e}")
            raise AIGenerationError(f"Failed to generate image with Stability AI: {e}")

    def generate_image_with_reference(
        self,
        prompt: str,
        reference_image_path: Path,
        negative_prompt: Optional[str] = None,
        style_strength: float = 0.5,
    ) -> str:
        """
        Generate an image using a reference image for style/composition.

        Args:
            prompt: Text description of the desired image
            reference_image_path: Path to reference image
            negative_prompt: Optional negative prompt
            style_strength: How much to use the reference (0.0-1.0, higher = more influence)

        Returns:
            str: Relative path to the saved image
        """
        if not self.model:
            raise ModelNotLoadedError("Stability AI model not loaded")

        try:
            logger.info(f"Generating image with reference: {reference_image_path}")

            # Read and encode reference image
            with open(reference_image_path, 'rb') as f:
                image_bytes = f.read()
                image_base64 = base64.b64encode(image_bytes).decode('utf-8')

            # Build payload for image-to-image
            payload = {
                "text_prompts": [
                    {
                        "text": prompt,
                        "weight": 1
                    }
                ],
                "init_image": image_base64,
                "init_image_mode": "IMAGE_STRENGTH",
                "image_strength": 1.0 - style_strength,  # Higher strength = less influence from original
                "cfg_scale": 7,
                "samples": 1,
                "steps": 30,
            }

            if negative_prompt:
                payload["text_prompts"].append({
                    "text": negative_prompt,
                    "weight": -1
                })

            # Make API request to image-to-image endpoint
            response = requests.post(
                f"{self.api_host}/v1/generation/{self.model}/image-to-image",
                headers={
                    "Accept": "application/json",
                    "Authorization": f"Bearer {self.api_key}"
                },
                json=payload,
            )

            if response.status_code != 200:
                # Try to get detailed error message
                error_msg = response.text
                try:
                    error_data = response.json()
                    error_msg = error_data.get('message', response.text)
                except:
                    pass

                # Check for insufficient balance conditions
                balance_indicators = [
                    "not have enough balance",
                    "insufficient balance",
                    "not enough credits",
                    "grant"
                ]

                error_msg_lower = error_msg.lower()
                is_balance_error = any(indicator in error_msg_lower for indicator in balance_indicators)

                # Raise insufficient balance error for credit-related issues
                if response.status_code in [400, 402, 403, 429] and is_balance_error:
                    raise StabilityInsufficientBalance(f"Stability AI insufficient balance: {error_msg}")

                # For 402/403/429 without clear balance message, also assume it's balance-related
                if response.status_code in [402, 403, 429]:
                    raise StabilityInsufficientBalance(f"Stability AI credit/balance issue: {error_msg}")

                # For other errors, fallback to text-to-image
                logger.warning(f"Image-to-image failed ({response.status_code}), falling back to text-to-image")
                return self.generate_image(prompt, negative_prompt)

            # Parse response
            data = response.json()

            if not data.get("artifacts"):
                raise AIGenerationError("No images returned from Stability AI")

            # Get the first generated image
            result_image_base64 = data["artifacts"][0]["base64"]

            # Decode and save image
            image_bytes = base64.b64decode(result_image_base64)
            filename = f"{uuid.uuid4()}.png"
            filepath = self.static_dir / filename

            with open(filepath, 'wb') as f:
                f.write(image_bytes)

            logger.info(f"Image generated with reference: {filename}")

            return f"/static/images/{filename}"

        except StabilityInsufficientBalance:
            # Re-raise balance errors without conversion (for fallback handling)
            raise
        except AIGenerationError:
            raise
        except Exception as e:
            logger.error(f"Image-to-image generation failed: {e}, falling back to text-to-image")
            # Fallback to regular generation
            return self.generate_image(prompt, negative_prompt)

    def is_loaded(self) -> bool:
        """Check if the Stability AI model is configured."""
        return self.model is not None and self.api_key is not None

    @staticmethod
    def _get_dimensions(aspect_ratio: str) -> tuple[int, int]:
        """
        Convert aspect ratio to dimensions supported by Stability AI.

        Args:
            aspect_ratio: Aspect ratio string (e.g., "1:1", "16:9")

        Returns:
            Tuple of (width, height)
        """
        # Stability AI SDXL supports various dimensions
        # Must be multiples of 64 and between 128-1536
        aspect_ratios = {
            "1:1": (1024, 1024),
            "16:9": (1344, 768),
            "9:16": (768, 1344),
            "4:3": (1152, 896),
            "3:4": (896, 1152),
            "3:2": (1216, 832),
            "2:3": (832, 1216),
        }

        return aspect_ratios.get(aspect_ratio, (1024, 1024))


# Singleton instance
stability_ai_generator = StabilityAIImageGenerator()
