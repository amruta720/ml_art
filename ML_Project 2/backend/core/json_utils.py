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
        logger.error(f"Problematic text (first 500 chars): {text[:500]}")
        raise


def fix_common_json_issues(text: str) -> str:
    """
    Fix common JSON syntax issues from LLM output.

    Args:
        text: JSON text with potential issues

    Returns:
        str: Fixed JSON text
    """
    # Remove trailing commas before closing braces/brackets
    text = re.sub(r',(\s*[}\]])', r'\1', text)

    # Fix single quotes to double quotes (careful with contractions)
    # Only replace single quotes that look like JSON string delimiters
    text = re.sub(r"'([^']*)'(\s*:)", r'"\1"\2', text)  # Keys
    text = re.sub(r":\s*'([^']*)'", r': "\1"', text)    # Values after colons

    # Fix unescaped newlines in strings
    # This is tricky - we need to find strings and escape newlines in them
    # For now, just remove literal newlines between quotes
    text = re.sub(r'"\s*\n\s*"', '" "', text)

    # Fix missing commas between array elements (heuristic)
    # Look for }\n\s*{ pattern (two objects without comma between)
    text = re.sub(r'}\s*\n\s*{', '},\n{', text)

    # Fix missing commas between object properties (heuristic)
    # Look for "\n\s*" pattern (string value followed by new property without comma)
    text = re.sub(r'"\s*\n\s*"([^"]+)"(\s*:)', r'",\n"\1"\2', text)

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
