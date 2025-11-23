"""Text Editor Agent for inline text editing."""
import logging
from typing import Optional

from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class TextEditorAgent(BaseAgent):
    """Agent that rewrites small pieces of text in children's storybooks."""

    SYSTEM_INSTRUCTIONS = """You are an assistant that rewrites small pieces of text in children's storybooks.

Your role:
1. Read the original text and the user's editing instruction
2. Apply the instruction to rewrite the text
3. Keep the text child-friendly, wholesome, and appropriate for children
4. Maintain the original meaning unless the instruction explicitly changes it
5. Keep the length similar to the original (unless instructed otherwise)
6. Use natural, age-appropriate language

CRITICAL: Respond with ONLY the rewritten text, nothing else. No explanations, no quotes, no formatting - just the edited text itself."""

    def __init__(self):
        """Initialize the Text Editor Agent."""
        super().__init__(
            role="Text Editor Agent",
            instructions=self.SYSTEM_INSTRUCTIONS
        )

    def edit_text(
        self,
        original_text: str,
        instruction: str,
        context: Optional[str] = None
    ) -> str:
        """
        Edit a piece of text according to the instruction.

        Args:
            original_text: The text to edit
            instruction: How to edit the text
            context: Optional context about the text (e.g., "Kid talking to robot")

        Returns:
            The edited text
        """
        user_message = f"Original text: {original_text}\n\nInstruction: {instruction}"
        if context:
            user_message = f"Context: {context}\n\n{user_message}"

        try:
            edited_text = self._call_llm(user_message, temperature=0.7, max_tokens=500)

            # Clean up the response (remove quotes if present)
            edited_text = edited_text.strip()
            if edited_text.startswith('"') and edited_text.endswith('"'):
                edited_text = edited_text[1:-1]
            if edited_text.startswith("'") and edited_text.endswith("'"):
                edited_text = edited_text[1:-1]

            logger.info(f"Edited text: '{original_text}' -> '{edited_text}'")
            return edited_text

        except Exception as e:
            logger.error(f"Text editing failed: {e}")
            # Return original text as fallback
            return original_text

    def process(self, input_data: str) -> str:
        """Process method for compatibility."""
        return self.edit_text(input_data, "improve this text")


# Singleton instance
text_editor_agent = TextEditorAgent()
