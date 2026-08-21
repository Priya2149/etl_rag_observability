from collections.abc import Callable, Iterable
from dataclasses import dataclass
from time import perf_counter
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ValidationError

from .models import ToolCall, ToolExecutionResult

ToolInputT = TypeVar("ToolInputT", bound=BaseModel)
ToolOutputT = TypeVar("ToolOutputT", bound=BaseModel)


class ToolExecutionError(RuntimeError):
    """A safe, user-facing tool failure without an internal traceback."""


@dataclass(frozen=True)
class ApplicationTool(Generic[ToolInputT, ToolOutputT]):
    name: str
    description: str
    input_model: type[ToolInputT]
    output_model: type[ToolOutputT]
    handler: Callable[[ToolInputT], ToolOutputT]

    def openai_definition(self) -> dict[str, Any]:
        schema = _strict_json_schema(self.input_model.model_json_schema())
        return {
            "type": "function",
            "name": self.name,
            "description": self.description,
            "parameters": schema,
            "strict": True,
        }


def _strict_json_schema(value: Any) -> Any:
    if isinstance(value, dict):
        schema = {key: _strict_json_schema(item) for key, item in value.items()}
        if schema.get("type") == "object" or "properties" in schema:
            properties = schema.get("properties", {})
            schema["additionalProperties"] = False
            schema["required"] = list(properties)
        schema.pop("default", None)
        return schema
    if isinstance(value, list):
        return [_strict_json_schema(item) for item in value]
    return value


class ToolRegistry:
    def __init__(self, tools: Iterable[ApplicationTool[Any, Any]] = ()):
        self._tools = {tool.name: tool for tool in tools}

    @property
    def names(self) -> list[str]:
        return list(self._tools)

    def definitions(self, names: Iterable[str] | None = None) -> list[dict[str, Any]]:
        selected = self._select(names)
        return [tool.openai_definition() for tool in selected]

    def execute(self, call: ToolCall) -> ToolExecutionResult:
        started_at = perf_counter()
        tool = self._tools.get(call.name)
        if tool is None:
            return self._failure(call, started_at, f"Unknown tool '{call.name}'.")
        if not call.arguments_valid:
            return self._failure(
                call, started_at, f"Invalid arguments for tool '{call.name}'."
            )

        try:
            tool_input = tool.input_model.model_validate(call.arguments)
            output = tool.output_model.model_validate(tool.handler(tool_input))
        except ValidationError:
            return self._failure(
                call, started_at, f"Invalid arguments for tool '{call.name}'."
            )
        except ToolExecutionError as exc:
            return self._failure(call, started_at, str(exc))
        except Exception:  # noqa: BLE001
            return self._failure(call, started_at, f"Tool '{call.name}' failed.")

        data = output.model_dump(mode="json")
        return ToolExecutionResult(
            call_id=call.call_id,
            name=call.name,
            success=True,
            data=data,
            duration_ms=round((perf_counter() - started_at) * 1000),
            sources=list(data.get("sources", [])),
        )

    def _select(self, names: Iterable[str] | None) -> list[ApplicationTool[Any, Any]]:
        if names is None:
            return list(self._tools.values())
        return [self._tools[name] for name in names if name in self._tools]

    @staticmethod
    def _failure(call: ToolCall, started_at: float, error: str) -> ToolExecutionResult:
        return ToolExecutionResult(
            call_id=call.call_id,
            name=call.name,
            success=False,
            error=error,
            duration_ms=round((perf_counter() - started_at) * 1000),
        )
