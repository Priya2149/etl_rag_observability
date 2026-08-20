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
