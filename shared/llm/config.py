import os

from pydantic import BaseModel, Field, field_validator


class LLMSettings(BaseModel):
    provider: str = "none"
    openai_api_key: str | None = None
    openai_model: str = ""
    timeout_seconds: float = Field(default=60, gt=0)
    max_retries: int = Field(default=2, ge=0, le=5)
    retry_base_seconds: float = Field(default=0.5, ge=0)

    @field_validator("provider")
    @classmethod
    def normalize_provider(cls, value: str) -> str:
        return value.strip().lower()

    @classmethod
    def from_env(cls) -> "LLMSettings":
        return cls(
            provider=os.getenv("LLM_PROVIDER", "none"),
            openai_api_key=os.getenv("OPENAI_API_KEY") or None,
            openai_model=os.getenv("OPENAI_MODEL", ""),
            timeout_seconds=os.getenv("LLM_TIMEOUT_SECONDS", "60"),
            max_retries=os.getenv("LLM_MAX_RETRIES", "2"),
            retry_base_seconds=os.getenv("LLM_RETRY_BASE_SECONDS", "0.5"),
        )
