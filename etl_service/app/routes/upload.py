from fastapi import APIRouter, UploadFile, File, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
import json

from app.db import get_db, SessionLocal
from app.models import PipelineRun
from app.services.file_handler import save_uploaded_file
from app.services.etl import process_data

router = APIRouter(prefix="/etl", tags=["ETL"])


def process_pipeline_run(run_id: int):
    db = SessionLocal()

    try:
        run = db.query(PipelineRun).filter(PipelineRun.id == run_id).first()
        if not run:
            return

        run.status = "running"
        db.commit()

        result = process_data(run.filepath)
        run.total_rows = result["summary"]["total_rows"]
        run.total_columns = result["summary"]["total_columns"]
        run.anomalies = json.dumps(result["anomalies"])
        run.profile = json.dumps(result["profile"])
        run.quality_score = result["quality_score"]
        run.processing_time_ms = result["processing_time_ms"]
        run.status = "completed"
        db.commit()

    except Exception as e:
        run = db.query(PipelineRun).filter(PipelineRun.id == run_id).first()
        if run:
            run.status = "failed"
            run.error_message = str(e)
            db.commit()
    finally:
        db.close()


@router.post("/upload")
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported right now.")

    file_path = save_uploaded_file(file)

    run = PipelineRun(
        filename=file.filename,
        filepath=file_path,
        status="pending"
    )

    db.add(run)
    db.commit()
    db.refresh(run)

    background_tasks.add_task(process_pipeline_run, run.id)

    return {
        "message": "File uploaded successfully. Processing started in background.",
        "run_id": run.id,
        "filename": run.filename,
        "status": run.status
    }


@router.get("/runs")
def get_runs(db: Session = Depends(get_db)):
    runs = db.query(PipelineRun).order_by(PipelineRun.created_at.desc()).all()

    return [
        {
            "id": run.id,
            "filename": run.filename,
            "status": run.status,
            "total_rows": run.total_rows,
            "total_columns": run.total_columns,
            "quality_score": run.quality_score,
            "processing_time_ms": run.processing_time_ms,
            "created_at": run.created_at,
            "updated_at": run.updated_at
        }
        for run in runs
    ]


@router.get("/runs/{run_id}")
def get_run_details(run_id: int, db: Session = Depends(get_db)):
    run = db.query(PipelineRun).filter(PipelineRun.id == run_id).first()

    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    return {
 "id": run.id,
        "filename": run.filename,
        "filepath": run.filepath,
        "status": run.status,
        "total_rows": run.total_rows,
        "total_columns": run.total_columns,
        "quality_score": run.quality_score,
        "processing_time_ms": run.processing_time_ms,
        "anomalies": json.loads(run.anomalies) if run.anomalies else None,
        "profile": json.loads(run.profile) if run.profile else None,
        "error_message": run.error_message,
        "created_at": run.created_at,
        "updated_at": run.updated_at
    }