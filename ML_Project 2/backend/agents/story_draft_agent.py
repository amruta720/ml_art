"""Phase 1: Story Draft & Outline Agent.

This agent generates a complete story outline with:
- Story title and logline
- Character descriptions
- Page-by-page outlines with scene descriptions
"""
import logging
import json
from typing import Optional
from agents.base_agent import BaseAgent
from core.exceptions import AIGenerationError
from core.json_utils import clean_and_parse_json

logger = logging.getLogger(__name__)


SYSTEM_INSTRUCTIONS = """You are a JSON-only assistant for creating children's storybook outlines.

You MUST return **STRICT VALID JSON** in exactly the following format:

{
  "title": "The Story Title",
  "logline": "One sentence summary of the story",
  "age_range": "4-7",
  "characters": [
    "Character name: brief description as a SINGLE STRING",
    "Another character: brief description as a SINGLE STRING"
  ],
  "pages": [
    {
      "page_number": 1,
      "title": "Page Title",
      "outline": "Brief description of what happens on this page",
      "scene_description": "Detailed visual description for illustration"
    }
  ]
}

RULES (must follow 100% strictly):

1. **Respond with JSON ONLY.**
   - No markdown
   - No backticks
   - No commentary
   - No text outside the JSON object

2. **ABSOLUTELY NO RAW NEWLINES inside any string.**
   - All string values must be single-line
   - If a newline is needed, ESCAPE it as \\n inside quotes
   - Do NOT insert line breaks inside JSON strings

3. **Characters MUST be simple strings, NOT objects.**
   - CORRECT: "Ellie the Elephant: A small brown elephant with big floppy ears who loves art"
   - WRONG: {"name": "Ellie", "description": "A small elephant"}
   - Each character is ONE string with format "Name: description"

4. **Do NOT add trailing commas.**

5. The output MUST begin with "{" and end with "}".

6. All JSON must validate with Python's json.loads().

7. Create age-appropriate, wholesome content with a clear story arc (beginning, middle, end).

VALID JSON EXAMPLE OUTPUT:

{
  "title": "Ellie's Big Adventure",
  "logline": "A small elephant discovers her talent for painting and shares joy with her friends",
  "age_range": "4-7",
  "characters": [
    "Ellie: A small brown elephant with big floppy ears who loves art",
    "Birdie: A cheerful blue bird who encourages Ellie"
  ],
  "pages": [
    {
      "page_number": 1,
      "title": "A Curious Discovery",
      "outline": "Ellie finds colorful paints in the forest and wonders what they are for",
      "scene_description": "A small brown elephant with big floppy ears standing in a sunny forest clearing, looking curiously at colorful paint jars on the ground, dappled sunlight through trees, watercolor style, warm and inviting"
    }
  ]
}

End of rules."""


class StoryDraftAgent(BaseAgent):
    """Agent for generating story outlines and structure (Phase 1)."""

    def __init__(self):
        """Initialize the story draft agent."""
        super().__init__(role="Story Draft Agent", instructions=SYSTEM_INSTRUCTIONS)

    def generate_story_outline(
        self,
        story_idea: str,
        num_pages: int,
        age_range: str = "4-7",
        style: Optional[str] = None,
        asset_context: Optional[str] = None,
    ) -> dict:
        """
        Generate a complete story outline.

        Args:
            story_idea: The story concept or theme
            num_pages: Number of pages (4-16)
            age_range: Target age range (e.g., "4-7")
            style: Optional visual style preference
            asset_context: Optional context from uploaded assets

        Returns:
            dict: Story outline with title, logline, characters, and page outlines

        Raises:
            AIGenerationError: If story generation fails
        """
        # Build the user prompt
        prompt = f"""Create a {num_pages}-page children's storybook outline.

Story Idea: {story_idea}
Target Age Range: {age_range}
Number of Pages: {num_pages}"""

        if style:
            prompt += f"\nVisual Style: {style}"

        if asset_context:
            prompt += f"\n\nREFERENCE MATERIALS PROVIDED:\n{asset_context}\n"
            prompt += "Use these references to inform the story's visual style, characters, or themes."

        prompt += """

Generate a complete story outline following the JSON format specified in your instructions.
Make it engaging, age-appropriate, and visually rich for illustrations."""

        logger.info(f"Generating story outline for: {story_idea} ({num_pages} pages)")

        try:
            # Call Ollama
            response_text = self._call_llm(prompt, temperature=0.7, max_tokens=2000)

            # Parse JSON response with robust cleanup
            try:
                story_data = clean_and_parse_json(response_text)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {e}")
                logger.error(f"Response text: {response_text}")
                raise AIGenerationError(f"Story outline generation returned invalid JSON: {e}")

            # Validate structure
            required_keys = ["title", "logline", "pages"]
            missing_keys = [key for key in required_keys if key not in story_data]
            if missing_keys:
                raise AIGenerationError(f"Story outline missing required keys: {missing_keys}")

            if not isinstance(story_data["pages"], list) or len(story_data["pages"]) == 0:
                raise AIGenerationError("Story outline must contain at least one page")

            # Ensure age_range and characters exist
            if "age_range" not in story_data:
                story_data["age_range"] = age_range
            if "characters" not in story_data:
                story_data["characters"] = []

            logger.info(f"Story outline generated: '{story_data['title']}' ({len(story_data['pages'])} pages)")

            return story_data

        except AIGenerationError:
            raise
        except Exception as e:
            logger.exception(f"Unexpected error during story outline generation: {e}")
            raise AIGenerationError(f"Story outline generation failed: {str(e)}")


# Singleton instance
story_draft_agent = StoryDraftAgent()
