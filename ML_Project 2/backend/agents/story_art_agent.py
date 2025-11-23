"""Phase 3: Story Art Prompt Agent.

This agent generates detailed art prompts for each page:
- Positive prompts optimized for image generation
- Negative prompts to avoid unwanted elements
- Maintains visual consistency across pages
"""
import logging
import json
from typing import List, Dict, Optional
from agents.base_agent import BaseAgent
from core.exceptions import AIGenerationError
from core.json_utils import clean_and_parse_json

logger = logging.getLogger(__name__)


SYSTEM_INSTRUCTIONS = """You are a JSON-only assistant.

Given a list of story pages, you will generate art prompts for each page.
You MUST return **STRICT VALID JSON** in exactly the following format:

{
  "pages": [
    {
      "page_number": 1,
      "art_prompt": "single line string with NO raw newline characters",
      "negative_prompt": "single line string with NO raw newline characters"
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
   - Strings must be one line
   - If a newline is needed, ESCAPE it as \\n inside quotes
   - Do NOT insert line breaks inside JSON strings

3. **Do NOT add trailing commas.**

4. The output MUST begin with "{" and end with "}".

5. Fields:
   - art_prompt must be a single-line description of the illustration
   - negative_prompt must be a single-line comma-separated list of negative tokens
   - page_number must match the given page input

6. DO NOT invent extra keys. Only return: page_number, art_prompt, negative_prompt.

7. All JSON must validate with Python's json.loads().

VALID JSON EXAMPLE OUTPUT:

{
  "pages": [
    {
      "page_number": 1,
      "art_prompt": "storybook illustration of a small elephant in a cozy art studio, warm lighting, watercolor style, high detail",
      "negative_prompt": "blurry, deformed, scary, violent, dark, horror, ugly, low quality"
    }
  ]
}

End of rules."""


class StoryArtAgent(BaseAgent):
    """Agent for generating art prompts (Phase 3)."""

    def __init__(self):
        """Initialize the story art agent."""
        super().__init__(role="Story Art Agent", instructions=SYSTEM_INSTRUCTIONS)

    def generate_art_prompts(
        self,
        story_title: str,
        characters: List[str],
        age_range: str,
        style: Optional[str],
        pages_data: List[Dict],
        asset_context: Optional[str] = None,
    ) -> dict:
        """
        Generate art prompts for all pages.

        Args:
            story_title: The story title
            characters: List of character descriptions
            age_range: Target age range
            style: Visual style (e.g., "watercolor", "digital art")
            pages_data: List of pages with outlines, scene descriptions, and narration
            asset_context: Optional context from uploaded assets

        Returns:
            dict: Pages with art_prompt and negative_prompt

        Raises:
            AIGenerationError: If art prompt generation fails
        """
        # Determine style keywords
        style_keywords = self._get_style_keywords(style)

        # Build context for the LLM
        prompt = f"""Story: "{story_title}"
Age Range: {age_range}
Visual Style: {style or 'storybook illustration'}

Characters (maintain consistent appearance):
"""
        for char in characters:
            prompt += f"- {char}\n"

        if asset_context:
            prompt += f"\nREFERENCE MATERIALS:\n{asset_context}\n"
            prompt += "Use these visual references to ensure style consistency.\n"

        prompt += "\nPage Details:\n"
        for page in pages_data:
            prompt += f"""
Page {page['page_number']}: {page.get('title', '')}
Scene Description: {page.get('scene_description', '')}
Narration: {page.get('narration', '')}
"""
            if page.get('dialogues'):
                prompt += "Dialogue:\n"
                for dialogue in page['dialogues']:
                    prompt += f"  {dialogue.get('speaker', '')}: \"{dialogue.get('text', '')}\"\n"

        prompt += f"""
Now, create detailed art prompts for each page.
Include the style: {style_keywords}
Ensure characters look consistent across all pages.
Follow the JSON format specified in your instructions."""

        logger.info(f"Generating art prompts for {len(pages_data)} pages of '{story_title}'")

        try:
            # Call Ollama
            response_text = self._call_llm(prompt, temperature=0.7, max_tokens=2000)

            # Parse JSON response with robust cleanup
            try:
                art_data = clean_and_parse_json(response_text)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {e}")
                logger.error(f"Response text: {response_text}")
                raise AIGenerationError(f"Art prompt generation returned invalid JSON: {e}")

            # Validate structure
            if "pages" not in art_data or not isinstance(art_data["pages"], list):
                raise AIGenerationError("Art prompts must contain 'pages' array")

            if len(art_data["pages"]) != len(pages_data):
                logger.warning(
                    f"Generated {len(art_data['pages'])} art prompts but expected {len(pages_data)}"
                )

            # Validate each page
            for page in art_data["pages"]:
                if "page_number" not in page or "art_prompt" not in page:
                    raise AIGenerationError(f"Art prompt page missing required fields: {page}")
                if "negative_prompt" not in page:
                    # Provide default negative prompt
                    page["negative_prompt"] = (
                        "blurry, deformed, scary, violent, dark, horror, ugly, "
                        "distorted, low quality, text, watermark, signature"
                    )

            logger.info(f"Art prompts generated for {len(art_data['pages'])} pages")

            return art_data

        except AIGenerationError:
            raise
        except Exception as e:
            logger.exception(f"Unexpected error during art prompt generation: {e}")
            raise AIGenerationError(f"Art prompt generation failed: {str(e)}")

    @staticmethod
    def _get_style_keywords(style: Optional[str]) -> str:
        """Convert style enum to art prompt keywords."""
        style_map = {
            "realistic": "realistic, photorealistic, detailed",
            "artistic": "artistic, painterly, expressive",
            "anime": "anime style, manga, Japanese animation",
            "fantasy": "fantasy art, magical, whimsical",
            "sci-fi": "sci-fi, futuristic, science fiction",
            "watercolor": "watercolor painting, soft colors, gentle brush strokes",
            "oil painting": "oil painting, rich colors, textured canvas",
            "digital art": "digital art, clean lines, vibrant colors",
        }
        return style_map.get(style.lower() if style else "", "children's book illustration, storybook art")


# Singleton instance
story_art_agent = StoryArtAgent()
