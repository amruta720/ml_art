"""Revision Agent for refining prompts based on user feedback."""
import logging

from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class RevisionAgent(BaseAgent):
    """Agent that revises prompts based on user feedback."""

    SYSTEM_INSTRUCTIONS = """You are an expert Revision Agent for image generation prompts.

Your role is to refine and modify existing prompts based on user feedback.

Guidelines:
1. Analyze the original prompt and user feedback
2. Intelligently incorporate the requested changes
3. Preserve elements the user didn't ask to change
4. Enhance the prompt with technical quality keywords
5. Ensure the revised prompt is optimized for Stable Diffusion
6. Keep prompts under 200 words
7. Use comma-separated descriptors

Examples:
Original: "a serene mountain lake at sunset"
Feedback: "make it more dramatic with stormy clouds"
Output: "dramatic mountain lake scene, turbulent stormy clouds, intense sunset breaking through storm, lightning in distance, rough water surface, dark moody atmosphere, cinematic lighting, highly detailed, 4k quality"

Original: "a cute robot"
Feedback: "make it look vintage and steampunk"
Output: "vintage steampunk robot, brass and copper materials, intricate gears and cogs visible, Victorian era design, weathered patina, ornate details, retro-futuristic, mechanical precision, soft warm lighting, detailed metalwork"

Return ONLY the revised prompt, nothing else."""

    def __init__(self):
        """Initialize the Revision Agent."""
        super().__init__(
            role="Revision Agent",
            instructions=self.SYSTEM_INSTRUCTIONS
        )

    def revise_prompt(self, original_prompt: str, feedback: str, style: str = None) -> str:
        """
        Revise a prompt based on user feedback.

        Args:
            original_prompt: The original prompt
            feedback: User's feedback for revision
            style: Optional style to apply

        Returns:
            str: Revised prompt
        """
        user_message = f"Original prompt: {original_prompt}\nUser feedback: {feedback}"
        if style:
            user_message += f"\nDesired style: {style}"

        try:
            revised = self._call_llm(user_message, temperature=0.7, max_tokens=300)
            logger.info(f"Revised prompt based on feedback: '{feedback[:50]}...'")
            return revised
        except Exception as e:
            logger.warning(f"Prompt revision failed: {e}")
            # Fallback: combine original prompt with feedback
            return f"{original_prompt}, {feedback}"

    def process(self, input_data: str) -> str:
        """Process method for compatibility."""
        # Expected format: "original_prompt|feedback"
        parts = input_data.split("|", 1)
        if len(parts) == 2:
            return self.revise_prompt(parts[0], parts[1])
        return input_data


# Singleton instance
revision_agent = RevisionAgent()
