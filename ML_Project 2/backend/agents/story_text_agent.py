"""Phase 2: Story Text & Dialogue Agent.

This agent takes a story outline and generates:
- Flowing narration for each page
- Character dialogues
- Maintains consistency across pages
"""
import logging
import json
from typing import List, Dict, Optional
from agents.base_agent import BaseAgent
from core.exceptions import AIGenerationError
from core.json_utils import clean_and_parse_json

logger = logging.getLogger(__name__)


SYSTEM_INSTRUCTIONS = """You are a JSON-only assistant for creating children's storybook narration and dialogue.

You MUST return **STRICT VALID JSON** in exactly the following format:

{
  "pages": [
    {
      "page_number": 1,
      "narration": "single line narration text with NO raw newline characters",
      "dialogues": [
        {
          "speaker": "Character Name",
          "text": "What the character says"
        }
      ]
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
   - All string values (narration, dialogue text) must be single-line
   - If a paragraph break is needed, use \\n inside quotes
   - Do NOT insert line breaks inside JSON strings

3. **Do NOT add trailing commas.**

4. The output MUST begin with "{" and end with "}".

5. All JSON must validate with Python's json.loads().

6. Write engaging, age-appropriate prose:
   - Use simple, clear language
   - Include sensory details
   - Keep narration focused and concise
   - Make dialogue sound natural

7. Dialogues can be empty array [] if no dialogue is needed on that page.

VALID JSON EXAMPLE OUTPUT:

{
  "pages": [
    {
      "page_number": 1,
      "narration": "Ellie the elephant discovers a box of colorful paints in the sunny forest clearing. Her big floppy ears perk up with curiosity as she carefully picks up a paintbrush with her trunk. The forest sparkles with morning light, and Ellie feels a flutter of excitement in her chest.",
      "dialogues": [
        {
          "speaker": "Ellie",
          "text": "What beautiful colors! I wonder what these are for?"
        }
      ]
    }
  ]
}

End of rules."""


class StoryTextAgent(BaseAgent):
    """Agent for generating narration and dialogue (Phase 2)."""

    def __init__(self):
        """Initialize the story text agent."""
        super().__init__(role="Story Text Agent", instructions=SYSTEM_INSTRUCTIONS)

    def generate_page_text(
        self,
        story_title: str,
        story_logline: str,
        characters: List[str],
        age_range: str,
        pages_outline: List[Dict],
    ) -> dict:
        """
        Generate narration and dialogue for all pages.

        Args:
            story_title: The story title
            story_logline: One-sentence story summary
            characters: List of character descriptions
            age_range: Target age range
            pages_outline: List of page outlines from Phase 1

        Returns:
            dict: Pages with narration and dialogues

        Raises:
            AIGenerationError: If text generation fails
        """
        # Build context for the LLM
        prompt = f"""Story: "{story_title}"
Logline: {story_logline}
Age Range: {age_range}

Characters:
"""
        for char in characters:
            prompt += f"- {char}\n"

        prompt += "\nPage Outlines:\n"
        for page in pages_outline:
            prompt += f"""
Page {page['page_number']}: {page['title']}
Outline: {page['outline']}
Scene: {page['scene_description']}
"""

        prompt += """
Now, write flowing narration and natural dialogue for each page.
Follow the JSON format specified in your instructions.
Make the text engaging, age-appropriate, and emotionally resonant."""

        logger.info(f"Generating text for {len(pages_outline)} pages of '{story_title}'")

        try:
            # Call Ollama
            response_text = self._call_llm(prompt, temperature=0.7, max_tokens=2000)

            # Parse JSON response with robust cleanup
            try:
                text_data = clean_and_parse_json(response_text)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {e}")
                logger.error(f"Response text: {response_text}")
                raise AIGenerationError(f"Story text generation returned invalid JSON: {e}")

            # Validate structure
            if "pages" not in text_data or not isinstance(text_data["pages"], list):
                raise AIGenerationError("Story text must contain 'pages' array")

            if len(text_data["pages"]) != len(pages_outline):
                logger.warning(
                    f"Generated {len(text_data['pages'])} pages but expected {len(pages_outline)}"
                )

            # Validate each page
            for page in text_data["pages"]:
                if "page_number" not in page or "narration" not in page:
                    raise AIGenerationError(f"Page missing required fields: {page}")
                if "dialogues" not in page:
                    page["dialogues"] = []

            logger.info(f"Story text generated for {len(text_data['pages'])} pages")

            return text_data

        except AIGenerationError:
            raise
        except Exception as e:
            logger.exception(f"Unexpected error during story text generation: {e}")
            raise AIGenerationError(f"Story text generation failed: {str(e)}")


# Singleton instance
story_text_agent = StoryTextAgent()
