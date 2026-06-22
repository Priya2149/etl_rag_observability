import json
import time

from app.models import (
    WorkflowStep
)

from app.services.planner_agent import (
    run_planner
)

from app.services.evaluator_agent import (
    run_evaluator
)

from app.services.report_agent import (
    build_report
)
def add_step(
    db,
    workflow_id,
    agent_name,
    step_name,
    status,
    input_payload,
    output_payload,
    duration_ms,
    error_message=None,
):
    step = WorkflowStep(
        workflow_run_id=workflow_id,
        agent_name=agent_name,
        step_name=step_name,
        status=status,
        input_payload=json.dumps(input_payload),
        output_payload=json.dumps(output_payload),
        duration_ms=duration_ms,
        error_message=error_message,
    )

    db.add(step)
    db.commit()


def run_workflow(db, workflow):
    try:
        payload = json.loads(workflow.input_payload) if workflow.input_payload else {}

        start = time.perf_counter()
        planner_result = run_planner(payload)
        add_step(
            db,
            workflow.id,
            "planner_agent",
            "planning",
            "completed",
            payload,
            planner_result,
            int((time.perf_counter() - start) * 1000),
        )

        # This should be replaced with your real ETL/RAG service calls
        rag_result = {
            "chunks_used": 1,
            "retrieved_count": 1,
            "risk_level": "low",
            "answer": "Workflow prepared for human review."
        }

        add_step(
            db,
            workflow.id,
            "rag_agent",
            "retrieval",
            "completed",
            payload,
            rag_result,
            50,
        )

        start = time.perf_counter()
        evaluation_result = run_evaluator(rag_result)
        add_step(
            db,
            workflow.id,
            "evaluator_agent",
            "evaluation",
            "completed",
            rag_result,
            evaluation_result,
            int((time.perf_counter() - start) * 1000),
        )

        workflow.status = "waiting_for_approval"
        workflow.current_step = "human_review"
        db.commit()

    except Exception as e:
        workflow.status = "failed"
        workflow.error_message = str(e)
        db.commit()

        add_step(
            db,
            workflow.id,
            "orchestrator",
            "workflow_execution",
            "failed",
            {},
            {},
            0,
            str(e),
        )


def continue_after_approval(db, workflow):
    steps = (
        db.query(WorkflowStep)
        .filter(WorkflowStep.workflow_run_id == workflow.id)
        .order_by(WorkflowStep.created_at.asc())
        .all()
    )

    planner_result = None
    rag_result = None
    evaluation_result = None

    for step in steps:
        if step.step_name == "planning":
            planner_result = json.loads(step.output_payload) if step.output_payload else {}
        elif step.step_name == "retrieval":
            rag_result = json.loads(step.output_payload) if step.output_payload else {}
        elif step.step_name == "evaluation":
            evaluation_result = json.loads(step.output_payload) if step.output_payload else {}

    start = time.perf_counter()
    final_report = build_report(
        planner_result=planner_result,
        rag_result=rag_result,
        evaluation_result=evaluation_result,
    )

    add_step(
        db,
        workflow.id,
        "report_agent",
        "report_generation",
        "completed",
        {
            "planner_result": planner_result,
            "rag_result": rag_result,
            "evaluation_result": evaluation_result,
        },
        final_report,
        int((time.perf_counter() - start) * 1000),
    )

    workflow.status = "completed"
    workflow.current_step = "finished"
    workflow.final_output = json.dumps(final_report)

    db.commit()