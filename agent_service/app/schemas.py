from pydantic import BaseModel


class WorkflowRequest(BaseModel):
    dataset_id: int | None = None
    question: str | None = None