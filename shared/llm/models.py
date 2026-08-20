from typing import Any, Generic, Literal, TypeVar

from pydantic import BaseModel, Field


class ProviderCapabilities(BaseModel):
    streaming: bool = True
    structured_output: bool = True
    tool_calling: bool = False
    usage_metadata: bool = True


class TokenUsage(BaseModel):
    input_tokens: int | None = Field(default=None, ge=0)
    output_tokens: int | None = Field(default=None, ge=0)
    total_tokens: int | None = Field(default=None, ge=0)


class LLMRequest(BaseModel):
    input: str = Field(min_length=1)
    instructions: str | None = None
    context: list[str] = Field(default_factory=list)
    sources: list[str] = Field(default_factory=list)
    tools: list[dict[str, Any]] = Field(default_factory=list)
    tool_choice: str | dict[str, Any] | None = None


class GroundedAnswer(BaseModel):
    answer: str = Field(min_length=1)
    sources: list[str] = Field(default_factory=list)


class LLMResult(BaseModel):
    output: str
    request_id: str
    provider: str
    model: str
    usage: TokenUsage = Field(default_factory=TokenUsage)


StructuredOutputT = TypeVar("StructuredOutputT", bound=BaseModel)


class StructuredLLMResult(BaseModel, Generic[StructuredOutputT]):
    output: StructuredOutputT
    request_id: str
    provider: str
    model: str
    usage: TokenUsage = Field(default_factory=TokenUsage)


class LLMStreamEvent(BaseModel):
    type: Literal["delta", "completed"]
    delta: str | None = None
    request_id: str | None = None
    provider: str
    model: str
    usage: TokenUsage = Field(default_factory=TokenUsage)
