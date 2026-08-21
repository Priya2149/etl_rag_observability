from pydantic import BaseModel, Field


class WorkflowRequest(BaseModel):
    dataset_id: int | None = None
    question: str | None = None


class AgentQueryRequest(BaseModel):
    query: str = Field(min_length=1, max_length=4000)


class AgentWorkflowMetadata(BaseModel):
    selected_route: str
    tool_call_count: int = 0
    tool_execution_duration_ms: int = 0
    tool_iterations: int = 0
    retries: int = 0
    errors: list[str] = Field(default_factory=list)
    usage: dict[str, int | None] = Field(default_factory=dict)


class AgentQueryResponse(BaseModel):
    answer: str = Field(min_length=1)
    sources: list[str] = Field(default_factory=list)
    tools_used: list[str] = Field(default_factory=list)
    request_id: str
    provider: str
    model: str
    workflow: AgentWorkflowMetadata
