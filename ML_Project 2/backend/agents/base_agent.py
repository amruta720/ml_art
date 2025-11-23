"""Base agent class for LLM interactions using Ollama (free local LLM)."""
import ollama
from typing import Optional
import logging

from config import settings

logger = logging.getLogger(__name__)


class BaseAgent:
    """Base class for all AI agents using Ollama."""

    def __init__(self, role: str, instructions: str):
        """
        Initialize the base agent.

        Args:
            role: The agent's role/name
            instructions: System instructions for the agent
        """
        self.role = role
        self.instructions = instructions
        self.model = settings.ollama_model
        self.client = ollama.Client(host=settings.ollama_host)
        logger.info(f"Initialized {role} agent with Ollama model: {self.model}")

    def _call_llm(
        self,
        user_message: str,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """
        Call the LLM with the given message using Ollama.

        Args:
            user_message: User message to send
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Returns:
            str: LLM response
        """
        try:
            # Combine system instructions and user message
            full_prompt = f"{self.instructions}\n\nUser: {user_message}\nAssistant:"

            response = self.client.generate(
                model=self.model,
                prompt=full_prompt,
                options={
                    "temperature": temperature,
                    "num_predict": max_tokens,
                }
            )

            result = response['response'].strip()
            logger.info(f"{self.role} generated response")
            return result
        except Exception as e:
            logger.error(f"{self.role} LLM call failed: {e}")
            logger.warning(f"Make sure Ollama is running and model '{self.model}' is downloaded")
            raise

    def process(self, input_data: str) -> str:
        """
        Process input data. To be overridden by subclasses.

        Args:
            input_data: Input to process

        Returns:
            str: Processed output
        """
        raise NotImplementedError("Subclasses must implement process()")
