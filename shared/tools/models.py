from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ToolInput(BaseModel):
    model_config = ConfigDict(extra="forbid")


class SearchDocumentsInput(ToolInput):
    query: str = Field(min_length=1, max_length=4000)


class DatasetSchemaInput(ToolInput):
    run_id: int | None = Field(default=None, ge=1)


class DatasetProfileInput(ToolInput):
    run_id: int | None = Field(default=None, ge=1)


class PipelineStatusInput(ToolInput):
    run_id: int | None = Field(default=None, ge=1)


class SearchDocumentsOutput(BaseModel):
    query: str
    retrieved_chunks: list[dict[str, Any]] = Field(default_factory=list)
    sources: list[str] = Field(default_factory=list)
    evaluation: dict[str, Any] = Field(default_factory=dict)
    summary: str


class DatasetSchemaOutput(BaseModel):
    run_id: int
    filename: str
    columns: list[dict[str, Any]] = Field(default_factory=list)
    schema_issues: list[str] = Field(default_factory=list)
    summary: str


class DatasetProfileOutput(BaseModel):
    run_id: int
    filename: str
    status: str
    quality_score: int | float | None = None
    total_rows: int | None = None
    total_columns: int | None = None
    anomalies: Any = None
    profile: dict[str, Any] | None = None
    summary: str


class PipelineStatusOutput(BaseModel):
    run_id: int
    filename: str
    status: str
    quality_score: int | float | None = None
    processing_time_ms: int | None = None
    error_message: str | None = None
    summary: str


class ToolCall(BaseModel):
    call_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    arguments: dict[str, Any] = Field(default_factory=dict)
    arguments_valid: bool = True


class ToolExecutionResult(BaseModel):
    call_id: str
    name: str
    success: bool
    data: dict[str, Any] | None = None
    error: str | None = None
    duration_ms: int = Field(default=0, ge=0)
    retries: int = Field(default=0, ge=0)
    sources: list[str] = Field(default_factory=list)
