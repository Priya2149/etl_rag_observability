from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Text,
    ForeignKey
)

from sqlalchemy.orm import relationship
from datetime import datetime

from app.db import Base


class WorkflowRun(Base):
    __tablename__ = "workflow_runs"

    id = Column(Integer, primary_key=True, index=True)

    workflow_name = Column(String)

    status = Column(String)

    current_step = Column(String)

    input_payload = Column(Text)

    final_output = Column(Text)

    error_message = Column(Text)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    steps = relationship(
        "WorkflowStep",
        back_populates="workflow"
    )


class WorkflowStep(Base):
    __tablename__ = "workflow_steps"

    id = Column(Integer, primary_key=True)

    workflow_run_id = Column(
        Integer,
        ForeignKey("workflow_runs.id")
    )

    agent_name = Column(String)

    step_name = Column(String)

    status = Column(String)

    input_payload = Column(Text)

    output_payload = Column(Text)

    duration_ms = Column(Integer)

    error_message = Column(Text)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    workflow = relationship(
        "WorkflowRun",
        back_populates="steps"
    )