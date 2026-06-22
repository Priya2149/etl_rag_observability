from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import json

from app.db import get_db
from app.models import WorkflowRun, WorkflowStep
from app.schemas import WorkflowRequest
from app.services.orchestrator import run_workflow, continue_after_approval
from app.services.langgraph_workflow import run_langgraph_until_approval, run_langgraph_report

router = APIRouter(prefix="/agent", tags=["Agent"])


@router.post("/workflow")
def create_workflow(request: WorkflowRequest, db: Session = Depends(get_db)):
    workflow = WorkflowRun(
        workflow_name="etl_rag_agentic_workflow",
        status="running",
        current_step="planning",
        input_payload=json.dumps(request.dict()),
    )

    db.add(workflow)
    db.commit()
    db.refresh(workflow)

    run_workflow(db, workflow)

    return {
        "workflow_id": workflow.id,
        "status": workflow.status,
        "current_step": workflow.current_step,
    }


@router.get("/workflows")
def list_workflows(db: Session = Depends(get_db)):
    workflows = db.query(WorkflowRun).order_by(WorkflowRun.created_at.desc()).all()

    return [
        {
            "id": workflow.id,
            "workflow_name": workflow.workflow_name,
            "status": workflow.status,
            "current_step": workflow.current_step,
            "created_at": workflow.created_at,
            "updated_at": workflow.updated_at,
        }
        for workflow in workflows
    ]


@router.get("/workflow/{workflow_id}")
def get_workflow(workflow_id: int, db: Session = Depends(get_db)):
    workflow = db.query(WorkflowRun).filter(WorkflowRun.id == workflow_id).first()

    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    steps = (
        db.query(WorkflowStep)
        .filter(WorkflowStep.workflow_run_id == workflow_id)
        .order_by(WorkflowStep.created_at.asc())
        .all()
    )

    return {
        "id": workflow.id,
        "workflow_name": workflow.workflow_name,
        "status": workflow.status,
        "current_step": workflow.current_step,
        "input_payload": json.loads(workflow.input_payload) if workflow.input_payload else None,
        "final_output": json.loads(workflow.final_output) if workflow.final_output else None,
        "error_message": workflow.error_message,
        "created_at": workflow.created_at,
        "updated_at": workflow.updated_at,
        "steps": [
            {
                "id": step.id,
                "agent_name": step.agent_name,
                "step_name": step.step_name,
                "status": step.status,
                "input_payload": json.loads(step.input_payload) if step.input_payload else None,
                "output_payload": json.loads(step.output_payload) if step.output_payload else None,
                "duration_ms": step.duration_ms,
                "error_message": step.error_message,
                "created_at": step.created_at,
            }
            for step in steps
        ],
    }


@router.post("/workflow/{workflow_id}/approve")
def approve_workflow(workflow_id: int, db: Session = Depends(get_db)):
    workflow = db.query(WorkflowRun).filter(WorkflowRun.id == workflow_id).first()

    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    if workflow.status != "waiting_for_approval":
        raise HTTPException(status_code=400, detail="Workflow is not waiting for approval")

    continue_after_approval(db, workflow)

    return {
        "workflow_id": workflow.id,
        "status": workflow.status,
        "current_step": workflow.current_step,
    }


@router.post("/workflow/{workflow_id}/reject")
def reject_workflow(workflow_id: int, db: Session = Depends(get_db)):
    workflow = db.query(WorkflowRun).filter(WorkflowRun.id == workflow_id).first()

    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    workflow.status = "rejected"
    workflow.current_step = "human_review"
    workflow.final_output = json.dumps({
        "message": "Workflow rejected during human review."
    })

    db.commit()

    return {
        "workflow_id": workflow.id,
        "status": workflow.status,
    }


@router.post("/workflow/{workflow_id}/retry")
def retry_workflow(workflow_id: int, db: Session = Depends(get_db)):
    workflow = db.query(WorkflowRun).filter(WorkflowRun.id == workflow_id).first()

    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    if workflow.status != "failed":
        raise HTTPException(status_code=400, detail="Only failed workflows can be retried")

    workflow.status = "running"
    workflow.current_step = "planning"
    workflow.error_message = None

    db.commit()
    db.refresh(workflow)

    run_workflow(db, workflow)

    return {
        "workflow_id": workflow.id,
        "status": workflow.status,
        "current_step": workflow.current_step,
    }
@router.post("/workflow/langgraph")
def create_langgraph_workflow(request: WorkflowRequest, db: Session = Depends(get_db)):
    workflow = WorkflowRun(
        workflow_name="langgraph_etl_rag_workflow",
        status="running",
        current_step="planning",
        input_payload=json.dumps(request.dict()),
    )

    db.add(workflow)
    db.commit()
    db.refresh(workflow)

    try:
        state = run_langgraph_until_approval(request.dict())

        workflow.status = state.get("status", "waiting_for_approval")
        workflow.current_step = state.get("current_step", "human_review")

        db.commit()

        return {
            "workflow_id": workflow.id,
            "engine": "langgraph",
            "status": workflow.status,
            "current_step": workflow.current_step,
            "state": state,
        }

    except Exception as e:
        workflow.status = "failed"
        workflow.error_message = str(e)
        db.commit()

        raise HTTPException(status_code=500, detail=str(e))


@router.post("/workflow/{workflow_id}/langgraph/approve")
def approve_langgraph_workflow(workflow_id: int, db: Session = Depends(get_db)):
    workflow = db.query(WorkflowRun).filter(WorkflowRun.id == workflow_id).first()

    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    if workflow.status != "waiting_for_approval":
        raise HTTPException(status_code=400, detail="Workflow is not waiting for approval")

    input_payload = json.loads(workflow.input_payload) if workflow.input_payload else {}
    state = run_langgraph_until_approval(input_payload)
    final_state = run_langgraph_report(state)

    workflow.status = "completed"
    workflow.current_step = "finished"
    workflow.final_output = json.dumps(final_state.get("final_report"))

    db.commit()

    return {
        "workflow_id": workflow.id,
        "engine": "langgraph",
        "status": workflow.status,
        "final_output": final_state.get("final_report"),
    }