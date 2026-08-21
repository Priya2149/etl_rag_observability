from pydantic import BaseModel, ConfigDict, Field

from shared.tools import ApplicationTool, ToolCall, ToolExecutionError, ToolRegistry


class LookupInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    run_id: int | None = Field(default=None, ge=1)


class LookupOutput(BaseModel):
    summary: str


def registry(handler=lambda payload: LookupOutput(summary=str(payload.run_id))):
    return ToolRegistry(
        [
            ApplicationTool(
                name="lookup",
                description="Look up a run.",
                input_model=LookupInput,
                output_model=LookupOutput,
                handler=handler,
            )
        ]
    )


def test_openai_tool_definition_is_strict_and_nullable_fields_are_required():
    definition = registry().definitions()[0]

    assert definition["type"] == "function"
    assert definition["name"] == "lookup"
    assert definition["strict"] is True
    assert definition["parameters"]["additionalProperties"] is False
    assert definition["parameters"]["required"] == ["run_id"]


def test_tool_arguments_are_validated_before_execution():
    result = registry().execute(
        ToolCall(call_id="call-1", name="lookup", arguments={"run_id": 0})
    )

    assert result.success is False
    assert result.error == "Invalid arguments for tool 'lookup'."


def test_tool_rejects_malformed_model_arguments_even_when_fields_are_optional():
    result = registry().execute(
        ToolCall(
            call_id="call-1",
            name="lookup",
            arguments={},
            arguments_valid=False,
        )
    )

    assert result.success is False
    assert result.error == "Invalid arguments for tool 'lookup'."


def test_tool_execution_returns_typed_data_and_duration():
    result = registry().execute(
        ToolCall(call_id="call-1", name="lookup", arguments={"run_id": 7})
    )

    assert result.success is True
    assert result.data == {"summary": "7"}
    assert result.duration_ms >= 0


def test_tool_failure_is_sanitized():
    def fail(_):
        raise ValueError("database password appeared here")

    result = registry(fail).execute(
        ToolCall(call_id="call-1", name="lookup", arguments={"run_id": None})
    )

    assert result.success is False
    assert result.error == "Tool 'lookup' failed."


def test_safe_tool_errors_are_preserved():
    def fail(_):
        raise ToolExecutionError("Run was not found.")

    result = registry(fail).execute(
        ToolCall(call_id="call-1", name="lookup", arguments={"run_id": None})
    )

    assert result.error == "Run was not found."
