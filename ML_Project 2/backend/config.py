"""Application configuration using Pydantic settings."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Ollama Configuration (Free Local LLM)
    ollama_model: str = "llama3.2"
    ollama_host: str = "http://localhost:11434"

    # Image Generation Backend Selection
    # Options: "local_diffusion", "stability_ai", or "gemini_imagen"
    image_backend: str = "local_diffusion"

    # Stability AI Configuration (only used if image_backend = "stability_ai")
    # Get your API key from https://platform.stability.ai/account/keys
    stability_api_key: Optional[str] = None

    # Google Gemini Configuration (only used if image_backend = "gemini_imagen")
    # Set GEMINI_API_KEY in environment variables
    gemini_api_key: Optional[str] = None

    # Stable Diffusion Configuration
    # Using runwayml/stable-diffusion-v1-5 (publicly available, no auth required)
    stable_diffusion_model: str = "runwayml/stable-diffusion-v1-5"

    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000

    # File Storage
    static_dir: str = "static/images"
    max_image_size: int = 1024

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()
