"""Prompt Stylist Agent for enhancing image prompts."""
from typing import Optional
import logging

from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class PromptStylistAgent(BaseAgent):
    """Agent that enhances and styles image generation prompts."""

    SYSTEM_INSTRUCTIONS = """You are an expert Prompt Stylist for AI image generation.

Your role is to transform user prompts into detailed, optimized prompts for Stable Diffusion.

Guidelines:
1. Enhance prompts with rich visual details (lighting, composition, atmosphere)
2. Add technical quality keywords (e.g., "highly detailed", "4k", "professional")
3. Maintain the core concept from the original prompt
4. Apply the requested style if provided
5. Keep prompts under 200 words
6. Use comma-separated descriptors

Examples:
Input: "a cat"
Output: "a fluffy orange tabby cat, sitting elegantly, soft natural lighting, detailed fur texture, photorealistic, 4k quality, sharp focus"

Input: "sunset over mountains" (style: oil painting)
Output: "majestic mountain range at golden hour sunset, oil painting style, rich warm colors, dramatic clouds, visible brush strokes, textured canvas, masterful composition, reminiscent of Albert Bierstadt"

Return ONLY the enhanced prompt, nothing else."""

    def __init__(self):
        """Initialize the Prompt Stylist Agent."""
        super().__init__(
            role="Prompt Stylist",
            instructions=self.SYSTEM_INSTRUCTIONS
        )

    def enhance_prompt(self, prompt: str, style: Optional[str] = None) -> str:
        """
        Enhance a user prompt for image generation.

        Args:
            prompt: Original user prompt
            style: Optional style to apply

        Returns:
            str: Enhanced prompt
        """
        user_message = f"Original prompt: {prompt}"
        if style:
            user_message += f"\nDesired style: {style}"

        try:
            enhanced = self._call_llm(user_message, temperature=0.7, max_tokens=300)
            logger.info(f"Enhanced prompt from '{prompt[:50]}...' to '{enhanced[:50]}...'")
            return enhanced
        except Exception as e:
            logger.warning(f"Prompt enhancement failed, using original: {e}")
            # Fallback to original prompt if enhancement fails
            return prompt

    def process(self, input_data: str) -> str:
        """Process method for compatibility."""
        return self.enhance_prompt(input_data)


# Singleton instance
prompt_stylist = PromptStylistAgent()
