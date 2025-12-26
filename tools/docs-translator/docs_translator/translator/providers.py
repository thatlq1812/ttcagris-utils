"""AI Provider implementations."""

from abc import ABC, abstractmethod
from typing import Optional

from tenacity import (
    retry, 
    stop_after_attempt, 
    wait_exponential, 
    retry_if_exception_type,
    before_sleep_log,
)

from docs_translator.logging import get_logger, debug, warning, error

logger = get_logger()


class TranslationError(Exception):
    """Error during translation."""

    pass


class RateLimitError(TranslationError):
    """API rate limit exceeded."""

    pass


class BaseProvider(ABC):
    """Abstract base class for AI providers."""

    def __init__(
        self,
        api_key: str,
        model: str,
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ):
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self._client = None
        debug(f"Initialized {self.__class__.__name__} with model: {model}")

    @abstractmethod
    def _init_client(self):
        """Initialize the API client."""
        pass

    @abstractmethod
    def translate(self, text: str, system_prompt: str) -> str:
        """Translate text using the AI model.

        Args:
            text: Text to translate
            system_prompt: System instruction for translation

        Returns:
            Translated text
        """
        pass

    @property
    def client(self):
        """Lazy-load the client."""
        if self._client is None:
            self._init_client()
        return self._client


class GeminiProvider(BaseProvider):
    """Google Gemini provider."""

    def _init_client(self):
        """Initialize Gemini client."""
        try:
            import google.generativeai as genai

            genai.configure(api_key=self.api_key)
            self._genai = genai
            debug("Gemini client initialized")
        except ImportError:
            raise ImportError("google-generativeai package not installed. Run: pip install google-generativeai")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=60),
        retry=retry_if_exception_type((RateLimitError, ConnectionError)),
        before_sleep=before_sleep_log(logger, 30),  # WARNING level
        reraise=True,
    )
    def translate(self, text: str, system_prompt: str) -> str:
        """Translate using Gemini."""
        _ = self.client  # Ensure client is initialized

        try:
            # Ensure model name has correct format
            model_name = self.model
            if not model_name.startswith("models/"):
                model_name = f"models/{model_name}"
            
            # Create model with system instruction
            model = self._genai.GenerativeModel(
                model_name=model_name,
                system_instruction=system_prompt,
                generation_config={
                    "temperature": self.temperature,
                    "max_output_tokens": self.max_tokens,
                },
            )

            response = model.generate_content(text)

            if not response.text:
                raise TranslationError("Empty response from Gemini")

            return response.text.strip()

        except Exception as e:
            error_str = str(e).lower()
            if "quota" in error_str or "rate" in error_str or "429" in error_str:
                warning(f"Gemini rate limit hit, will retry: {e}")
                raise RateLimitError(f"Gemini rate limit: {e}")
            error(f"Gemini error: {e}")
            raise TranslationError(f"Gemini error: {e}")


class OpenAIProvider(BaseProvider):
    """OpenAI provider."""

    def _init_client(self):
        """Initialize OpenAI client."""
        try:
            from openai import OpenAI

            self._client = OpenAI(api_key=self.api_key)
            debug("OpenAI client initialized")
        except ImportError:
            raise ImportError("openai package not installed. Run: pip install openai")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=60),
        retry=retry_if_exception_type((RateLimitError, ConnectionError)),
        before_sleep=before_sleep_log(logger, 30),
        reraise=True,
    )
    def translate(self, text: str, system_prompt: str) -> str:
        """Translate using OpenAI."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text},
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )

            if not response.choices:
                raise TranslationError("Empty response from OpenAI")

            return response.choices[0].message.content.strip()

        except Exception as e:
            error_str = str(e).lower()
            if "rate" in error_str or "429" in error_str:
                warning(f"OpenAI rate limit hit, will retry: {e}")
                raise RateLimitError(f"OpenAI rate limit: {e}")
            error(f"OpenAI error: {e}")
            raise TranslationError(f"OpenAI error: {e}")


class ClaudeProvider(BaseProvider):
    """Anthropic Claude provider."""

    def _init_client(self):
        """Initialize Claude client."""
        try:
            import anthropic

            self._client = anthropic.Anthropic(api_key=self.api_key)
            debug("Claude client initialized")
        except ImportError:
            raise ImportError("anthropic package not installed. Run: pip install anthropic")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=60),
        retry=retry_if_exception_type((RateLimitError, ConnectionError)),
        before_sleep=before_sleep_log(logger, 30),
        reraise=True,
    )
    def translate(self, text: str, system_prompt: str) -> str:
        """Translate using Claude."""
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": text},
                ],
            )

            if not response.content:
                raise TranslationError("Empty response from Claude")

            return response.content[0].text.strip()

        except Exception as e:
            error_str = str(e).lower()
            if "rate" in error_str or "429" in error_str:
                warning(f"Claude rate limit hit, will retry: {e}")
                raise RateLimitError(f"Claude rate limit: {e}")
            error(f"Claude error: {e}")
            raise TranslationError(f"Claude error: {e}")


def create_provider(
    provider_name: str,
    api_key: str,
    model: str,
    temperature: float = 0.3,
    max_tokens: int = 4096,
) -> BaseProvider:
    """Factory function to create the appropriate provider.

    Args:
        provider_name: 'gemini', 'openai', or 'claude'
        api_key: API key for the provider
        model: Model ID to use
        temperature: Generation temperature
        max_tokens: Maximum tokens for response

    Returns:
        Appropriate provider instance
    """
    providers = {
        "gemini": GeminiProvider,
        "openai": OpenAIProvider,
        "claude": ClaudeProvider,
    }

    if provider_name not in providers:
        raise ValueError(f"Unknown provider: {provider_name}. Choose from: {list(providers.keys())}")

    return providers[provider_name](
        api_key=api_key,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
    )
