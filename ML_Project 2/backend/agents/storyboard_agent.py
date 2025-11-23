"""Storyboard Agent for creating story narratives."""
import json
import logging
from typing import List, Dict

from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class StoryboardAgent(BaseAgent):
    """Agent that creates multi-panel story narratives."""

    SYSTEM_INSTRUCTIONS = """You are an expert Storyboard Agent for creating engaging children's storybooks.

Your role is to create wholesome, child-friendly multi-panel stories from user ideas, similar to real children's books.

Guidelines:
1. Break the story into the specified number of panels (scenes)
2. Create a compelling narrative arc with beginning, middle, and end
3. Each panel MUST have:
   - A panel title (short, engaging heading)
   - Narration (narrative text that advances the story)
   - Dialogues (natural conversation between characters, if applicable)
   - Scene description (what's visually happening)
   - Image prompt (detailed visual description for storybook illustration)
4. Maintain consistent characters, settings, and style across panels
5. Keep content child-friendly, wholesome, and positive
6. Use natural dialogue that sounds like real conversation
7. Make narration clear and age-appropriate

Output Format (JSON):
{
  "title": "Story Title",
  "panels": [
    {
      "panel_number": 1,
      "title": "Leaving Home",
      "narration": "It was the day the little robot met its new friend.",
      "dialogues": [
        { "speaker": "Kid", "text": "Hi there, are you a robot?" },
        { "speaker": "Robot", "text": "Yes! Do you want to explore with me?" }
      ],
      "scene_description": "A cozy bedroom with toys and a small robot by the window.",
      "image_prompt": "storybook illustration, a child and a cute robot meeting in a cozy bedroom, soft colors, warm light, children's book style"
    },
    ...
  ]
}

Return ONLY valid JSON, nothing else. Ensure every panel follows this exact structure."""

    def __init__(self):
        """Initialize the Storyboard Agent."""
        super().__init__(
            role="Storyboard Agent",
            instructions=self.SYSTEM_INSTRUCTIONS
        )

    def create_storyboard(self, story_idea: str, num_panels: int, style: str = None) -> Dict:
        """
        Create a storyboard from a story idea.

        Args:
            story_idea: The story concept or theme
            num_panels: Number of panels to create
            style: Optional visual style for consistency

        Returns:
            Dict with 'title' and 'panels' keys
        """
        user_message = f"Story idea: {story_idea}\nNumber of panels: {num_panels}"
        if style:
            user_message += f"\nVisual style: {style}"

        try:
            response = self._call_llm(user_message, temperature=0.8, max_tokens=2000)

            # Parse JSON response
            storyboard = json.loads(response)

            # Validate structure
            if "title" not in storyboard or "panels" not in storyboard:
                raise ValueError("Invalid storyboard structure")

            if len(storyboard["panels"]) != num_panels:
                logger.warning(f"Expected {num_panels} panels, got {len(storyboard['panels'])}")

            logger.info(f"Created storyboard: '{storyboard['title']}' with {len(storyboard['panels'])} panels")
            return storyboard

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse storyboard JSON: {e}")
            # Return fallback structure
            return self._create_fallback_storyboard(story_idea, num_panels)
        except Exception as e:
            logger.error(f"Storyboard creation failed: {e}")
            return self._create_fallback_storyboard(story_idea, num_panels)

    def _create_fallback_storyboard(self, story_idea: str, num_panels: int) -> Dict:
        """Create a simple fallback storyboard if AI generation fails."""
        return {
            "title": f"Story: {story_idea[:50]}",
            "panels": [
                {
                    "panel_number": i + 1,
                    "description": f"Panel {i + 1} of the story: {story_idea}",
                    "image_prompt": f"{story_idea}, scene {i + 1}"
                }
                for i in range(num_panels)
            ]
        }

    def process(self, input_data: str) -> str:
        """Process method for compatibility."""
        result = self.create_storyboard(input_data, 4)
        return json.dumps(result)


# Singleton instance
storyboard_agent = StoryboardAgent()
