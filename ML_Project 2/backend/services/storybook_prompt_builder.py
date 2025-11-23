"""Helper functions for building storybook image prompts."""
from typing import Optional, Tuple


def build_storybook_image_prompt(
    scene_description: str,
    style_preset: Optional[str] = None,
    tone: str = "wholesome, child-friendly",
) -> Tuple[str, Optional[str]]:
    """
    Build a (prompt, negative_prompt) suitable for storybook illustrations.

    Args:
        scene_description: Description of the visual scene
        style_preset: Optional style (e.g., "watercolor", "digital art")
        tone: Tone/mood for the illustration

    Returns:
        Tuple of (positive_prompt, negative_prompt)
    """
    # Build positive prompt
    style_keywords = "storybook illustration, children's book art, soft colors, clean lines, high quality"

    if style_preset:
        style_keywords += f", {style_preset} style"

    positive_prompt = f"{scene_description}, {style_keywords}, {tone}"

    # Build negative prompt (things to avoid in children's books)
    negative_prompt = (
        "gore, blood, violence, horror, disturbing, NSFW, scary, deformed, "
        "glitch, watermark, text, signature, extra limbs, malformed, "
        "low quality, blurry, dark, gloomy, sad"
    )

    return positive_prompt, negative_prompt


def enhance_storybook_prompt_with_style(
    image_prompt: str,
    style_preset: Optional[str] = None,
) -> str:
    """
    Enhance an existing image prompt with storybook-specific styling.

    Args:
        image_prompt: The base image prompt
        style_preset: Optional style preset

    Returns:
        Enhanced prompt with storybook styling
    """
    enhancements = []

    # Add storybook-specific keywords if not already present
    if "storybook" not in image_prompt.lower() and "children's book" not in image_prompt.lower():
        enhancements.append("storybook illustration")
        enhancements.append("children's book art")

    # Add quality keywords
    if "high quality" not in image_prompt.lower():
        enhancements.append("high quality")

    # Add style preset
    if style_preset and style_preset.lower() not in image_prompt.lower():
        enhancements.append(f"{style_preset} style")

    # Add wholesome keywords
    if "wholesome" not in image_prompt.lower():
        enhancements.append("wholesome")

    # Combine
    if enhancements:
        return f"{image_prompt}, {', '.join(enhancements)}"
    return image_prompt
