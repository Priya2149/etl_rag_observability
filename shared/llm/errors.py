class LLMError(Exception):
    """Base error for provider-independent LLM failures."""


class LLMConfigurationError(LLMError):
    """Raised when the selected provider is not configured safely."""


class LLMProviderError(LLMError):
    """Raised when an outbound provider request fails."""


class LLMRateLimitError(LLMProviderError):
    """Raised when a provider rate limit remains exhausted after retries."""
