"""Custom exceptions for the application."""


class AIGenerationError(Exception):
    """Raised when AI generation fails."""
    pass


class ModelNotLoadedError(Exception):
    """Raised when trying to use an unloaded model."""
    pass


class InvalidPromptError(Exception):
    """Raised when prompt validation fails."""
    pass


class StabilityInsufficientBalanceError(Exception):
    """Raised when Stability AI API returns insufficient balance/credits error."""
    pass
