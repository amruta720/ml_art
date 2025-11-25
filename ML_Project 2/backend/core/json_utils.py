"""Utilities for handling JSON parsing with LLM-generated content."""
import json
import re
import logging

logger = logging.getLogger(__name__)


def clean_and_parse_json(response_text: str) -> dict:
    """
    Clean and parse JSON from LLM response, handling common formatting issues.

    Args:
        response_text: Raw text response from LLM

    Returns:
        dict: Parsed JSON object

    Raises:
        json.JSONDecodeError: If JSON cannot be parsed after cleanup attempts
    """
    # Step 1: Remove markdown code blocks
    text = response_text.strip()
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()

    # Remove invisible/control characters except newlines and tabs
    # Keep \n (10), \r (13), \t (9) but remove other control chars
    text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\r\t')

    # Step 2: Try parsing as-is
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        logger.warning(f"Initial JSON parse failed: {e}")

    # Step 3: Try to fix common issues
    try:
        text = fix_common_json_issues(text)
        return json.loads(text)
    except json.JSONDecodeError as e:
        logger.error(f"JSON repair failed: {e}")
        logger.error(f"Full response length: {len(text)} characters")
        logger.error(f"Response (first 1000 chars): {text[:1000]}")
        logger.error(f"Response (last 500 chars): {text[-500:]}")

        # Debug: show hex dump of problematic area
        if hasattr(e, 'pos') and e.pos:
            start = max(0, e.pos - 20)
            end = min(len(text), e.pos + 20)
            problem_area = text[start:end]
            hex_dump = ' '.join(f'{ord(c):02x}' for c in problem_area)
            logger.error(f"Hex dump around error position {e.pos}: {hex_dump}")
            logger.error(f"Text around error: {repr(problem_area)}")

        raise


def fix_common_json_issues(text: str) -> str:
    """
    Fix common JSON syntax issues from LLM output.

    Args:
        text: JSON text with potential issues

    Returns:
        str: Fixed JSON text
    """
    # Only apply fixes if needed - don't break valid JSON!
    # First, try to parse as-is
    try:
        json.loads(text)
        # JSON is valid, return it unchanged
        return text
    except json.JSONDecodeError:
        # JSON is broken, apply fixes
        pass

    # Remove trailing commas before closing braces/brackets
    text = re.sub(r',(\s*[}\]])', r'\1', text)

    # Fix missing commas between array elements
    # Look for }\n\s*{ pattern (two objects without comma between)
    text = re.sub(r'}\s*\n\s*{', '},\n{', text)

    # Fix incomplete JSON - check if braces/brackets are balanced
    text = balance_json_brackets(text)

    return text


def balance_json_brackets(text: str) -> str:
    """
    Ensure JSON has balanced brackets and braces.

    Args:
        text: JSON text

    Returns:
        str: JSON with balanced brackets
    """
    # Count opening and closing braces/brackets
    open_brace = text.count('{')
    close_brace = text.count('}')
    open_bracket = text.count('[')
    close_bracket = text.count(']')

    # Add missing closing braces
    if open_brace > close_brace:
        text = text.rstrip() + '\n' + ('  ' * (open_bracket - close_bracket)) + ('}' * (open_brace - close_brace))

    # Add missing closing brackets
    if open_bracket > close_bracket:
        text = text.rstrip() + (']' * (open_bracket - close_bracket))

    return text


def extract_json_from_text(text: str) -> str:
    """
    Extract JSON object from text that may contain other content.

    Args:
        text: Text containing JSON

    Returns:
        str: Extracted JSON text
    """
    # Try to find JSON object boundaries
    # Look for outermost { ... } or [ ... ]

    # Find first { or [
    start_brace = text.find('{')
    start_bracket = text.find('[')

    if start_brace == -1 and start_bracket == -1:
        return text

    # Use whichever comes first
    if start_brace != -1 and (start_bracket == -1 or start_brace < start_bracket):
        start = start_brace
        opener = '{'
        closer = '}'
    else:
        start = start_bracket
        opener = '['
        closer = ']'

    # Find matching closer
    depth = 0
    for i in range(start, len(text)):
        if text[i] == opener:
            depth += 1
        elif text[i] == closer:
            depth -= 1
            if depth == 0:
                return text[start:i+1]

    # If we didn't find a matching closer, return everything from start
    return text[start:]
