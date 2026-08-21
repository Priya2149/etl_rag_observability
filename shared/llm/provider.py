from abc import ABC, abstractmethod
from collections.abc import Iterator
from typing import TypeVar

from pydantic import BaseModel

from .models import (
    LLMRequest,
    LLMResult,
    LLMStreamEvent,
    ProviderCapabilities,
    StructuredLLMResult,
    ToolResultContinuation,
    ToolSelectionResult,
)

StructuredOutputT = TypeVar("StructuredOutputT", bound=BaseModel)


class LLMProvider(ABC):
    name: str
    model: str
    capabilities: ProviderCapabilities

    @abstractmethod
    def generate(self, request: LLMRequest) -> LLMResult:
        raise NotImplementedError

    @abstractmethod
    def generate_structured(
        self,
        request: LLMRequest,
        response_model: type[StructuredOutputT],
    ) -> StructuredLLMResult[StructuredOutputT]:
        raise NotImplementedError

    @abstractmethod
    def stream(self, request: LLMRequest) -> Iterator[LLMStreamEvent]:
        raise NotImplementedError

    def select_tools(self, request: LLMRequest) -> ToolSelectionResult:
        raise NotImplementedError

    def generate_structured_with_tool_results(
        self,
        request: LLMRequest,
        continuation: ToolResultContinuation,
        response_model: type[StructuredOutputT],
    ) -> StructuredLLMResult[StructuredOutputT]:
        raise NotImplementedError
