from crewai_tools import BaseTool
from groq import Groq
import os
import json
import logging
from typing import Optional
from utils.debugging import debug_groq_call
import time

logger = logging.getLogger(__name__)

class GroqLLM:
    """Groq Language Model implementation for CrewAI"""

    def __init__(self,
                 model: str = "llama-3.1-405b-reasoning",
                 temperature: float = 0.7,
                 max_tokens: int = 4000):
        """
        Initialize Groq LLM

        Args:
            model: Groq model name
            temperature: Response creativity (0.0 to 1.0)
            max_tokens: Maximum tokens in response
        """
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY environment variable is required")

        self.client = Groq(api_key=self.api_key)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

        logger.info(f"Initialized GroqLLM with model: {model}")

    def __call__(self, prompt: str) -> str:
        """
        Call Groq API with prompt

        Args:
            prompt: Input prompt for the model

        Returns:
            Generated response text
        """
        start_time = time.time()

        try:
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "user", "content": prompt}
                ],
                model=self.model,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                stream=False
            )

            result = response.choices[0].message.content
            execution_time = time.time() - start_time

            # Debug the API call
            debug_groq_call(prompt, result, execution_time)

            return result

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Groq API call failed: {str(e)}")
            debug_groq_call(prompt, f"ERROR: {str(e)}", execution_time)

            # Return error message instead of raising to prevent CrewAI crashes
            return f"Error calling Groq API: {str(e)}"

    def generate(self, prompt: str) -> str:
        """Alternative method name for compatibility"""
        return self.__call__(prompt)

    def bind(self, stop: list):
        """
        This method is a required workaround for CrewAI.
        It must be present for CrewAI to correctly handle
        stop sequences when using custom LLMs.
        """
        return self