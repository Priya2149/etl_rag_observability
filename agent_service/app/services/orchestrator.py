import json
import time

from app.models import WorkflowStep
from app.services.planner_agent import run_planner
from app.services.etl_agent import run_etl_agent
from app.services.rag_agent import run_rag_agent
from app.services.evaluator_agent import run_evaluator
from app.services.report_agent import build_report
from app.services.tool_client import get_etl_run_details, ask_rag_service


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

        start = time.perf_counter()
        etl_result = run_etl_agent(payload, get_etl_run_details)
        add_step(
            db,
            workflow.id,
            "etl_agent",
            "etl_context_fetch",
            etl_result.get("status", "completed"),
            payload,
            etl_result,
            int((time.perf_counter() - start) * 1000),
        )

        start = time.perf_counter()
        rag_result = run_rag_agent(payload, ask_rag_service)
        add_step(
            db,
            workflow.id,
            "rag_agent",
            "rag_retrieval",
            rag_result.get("status", "completed"),
            payload,
            rag_result,
            int((time.perf_counter() - start) * 1000),
        )

        start = time.perf_counter()
        evaluation_result = run_evaluator(etl_result, rag_result)
        add_step(
            db,
            workflow.id,
            "evaluator_agent",
            "evaluation",
            "completed",
            {
                "etl_result": etl_result,
                "rag_result": rag_result,
            },
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

    planner_result = {}
    etl_result = {}
    rag_result = {}
    evaluation_result = {}

    for step in steps:
        output = json.loads(step.output_payload) if step.output_payload else {}

        if step.step_name == "planning":
            planner_result = output
        elif step.step_name == "etl_context_fetch":
            etl_result = output
        elif step.step_name == "rag_retrieval":
            rag_result = output
        elif step.step_name == "evaluation":
            evaluation_result = output

    start = time.perf_counter()
    final_report = build_report(
        planner_result=planner_result,
        etl_result=etl_result,
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
            "etl_result": etl_result,
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